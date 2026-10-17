import asyncio
import copy
from datetime import date
from decimal import Decimal

import pandas as pd
import pyarrow.parquet as pq
import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.connectors import Connectors
from app.dashboard_models import ChartViewState
from app.errors import AppError
from app.hierarchy import adjust_plan, capture_history, distribute, evaluate_recipe, reconcile
from app.main import create_app
from app.maintenance import reset_history
from app.metric_examples import seed_metrics
from app.metrics import MetricAction, MetricDefinition, Metrics, MetricWrite, compile_metric
from app.planning_models import PlanningCreate
from app.report_models import ReportCreate
from app.report_repository import ReportRepository
from app.repository import Repository
from app.retail_generator import GeneratorConfig, generate
from app.storage import MemoryStore


@pytest.fixture(scope="module")
def bundle(tmp_path_factory):
    path = tmp_path_factory.mktemp("metrics") / "retail"
    generate(
        GeneratorConfig(
            start=date(2023, 1, 1),
            end=date(2023, 3, 31),
            orders_per_day=2,
            customers=64,
            products=8,
            stores=4,
        ),
        path,
    )
    return path


async def library():
    store, settings = MemoryStore(), Settings(data_profile="timeseries")
    await seed_metrics(store, settings)
    service = Metrics(store, settings)
    values = await store.list("metrics")
    return store, settings, service, {v["draft"]["name"]: v for v in values}


async def test_metrics_seed_roundtrip_versions_and_atomic_conflict():
    store, settings, service, metrics = await library()
    assert len(metrics) == 16
    assert await seed_metrics(store, settings) == []
    metric = metrics["Merchandise revenue"]
    old = await service.snapshot(metric["id"])
    definition = MetricDefinition.model_validate(
        metric["draft"] | {"description": "A new visitor definition."}
    )
    body = MetricWrite(
        definition=definition, expected_revision=metric["revision"], request_id="concurrent_change"
    )
    outcomes = await asyncio.gather(
        service.mutate("visitor", "draft", body, metric["id"]),
        service.mutate("other", "draft", body, metric["id"]),
        return_exceptions=True,
    )
    assert sum(isinstance(v, AppError) and v.status == 409 for v in outcomes) == 1
    current = await service.get(metric["id"])
    await service.mutate(
        "visitor",
        "publish",
        MetricAction(expected_revision=current["revision"], request_id="publish_new_version"),
        metric["id"],
    )
    assert (await service.snapshot(metric["id"], 1)) == old
    assert (await service.snapshot(metric["id"]))["version"] == 2


@pytest.mark.parametrize(
    "name,field",
    [
        ("Merchandise revenue", "revenue"),
        ("Gross merchandise sales", "gross_sales"),
        ("Discounts", "discount_amount"),
        ("Units sold", "units"),
    ],
)
async def test_compiler_matches_independent_order_totals(bundle, name, field):
    _, _, service, metrics = await library()
    snapshot = await service.snapshot(metrics[name]["id"])
    connectors = Connectors(Settings(data_profile="timeseries", retail_bundle_path=str(bundle)))
    await connectors.start()
    try:
        query = compile_metric(snapshot, "agentic_bi_demo", grain="total")
        result = await connectors.query("bigquery", query, "test_metric", 0)
        independent = sum(r[field] for r in pq.read_table(bundle / "sales_orders.parquet").to_pylist())
        assert Decimal(str(result.rows[0]["value"])) == independent
    finally:
        await connectors.close()


