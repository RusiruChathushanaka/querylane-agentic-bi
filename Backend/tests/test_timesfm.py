import asyncio
import copy
import datetime as dt
import json
import threading
import time
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from google.api_core.exceptions import Forbidden, NotFound

from app.config import Settings
from app.connectors import Connectors
from app.errors import AppError
from app.report_forecasting import choose, compare, reserve_candidates
from app.report_models import ForecastSpec, ReportCreate
from app.report_repository import ReportRepository
from app.report_statistics import prepare_series
from app.repository import Repository
from app.sql_guard import validate_sql
from app.storage import MemoryStore
from app.timesfm import TimesFM, batches, contexts, digest, parse_output, policy, query


def spec(**kw):
    return ForecastSpec(task_id="trend", date_column="date", target="sales", grain="day", horizon=7, **kw)


def series(n=140, drivers=False):
    return [
        {
            "date": (dt.date(2025, 1, 1) + dt.timedelta(days=i)).isoformat(),
            "sales": 100 + i * 0.5 + (i % 7) * 2,
            **({"promotion": i % 2} if drivers else {}),
        }
        for i in range(n)
    ]


async def engine_run(**kwargs):
    settings = Settings(
        environment="test", report_timesfm_enabled=True, report_timesfm_verified=True, **kwargs
    )
    store = MemoryStore()
    repo = ReportRepository(store, settings)
    chat = await Repository(store, settings).create_conversation("Forecast", "all")
    run = await repo.create(
        chat["id"], "guest", ReportCreate(question="Forecast sales", idempotency_key=uuid.uuid4().hex)
    )
    lease = await repo.claim(run["id"])
    connectors = Connectors(settings)
    engine = SimpleNamespace(settings=settings, repo=repo, connectors=connectors, stage=AsyncMock())
    return engine, run, lease


def scores(error):
    return {"mae": error, "rmse": error, "folds": [{"mae": error} for _ in range(3)], "errors": [error] * 21}


def local_result(rows, s, *, scenario=False):
    final_dates = [
        (dt.date.fromisoformat(rows[-1]["date"]) + dt.timedelta(days=i + 1)).isoformat()
        for i in range(s.horizon)
    ]
    return {
        "method": "ets",
        "cutoff": rows[-1]["date"],
        "horizon": s.horizon,
        "grain": "day",
        "target": "sales",
        "drivers": s.drivers,
        "scenario_name": None,
        "assumptions": [],
        "limitations": [],
        "interval": None,
        "data_hash": digest(rows),
        "fits": 8,
        "fit_seconds": 1,
        "rows": [
            {"date": r["date"], "observed": r["sales"], "forecast": None, "scenario": None} for r in rows
        ]
        + [{"date": d, "observed": None, "forecast": 200, "scenario": None} for d in final_dates],
        "evaluation": {
            "seasonal_naive": scores(10),
            "ets": scores(8),
            **({"driver_ridge": scores(6)} if scenario else {}),
        },
        "scores": {},
        "scenario_candidate": {
            "method": "driver_ridge",
            "baseline": [200] * s.horizon,
            "scenario": [210] * s.horizon,
        }
        if scenario
        else None,
    }


def output(batch, values=None):
    return [
        {
            "series": name,
            "stamp": dt.date.fromisoformat(date),
            "predicted": values(name, date) if values else 100,
            "ai_forecast_status": "",
            "lower_bound": 80,
            "upper_bound": 120,
        }
        for name, dates in batch["expected"].items()
        for date in dates
    ]


