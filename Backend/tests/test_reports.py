import asyncio
import io
import json
import os
import sys
import time
import uuid
import zipfile
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.errors import AppError
from app.main import create_app
from app.maintenance import reset_history
from app.models import VisualizationSpec
from app.report_dispatch import ReportDispatcher
from app.report_engine import ReportEngine
from app.report_exports import ExportStorage, _render
from app.report_harness import ReportPolicy
from app.report_models import ReportClarification, ReportCreate, ReportDraft
from app.report_repository import ReportRepository
from app.report_statistics import _forecast, factual_claims
from app.repository import Repository
from app.storage import MemoryStore


@pytest.fixture(
    autouse=True, params=["memory", "firestore"] if os.environ.get("FIRESTORE_EMULATOR_HOST") else ["memory"]
)
async def storage_adapter(request, monkeypatch):
    clients = []
    if request.param == "firestore":
        from google.auth.credentials import AnonymousCredentials

        from app.storage import FirestoreStore

        class Namespace:
            def __init__(self, client, prefix):
                self.base, self.prefix = client, prefix

            def collection(self, path):
                return self.base.collection(f"report_test_runs/{self.prefix}/{path}")

            def document(self, path):
                return self.base.document(f"report_test_runs/{self.prefix}/{path}")

            def __getattr__(self, name):
                return getattr(self.base, name)

        def factory():
            store = FirestoreStore("demo-querylane", "(default)", credentials=AnonymousCredentials())
            store.client = Namespace(store.client, uuid.uuid4().hex)
            clients.append(store)
            return store

        monkeypatch.setattr(sys.modules[__name__], "MemoryStore", factory)
    yield request.param
    for store in clients:
        await store.close()


def body(question="Show monthly revenue as a line chart", **kw):
    return ReportCreate(question=question, idempotency_key=uuid.uuid4().hex, **kw)


async def setup(**kw):
    store = MemoryStore()
    settings = Settings(environment="test", **kw)
    chat = await Repository(store, settings).create_conversation("Report", "all")
    return store, settings, chat, ReportRepository(store, settings)


async def started(**kw):
    store, settings, chat, repo = await setup(**kw)
    run = await repo.create(chat["id"], "guest", body())
    lease = await repo.claim(run["id"])
    return store, settings, chat, repo, run, lease


async def test_idempotency_and_separate_chat_lease():
    store, settings, chat, repo = await setup()
    request = body()
    a, b = await asyncio.gather(
        repo.create(chat["id"], "guest", request), repo.create(chat["id"], "guest", request)
    )
    assert a == b
    with pytest.raises(AppError, match="request key"):
        await repo.create(chat["id"], "guest", request.model_copy(update={"question": "other"}))
    with pytest.raises(AppError, match="already active"):
        await repo.create(chat["id"], "guest", body())
    quick, _ = await Repository(store, settings).begin(chat["id"], "guest", "monthly sales", "normal-chat")
    assert quick["status"] == "running"
    assert (await store.get("conversations", chat["id"]))["active_run"] == quick["id"]


async def test_daily_report_quota_atomic_and_preserved_after_reset():
    store, settings, _, repo = await setup(report_guest_daily_limit=1)
    chats = [await Repository(store, settings).create_conversation("A", "all") for _ in range(2)]
    results = await asyncio.gather(
        *(repo.create(c["id"], "guest", body()) for c in chats), return_exceptions=True
    )
    assert sum(isinstance(r, AppError) for r in results) == 1
    await reset_history(store)
    chat = await Repository(store, settings).create_conversation("new", "all")
    with pytest.raises(AppError, match="usage limit"):
        await repo.create(chat["id"], "guest", body())


async def test_fencing_expiry_concurrency_and_checkpoint_replay():
    store, settings, chat, repo, run, lease = await started()
    with pytest.raises(AppError, match="already running"):
        await repo.claim(run["id"])
    await repo.checkpoint(lease, "evidence", {"value": 10})
    assert await repo.checkpoint(lease, "evidence", {"value": 20}) == {"value": 10}
    value = await repo.get("report_runs", run["id"])
    value["lease_until"] = time.time() - 1
    await store.put("report_runs", run["id"], value)
    replacement = await repo.claim(run["id"])
    with pytest.raises(AppError, match="no longer owns"):
        await repo.checkpoint(lease, "late", {"value": 99})
    assert await repo.read_checkpoint(run["id"], "evidence") == {"value": 10}
    await repo.heartbeat(replacement)
    for i in range(2):
        c = await Repository(store, settings).create_conversation(str(i), "all")
        r = await repo.create(c["id"], f"guest-{i}", body())
        if i == 0:
            await repo.claim(r["id"])
        else:
            with pytest.raises(AppError, match="occupied"):
                await repo.claim(r["id"])