@pytest.mark.parametrize(
    "name",
    [
        "Average order value",
        "Merchandise margin",
        "Merchandise margin percentage",
        "Discount percentage",
        "Refund-date net revenue",
    ],
)
async def test_derived_components_are_aggregated_before_ratio(bundle, name):
    _, _, service, metrics = await library()
    snapshot = await service.snapshot(metrics[name]["id"])
    connectors = Connectors(Settings(data_profile="timeseries", retail_bundle_path=str(bundle)))
    await connectors.start()
    try:
        result = await connectors.query(
            "bigquery", compile_metric(snapshot, "agentic_bi_demo", grain="total"), "test_derived", 0
        )
        orders = pq.read_table(bundle / "sales_orders.parquet").to_pylist()
        items = pq.read_table(bundle / "sales_order_items.parquet").to_pylist()
        returns = pq.read_table(bundle / "sales_returns.parquet").to_pylist()
        revenue = sum(r["revenue"] for r in orders)
        margin = revenue - sum(r["cost_amount"] for r in items)
        expected = {
            "Average order value": revenue / len(orders),
            "Merchandise margin": margin,
            "Merchandise margin percentage": margin / revenue,
            "Discount percentage": sum(r["discount_amount"] for r in orders)
            / sum(r["gross_sales"] for r in orders),
            "Refund-date net revenue": revenue - sum(r["refund_amount"] for r in returns),
        }[name]
        assert float(result.rows[0]["value"]) == pytest.approx(float(expected))
        assert (
            "numerator" in result.rows[0]
            if "value" in name or "percentage" in name
            else "left_component" in result.rows[0]
        )
    finally:
        await connectors.close()


@pytest.mark.parametrize(
    "patch",
    [
        {"formula": {"operation": "sum", "measure": "password"}},
        {"formula": {"operation": "sum", "measure": "orders"}},
        {"formula": {"operation": "sum", "measure": "revenue; DELETE FROM sales_orders"}},
        {"unit": "percent"},
        {"time_basis": "refund_date", "formula": {"operation": "sum", "measure": "cost"}},
    ],
)
async def test_metric_invalid_definitions_never_compile(patch):
    _, _, service, metrics = await library()
    d = MetricDefinition.model_validate(metrics["Merchandise revenue"]["draft"] | patch)
    with pytest.raises(AppError):
        await service.validate(d)


def history_fixture():
    months = pd.date_range("2023-01-01", periods=45, freq="MS").strftime("%Y-%m").tolist()
    stores = [
        {"store_id": "A", "store_name": "A", "region": "North"},
        {"store_id": "B", "store_name": "B", "region": "South"},
    ]
    sr, pr = [], []
    for i, month in enumerate(months):
        value = 100 + (i % 12) * 10
        sr += [
            {"month": month, "store_id": "A", "value": str(value)},
            {"month": month, "store_id": "B", "value": str(value * 2)},
        ]
        pr += [
            {
                "month": month,
                "product_id": "X",
                "product_name": "X",
                "category": "Goods",
                "value": str(value),
            },
            {
                "month": month,
                "product_id": "Y",
                "product_name": "Y",
                "category": "Goods",
                "value": str(value * 2),
            },
        ]
    return capture_history(sr, pr, stores, months)


def coherent(predictions, nodes):
    for level in ("region", "category"):
        ids = [k for k, n in nodes.items() if n["level"] == level]
        for i, value in enumerate(predictions["company"]):
            assert sum(Decimal(str(predictions[k][i])) for k in ids) == Decimal(str(value))
    for key, node in nodes.items():
        children = [k for k, n in nodes.items() if n["parent"] == key]
        if children and key != "company":
            for i, value in enumerate(predictions[key]):
                assert sum(Decimal(str(predictions[k][i])) for k in children) == Decimal(str(value))


def plan_fixture():
    history = history_fixture()
    return {
        "history": history,
        "predictions": reconcile(history, {}, 45, 3, baseline=True),
        "horizon": 3,
        "kind": "statistical_forecast",
        "adjustments": [],
    }


def test_reconciliation_cents_zeros_and_whole_recipe_gate():
    assert distribute(1, [1, 1, 1]) == [0.34, 0.33, 0.33]
    assert distribute(0, [0, 0]) == [0, 0]
    with pytest.raises(AppError):
        distribute(1, [0, 0])
    history = history_fixture()
    baseline = reconcile(history, {}, 45, 3, baseline=True)
    coherent(baseline, history["nodes"])
    folds = []
    for origin in (36, 39, 42):
        folds.append(
            {
                key: [float(v) for v in node["history"][origin : origin + 3]]
                for key, node in history["nodes"].items()
                if node["level"] in {"company", "region", "category"}
            }
        )
    result = evaluate_recipe(history, folds, 3)
    assert result["selected"] == "coherent_seasonal_naive"  # exact seasonal baseline cannot be beaten