@pytest.mark.parametrize("n", [45, 1369])
def test_full_monthly_daily_input_and_fold_cutoffs(n):
    import pandas as pd

    rows = series(n)
    s = spec()
    if n == 45:
        rows = [
            {"date": d.date().isoformat(), "sales": 100 + i}
            for i, d in enumerate(pd.date_range("2023-01-01", periods=45, freq="MS"))
        ]
        s = spec().model_copy(update={"grain": "month", "horizon": 3})
    p = prepare_series(rows, s.model_dump())
    batch = batches(p)
    for i, origin in enumerate([n - 3 * p["horizon"], n - 2 * p["horizon"], n - p["horizon"]]):
        group = [r for r in batch["rows"] if r["series"] == f"fold_{i}"]
        assert len(group) == origin
        assert group[-1]["stamp"] == rows[origin - 1]["date"]
        assert not set(r["stamp"] for r in group) & set(batch["expected"][f"fold_{i}"])
    assert len(batches(p, final=True)["rows"]) == n


@pytest.mark.parametrize("fault", ["gap", "duplicate", "null", "negative", "partial_input"])
def test_invalid_saved_history_is_never_imputed(fault):
    rows = series()
    if fault == "gap":
        rows.pop(20)
    if fault == "duplicate":
        rows.append(rows[0])
    if fault == "null":
        rows[0]["sales"] = None
    if fault == "negative":
        rows[0]["sales"] = -1
    if fault == "partial_input":
        rows = rows[:15]
    with pytest.raises(ValueError):
        prepare_series(rows, spec().model_dump())


def test_driver_context_is_explicit_and_future_targets_are_null():
    rows = series(140, True)
    s = spec(
        drivers=["promotion"], future_drivers=[{"promotion": 0}] * 7, scenario_drivers=[{"promotion": 1}] * 7
    )
    prepared = prepare_series(rows, s.model_dump())
    assert contexts(prepared) == [96] * 4
    for final in (False, True):
        batch = batches(prepared, final=final)
        for name, dates in batch["expected"].items():
            group = [r for r in batch["rows"] if r["series"] == name]
            assert sum(r["value"] is not None for r in group) == 96
            assert all(r["value"] is None for r in group if r["stamp"] in dates)
            assert len(group) == 96 + 7


def test_short_monthly_covariates_are_withheld_without_padding():
    import pandas as pd

    rows = [
        {"date": d.date().isoformat(), "sales": 100 + i, "promotion": i % 2}
        for i, d in enumerate(pd.date_range("2023-01-01", periods=45, freq="MS"))
    ]
    s = spec(drivers=["promotion"], future_drivers=[{"promotion": 0}] * 3).model_copy(
        update={"grain": "month", "horizon": 3}
    )
    with pytest.raises(ValueError, match="64 complete"):
        batches(prepare_series(rows, s.model_dump()))


@pytest.mark.parametrize("paths", [[], [{"promotion": 9}] * 7, [{"wrong": 0}] * 7])
def test_future_driver_assumptions_are_required_and_bounded(paths):
    s = spec(drivers=["promotion"], future_drivers=paths)
    with pytest.raises(ValueError):
        batches(prepare_series(series(drivers=True), s.model_dump()))


def test_model_sql_cannot_enable_forecasting():
    settings = Settings()
    with pytest.raises(AppError):
        validate_sql(
            "SELECT * FROM AI.FORECAST(TABLE sales_orders, data_col => 'revenue', timestamp_col => 'order_date')",
            "bigquery",
            settings.google_cloud_project,
            settings.bigquery_dataset,
        )


@pytest.mark.parametrize("driver", [False, True])
def test_fixed_query_uses_parameters_and_only_internal_aliases(driver):
    s = spec(drivers=["promotion"] if driver else [], future_drivers=[{"promotion": 0}] * 7 if driver else [])
    batch = batches(prepare_series(series(drivers=driver), s.model_dump()))
    sql = query(batch)
    assert "@payload" in sql and "TimesFM 3.0" in sql
    assert "sales_orders" not in sql and "promotion" not in sql
    assert ("future_covariate_cols" in sql) == driver
    assert "CROSS JOIN" not in sql