async def test_budgets_survive_worker_recovery_and_prevent_overspend():
    store, _, _, repo, run, lease = await started(report_model_calls=2)
    await repo.spend(lease, model_calls=2)
    with pytest.raises(AppError, match="budget"):
        await repo.spend(lease, model_calls=1)
    current = await repo.get("report_runs", run["id"])
    assert current["budgets"]["model_calls"] == 2
    await repo.spend(lease, output_tokens=2000)
    await repo.spend(lease, output_tokens=-1000)
    assert (await repo.guard(lease))["budgets"]["output_tokens"] == 1000


async def test_owner_clarifications_busy_rules_and_cancellation():
    _, _, _, repo, run, lease = await started()
    await repo.finish(lease, "waiting_input", clarification="Which metric?")
    with pytest.raises(AppError, match="initiating guest"):
        await repo.clarify(run["id"], "other", ReportClarification(answer="Revenue", expected_revision=1))
    resumed = await repo.clarify(
        run["id"], "guest", ReportClarification(answer="Revenue", expected_revision=1)
    )
    assert resumed["status"] == "queued"
    with pytest.raises(AppError, match="changed"):
        await repo.clarify(run["id"], "guest", ReportClarification(answer="Revenue", expected_revision=1))
    lease = await repo.claim(run["id"])
    await repo.cancel(run["id"], "guest")
    with pytest.raises(AppError, match="cancellation"):
        await repo.checkpoint(lease, "late", 1)
    await repo.finish(lease, "cancelled")
    assert (await repo.get("reports", run["report_id"]))["active_run"] is None


async def test_outbox_recovers_abandoned_workers_and_queued_cancellation():
    store, _, _, repo, run, lease = await started()
    dispatcher = ReportDispatcher(repo, None)
    current = await repo.get("report_runs", run["id"])
    current["lease_until"] = time.time() - 1
    await store.put("report_runs", run["id"], current)
    await dispatcher.reconcile()
    current = await repo.get("report_runs", run["id"])
    assert current["status"] == "queued" and current["delivery"] == 1
    assert (await store.get("report_outbox", run["id"]))["pending"]
    await repo.cancel(run["id"], "guest")
    await dispatcher.reconcile()
    assert (await repo.get("report_runs", run["id"]))["status"] == "cancelled"


def sample_artifact(*, complete=True):
    return {
        "id": "evidence",
        "title": "Monthly revenue",
        "conversation_id": "chat",
        "row_count": 3,
        "complete": complete,
        "created_at": "2026-01-01",
        "columns": [{"name": "month", "type": "STRING"}, {"name": "revenue", "type": "NUMERIC"}],
        "visualization": VisualizationSpec(
            type="line",
            title="Monthly revenue",
            x="month",
            y=["revenue"],
            version=2,
            dimension_kind="temporal",
            granularity="month",
            measures=[{"field": "revenue", "unit": "currency", "currency": "USD", "additive": True}],
        ).model_dump(mode="json"),
        "provenance": [
            {
                "source": "bigquery",
                "sql": "SELECT...",
                "executed_at": "2026-01-01",
                "elapsed_ms": 0,
                "row_count": 3,
            }
        ],
        "assumptions": [],
    }


@pytest.mark.parametrize("complete", [True, False])
def test_independent_decimal_claims_and_no_partial_totals(complete):
    claims = factual_claims(
        sample_artifact(complete=complete),
        [
            {"month": "2025-01", "revenue": "10.10"},
            {"month": "2025-02", "revenue": "20.20"},
            {"month": "2025-03", "revenue": "0"},
        ],
    )
    assert any(c["value"] == "20.20" for c in claims)
    totals = [c for c in claims if c["calculation"].startswith("total")]
    assert len(totals) == int(complete)
    if complete:
        assert totals[0]["value"] == "30.30"


def test_report_writer_cannot_invent_numbers_or_references():
    engine = object.__new__(ReportEngine)
    claims = [{"id": "c_a", "label": "Revenue", "formatted": "USD 10.00"}]
    draft = ReportDraft(
        summary="Saved revenue {{claim:c_a}}.",
        sections=[
            {
                "id": "summary",
                "title": "Findings",
                "markdown": "Use {{claim:c_a}}.",
                "claim_ids": ["c_a"],
                "artifact_ids": ["evidence"],
            }
        ],
    )
    assert engine.validated_draft(draft, claims, ["evidence"])["summary"] == "Saved revenue USD 10.00."
    for text in ["Revenue is 100", "{{claim:c_unknown}}", "<script>oops</script>", "https://evil.example"]:
        with pytest.raises(ValueError):
            engine.validated_draft(draft.model_copy(update={"summary": text}), claims, ["evidence"])


def series(n=140):
    from datetime import date, timedelta

    return [
        {"date": (date(2025, 1, 1) + timedelta(days=i)).isoformat(), "sales": float(100 + i % 7 * 4)}
        for i in range(n)
    ]