def test_complete_recipe_promotes_better_forecasts_with_training_only_allocations():
    history = history_fixture()
    for node in history["nodes"].values():
        node["history"] = [str(Decimal(v) * (100 + i) / 100) for i, v in enumerate(node["history"])]
    folds = [
        {
            key: [float(v) for v in node["history"][origin : origin + 3]]
            for key, node in history["nodes"].items()
            if node["level"] in {"company", "region", "category"}
        }
        for origin in (36, 39, 42)
    ]
    score = evaluate_recipe(history, folds, 3)
    assert score["selected"] == "adaptive" and score["adaptive"] < score["baseline"] * 0.95


def test_metric_forecast_guard_rejects_changed_target_and_grain():
    from app.metric_forecasts import verify_forecast_values

    canonical = [{"date": "2026-01-01", "revenue": "100.00"}]
    verify_forecast_values(canonical, canonical, "date", "revenue")
    for changed in (
        [{"date": "2026-01-01", "revenue": 101}],
        canonical + canonical,
        [{"date": "2026-02-01", "revenue": 100}],
        [{"date": "2026-01-01", "revenue": None}],
    ):
        with pytest.raises(AppError):
            verify_forecast_values(changed, canonical, "date", "revenue")


async def test_catalog_forecast_aliases_weekly_partials_and_target_comparisons(bundle):
    from app.adk_sessions import FirestoreSessionService
    from app.ai import AI
    from app.report_models import ForecastSpec

    store, _, _, metrics = await library()
    settings = Settings(data_profile="timeseries", retail_bundle_path=str(bundle))
    connectors = Connectors(settings)
    await connectors.start()
    ai = AI(settings, FirestoreSessionService(store), connectors, store)
    try:
        monthly, _ = await ai.plan(
            "Monthly merchandise revenue",
            [],
            "all",
            "catalog_alias",
            forecast_spec=ForecastSpec(
                task_id="revenue", date_column="period", target="sales", grain="month"
            ),
        )
        result = await connectors.query("bigquery", monthly.queries[0].sql, "monthly_catalog", 0)
        assert set(result.rows[0]) == {"period", "sales"}
        assert monthly.metric_snapshots[0]["id"] == metrics["Merchandise revenue"]["id"]
        weekly, _ = await ai.plan(
            "Weekly merchandise revenue",
            [],
            "all",
            "weekly_alias",
            forecast_spec=ForecastSpec(task_id="revenue", date_column="period", target="sales", grain="week"),
        )
        result = await connectors.query("bigquery", weekly.queries[0].sql, "weekly_catalog", 0)
        assert str(result.rows[0]["period"])[:10] == "2023-01-02"  # partial initial Sunday is excluded
        target, _ = await ai.plan(
            "Monthly merchandise revenue compared with targets", [], "all", "catalog_target"
        )
        assert len(target.queries) == 2 and target.fusion is not None
        for i, q in enumerate(target.queries):
            result = await connectors.query(q.source, q.sql, "catalog_target", i)
            assert len(result.rows) == 3
    finally:
        await ai.close()
        await connectors.close()


@pytest.mark.parametrize("node", ["company", "region:North", "store:A", "category:Goods", "product:X"])
@pytest.mark.parametrize("operation,value", [("percent", 10), ("percent", -100), ("set", 123.45)])
def test_adjustments_remain_coherent_without_mutating_statistical_evidence(node, operation, value):
    document = plan_fixture()
    before = copy.deepcopy(document)
    adjusted = adjust_plan(document, node, operation, value, "Business planning assumption")
    coherent(adjusted["predictions"], adjusted["history"]["nodes"])
    assert adjusted["kind"] == "adjusted_plan" and document == before


async def test_shared_admission_fitting_profile_replay_and_fencing():
    store, settings = MemoryStore(), Settings(report_guest_daily_limit=2, report_workspace_daily_limit=2)
    repo = ReportRepository(store, settings)
    body = PlanningCreate(objective="Quarterly retail planning", request_id="forecast_request")
    job = await repo.create_job("forecast", "g", body, {})
    replay = await repo.create_job("forecast", "g", body, {})
    assert replay["id"] == job["id"]
    lease = await repo.claim(job["id"])
    await repo.spend(lease, fits=128)
    with pytest.raises(AppError):
        await repo.spend(lease, fits=1)
    await repo.finish(lease, "failed", error="Test failure")
    assert not (await store.get("forecast_plans", job["root_id"]))["active_run"]
    conv = await Repository(store, settings).create_conversation("Normal report", "all")
    await repo.create(conv["id"], "g", ReportCreate(question="Revenue", idempotency_key="normal_report"))
    with pytest.raises(AppError) as exc:
        await repo.create_job(
            "dashboard",
            "another",
            PlanningCreate(objective="Retail dashboard", request_id="dashboard_request"),
            {},
        )
    assert exc.value.status == 429