@pytest.mark.parametrize("fault", ["status", "unknown", "missing", "duplicate", "nan", "date"])
def test_provider_output_is_strictly_checked(fault):
    batch = batches(prepare_series(series(), spec().model_dump()))
    rows = output(batch)
    if fault == "status":
        rows[0]["ai_forecast_status"] = "error"
    if fault == "unknown":
        rows[0]["series"] = "other"
    if fault == "missing":
        rows.pop()
    if fault == "duplicate":
        rows.append(rows[0])
    if fault == "nan":
        rows[0]["predicted"] = float("nan")
    if fault == "date":
        rows[0]["stamp"] = dt.date(2000, 1, 1)
    with pytest.raises(AppError):
        parse_output(rows, batch)


@pytest.mark.parametrize("remote,expected", [(9, "ets"), (7, "timesfm_3"), (8, "ets"), (9.6, "ets")])
def test_promotion_requires_improvement_and_ties_favor_statistics(remote, expected):
    assert choose({"seasonal_naive": scores(10), "ets": scores(8), "timesfm_3": scores(remote)}) == expected


async def test_reservations_are_fenced_atomic_and_replayed_once():
    engine, run, lease = await engine_run()
    plan = {"tasks": [1], "forecasts": [spec().model_dump()]}
    a, b = await asyncio.gather(
        reserve_candidates(engine, run, lease, plan), reserve_candidates(engine, run, lease, plan)
    )
    assert a == b and a["0"]["admitted"]
    budgets = (await engine.repo.guard(lease))["budgets"]
    assert budgets["timesfm_targets"] == 1 and budgets["queries"] == 2
    assert (await engine.repo.get("report_runs", run["id"]))["workflow_version"] == 2
    stale = dict(lease, generation=lease["generation"] + 1)
    with pytest.raises(AppError, match="no longer owns"):
        await engine.repo.reserve_once(stale, "other", {}, {})


async def test_policy_frozen_and_default_off():
    assert not policy(Settings())["enabled"]
    assert not policy(Settings(report_timesfm_enabled=True))["enabled"]
    engine, run, lease = await engine_run()
    engine.settings.report_timesfm_enabled = False
    assert run["brief"]["forecast_policy"]["enabled"]
    plan = {"tasks": [1, 2, 3, 4, 5], "forecasts": [spec().model_dump()] * 3}
    result = await reserve_candidates(engine, run, lease, plan)
    assert sum(x["admitted"] for x in result.values()) == 1


@pytest.mark.parametrize("behavior", ["wins", "loses", "fails", "invalid_final", "budget"])
async def test_comparison_and_recovery_use_saved_local_evidence(monkeypatch, behavior):
    engine, run, lease = await engine_run()
    rows, s = series(), spec()
    await reserve_candidates(engine, run, lease, {"tasks": [1], "forecasts": [s.model_dump()]})
    local = local_result(rows, s)
    mock_local = AsyncMock(return_value=local)
    monkeypatch.setattr("app.report_forecasting.forecast", mock_local)
    calls = []

    async def execute(self, active, owner, operation, batch):
        calls.append(batch["phase"])
        if behavior in {"fails", "budget"}:
            raise AppError("Unavailable", 422, "timesfm_budget")

        def predicted(name, date):
            if batch["phase"] == "final":
                return -1 if behavior == "invalid_final" else 220
            source = next(r for r in rows if r["date"] == date)
            return source["sales"] + (1 if behavior in {"wins", "invalid_final"} else 15)

        return {
            "series": parse_output(output(batch, predicted), batch),
            "job_id": "test",
            "context": batch["context"],
        }

    monkeypatch.setattr(TimesFM, "execute", execute)
    result = await compare(engine, run, lease, 0, rows, s)
    assert result["method"] == ("timesfm_3" if behavior == "wins" else "ets")
    assert result["rows"][-1]["forecast"] == (220 if behavior == "wins" else 200)
    assert result["interval"] is None
    replay = await compare(engine, run, lease, 0, rows, s)
    assert replay == result and mock_local.await_count == 1
    assert len(calls) == (2 if behavior in {"wins", "invalid_final"} else 1)