@pytest.mark.parametrize(
    "case", ["short", "gap", "null", "duplicate", "negative", "rate", "unknown", "huge_horizon"]
)
def test_forecast_rejects_invalid_inputs(case):
    from app.report_models import ForecastSpec

    rows = series()
    spec = ForecastSpec(task_id="trend", date_column="date", target="sales", grain="day", horizon=7)
    if case == "short":
        rows = rows[:15]
    if case == "gap":
        rows.pop(10)
    if case == "null":
        rows[0]["sales"] = None
    if case == "duplicate":
        rows.append(rows[0])
    if case == "negative":
        rows[0]["sales"] = -1
    if case == "rate":
        spec.domain = "fraction"
    if case == "unknown":
        spec.target = "missing"
    if case == "huge_horizon":
        spec.horizon = 91
    with pytest.raises(ValueError):
        _forecast(rows, spec.model_dump(mode="json"), 12, 15)


def test_forecast_full_horizon_independent_seasonal_fixture():
    from app.report_models import ForecastSpec

    spec = ForecastSpec(task_id="trend", date_column="date", target="sales", grain="day", horizon=7)
    result = _forecast(series(), spec.model_dump(mode="json"), 12, 15)
    future = result["rows"][-7:]
    assert [r["forecast"] for r in future] == [100 + i * 4 for i in range(7)]
    assert result["method"] == "seasonal_naive"
    assert result["scores"]["seasonal_naive"]["mae"] == 0
    assert len(result["scores"]["seasonal_naive"]["folds"]) == 3
    assert all(r["observed"] is None for r in future)
    assert all(r["forecast"] is None for r in result["rows"][:-7])


@pytest.mark.parametrize("kind", ["constant", "target_leak", "future_feature", "missing_future"])
def test_driver_scenarios_require_supported_nonleaking_explicit_paths(kind):
    from app.report_models import ForecastSpec

    rows = series()
    key = "future_sales" if kind == "future_feature" else "promotion"
    for i, row in enumerate(rows):
        row[key] = 1 if kind == "constant" else row["sales"] if kind == "target_leak" else i % 5
    spec = ForecastSpec(
        task_id="trend", date_column="date", target="sales", grain="day", horizon=7, drivers=[key]
    )
    with pytest.raises(ValueError):
        _forecast(rows, spec.model_dump(mode="json"), 12, 15)


async def test_policy_blocks_tools_and_enforces_model_budget():
    _, _, _, repo, _, lease = await started(report_model_calls=1)
    policy = ReportPolicy(repo, lease)
    request = SimpleNamespace(tools_dict={}, config=SimpleNamespace(max_output_tokens=1000))
    context = SimpleNamespace(invocation_id="a")
    await policy.before_model_callback(callback_context=context, llm_request=request)
    await policy.after_model_callback(
        callback_context=context,
        llm_response=SimpleNamespace(
            usage_metadata=SimpleNamespace(candidates_token_count=50, thoughts_token_count=50)
        ),
    )
    assert (await repo.guard(lease))["budgets"]["output_tokens"] == 100
    with pytest.raises(AppError, match="budget"):
        await policy.before_model_callback(callback_context=context, llm_request=request)
    request.tools_dict = {"shell": {}}
    with pytest.raises(AppError, match="unrestricted"):
        await policy.before_model_callback(callback_context=context, llm_request=request)


async def test_export_storage_immutable_integrity_and_path_traversal(tmp_path):
    storage = ExportStorage(Settings(report_local_directory=str(tmp_path)))
    metadata = await storage.save("reports/a/report.pdf", b"original", "application/pdf")
    assert await storage.read(metadata) == b"original"
    assert await storage.save("reports/a/report.pdf", b"original", "application/pdf") == metadata
    with pytest.raises(AppError, match="conflict"):
        await storage.save("reports/a/report.pdf", b"changed", "application/pdf")
    with pytest.raises(AppError, match="path"):
        await storage.save("../../outside", b"x", "application/pdf")
    (tmp_path / metadata["key"]).write_bytes(b"corrupt")
    with pytest.raises(AppError, match="integrity"):
        await storage.read(metadata)