async def test_metric_publication_and_forecast_job_api_validation(bundle):
    store, settings, _, metrics = await library()
    settings.report_dispatch = "disabled"
    settings.retail_bundle_path = str(bundle)
    with TestClient(create_app(settings, store_override=store)) as client:
        token = client.post("/api/v1/guest-sessions").json()["token"]
        assert len(client.get("/api/v1/metrics").json()["metrics"]) == 16
        response = client.post(
            "/api/v1/forecast-plans",
            json={
                "objective": "Retail forecast",
                "request_id": "request_1234",
                "metric": {"id": metrics["Merchandise revenue"]["id"], "version": 1},
            },
            headers={"Authorization": "Bearer " + token},
        )
        assert response.status_code == 503
        assert client.post("/api/v1/metrics", json={}).status_code in {401, 422}


async def test_metric_archival_keeps_published_dependency_and_reset_history():
    store, _, service, metrics = await library()
    metric = metrics["Merchandise revenue"]
    snap = await service.snapshot(metric["id"])
    await service.mutate(
        "guest",
        "archive",
        MetricAction(expected_revision=metric["revision"], request_id="archive_metric"),
        metric["id"],
    )
    assert await service.snapshot(metric["id"], 1) == snap
    with pytest.raises(AppError):
        await service.snapshot(metric["id"])
    await reset_history(store)
    assert (await service.get(metric["id"]))["archived"]


async def test_dashboard_job_review_atomic_publication_replay_and_undo(bundle, monkeypatch):
    from unittest.mock import AsyncMock

    store, settings, _, _ = await library()
    settings.retail_bundle_path = str(bundle)
    settings.report_dispatch = "cloud_tasks"
    with TestClient(create_app(settings, store_override=store)) as client:
        s = client.app.state.services
        monkeypatch.setattr(s.report_dispatcher, "enqueue", AsyncMock())
        headers = {"Authorization": "Bearer " + client.post("/api/v1/guest-sessions").json()["token"]}
        response = client.post(
            "/api/v1/dashboard-builds",
            headers=headers,
            json={"objective": "Create a revenue dashboard", "request_id": "dashboard_build_e2e"},
        )
        assert response.status_code == 202, response.text
        run_id = response.json()["id"]
        client.portal.call(s.report_engine.work, run_id)
        response = client.get(f"/api/v1/dashboard-builds/{run_id}", headers=headers)
        root = response.json()
        assert root["status"] == "review", root
        assert len(root["proposal"]["cards"]) == 4
        assert client.get("/api/v1/dashboards").json()["dashboards"] == []
        assert client.get("/api/v1/reports").json()["reports"] == []
        body = {"expected_revision": root["revision"], "request_id": "publish_dashboard_e2e"}
        result = client.post(f"/api/v1/dashboard-builds/{run_id}/publish", headers=headers, json=body)
        assert result.status_code == 200, result.text
        replay = client.post(f"/api/v1/dashboard-builds/{run_id}/publish", headers=headers, json=body)
        assert replay.json() == result.json()
        board = client.get("/api/v1/dashboards/" + result.json()["dashboard_id"]).json()
        assert board["card_count"] == 4
        undo = client.post(
            f"/api/v1/dashboard-builds/{run_id}/undo",
            headers=headers,
            json={
                "expected_revision": result.json()["build"]["revision"],
                "request_id": "undo_dashboard_e2e",
            },
        )
        assert undo.status_code == 200, undo.text
        assert client.get("/api/v1/dashboards/" + board["id"]).json()["card_count"] == 0
        current = client.get(f"/api/v1/dashboards/{board['id']}").json()
        monkeypatch.setattr(s.connectors, "query", AsyncMock(side_effect=AssertionError("Saved reuse only")))
        second = client.post(
            "/api/v1/dashboard-builds",
            headers=headers,
            json={
                "objective": "Create a revenue dashboard",
                "request_id": "improve_existing_dashboard",
                "dashboard_id": board["id"],
                "expected_revision": current["revision"],
            },
        ).json()
        client.portal.call(s.report_engine.work, second["id"])
        built = client.get(f"/api/v1/dashboard-builds/{second['id']}", headers=headers).json()
        assert built["status"] == "review", built
        assert all(c["reused"] for c in built["proposal"]["cards"])
        current["revision"] += 1
        client.portal.call(
            store.put, "dashboards", board["id"], {k: v for k, v in current.items() if k != "items"}
        )
        conflict = client.post(
            f"/api/v1/dashboard-builds/{second['id']}/publish",
            headers=headers,
            json={"expected_revision": built["revision"], "request_id": "conflict_build"},
        )
        assert conflict.status_code == 409
        rebased = client.patch(
            f"/api/v1/dashboard-builds/{second['id']}",
            headers=headers,
            json={
                **{k: v for k, v in built["proposal"].items() if k != "omitted"},
                "expected_revision": built["revision"],
                "request_id": "rebase_existing",
                "rebase": True,
            },
        )
        assert rebased.status_code == 200, rebased.text
        applied = client.post(
            f"/api/v1/dashboard-builds/{second['id']}/publish",
            headers=headers,
            json={
                "expected_revision": rebased.json()["revision"],
                "request_id": "publish_rebased",
            },
        )
        assert applied.status_code == 200, applied.text