async def test_scenario_uses_same_engine_for_baseline_and_alternative(monkeypatch):
    engine, run, lease = await engine_run()
    rows = series(drivers=True)
    s = spec(
        drivers=["promotion"], future_drivers=[{"promotion": 0}] * 7, scenario_drivers=[{"promotion": 1}] * 7
    )
    await reserve_candidates(engine, run, lease, {"tasks": [1], "forecasts": [s.model_dump()]})
    monkeypatch.setattr(
        "app.report_forecasting.forecast", AsyncMock(return_value=local_result(rows, s, scenario=True))
    )

    async def execute(self, active, owner, operation, batch):
        def value(name, date):
            if batch["phase"] == "final":
                return 250 if name == "scenario" else 230
            return next(r["sales"] for r in rows if r["date"] == date) + 1

        return {
            "series": parse_output(output(batch, value), batch),
            "context": batch["context"],
            "job_id": "scenario",
        }

    monkeypatch.setattr(TimesFM, "execute", execute)
    result = await compare(engine, run, lease, 0, rows, s)
    scenario = result["additional_predictions"][0]
    assert result["method"] == scenario["method"] == "timesfm_3"
    assert result["rows"][-1]["scenario"] is None
    assert scenario["rows"][-1]["forecast"] == 230 and scenario["rows"][-1]["scenario"] == 250


class FakeJob:
    def __init__(self, sql, config, batch):
        self.query, self.config, self.batch = sql, config, batch
        self.state = "DONE"
        self.error_result = None
        self.total_bytes_processed = 42
        self.cancelled = False

    def to_api_repr(self):
        return {"configuration": self.config.to_api_repr()}

    def result(self, **kwargs):
        return output(self.batch)

    def cancel(self, **kwargs):
        self.cancelled = True

    def reload(self, **kwargs):
        pass


class FakeClient:
    def __init__(self, batch):
        self.batch = batch
        self.job = None
        self.submissions = 0

    def get_job(self, *args, **kwargs):
        if self.job is None:
            raise NotFound("missing")
        return self.job

    def query(self, sql, job_config, **kwargs):
        if job_config.dry_run:
            return SimpleNamespace(total_bytes_processed=0)
        self.submissions += 1
        self.job = FakeJob(sql, job_config, self.batch)
        return self.job


async def test_adapter_reuses_existing_job_and_checkpoint_without_resubmission():
    engine, run, lease = await engine_run()
    await reserve_candidates(engine, run, lease, {"tasks": [1], "forecasts": [spec().model_dump()]})
    batch = batches(prepare_series(series(), spec().model_dump()))
    client = FakeClient(batch)
    engine.connectors.bq = client
    provider = TimesFM(engine.connectors, engine.repo)
    first = await provider.execute(run, lease, "0", batch)
    second = await provider.execute(run, lease, "0", batch)
    assert first == second and client.submissions == 1
    # Simulate a crash after external completion but before the result checkpoint.
    await engine.repo.store.delete(f"report_runs/{run['id']}/checkpoints", "timesfm_job_0_backtest_result")
    third = await provider.execute(run, lease, "0", batch)
    assert third["identity"] == first["identity"] and client.submissions == 1
    assert (await engine.repo.guard(lease))["budgets"]["timesfm_seconds"] < 2


