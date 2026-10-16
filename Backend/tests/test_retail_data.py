import hashlib
import json
from dataclasses import replace
from datetime import date
from decimal import Decimal
from unittest.mock import Mock

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from app.adk_sessions import FirestoreSessionService
from app.ai import AI
from app.analysis import AnalysisService
from app.config import Settings
from app.connectors import Connectors
from app.errors import AppError
from app.repository import Repository
from app.retail_generator import GeneratorConfig, generate, read_manifest
from app.retail_schema import BY_NAME, SOURCE_TABLES
from app.retail_upload import merge_bigquery, upload_plan
from app.retail_validation import validate_bundle
from app.sql_guard import validate_sql
from app.storage import MemoryStore


@pytest.fixture(scope="module")
def bundle(tmp_path_factory):
    output = tmp_path_factory.mktemp("retail") / "history"
    config = GeneratorConfig(
        start=date(2023, 1, 1), end=date(2024, 3, 5), orders_per_day=2, customers=64, products=16, stores=4
    )
    generate(config, output)
    return output, config


def rows(directory, table):
    return pq.read_table(directory / f"{table}.parquet").to_pylist()


def test_full_reconciliation_and_zero_sales_date(bundle):
    directory, _ = bundle
    report = validate_bundle(directory)
    assert report["passed"] and len(report["checks"]) >= 25
    orders = rows(directory, "sales_orders")
    assert all(r["order_date"] != date(2024, 2, 29) for r in orders)
    assert any(r["calendar_date"] == date(2024, 2, 29) for r in rows(directory, "calendar"))
    assert any(r["return_date"] > r["order_date"] for r in rows(directory, "sales_returns"))
    assert len(rows(directory, "sales_order_items")) > len(orders)


def test_reproducible_files_and_existing_output_protection(bundle, tmp_path):
    directory, config = bundle
    again = generate(config, tmp_path / "again")
    original = read_manifest(directory)
    assert original == again
    with pytest.raises(ValueError, match="already exists"):
        generate(config, directory)


def test_extension_preserves_existing_keys_and_adds_delayed_refunds(bundle, tmp_path):
    directory, config = bundle
    new_dir = tmp_path / "extension"
    updated = generate(replace(config, end=date(2024, 4, 10)), new_dir)
    original = read_manifest(directory)
    assert original["configuration_id"] == updated["configuration_id"]
    for table in BY_NAME.values():
        old = {tuple(r[k] for k in table.key): r["record_hash"] for r in rows(directory, table.name)}
        new = {tuple(r[k] for k in table.key): r["record_hash"] for r in rows(new_dir, table.name)}
        assert all(new[k] == value for k, value in old.items()), table.name
    assert updated["files"]["sales_orders"]["rows"] > original["files"]["sales_orders"]["rows"]
    assert any(
        r["order_date"] <= config.end and r["return_date"] > config.end
        for r in rows(new_dir, "sales_returns")
    )


def test_corrupt_files_and_manifest_paths_are_rejected(bundle, tmp_path):
    import shutil

    directory, _ = bundle
    copied = tmp_path / "tampered"
    shutil.copytree(directory, copied)
    manifest = json.loads((copied / "manifest.json").read_text())
    manifest["files"]["sales_orders"]["file"] = "../outside.parquet"
    (copied / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="file path"):
        read_manifest(copied)
    manifest["files"]["sales_orders"]["file"] = "sales_orders.parquet"
    manifest["files"]["sales_orders"]["sha256"] = "bad"
    (copied / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="Checksum"):
        read_manifest(copied)


def test_independent_validation_detects_changed_money_even_with_updated_checksum(bundle, tmp_path):
    import shutil

    directory, _ = bundle
    copied = tmp_path / "bad-money"
    shutil.copytree(directory, copied)
    altered = rows(copied, "sales_orders")
    altered[0]["revenue"] += Decimal("1.00")
    path = copied / "sales_orders.parquet"
    pq.write_table(pa.Table.from_pylist(altered, schema=BY_NAME["sales_orders"].arrow_schema()), path)
    manifest = json.loads((copied / "manifest.json").read_text())
    manifest["files"]["sales_orders"]["sha256"] = hashlib.sha256(path.read_bytes()).hexdigest()
    (copied / "manifest.json").write_text(json.dumps(manifest))
    report = validate_bundle(copied)
    assert not report["passed"]
    assert any(not c["passed"] and "monetary" in c["check"] for c in report["checks"])