async def test_full_forecast_worker_saved_versions_exports_and_dashboard_pin(tmp_path, monkeypatch):
    from unittest.mock import AsyncMock

    path = tmp_path / "history"
    generate(
        GeneratorConfig(
            start=date(2023, 1, 1),
            end=date(2026, 9, 30),
            orders_per_day=2,
            customers=64,
            products=8,
            stores=4,
        ),
        path,
    )
    store, settings, _, metrics = await library()
    settings.retail_bundle_path = str(path)
    settings.report_dispatch = "cloud_tasks"
    settings.report_local_directory = str(tmp_path / "exports")
    with TestClient(create_app(settings, store_override=store)) as client:
        s = client.app.state.services
        monkeypatch.setattr(s.report_dispatcher, "enqueue", AsyncMock())
        headers = {"Authorization": "Bearer " + client.post("/api/v1/guest-sessions").json()["token"]}
        response = client.post(
            "/api/v1/forecast-plans",
            headers=headers,
            json={
                "objective": "Plan quarterly revenue across stores and products",
                "request_id": "full_forecast_plan",
                "hierarchy": "products",
                "metric": {"id": metrics["Merchandise revenue"]["id"], "version": 1},
            },
        )
        assert response.status_code == 202, response.text
        run_id = response.json()["id"]
        client.portal.call(s.report_engine.work, run_id)
        run = client.get("/api/v1/report-runs/" + run_id).json()
        assert run["status"] == "complete", run
        root = client.get("/api/v1/forecast-plans/" + run_id).json()
        saved = client.get(f"/api/v1/forecast-plans/{run_id}/revisions/1").json()
        doc = saved["document"]
        assert doc["preferred_view"] == "products"
        assert len(doc["history"]["months"]) == 45 and doc["future_months"] == [
            "2026-10",
            "2026-11",
            "2026-12",
        ]
        coherent(doc["predictions"], doc["history"]["nodes"])
        for fmt, signature in (("pdf", b"%PDF"), ("data", b"PK"), ("json", b"{")):
            downloaded = client.get(f"/api/v1/forecast-plans/{run_id}/revisions/1/downloads/{fmt}")
            assert downloaded.status_code == 200 and downloaded.content.startswith(signature), (
                downloaded.text[:200]
            )
        # Opening, chart preparation, downloads and adjustments cannot run new source queries.
        monkeypatch.setattr(
            s.connectors, "query", AsyncMock(side_effect=AssertionError("No inference on saved views"))
        )
        artifact = client.post(
            f"/api/v1/forecast-plans/{run_id}/revisions/1/artifacts/company", headers=headers
        )
        assert artifact.status_code == 200
        adjusted = client.post(
            f"/api/v1/forecast-plans/{run_id}/adjustments",
            headers=headers,
            json={
                "expected_revision": root["revision"],
                "base_version": 1,
                "node_id": "company",
                "operation": "percent",
                "value": 10,
                "reason": "Visitor business assumption",
                "request_id": "saved_adjustment",
            },
        )
        assert adjusted.status_code == 200, adjusted.text
        newer = client.get(f"/api/v1/forecast-plans/{run_id}/revisions/2").json()["document"]
        coherent(newer["predictions"], newer["history"]["nodes"])
        import hashlib
        import json

        adjusted_files = {
            fmt: client.get(f"/api/v1/forecast-plans/{run_id}/revisions/2/downloads/{fmt}").content
            for fmt in ("pdf", "data", "json")
        }
        manifest = json.loads(adjusted_files["json"])
        for fmt in ("pdf", "data"):
            assert manifest["export_checksums"][fmt] == hashlib.sha256(adjusted_files[fmt]).hexdigest(), (
                fmt,
                len(adjusted_files[fmt]),
                adjusted_files[fmt][:100],
            )
        assert client.get(f"/api/v1/forecast-plans/{run_id}/revisions/1").json()["document"] == doc
        board = client.post(
            "/api/v1/dashboards",
            headers=headers,
            json={"name": "Planning results", "request_id": "planning_board"},
        ).json()["dashboard"]
        pinned = client.post(
            f"/api/v1/dashboards/{board['id']}/items",
            headers=headers,
            json={
                "expected_revision": board["revision"],
                "request_id": "pin_saved_forecast",
                "artifact_id": artifact.json()["id"],
                "title": "Company plan",
                "view": ChartViewState(
                    view="line", primary="observed", visible_measures=["observed", "forecast"]
                ).model_dump(mode="json"),
            },
        )
        assert pinned.status_code == 200, pinned.text
        assert client.get(f"/api/v1/dashboards/{board['id']}").json()["card_count"] == 1