async def test_full_fixture_report_api_downloads_revisions_pins_and_reset(tmp_path):
    # Full graph and source execution; render in-process to make the fixture fast and inspectable.
    store = MemoryStore()
    app = create_app(Settings(environment="test", report_local_directory=str(tmp_path)), store_override=store)
    with TestClient(app) as client:
        h = {"Authorization": "Bearer " + client.post("/api/v1/guest-sessions").json()["token"]}
        chat = client.post("/api/v1/conversations", json={"source": "all"}, headers=h).json()
        # Child-process rendering is separately verified by the local smoke script.
        with pytest.MonkeyPatch.context() as patch:

            async def render_fast(document, artifacts):
                return await asyncio.to_thread(_render, document, artifacts)

            patch.setattr("app.report_engine.render", render_fast)
            request = body().model_dump()
            response = client.post(f"/api/v1/conversations/{chat['id']}/reports", json=request, headers=h)
            assert response.status_code == 202
            run = response.json()
            for _ in range(300):
                run = client.get(f"/api/v1/report-runs/{run['id']}").json()
                if run["status"] in {"complete", "failed"}:
                    break
                time.sleep(0.05)
            assert run["status"] == "complete", run
            rid = run["report_id"]
            value = client.get(f"/api/v1/reports/{rid}/revisions/1").json()
            assert value["document"]["claims"] and value["document"]["data_profile"] == "legacy"
            assert "exports" not in value
            original = {}
            for fmt, signature in [("pdf", b"%PDF"), ("docx", b"PK"), ("data", b"PK")]:
                download = client.get(f"/api/v1/reports/{rid}/revisions/1/downloads/{fmt}")
                assert download.status_code == 200 and download.content.startswith(signature)
                original[fmt] = download.content
            archive = zipfile.ZipFile(io.BytesIO(original["data"]))
            manifest = json.loads(archive.read("manifest.json"))
            assert manifest["version"] == 1 and manifest["datasets"][0]["rows"] == 9
            public_report = client.get(f"/api/v1/reports/{rid}").json()
            denied = client.patch(
                f"/api/v1/reports/{rid}",
                json={"name": "No token", "expected_revision": public_report["revision"]},
            )
            assert denied.status_code == 401
            renamed = client.patch(
                f"/api/v1/reports/{rid}",
                json={"name": "Retail report", "expected_revision": public_report["revision"]},
                headers=h,
            )
            assert renamed.status_code == 200
            stale = client.patch(
                f"/api/v1/reports/{rid}",
                json={"name": "Stale", "expected_revision": public_report["revision"]},
                headers=h,
            )
            assert stale.status_code == 409
            # Presentation revisions remain usable even when analytical sources are offline.
            patch.setattr(
                app.state.services.connectors,
                "ensure_data_ready",
                AsyncMock(side_effect=AssertionError("Presentation must use saved evidence only.")),
            )
            patch.setattr(
                app.state.services.connectors,
                "query",
                AsyncMock(side_effect=AssertionError("Presentation cannot query sources.")),
            )
            rev = client.post(
                f"/api/v1/reports/{rid}/revisions",
                json={
                    **body("Make the report technical", style="technical").model_dump(),
                    "base_version": 1,
                    "mode": "presentation",
                    "expected_revision": renamed.json()["revision"],
                },
                headers=h,
            )
            assert rev.status_code == 202
            for _ in range(300):
                state = client.get(f"/api/v1/report-runs/{rev.json()['id']}").json()
                if state["status"] in {"complete", "failed"}:
                    break
                time.sleep(0.05)
            assert state["status"] == "complete", state
            new = client.get(f"/api/v1/reports/{rid}/revisions/2").json()
            assert new["document"]["artifact_ids"] == value["document"]["artifact_ids"]
            assert new["document"]["style"] == "technical"
            for fmt in original:
                assert (
                    client.get(f"/api/v1/reports/{rid}/revisions/1/downloads/{fmt}").content == original[fmt]
                )
            board = client.post(
                "/api/v1/dashboards",
                json={"name": "Report evidence", "request_id": uuid.uuid4().hex},
                headers=h,
            ).json()["dashboard"]
            pinned = client.post(
                f"/api/v1/dashboards/{board['id']}/items",
                json={
                    "expected_revision": board["revision"],
                    "request_id": uuid.uuid4().hex,
                    "artifact_id": value["document"]["artifact_ids"][0],
                    "view": {"view": "table", "primary": "revenue", "visible_measures": ["revenue"]},
                },
                headers=h,
            )
            assert pinned.status_code == 200, pinned.text
            public_report = client.get(f"/api/v1/reports/{rid}").json()
            deleted = client.delete(
                f"/api/v1/reports/{rid}?expected_revision={public_report['revision']}", headers=h
            )
            assert deleted.status_code == 200
            assert client.get("/api/v1/reports?deleted=true").json()["reports"][0]["id"] == rid
            assert (
                client.post(
                    f"/api/v1/reports/{rid}/restore",
                    json={"expected_revision": deleted.json()["revision"]},
                    headers=h,
                ).status_code
                == 200
            )
            # Use the server loop for its lock-backed store.
            client.portal.call(reset_history, store)
            assert client.get(f"/api/v1/reports/{rid}/revisions/1/downloads/pdf").content == original["pdf"]
            assert client.get(f"/api/v1/artifacts/{value['document']['artifact_ids'][0]}").status_code == 200
            assert client.get(f"/api/v1/dashboards/{board['id']}").status_code == 200