@pytest.mark.parametrize("fault", ["identity", "permission", "status"])
async def test_adapter_failure_is_saved_without_new_job(monkeypatch, fault):
    engine, run, lease = await engine_run()
    await reserve_candidates(engine, run, lease, {"tasks": [1], "forecasts": [spec().model_dump()]})
    batch = batches(prepare_series(series(), spec().model_dump()))
    client = FakeClient(batch)
    engine.connectors.bq = client
    if fault == "permission":

        def reject(*a, **kw):
            raise Forbidden("private provider body")

        client.get_job = reject
    else:
        client.job = FakeJob(
            query(batch), SimpleNamespace(to_api_repr=lambda: {"queryParameters": []}), batch
        )
        if fault == "status":
            client.job.error_result = {"reason": "invalidQuery"}
    with pytest.raises(AppError):
        await TimesFM(engine.connectors, engine.repo).execute(run, lease, "0", batch)
    with pytest.raises(AppError):
        await TimesFM(engine.connectors, engine.repo).execute(run, lease, "0", batch)
    assert client.submissions == 0
    saved = await engine.repo.read_checkpoint(run["id"], "timesfm_job_0_backtest_result")
    assert "private provider body" not in json.dumps(saved)


async def test_cancellation_before_submission_prevents_any_job():
    engine, run, lease = await engine_run()
    await reserve_candidates(engine, run, lease, {"tasks": [1], "forecasts": [spec().model_dump()]})
    batch = batches(prepare_series(series(), spec().model_dump()))
    client = FakeClient(batch)
    engine.connectors.bq = client
    engine.connectors.cancel_flags[run["id"]] = threading.Event()
    engine.connectors.cancel_flags[run["id"]].set()
    with pytest.raises(AppError) as failure:
        await TimesFM(engine.connectors, engine.repo).execute(run, lease, "0", batch)
    assert failure.value.code == "cancelled" and client.submissions == 0


async def test_engine_recovers_primary_and_separate_scenario_artifacts(monkeypatch):
    from app.models import VisualizationSpec
    from app.report_engine import ReportEngine

    setup, run, lease = await engine_run()
    rows = series(drivers=True)
    s = spec(
        drivers=["promotion"], future_drivers=[{"promotion": 0}] * 7, scenario_drivers=[{"promotion": 1}] * 7
    )
    source = {
        "id": "saved_source",
        "title": "Saved daily sales",
        "complete": True,
        "row_count": len(rows),
        "columns": [
            {"name": name, "type": kind}
            for name, kind in [("date", "DATE"), ("sales", "DOUBLE"), ("promotion", "INTEGER")]
        ],
        "visualization": VisualizationSpec(
            type="line",
            title="Saved sales",
            x="date",
            y=["sales"],
            version=2,
            dimension_kind="temporal",
            granularity="day",
            measures=[{"field": "sales", "unit": "currency", "currency": "USD"}],
        ).model_dump(mode="json"),
        "assumptions": [],
        "provenance": [],
        "created_at": "2025-01-01",
    }
    plan = {"tasks": [{"id": "trend"}], "forecasts": [s.model_dump()]}
    await setup.repo.save_artifact(lease, source, rows, "evidence_0_trend")
    await setup.repo.checkpoint(lease, "final_plan_0", plan)
    await reserve_candidates(setup, run, lease, plan)
    monkeypatch.setattr(
        "app.report_forecasting.forecast", AsyncMock(return_value=local_result(rows, s, scenario=True))
    )

    async def execute(self, active, owner, operation, batch):
        def value(name, date):
            if batch["phase"] == "final":
                return 250 if name == "scenario" else 230
            return next(r["sales"] for r in rows if r["date"] == date) + 1

        return {
            "series": parse_output(output(batch, value), batch),
            "context": batch["context"],
            "job_id": "test",
        }

    monkeypatch.setattr(TimesFM, "execute", execute)
    engine = ReportEngine(
        SimpleNamespace(settings=setup.settings, ai=None, connectors=setup.connectors), setup.repo, None
    )
    original = setup.repo.save_artifact
    crashed = False

    async def crash(lease, artifact, values, key):
        nonlocal crashed
        if "scenario" in key and not crashed:
            crashed = True
            raise RuntimeError("crash after primary artifact")
        return await original(lease, artifact, values, key)

    monkeypatch.setattr(setup.repo, "save_artifact", crash)
    with pytest.raises(RuntimeError, match="after primary"):
        await engine.analyze(run, lease)
    await engine.analyze(run, lease)
    result = await setup.repo.read_checkpoint(run["id"], "analysis")
    assert len(result["artifact_ids"]) == 3
    primary = await setup.repo.get("artifacts", result["artifact_ids"][1])
    scenario = await setup.repo.get("artifacts", result["artifact_ids"][2])
    assert primary["prediction"]["kind"] == "forecast"
    assert scenario["prediction"]["kind"] == "scenario"
    assert primary["prediction"]["method"] == scenario["prediction"]["method"] == "timesfm_3"
    assert primary["prediction"]["source_artifact_id"] == "saved_source"
    assert "scenario" not in primary["visualization"]["y"]
    assert "scenario" in scenario["visualization"]["y"]
    assert primary["prediction"]["comparison"]["jobs"]
    assert len(json.dumps(await setup.repo.read_checkpoint(run["id"], "timesfm_capture_0"))) < 10000