async def test_numerical_preview_is_saved_and_idempotent(bundle):
    from types import SimpleNamespace

    from app.metrics import MetricQuery

    store, settings, service, metrics = await library()
    settings.retail_bundle_path = str(bundle)
    connectors = Connectors(settings)
    await connectors.start()
    calls = 0
    original = connectors.query

    async def counted(*args, **kwargs):
        nonlocal calls
        calls += 1
        return await original(*args, **kwargs)

    connectors.query = counted
    services = SimpleNamespace(connectors=connectors)
    body = MetricQuery(start=date(2023, 1, 1), end=date(2023, 3, 31), request_id="saved_preview_001")
    try:
        a = await service.preview(services, "visitor", metrics["Merchandise revenue"]["id"], body)
        b = await service.preview(services, "visitor", metrics["Merchandise revenue"]["id"], body)
        assert a == b and calls == 1
        with pytest.raises(AppError, match="Request ID already used"):
            await service.preview(
                services,
                "visitor",
                metrics["Merchandise revenue"]["id"],
                body.model_copy(update={"grain": "total"}),
            )
        assert all(v["count"] == 1 for v in await store.list("quotas"))
    finally:
        await connectors.close()


async def test_planning_expiry_preserves_report_and_dashboard_retention():
    from unittest.mock import AsyncMock

    from app.maintenance import purge_planning

    store, exports = MemoryStore(), AsyncMock()
    for pid in ("pinned", "reported", "expired"):
        await store.put("forecast_plans", pid, {"deleted": True, "recover_until": 1})
        await store.put("report_runs", pid, {"id": pid, "root_id": pid, "status": "complete"})
    await store.put("system", "forecast_plans_capacity", {"count": 3})
    await store.put("dashboard_artifact_refs", "a", {"count": 1})
    await store.put("artifacts", "a", {"forecast_plan_id": "pinned"})
    await store.put("plan_report_refs", "r", {"plan_id": "reported"})
    await store.put("dashboard_builds", "b", {"status": "review", "expires_at": 1})
    await store.put("report_runs", "b", {"id": "b", "root_id": "b", "status": "complete"})
    await store.put("system", "dashboard_builds_capacity", {"count": 1})
    result = await purge_planning(store, exports, now=10)
    assert result == {"dashboard_builds": 1, "forecast_plans": 1}
    assert await store.get("forecast_plans", "pinned")
    assert await store.get("forecast_plans", "reported")
    assert not await store.get("forecast_plans", "expired")
    assert (await store.get("system", "forecast_plans_capacity"))["count"] == 2