async def test_graph_preserves_clarification_without_running_downstream_stages():
    from google.adk.sessions import InMemorySessionService

    from app.report_engine import NeedsInput
    from app.report_harness import run_report_graph

    _, settings, _, repo, run, lease = await started()
    services = SimpleNamespace(sessions=InMemorySessionService())
    engine = SimpleNamespace(
        repo=repo,
        settings=settings,
        services=services,
        prepare=AsyncMock(side_effect=NeedsInput("Which period?")),
        gather=AsyncMock(),
        analyze=AsyncMock(),
        compose=AsyncMock(),
        publish=AsyncMock(),
    )
    with pytest.raises(NeedsInput):
        await run_report_graph(engine, run, lease)
    engine.gather.assert_not_awaited()
    engine.publish.assert_not_awaited()


@pytest.mark.parametrize(
    "sql,source",
    [
        (
            "SELECT FORMAT_DATE('%Y-%m', order_date) AS month, SUM(revenue) AS revenue FROM orders GROUP BY month",
            "bigquery",
        ),
        ("SELECT TO_CHAR(month, 'YYYY-MM') AS month FROM retail.regional_targets", "postgres"),
    ],
)
def test_approved_date_formatting_typed_sqlglot_alias(sql, source):
    from app.sql_guard import validate_sql

    assert validate_sql(sql, source, "project", "demo")


async def test_completed_artifacts_survive_reset_and_active_report_fences_maintenance():
    store, _, _, repo, run, lease = await started()
    artifact = sample_artifact()
    rows = [{"month": "2025-01", "revenue": "10.10"}]
    artifact["row_count"] = 1
    await repo.save_artifact(lease, artifact, rows, "saved")
    with pytest.raises(AppError, match="did not drain"):
        await reset_history(store, timeout=0)
    assert (await store.get("system", "history_maintenance"))["active"]
    from app.maintenance import clear_maintenance

    await clear_maintenance(store)
    await repo.finish(lease, "failed", error="test")
    await reset_history(store)
    assert await store.get("artifacts", artifact["id"])
    assert await repo.read_checkpoint(run["id"], "saved") == artifact["id"]


async def test_source_profile_mismatch_fails_before_model_or_queries(tmp_path):
    store, settings, _, repo, run, lease = await started()
    run["brief"]["data_profile"] = "timeseries"
    engine = ReportEngine(
        SimpleNamespace(
            settings=settings, ai=None, connectors=SimpleNamespace(ensure_data_ready=AsyncMock())
        ),
        repo,
        ExportStorage(Settings(report_local_directory=str(tmp_path))),
    )
    with pytest.raises(AppError, match="source profile"):
        await engine.prepare(run, lease)


def test_prediction_presentation_does_not_claim_projected_peaks_are_observed():
    from app.chart_presentation import present

    artifact = sample_artifact()
    artifact["prediction"] = {"method": "seasonal_naive", "cutoff": "2025-02-01"}
    result = present(
        artifact,
        [
            {"month": "2025-01", "revenue": 10},
            {"month": "2025-02", "revenue": 20},
            {"month": "2025-03", "revenue": 1000},
        ],
    )
    assert not result["insights"] and not result["annotations"]
    assert all(not r["_detail"] for r in result["rows"])


@pytest.mark.parametrize("count,zero_index,total", [(45, None, "45"), (1369, 100, "1368")])
def test_complete_monthly_daily_claims_independent_fixtures(count, zero_index, total):
    artifact = sample_artifact()
    artifact["row_count"] = count
    rows = [{"month": str(i), "revenue": "0" if i == zero_index else "1"} for i in range(count)]
    claims = factual_claims(artifact, rows)
    assert next(c["value"] for c in claims if c["calculation"].startswith("total")) == total


async def test_artifact_checkpoint_never_rewrites_saved_pages():
    store, _, _, repo, _, lease = await started()
    artifact = sample_artifact()
    artifact["row_count"] = 1
    await repo.save_artifact(lease, artifact, [{"month": "2025-01", "revenue": "10"}], "evidence")
    await repo.save_artifact(lease, artifact, [{"month": "2025-01", "revenue": "999"}], "evidence")
    assert (await store.get("artifacts/evidence/pages", "0"))["rows"][0]["revenue"] == "10"