async def test_cached_provider_results_reject_a_different_payload():
    engine, run, lease = await engine_run()
    await reserve_candidates(engine, run, lease, {"tasks": [1], "forecasts": [spec().model_dump()]})
    batch = batches(prepare_series(series(), spec().model_dump()))
    engine.connectors.bq = FakeClient(batch)
    provider = TimesFM(engine.connectors, engine.repo)
    await provider.execute(run, lease, "0", batch)
    changed = copy.deepcopy(batch)
    changed["rows"][0]["value"] += 1
    with pytest.raises(AppError, match="different inputs"):
        await provider.execute(run, lease, "0", changed)


async def test_expired_inference_can_recover_completed_job_without_restart():
    engine, run, lease = await engine_run()
    await reserve_candidates(engine, run, lease, {"tasks": [1], "forecasts": [spec().model_dump()]})
    batch = batches(prepare_series(series(), spec().model_dump()))
    client = FakeClient(batch)
    engine.connectors.bq = client
    provider = TimesFM(engine.connectors, engine.repo)
    await provider.execute(run, lease, "0", batch)
    collection = f"report_runs/{run['id']}/checkpoints"
    await engine.repo.store.delete(collection, "timesfm_job_0_backtest_result")
    reservation = await engine.repo.store.get(collection, "timesfm_job_0_backtest")
    reservation["value"]["deadline"] = time.time() - 60
    await engine.repo.store.delete(collection, "timesfm_job_0_backtest_settled")
    active = await engine.repo.store.get("report_runs", run["id"])
    active["budgets"]["timesfm_seconds"] = 45
    await engine.repo.store.put("report_runs", run["id"], active)
    await engine.repo.store.put(collection, "timesfm_job_0_backtest", reservation)
    await provider.execute(run, lease, "0", batch)
    assert client.submissions == 1
    assert (await engine.repo.guard(lease))["budgets"]["timesfm_seconds"] == 45


async def test_late_submission_is_cancelled_after_waiter_cancellation(monkeypatch):
    engine, run, lease = await engine_run()
    await reserve_candidates(engine, run, lease, {"tasks": [1], "forecasts": [spec().model_dump()]})
    batch = batches(prepare_series(series(), spec().model_dump()))
    client = FakeClient(batch)
    entered, release = threading.Event(), threading.Event()
    original = client.query

    def blocked(*args, **kwargs):
        if not kwargs["job_config"].dry_run:
            entered.set()
            release.wait(2)
        return original(*args, **kwargs)

    client.query = blocked
    engine.connectors.bq = client
    task = asyncio.create_task(TimesFM(engine.connectors, engine.repo).execute(run, lease, "0", batch))
    await asyncio.to_thread(entered.wait, 2)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    engine.connectors.forget(run["id"])
    release.set()
    for _ in range(100):
        if client.job and client.job.cancelled:
            break
        await asyncio.sleep(0.01)
    assert client.job.cancelled