@pytest.mark.parametrize(
    "months,stores,products",
    [
        (["2023-01", "2023-03"], [{"store_id": "s", "region": "N"}], [{"product_id": "p", "category": "C"}]),
        (["2023-01"], [{"store_id": "s", "region": None}], [{"product_id": "p", "category": "C"}]),
        (["2023-01"], [{"store_id": "s", "region": "N"}], [{"product_id": "p", "category": ""}]),
    ],
)
async def test_hierarchy_refuses_calendar_gaps_and_null_parent_mappings(months, stores, products):
    with pytest.raises(AppError):
        capture_history([], [], stores, months, products)


async def test_competing_public_aliases_require_clarification(bundle):
    from app.ai import AI
    from app.metrics import catalog_plan

    store, settings, service, metrics = await library()
    definition = copy.deepcopy(metrics["Merchandise revenue"]["draft"])
    definition.update(name="Different sales definition", aliases=["revenue"])
    other = await service.mutate(
        "other",
        "create",
        MetricWrite(definition=MetricDefinition.model_validate(definition), request_id="conflicting_metric"),
    )
    await service.mutate(
        "other",
        "publish",
        MetricAction(expected_revision=other["revision"], request_id="conflicting_publish"),
        other["id"],
    )
    settings.retail_bundle_path = str(bundle)
    connectors = Connectors(settings)
    await connectors.start()
    ai = AI(settings, None, connectors, store)
    try:
        plan = await catalog_plan(ai, "Monthly revenue", [], "all", "alias_test")
        assert plan.clarification and not plan.queries
        explicit = await catalog_plan(ai, "Monthly " + other["id"], [], "all", "alias_specific")
        assert explicit.metric_snapshots[0]["id"] == other["id"] and explicit.queries
    finally:
        await ai.close()
        await connectors.close()


def test_release_preparation_preserves_timesfm_planning_and_dataset_configuration():
    import runpy
    from pathlib import Path

    helper = runpy.run_path(str(Path(__file__).resolve().parents[2] / "infra/runtime_settings.py"))
    prior = {
        "DATA_PROFILE": "timeseries",
        "SOURCE_ROW_LIMIT": "30000",
        "REPORT_TIMESFM_ENABLED": "true",
        "REPORT_TIMESFM_VERIFIED": "true",
        "REPORT_FITS": "64",
        "PLANNING_ENABLED": "true",
        "FORECAST_PLAN_FIT_LIMIT": "96",
    }
    env = helper["preserve_analysis_settings"]({"DATA_PROFILE": "timeseries"}, prior)
    assert all(env[k] == v for k, v in prior.items())
    fresh = helper["preserve_analysis_settings"]({"DATA_PROFILE": "timeseries"}, {})
    assert fresh["PLANNING_ENABLED"] == "false" and fresh["FORECAST_PLAN_FIT_LIMIT"] == "128"
    assert "REPORT_TIMESFM_ENABLED" not in fresh


async def test_multi_metric_answers_retain_ratio_component_evidence(bundle):
    from app.ai import AI
    from app.metrics import catalog_plan

    store, settings, _, _ = await library()
    settings.retail_bundle_path = str(bundle)
    connectors = Connectors(settings)
    await connectors.start()
    ai = AI(settings, None, connectors, store)
    try:
        plan = await catalog_plan(
            ai, "Monthly merchandise revenue and average order value", [], "all", "multi_metric"
        )
        result = await connectors.query("bigquery", plan.queries[0].sql, "multi_metric", 0)
        i = next(
            i for i, m in enumerate(plan.metric_snapshots) if m["definition"]["name"] == "Average order value"
        )
        for row in result.rows:
            assert Decimal(str(row[f"metric_{i}_numerator"])) / Decimal(
                str(row[f"metric_{i}_denominator"])
            ) == pytest.approx(Decimal(str(row[f"metric_{i}"])))
    finally:
        await ai.close()
        await connectors.close()