async def test_fenced_report_adk_sessions_reject_old_worker_and_survive_reset():
    from google.adk.events import Event

    from app.adk_sessions import FirestoreSessionService
    from app.errors import StaleLease
    from app.report_repository import active_report_lease

    store, _, _, repo, run, lease = await started()
    sessions = FirestoreSessionService(store, collection="report_adk_sessions")
    token = active_report_lease.set(lease)
    try:
        session = await sessions.create_session(
            app_name="report", user_id="public", session_id=f"report_{run['id']}_1"
        )
        current = await repo.get("report_runs", run["id"])
        current["lease_until"] = time.time() - 1
        await store.put("report_runs", run["id"], current)
        replacement = await repo.claim(run["id"])
        with pytest.raises(StaleLease):
            await sessions.append_event(session, Event(author="old", output="late"))
        await repo.finish(replacement, "failed", error="test")
    finally:
        active_report_lease.reset(token)
    await reset_history(store)
    assert await sessions.get_session(app_name="report", user_id="public", session_id=session.id)


async def test_checkpointed_queries_are_not_reexecuted_after_worker_recovery(tmp_path):
    from app.adk_sessions import FirestoreSessionService
    from app.ai import AI
    from app.connectors import Connectors

    store, settings, _, repo, run, lease = await started()
    connectors = Connectors(settings)
    await connectors.start()
    connectors.query = AsyncMock(wraps=connectors.query)
    services = SimpleNamespace(
        settings=settings,
        connectors=connectors,
        repo=Repository(store, settings),
        ai=AI(settings, FirestoreSessionService(store), connectors, store),
    )
    engine = ReportEngine(services, repo, ExportStorage(Settings(report_local_directory=str(tmp_path))))
    await engine.prepare(run, lease)
    await engine.gather(run, lease)
    assert connectors.query.await_count == 1
    state = await repo.get("report_runs", run["id"])
    state["lease_until"] = time.time() - 1
    await store.put("report_runs", run["id"], state)
    replacement = await repo.claim(run["id"])
    await engine.gather(run, replacement)
    assert connectors.query.await_count == 1
    await connectors.close()


async def test_recovery_uses_saved_sql_repair_and_its_attempt_identity(tmp_path):
    from app.adk_sessions import FirestoreSessionService
    from app.ai import AI
    from app.connectors import Connectors

    store, settings, _, repo, run, lease = await started()
    connectors = Connectors(settings)
    await connectors.start()
    ai = AI(settings, FirestoreSessionService(store), connectors, store)
    services = SimpleNamespace(
        settings=settings, connectors=connectors, repo=Repository(store, settings), ai=ai
    )
    engine = ReportEngine(services, repo, ExportStorage(Settings(report_local_directory=str(tmp_path))))
    await engine.prepare(run, lease)
    valid, retrieval = await ai.plan(run["brief"]["question"], [], "all", run["conversation_id"])
    invalid = valid.model_dump(mode="json")
    invalid["queries"][0]["sql"] = "SELECT nonexistent_column FROM orders"
    await repo.checkpoint(lease, "query_plan_0_main", {"plan": invalid, "retrieval": retrieval})
    await repo.checkpoint(lease, "repair_0_main_0_1", valid.model_dump(mode="json"))
    ai.plan = AsyncMock(side_effect=AssertionError("A saved repair must not request another model call."))
    engine._query = AsyncMock(wraps=engine._query)
    await engine.gather(run, lease)
    assert engine._query.await_args_list[0].args[-1] == 1
    assert engine._query.await_args_list[0].args[3].sql == valid.queries[0].sql
    assert await repo.read_checkpoint(run["id"], "evidence_0_main")
    await connectors.close()


async def test_purge_expired_report_preserves_dashboard_owned_artifacts(tmp_path):
    from app.maintenance import purge_reports

    store, settings, _, repo, run, lease = await started()
    artifact = sample_artifact()
    artifact["row_count"] = 1
    await repo.save_artifact(lease, artifact, [{"month": "2025-01", "revenue": "10"}], "evidence")
    await store.put("dashboard_artifact_refs", artifact["id"], {"count": 1})
    await repo.finish(lease, "failed", error="fixture")
    report = await repo.get("reports", run["report_id"])
    report.update(deleted=True, recover_until=time.time() - 1)
    await store.put("reports", report["id"], report)
    result = await purge_reports(store, ExportStorage(Settings(report_local_directory=str(tmp_path))))
    assert result["purged_reports"] == 1
    assert await store.get("artifacts", artifact["id"])
    assert not await store.get("report_artifact_refs", artifact["id"])
    assert not await store.get("report_runs", run["id"])


async def test_expired_waiting_report_releases_conversation_slot():
    store, _, _, repo, run, lease = await started()
    await repo.finish(lease, "waiting_input", clarification="Period?")
    current = await repo.get("report_runs", run["id"])
    current["expires_at"] = time.time() - 1
    await store.put("report_runs", run["id"], current)
    await ReportDispatcher(repo, None).reconcile()
    assert (await repo.get("report_runs", run["id"]))["status"] == "failed"
    assert (await store.get("report_conversations", run["conversation_id"]))["run_id"] is None