def test_fallback_can_retain_all_separate_scenario_artifacts():
    from app.report_engine import ReportEngine

    engine = object.__new__(ReportEngine)
    ids = [f"evidence_{i}" for i in range(17)]
    draft = engine.fallback({"artifact_ids": ids, "claims": []})
    assert len(draft.sections) <= 12
    assert [a for section in draft.sections for a in section.artifact_ids] == ids


async def test_ambiguous_submission_remains_recoverable_under_same_job_id():
    engine, run, lease = await engine_run()
    await reserve_candidates(engine, run, lease, {"tasks": [1], "forecasts": [spec().model_dump()]})
    batch = batches(prepare_series(series(), spec().model_dump()))
    client = FakeClient(batch)
    query_original, get_original = client.query, client.get_job
    hidden = False

    def submit(*args, **kwargs):
        nonlocal hidden
        result = query_original(*args, **kwargs)
        if not kwargs["job_config"].dry_run:
            hidden = True
            raise TimeoutError("lost submission response")
        return result

    def lookup(*args, **kwargs):
        nonlocal hidden
        if hidden:
            hidden = False
            raise NotFound("not visible yet")
        return get_original(*args, **kwargs)

    client.query, client.get_job = submit, lookup
    engine.connectors.bq = client
    provider = TimesFM(engine.connectors, engine.repo)
    with pytest.raises(AppError) as error:
        await provider.execute(run, lease, "0", batch)
    assert error.value.code == "timesfm_reconcile"
    assert await engine.repo.read_checkpoint(run["id"], "timesfm_job_0_backtest_result") is None
    result = await provider.execute(run, lease, "0", batch)
    assert result["series"] and client.submissions == 1


def test_saved_prediction_downloads_retain_model_values_and_version(monkeypatch):
    import io
    import zipfile

    from app.report_exports import _render

    monkeypatch.setattr(
        TimesFM, "execute", AsyncMock(side_effect=AssertionError("Downloads cannot invoke inference"))
    )
    rows = [{"date": "2026-10-01", "observed": None, "forecast": 123.45}]
    prediction = {
        "method": "timesfm_3",
        "model": "TimesFM 3.0",
        "preview": True,
        "cutoff": "2026-09-30",
        "horizon": 1,
        "comparison": {"input_hash": "frozen"},
    }
    artifact = {
        "id": "prediction",
        "title": "Saved prediction",
        "complete": True,
        "columns": [{"name": name} for name in rows[0]],
        "visualization": {"type": "table"},
        "provenance": [],
        "prediction": prediction,
    }
    document = {
        "report_id": "report",
        "version": 2,
        "created_at": "2026-10-17",
        "title": "Evidence",
        "summary": "Saved predictions, not observed facts.",
        "claims": [],
        "data_profile": "timeseries",
        "model": "gemini-3.8-flash",
        "mode_note": "Verified fixture",
        "limitations": ["No validated prediction intervals."],
        "sections": [{"title": "Forecast", "markdown": "Evidence", "artifact_ids": ["prediction"]}],
    }
    files = _render(document, {"prediction": (artifact, rows)})
    assert files["pdf"].startswith(b"%PDF")
    word = zipfile.ZipFile(io.BytesIO(files["docx"])).read("word/document.xml").decode()
    assert "TimesFM 3.0" in word and "123.45" in word and "Version 2" in word
    archive = zipfile.ZipFile(io.BytesIO(files["data"]))
    manifest = json.loads(archive.read("manifest.json"))
    assert manifest["version"] == 2 and manifest["datasets"][0]["prediction"] == prediction
    csv = archive.read(manifest["datasets"][0]["file"]).decode()
    assert "123.45" in csv and len(csv.splitlines()) == 2