def test_upload_plan_does_not_request_credentials_and_targets_only_new_tables(bundle, monkeypatch):
    credentials = Mock(side_effect=AssertionError("No credentials in dry run"))
    monkeypatch.setattr("app.retail_upload.operator_credentials", credentials)
    plan = upload_plan(bundle[0])
    assert plan["postgres_schema"] == "retail_timeseries"
    assert {t["table"] for t in plan["tables"] if t["source"] == "bigquery"} == set(SOURCE_TABLES["bigquery"])
    assert not ({"orders", "order_items", "products", "returns"} & {t["table"] for t in plan["tables"]})
    credentials.assert_not_called()


def test_bigquery_publish_is_fenced_insert_only_and_one_transaction(monkeypatch):
    captured = []
    monkeypatch.setattr(
        "app.retail_upload.query", lambda client, sql, **kwargs: captured.append((sql, kwargs))
    )
    merge_bigquery(None, {name: f"stage_{name}" for name in SOURCE_TABLES["bigquery"]}, "owner")
    sql, params = captured[0]
    assert sql.count("BEGIN TRANSACTION") == sql.count("COMMIT TRANSACTION") == 1
    assert "Upload lease lost" in sql and params["owner"] == "owner"
    assert "WHEN MATCHED THEN UPDATE" not in sql and "DELETE FROM" not in sql
    assert sql.count("WHEN NOT MATCHED THEN INSERT") == 5
    assert sql.count("records differ") == 5


def test_expanded_schema_allowlist_does_not_expand_legacy_or_other_schemas():
    with pytest.raises(AppError):
        validate_sql("SELECT * FROM sales_orders", "bigquery", "p", "demo")
    assert "retail_timeseries" in validate_sql(
        "SELECT * FROM customer_profiles",
        "postgres",
        "p",
        "demo",
        tables=SOURCE_TABLES,
        postgres_schema="retail_timeseries",
    )
    for sql in [
        "SELECT * FROM retail.customer_profiles",
        "SELECT * FROM pg_catalog.pg_roles",
        "DELETE FROM customer_profiles",
    ]:
        with pytest.raises(AppError):
            validate_sql(
                sql, "postgres", "p", "demo", tables=SOURCE_TABLES, postgres_schema="retail_timeseries"
            )


async def test_time_series_pipeline_matches_independent_daily_monthly_and_yoy_values(bundle):
    directory, _ = bundle
    settings = Settings(data_profile="timeseries", retail_bundle_path=str(directory), guest_hourly_limit=100)
    connectors = Connectors(settings)
    store = MemoryStore()
    repo = Repository(store, settings)
    ai = AI(settings, FirestoreSessionService(store), connectors, store)
    analysis = AnalysisService(repo, connectors, ai, settings)
    data = rows(directory, "sales_orders")
    monthly = {}
    for row in data:
        monthly[row["month"]] = monthly.get(row["month"], Decimal(0)) + row["revenue"]

    async def ask(question):
        chat = await repo.create_conversation("Test", "all")
        run = await analysis.start(chat["id"], "guest", question, question.replace(" ", "-"))
        await analysis.tasks[run["id"]]
        assert (await repo.run(run["id"]))["status"] == "complete"
        artifact = next(a for a in await store.list("artifacts") if a["conversation_id"] == chat["id"])
        return [r for p in await store.list(f"artifacts/{artifact['id']}/pages") for r in p["rows"]]

    actual = await ask("Show monthly revenue")
    assert {r["month"]: Decimal(r["revenue"]) for r in actual} == monthly
    actual = await ask("Show YoY sales")
    jan = next(r for r in actual if r["month"] == "2024-01")
    assert Decimal(jan["previous_revenue"]) == monthly["2023-01"]
    expected = float((monthly["2024-01"] / monthly["2023-01"] - 1) * 100)
    assert float(jan["yoy_percent"]) == pytest.approx(expected, abs=0.011)
    actual = sorted(await ask("Show a 7-day rolling average"), key=lambda r: r["order_date"])
    leap = next(r for r in actual if r["order_date"] == "2024-02-29")
    assert Decimal(leap["revenue"]) == 0
    i = actual.index(leap)
    expected = sum(Decimal(r["revenue"]) for r in actual[i - 6 : i + 1]) / 7
    assert float(leap["rolling_7d"]) == pytest.approx(float(expected))
    actual = await ask("Compare monthly revenue with targets")
    assert len(actual) == 4 * len(monthly)
    assert sum(Decimal(r["revenue"]) for r in actual) == sum(monthly.values())