def test_learned_scenario_uses_explicit_supported_paths_and_passes_baseline_gate():
    import numpy as np

    from app.report_models import ForecastSpec

    rows = series(180)
    rng = np.random.default_rng(42)
    for i, row in enumerate(rows):
        driver = int(rng.integers(0, 6))
        row["promotion"] = driver
        row["sales"] = 200 + i * 0.3 + (i % 7) * 3 + driver * 20
    spec = ForecastSpec(
        task_id="trend",
        date_column="date",
        target="sales",
        grain="day",
        horizon=7,
        drivers=["promotion"],
        future_drivers=[{"promotion": 2}] * 7,
        scenario_drivers=[{"promotion": 4}] * 7,
        scenario_name="Visitor-supplied promotion path",
    )
    result = _forecast(rows, spec.model_dump(mode="json"), 12, 20)
    assert result["method"] == "driver_ridge"
    assert result["scores"]["driver_ridge"]["mae"] <= result["scores"]["seasonal_naive"]["mae"] * 0.95
    differences = [r["scenario"] - r["forecast"] for r in result["rows"][-7:]]
    assert all(30 < d < 50 for d in differences)  # Independent generating relationship: 20 × (4 − 2).
    assert any("not causal" in limitation for limitation in result["limitations"])


@pytest.mark.parametrize(
    "field,operation,expected",
    [
        ("revenue", "total", "640"),
        ("revenue", "minimum", "0"),
        ("revenue", "maximum", "180"),
        ("revenue", "latest", "180"),
        ("revenue", "previous adjacent period", "0"),
        ("revenue", "latest minus previous adjacent period", "180"),
        ("orders", "total", "64"),
        ("orders", "minimum", "0"),
        ("orders", "maximum", "18"),
        ("orders", "latest", "18"),
        ("orders", "previous adjacent period", "0"),
        ("orders", "latest minus previous adjacent period", "18"),
        ("refunds", "total", "36"),
        ("refunds", "minimum", "0"),
        ("refunds", "maximum", "10"),
        ("refunds", "latest", "10"),
        ("refunds", "previous adjacent period", "0"),
        ("refunds", "latest minus previous adjacent period", "10"),
        ("margin", "total", "100"),
        ("margin", "minimum", "-10"),
        ("margin", "maximum", "40"),
        ("margin", "latest", "25"),
        ("margin", "previous adjacent period", "30"),
        ("margin", "latest minus previous adjacent period", "-5"),
        ("return_rate", "minimum", "0"),
        ("return_rate", "maximum", "0.2"),
        ("refunds", "average", "6"),
        ("return_rate", "latest", "0.1"),
        ("return_rate", "previous adjacent period", "0.15"),
        ("return_rate", "latest minus previous adjacent period", "-0.05"),
    ],
)
def test_thirty_independent_retail_report_calculations(field, operation, expected):
    from decimal import Decimal

    measures = {
        "revenue": [100, 120, 90, 150, 0, 180],
        "orders": [10, 12, 9, 15, 0, 18],
        "refunds": [5, 6, 7, 8, 0, 10],
        "margin": [-10, 20, 40, -5, 30, 25],
        "return_rate": ["0.05", "0.1", "0", "0.2", "0.15", "0.1"],
    }
    rows = [{"month": f"2025-{i + 1:02d}", field: str(v)} for i, v in enumerate(measures[field])]
    artifact = sample_artifact()
    artifact.update(
        row_count=6, columns=[{"name": "month", "type": "STRING"}, {"name": field, "type": "NUMERIC"}]
    )
    artifact["visualization"].update(
        y=[field],
        measures=[
            {
                "field": field,
                "unit": "percent" if field == "return_rate" else "count" if field == "orders" else "currency",
                "currency": None if field in {"return_rate", "orders"} else "USD",
                "percent_scale": "fraction" if field == "return_rate" else None,
                "additive": field != "return_rate",
            }
        ],
    )
    claims = factual_claims(artifact, rows)
    claim = next(c for c in claims if c["calculation"].startswith(operation + "("))
    assert Decimal(claim["value"]) == Decimal(expected)
    if field == "return_rate":
        assert not any(c["calculation"].startswith("total(") for c in claims)


async def test_genuine_queue_backlog_is_not_mistaken_for_lost_delivery():
    store, _, chat, repo = await setup()
    run = await repo.create(chat["id"], "guest", body())
    await store.put(
        "report_outbox",
        run["id"],
        {"id": run["id"], "delivery": 0, "pending": False, "enqueued_at": time.time() - 1800},
    )
    await ReportDispatcher(repo, None).reconcile()
    assert (await repo.get("report_runs", run["id"]))["delivery"] == 0
    outbox = await store.get("report_outbox", run["id"])
    outbox["received_at"] = time.time() - 200
    await store.put("report_outbox", run["id"], outbox)
    await ReportDispatcher(repo, None).reconcile()
    assert (await repo.get("report_runs", run["id"]))["delivery"] == 1