@pytest.mark.parametrize(
    "question,use_catalog",
    [
        ("Monthly merchandise revenue, not an ad hoc calculation.", True),
        ("Monthly merchandise revenue; don't use ad-hoc calculations.", True),
        ("Monthly merchandise revenue without any ad hoc definition.", True),
        ("Monthly merchandise revenue; avoid using an ad hoc definition.", True),
        ("Use an ad hoc calculation for monthly merchandise revenue.", False),
        ("Ad hoc monthly merchandise revenue.", False),
        ("Not ad hoc; actually use an ad hoc calculation for monthly merchandise revenue.", False),
    ],
)
async def test_explicit_catalog_request_is_not_negated_by_ad_hoc_mention(bundle, question, use_catalog):
    from app.ai import AI
    from app.metrics import catalog_plan

    store, settings, _, metrics = await library()
    settings.retail_bundle_path = str(bundle)
    connectors = Connectors(settings)
    await connectors.start()
    ai = AI(settings, None, connectors, store)
    try:
        plan = await catalog_plan(ai, question, [], "bigquery", "negated_ad_hoc")
        if use_catalog:
            assert not plan.clarification
            assert plan.metric_snapshots[0]["id"] == metrics["Merchandise revenue"]["id"]
            assert plan.metric_snapshots[0]["version"] == 1
            result = await connectors.query("bigquery", plan.queries[0].sql, "negated_ad_hoc", 0)
            assert result.complete and len(result.rows) == 3
        else:
            assert plan is None
    finally:
        await ai.close()
        await connectors.close()


async def test_dashboard_deduplicates_equivalent_questions_before_execution(bundle, monkeypatch):
    from unittest.mock import AsyncMock

    from app.models import AnalysisPlan, SourceQuery, VisualizationSpec
    from app.planning_models import DashboardBlueprint

    store, settings, _, metrics = await library()
    settings.retail_bundle_path = str(bundle)
    settings.report_dispatch = "disabled"
    with TestClient(create_app(settings, store_override=store)) as client:
        s = client.app.state.services
        body = PlanningCreate(objective="Revenue comparison", request_id="dedup_equivalent_cards")
        run = client.portal.call(
            s.reports.create_job, "dashboard", "guest", body, {"metric_snapshots": [], "manual_skills": []}
        )
        lease = client.portal.call(s.reports.claim, run["id"])
        client.portal.call(s.reports.checkpoint, lease, "skills", {"snapshots": [], "warnings": []})
        snapshot = await s.metrics.snapshot(metrics["Merchandise revenue"]["id"])
        analysis = AnalysisPlan(
            title="Revenue",
            queries=[
                SourceQuery(
                    source="bigquery",
                    sql=compile_metric(snapshot, settings.bigquery_dataset),
                    purpose="Revenue",
                )
            ],
            visualization=VisualizationSpec(type="line", title="Revenue", x="date", y=["value"]),
        )
        s.settings.ai_backend = "gemini"
        monkeypatch.setattr(
            s.ai,
            "_structured",
            AsyncMock(
                return_value=DashboardBlueprint(
                    title="Revenue",
                    description="Review",
                    questions=[
                        {
                            "id": "a",
                            "question": "Monthly revenue",
                            "title": "Trend",
                            "purpose": "Revenue trend",
                        },
                        {
                            "id": "b",
                            "question": "Show sales by month",
                            "title": "Sales",
                            "purpose": "Sales trend",
                        },
                    ],
                )
            ),
        )
        monkeypatch.setattr(s.ai, "plan", AsyncMock(return_value=(analysis, "fixture")))
        monkeypatch.setattr(s.ai, "schema", AsyncMock(return_value=[]))
        monkeypatch.setattr(
            s.connectors, "query", AsyncMock(side_effect=AssertionError("Preparation cannot execute SQL"))
        )
        client.portal.call(s.planning_engine.prepare_dashboard, run, lease, 0)
        planned = client.portal.call(s.reports.read_checkpoint, run["id"], "final_plan_0")
        assert len(planned["tasks"]) == 1
        assert any("equivalent saved evidence" in item for item in planned["omitted"])
        s.connectors.query.assert_not_called()