async def test_calendar_year_filters_preserve_rolling_lookback_and_followup_context(bundle):
    from app.retail_planner import timeseries_plan

    directory, _ = bundle
    connectors = Connectors(Settings(data_profile="timeseries", retail_bundle_path=str(directory)))
    plan = timeseries_plan("Show a seven-day rolling average in 2024", [], "all")
    result = await connectors.query("bigquery", plan.queries[0].sql, "rolling-boundary", 0)
    daily = {}
    for row in rows(directory, "sales_orders"):
        daily[row["order_date"]] = daily.get(row["order_date"], Decimal(0)) + row["revenue"]
    from datetime import timedelta

    expected = sum(daily.get(date(2024, 1, 1) - timedelta(days=d), Decimal(0)) for d in range(7)) / 7
    assert str(result.rows[0]["order_date"]) == "2024-01-01"
    assert float(result.rows[0]["rolling_7d"]) == pytest.approx(float(expected))
    history = [{"role": "user", "text": "Show monthly revenue"}, {"role": "user", "text": "Only 2024"}]
    plan = timeseries_plan("Only 2024", history, "all")
    result = await connectors.query("bigquery", plan.queries[0].sql, "followup-year", 0)
    assert all(r["month"].startswith("2024-") for r in result.rows)
    plan = timeseries_plan("Show daily revenue", [], "all")
    result = await connectors.query("bigquery", plan.queries[0].sql, "dense-daily", 0)
    assert any(str(r["order_date"]) == "2024-02-29" and r["revenue"] == 0 for r in result.rows)


@pytest.mark.parametrize(
    "overrides",
    [{"end": date(2018, 1, 1)}, {"orders_per_day": 0}, {"customers": 1}, {"stores": 5}, {"products": 2}],
)
def test_generator_rejects_invalid_ranges_and_sizes(overrides):
    with pytest.raises(ValueError):
        replace(GeneratorConfig(), **overrides).validate()


@pytest.mark.parametrize("status", ["ready", "loading", "failed", None])
async def test_cloud_profile_fails_closed_until_both_sources_are_published(status):
    connectors = Connectors(Settings(data_profile="timeseries", data_backend="cloud"))
    connectors.bq = Mock()
    connectors.bq.query.return_value.result.return_value = (
        []
        if status is None
        else [{"status": status, "anchor_start": date(2023, 1, 1), "end_date": date(2026, 9, 30)}]
    )
    if status == "ready":
        await connectors.ensure_data_ready()
        assert "2026-09-30" in connectors.data_context
    else:
        with pytest.raises(AppError) as failure:
            await connectors.ensure_data_ready()
        assert failure.value.code == "data_import_busy"


async def test_cloud_profile_reports_missing_or_unreadable_import_state():
    connectors = Connectors(Settings(data_profile="timeseries", data_backend="cloud"))
    connectors.bq = Mock()
    connectors.bq.query.side_effect = RuntimeError("metadata unavailable")
    with pytest.raises(AppError) as failure:
        await connectors.ensure_data_ready()
    assert failure.value.code == "data_not_ready"