async def test_fixture_binder_errors_use_controlled_sql_repair_classification():
    from app.connectors import Connectors

    connectors = Connectors(Settings())
    with pytest.raises(AppError) as error:
        await connectors.query(
            "bigquery", "SELECT SUM(nonexistent_column) AS revenue FROM orders", "test-report"
        )
    assert error.value.code == "invalid_sql"
    with pytest.raises(AppError) as forbidden:
        await connectors.query("bigquery", "DELETE FROM orders", "test-report")
    assert forbidden.value.code == "unsafe_sql"


def test_worker_handlers_are_absent_from_public_application():
    app = create_app(Settings())
    assert not any(getattr(route, "path", "").startswith("/internal/reports") for route in app.routes)


async def test_structured_future_assumptions_are_preserved_without_model_defaults():
    _, _, _, repo, run, lease = await started()
    requirements = [{"target": "revenue", "drivers": ["promotion"], "grain": "month", "horizon": 3}]
    await repo.finish(
        lease, "waiting_input", clarification="Future promotion values?", requirements=requirements
    )
    current = await repo.get("report_runs", run["id"])
    assert current["clarification_requirements"] == requirements
    submitted = ReportClarification(
        answer="Keep baseline promotion unchanged; compare my alternative.",
        expected_revision=current["revision"],
        forecast_inputs={"revenue": {"baseline": [{"promotion": 0}] * 3, "scenario": [{"promotion": 2}] * 3}},
    )
    await repo.clarify(run["id"], "guest", submitted)
    resumed = await repo.get("report_runs", run["id"])
    assert resumed["clarification_requirements"] is None
    assert resumed["clarifications"][0]["forecast_inputs"]["revenue"]["baseline"] == [{"promotion": 0}] * 3
    for value in (float("inf"), float("nan")):
        with pytest.raises(ValueError):
            ReportClarification(
                answer="x",
                expected_revision=1,
                forecast_inputs={"revenue": {"baseline": [{"promotion": value}]}},
            )


def test_monthly_forecast_cutoff_is_period_end_not_bucket_start():
    import pandas as pd

    from app.report_models import ForecastSpec

    rows = [
        {"month": str(date.date()), "sales": 100 + i % 12}
        for i, date in enumerate(pd.date_range("2020-01-01", periods=72, freq="MS"))
    ]
    result = _forecast(
        rows,
        ForecastSpec(
            task_id="monthly", date_column="month", target="sales", grain="month", horizon=3
        ).model_dump(mode="json"),
        1,
        15,
    )
    assert result["cutoff"] == "2025-12-31"
    assert result["last_observed_period"] == "2025-12-01"
    assert result["rows"][-3]["date"] == "2026-01-01"


def test_static_report_axes_preserve_currency_and_percentage_scale():
    from app.report_exports import format_axis

    assert format_axis(1234, {"unit": "currency", "currency": "EUR"}) == "EUR 1,234"
    assert format_axis(0.125, {"unit": "percent", "percent_scale": "fraction"}) == "12.5%"
    assert format_axis(12.5, {"unit": "percent", "percent_scale": "whole"}) == "12.5%"
    assert format_axis(-5, {"unit": "count"}) == "-5"


def test_grouped_ratios_cannot_become_overall_unweighted_average_claims():
    artifact = sample_artifact()
    rows = [
        {"month": "2025-01", "revenue": 100, "orders": 1, "aov": 100, "rate": 0.1},
        {"month": "2025-02", "revenue": 900, "orders": 100, "aov": 9, "rate": 0.9},
    ]
    artifact.update(
        row_count=2,
        columns=[{"name": "month", "type": "STRING"}]
        + [{"name": field, "type": "NUMERIC"} for field in ("revenue", "orders", "aov", "rate")],
    )
    artifact["visualization"].update(
        y=["revenue", "orders", "aov", "rate"],
        measures=[
            {"field": "revenue", "unit": "currency", "currency": "USD", "additive": True},
            {"field": "orders", "unit": "count", "additive": True},
            {"field": "aov", "unit": "currency", "currency": "USD", "additive": False},
            {"field": "rate", "unit": "percent", "percent_scale": "fraction", "additive": False},
        ],
    )
    claims = factual_claims(artifact, rows)
    assert not any(c["calculation"].startswith(("average(aov)", "average(rate)")) for c in claims)
    # Unequal denominators: overall AOV is 1000 / 101, not (100 + 9) / 2.
    assert any(c["calculation"].startswith("total(revenue)") and c["value"] == "1000" for c in claims)
    assert any(c["calculation"].startswith("total(orders)") and c["value"] == "101" for c in claims)
    assert not any(c["value"] == "54.5" for c in claims)
