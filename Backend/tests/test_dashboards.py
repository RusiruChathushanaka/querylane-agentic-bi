import asyncio
import os
import sys
import time
import uuid
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.config import Settings
from app.dashboard_models import (
    ChartViewState,
    DashboardAction,
    DashboardCreate,
    DashboardItemPatch,
    DashboardLayout,
    DashboardPin,
)
from app.dashboards import Dashboards
from app.errors import AppError
from app.main import create_app
from app.maintenance import MAINTENANCE, clear_maintenance, purge_dashboards, reset_history
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
                return self.base.collection(f"test_runs/{self.prefix}/{path}")

            def document(self, path):
                return self.base.document(f"test_runs/{self.prefix}/{path}")

            def __getattr__(self, name):
                return getattr(self.base, name)

        def factory():
            store = FirestoreStore("demo-querylane", "(default)", credentials=AnonymousCredentials())
            store.client = Namespace(store.client, uuid.uuid4().hex)
            clients.append(store)
            return store

        monkeypatch.setattr(sys.modules[__name__], "MemoryStore", factory)
    yield request.param
    for client in clients:
        await client.close()


def request():
    return uuid.uuid4().hex


async def saved(store, key="artifact", *, complete=True, rows=None):
    rows = (
        rows
        if rows is not None
        else [{"month": "2024-01", "revenue": "10.20"}, {"month": "2024-02", "revenue": "0"}]
    )
    artifact = {
        "id": key,
        "conversation_id": "original",
        "title": "Revenue",
        "columns": [{"name": "month", "type": "STRING"}, {"name": "revenue", "type": "NUMERIC"}],
        "row_count": len(rows),
        "page_count": 1 if rows else 0,
        "complete": complete,
        "created_at": "2026-01-01T00:00:00Z",
        "data_profile": "timeseries",
        "visualization": {
            "type": "line",
            "title": "Revenue",
            "x": "month",
            "y": ["revenue"],
            "version": 2,
            "dimension_kind": "temporal",
            "granularity": "month",
            "measures": [{"field": "revenue", "unit": "currency", "currency": "USD", "additive": True}],
        },
        "provenance": [
            {
                "source": "bigquery",
                "executed_at": "2026-01-01T00:00:00Z",
                "sql": "SELECT month,SUM(revenue) FROM sales_orders GROUP BY month",
            }
        ],
        "assumptions": [],
    }
    await store.put("artifacts", key, artifact)
    if rows:
        await store.put(f"artifacts/{key}/pages", "0", {"rows": rows})
    return artifact


async def create(service, name="Sales"):
    return (await service.mutate("guest", "create", DashboardCreate(request_id=request(), name=name)))[
        "dashboard"
    ]


async def pin(service, board, artifact="artifact", view=None, req=None):
    return await service.mutate(
        "guest",
        "pin",
        DashboardPin(
            request_id=req or request(),
            expected_revision=board["revision"],
            artifact_id=artifact,
            view=view or ChartViewState(view="line", primary="revenue", visible_measures=["revenue"]),
        ),
        board["id"],
    )


def action(board, **kwargs):
    return DashboardAction(request_id=request(), expected_revision=board["revision"], **kwargs)


async def test_public_crud_idempotency_recovery_and_metadata_only():
    store = MemoryStore()
    service = Dashboards(store, Settings())
    body = DashboardCreate(request_id=request(), name="  Sales  ")
    first, retry = (
        await service.mutate("guest", "create", body),
        await service.mutate("guest", "create", body),
    )
    assert first == retry and first["dashboard"]["name"] == "Sales"
    assert "created_by" not in first["dashboard"]
    with pytest.raises(AppError, match="Request ID"):
        await service.mutate("guest", "create", body.model_copy(update={"name": "Different"}))
    await saved(store)
    result = await pin(service, first["dashboard"])
    board = result["dashboard"]
    assert board["card_count"] == 1 and not any(
        "rows" in i for i in (await service.detail(board["id"]))["items"]
    )
    deleted = await service.mutate("other", "delete", action(board), board["id"])
    assert not await service.list() and (await service.list(True))[0]["deleted"]
    restored = await service.mutate("other", "restore", action(deleted["dashboard"]), board["id"])
    assert restored["dashboard"]["card_count"] == 1
    assert (await store.get("dashboard_artifact_refs", "artifact"))["count"] == 1


async def test_same_result_in_two_boards_unpin_undo_and_old_retry_never_resurrects():
    store = MemoryStore()
    service = Dashboards(store, Settings())
    await saved(store)
    a, b = await create(service), await create(service, "Finance")
    key = request()
    result = await pin(service, a, req=key)
    a = result["dashboard"]
    item = result["item"]
    assert (await pin(service, {**a, "revision": 1}, req=key)) == result
    await pin(service, b)
    assert (await store.get("dashboard_artifact_refs", "artifact"))["count"] == 2
    removed = await service.mutate("guest", "unpin", action(a), a["id"], item["id"])
    assert (await service.detail(b["id"]))["card_count"] == 1
    assert await store.get("artifacts", "artifact")
    await pin(service, {**a, "revision": 1}, req=key)
    assert (await service.detail(a["id"]))["card_count"] == 0
    recovered = await service.mutate(
        "guest", "item_restore", action(removed["dashboard"]), a["id"], item["id"]
    )
    assert recovered["dashboard"]["card_count"] == 1
    assert (await store.get("dashboard_artifact_refs", "artifact"))["count"] == 2
    with pytest.raises(AppError) as duplicate:
        await pin(service, recovered["dashboard"])
    assert duplicate.value.code == "dashboard_already_pinned"


async def test_concurrent_writers_and_layout_validation():
    store = MemoryStore()
    service = Dashboards(store, Settings())
    await saved(store)
    board = await create(service)
    results = await asyncio.gather(pin(service, board), pin(service, board), return_exceptions=True)
    assert sum(isinstance(v, dict) for v in results) == 1
    assert next(v for v in results if isinstance(v, AppError)).code == "dashboard_conflict"
    board = await service.get(board["id"])
    with pytest.raises(AppError) as bad:
        await service.mutate(
            "guest",
            "layout",
            DashboardLayout(request_id=request(), expected_revision=board["revision"], item_ids=[]),
            board["id"],
        )
    assert bad.value.code == "dashboard_layout_invalid"


async def test_view_validation_partial_empty_missing_pages_and_no_arbitrary_fields():
    store = MemoryStore()
    service = Dashboards(store, Settings())
    board = await create(service)
    await saved(store, complete=False)
    view = ChartViewState(
        view="bar",
        start="2024-01-01",
        end="2024-02-29",
        primary="revenue",
        visible_measures=["revenue"],
        highlights=False,
        decimals=0,
        top=5,
    )
    result = await pin(service, board, view=view)
    assert (
        result["item"]["view"] == view.model_dump(mode="json") and not result["item"]["summary"]["complete"]
    )
    await saved(store, "empty", rows=[])
    result = await pin(service, result["dashboard"], "empty", ChartViewState(view="table"))
    assert result["item"]["summary"]["row_count"] == 0
    await saved(store, "bad")
    await store.delete("artifacts/bad/pages", "0")
    with pytest.raises(AppError) as missing:
        await pin(service, result["dashboard"], "bad")
    assert missing.value.code == "artifact_incomplete"
    await saved(store, "fields")
    with pytest.raises(AppError):
        await pin(
            service, result["dashboard"], "fields", ChartViewState(view="line", visible_measures=["password"])
        )


async def test_capacity_quotas_full_restore_and_failed_changes_do_not_charge():
    store = MemoryStore()
    service = Dashboards(
        store, Settings(dashboard_item_limit=1, dashboard_guest_hourly_limit=20, dashboard_limit=2)
    )
    await saved(store)
    await saved(store, "second")
    a = await create(service)
    p = await pin(service, a)
    a = p["dashboard"]
    item = p["item"]
    with pytest.raises(AppError) as full:
        await pin(service, a, "second")
    assert full.value.code == "dashboard_full" and (await service.get(a["id"]))["revision"] == a["revision"]
    removed = await service.mutate("guest", "unpin", action(a), a["id"], item["id"])
    p2 = await pin(service, removed["dashboard"], "second")
    with pytest.raises(AppError) as full:
        await service.mutate("guest", "item_restore", action(p2["dashboard"]), a["id"], item["id"])
    assert full.value.code == "dashboard_full"
    await create(service, "B")
    with pytest.raises(AppError) as limit:
        await create(service, "C")
    assert limit.value.code == "dashboard_capacity"
    limited = Dashboards(MemoryStore(), Settings(dashboard_guest_hourly_limit=1))
    await create(limited)
    with pytest.raises(AppError) as quota:
        await create(limited, "Second")
    assert quota.value.status == 429


async def test_reset_preserves_retained_pages_and_skills_but_removes_unpinned_history():
    store = MemoryStore()
    service = Dashboards(store, Settings())
    await saved(store)
    await saved(store, "unpinned")
    p = await pin(service, await create(service))
    await store.put("conversations", "original", {"id": "original"})
    await store.put("skills", "playbook", {"revision": 1})
    await store.put("skills/playbook/revisions", "1", {"instructions": "Definition"})
    result = await reset_history(store, timeout=0)
    assert result == {"preserved_artifacts": 1, "removed_artifacts": 1}
    assert await store.get("artifacts/artifact/pages", "0")
    assert not await store.get("artifacts", "unpinned") and not await store.get("conversations", "original")
    assert await store.get("skills/playbook/revisions", "1")
    assert (await service.detail(p["dashboard"]["id"]))["card_count"] == 1


async def test_reset_fences_new_writes_waits_existing_work_and_requires_explicit_failed_recovery():
    store = MemoryStore()
    repo = Repository(store, Settings())
    service = Dashboards(store, Settings())
    await saved(store)
    board = await create(service)
    chat = await repo.create_conversation("Active", "all")
    await repo.begin(chat["id"], "guest", "Question", "question-01")
    with pytest.raises(AppError) as busy:
        await reset_history(store, timeout=0)
    assert busy.value.code == "maintenance_busy" and (await store.get(*MAINTENANCE))["active"]
    with pytest.raises(AppError) as blocked:
        await pin(service, board)
    assert blocked.value.code == "maintenance"
    with pytest.raises(AppError):
        await repo.create_conversation("New", "all")
    await clear_maintenance(store)
    await pin(service, board)


async def test_reset_wins_pin_race_without_dangling_reference():
    store = MemoryStore()
    service = Dashboards(store, Settings())
    await saved(store)
    board = await create(service)
    original = service.validated

    async def validated(*args):
        result = await original(*args)
        await reset_history(store, timeout=0)
        return result

    service.validated = validated
    with pytest.raises(AppError) as missing:
        await pin(service, board)
    assert missing.value.code == "artifact_unavailable"
    assert not await store.get("dashboard_artifact_refs", "artifact")


async def test_purge_releases_only_expired_references_and_undo_keeps_other_board():
    store = MemoryStore()
    service = Dashboards(store, Settings())
    await saved(store)
    a, b = await create(service), await create(service, "B")
    first = await pin(service, a)
    await pin(service, b)
    await service.mutate("guest", "delete", action(first["dashboard"]), a["id"])
    assert (await purge_dashboards(store, timeout=0, now=time.time() + 31 * 86400))["purged_items"] == 1
    assert (await store.get("dashboard_artifact_refs", "artifact"))["count"] == 1
    await reset_history(store, timeout=0)
    assert await store.get("artifacts/artifact/pages", "0")


def test_http_routes_no_query_or_model_access_and_public_metadata():
    with TestClient(create_app(Settings(environment="test"), store_override=MemoryStore())) as client:
        services = client.app.state.services
        services.connectors.query = AsyncMock(side_effect=AssertionError("No SQL permitted"))
        services.ai.plan = AsyncMock(side_effect=AssertionError("No Gemini permitted"))
        headers = {"Authorization": "Bearer " + client.post("/api/v1/guest-sessions").json()["token"]}
        assert (
            client.post("/api/v1/dashboards", json={"name": "No guest", "request_id": request()}).status_code
            == 401
        )
        board = client.post(
            "/api/v1/dashboards", headers=headers, json={"name": "Shared", "request_id": request()}
        ).json()["dashboard"]
        assert client.get("/api/v1/dashboards").json()["dashboards"][0]["id"] == board["id"]
        response = client.put(
            f"/api/v1/dashboards/{board['id']}/layout",
            headers=headers,
            json={"item_ids": [], "expected_revision": 1, "request_id": request()},
        )
        assert response.status_code == 200
        assert services.connectors.query.await_count == 0 and services.ai.plan.await_count == 0


async def test_saved_card_view_edits_and_source_badges_follow_active_cards():
    store = MemoryStore()
    service = Dashboards(store, Settings())
    await saved(store)
    result = await pin(service, await create(service))
    board, item = result["dashboard"], result["item"]
    view = ChartViewState(
        view="area",
        visible_measures=["revenue"],
        primary="revenue",
        start="2024-02-01",
        highlights=False,
        decimals=1,
    )
    changed = await service.mutate(
        "another-visitor",
        "item_patch",
        DashboardItemPatch(
            expected_revision=board["revision"],
            request_id=request(),
            view=view,
            title="February review",
            note="Public note",
            width="wide",
        ),
        board["id"],
        item["id"],
    )
    assert changed["item"]["view"] == view.model_dump(mode="json")
    assert changed["item"]["width"] == "wide"
    assert (await store.get("artifacts", "artifact"))["title"] == "Revenue"
    removed = await service.mutate("guest", "unpin", action(changed["dashboard"]), board["id"], item["id"])
    assert removed["dashboard"]["sources"] == []
    assert not (await service.detail(board["id"]))["items"]


async def test_readiness_and_pin_do_not_require_the_voice_conversation_to_be_idle():
    store = MemoryStore()
    service = Dashboards(store, Settings())
    artifact = await saved(store)
    await store.put(
        "conversations", artifact["conversation_id"], {"active_run": "live", "lease_until": time.time() + 180}
    )
    result = await pin(service, await create(service))
    assert (await service.detail(result["dashboard"]["id"]))["items"][0]["conversation_available"]
    assert (await store.get("conversations", artifact["conversation_id"]))["active_run"] == "live"


async def test_layout_reorder_and_restore_keep_consistent_order():
    store = MemoryStore()
    service = Dashboards(store, Settings())
    await saved(store)
    await saved(store, "second")
    first = await pin(service, await create(service))
    second = await pin(service, first["dashboard"], "second")
    board = second["dashboard"]
    order = list(reversed(board["item_ids"]))
    result = await service.mutate(
        "guest",
        "layout",
        DashboardLayout(request_id=request(), expected_revision=board["revision"], item_ids=order),
        board["id"],
    )
    assert [i["id"] for i in (await service.detail(board["id"]))["items"]] == order
    removed = await service.mutate("guest", "unpin", action(result["dashboard"]), board["id"], order[0])
    restored = await service.mutate(
        "guest", "item_restore", action(removed["dashboard"]), board["id"], order[0]
    )
    assert restored["dashboard"]["item_ids"] == order


async def test_noop_changes_do_not_charge_quota_or_change_revision():
    from app.dashboard_models import DashboardPatch

    store = MemoryStore()
    service = Dashboards(store, Settings(dashboard_guest_hourly_limit=1))
    board = await create(service)
    result = await service.mutate(
        "guest",
        "patch",
        DashboardPatch(request_id=request(), expected_revision=board["revision"], name=board["name"]),
        board["id"],
    )
    assert result["dashboard"]["revision"] == board["revision"]
    layout = await service.mutate(
        "guest",
        "layout",
        DashboardLayout(request_id=request(), expected_revision=board["revision"], item_ids=[]),
        board["id"],
    )
    assert layout["dashboard"]["revision"] == board["revision"]


async def test_maintenance_scans_more_than_one_page_without_skipping_deleted_cursors():
    store = MemoryStore()
    # Independent documents model an older history larger than one maintenance scan page.
    for index in range(105):
        await store.put("artifacts", f"old-{index:03}", {"id": f"old-{index:03}"})
    result = await reset_history(store, timeout=0)
    assert result["removed_artifacts"] == 105
    assert [value async for _, value in store.iter_documents("artifacts")] == []


async def test_zero_model_and_connector_calls_for_full_saved_result_workflow():
    # All HTTP actions operate on a pre-existing immutable result, including its presentation and CSV.
    with TestClient(create_app(Settings(environment="test"), store_override=MemoryStore())) as client:
        services = client.app.state.services
        client.portal.call(saved, services.store)
        services.connectors.query = AsyncMock(side_effect=AssertionError("No source SQL"))
        services.ai.plan = AsyncMock(side_effect=AssertionError("No Gemini"))
        services.ai.answer = AsyncMock(side_effect=AssertionError("No interpreter"))
        headers = {"Authorization": "Bearer " + client.post("/api/v1/guest-sessions").json()["token"]}
        board = client.post(
            "/api/v1/dashboards", headers=headers, json={"name": "Saved only", "request_id": request()}
        ).json()["dashboard"]
        pin_body = {
            "request_id": request(),
            "expected_revision": board["revision"],
            "artifact_id": "artifact",
            "view": ChartViewState(view="line", visible_measures=["revenue"], primary="revenue").model_dump(
                mode="json"
            ),
        }
        pinned = client.post(f"/api/v1/dashboards/{board['id']}/items", headers=headers, json=pin_body)
        assert pinned.status_code == 200
        item = pinned.json()["item"]
        board = pinned.json()["dashboard"]
        for path in [
            f"/dashboards/{board['id']}",
            "/artifacts/artifact?metadata_only=true",
            "/artifacts/artifact/chart-data",
            "/artifacts/artifact/export.csv",
        ]:
            assert client.get("/api/v1" + path).status_code == 200
        removed = client.delete(
            f"/api/v1/dashboards/{board['id']}/items/{item['id']}?expected_revision={board['revision']}&request_id={request()}",
            headers=headers,
        )
        assert removed.status_code == 200
        for mock in [services.connectors.query, services.ai.plan, services.ai.answer]:
            assert mock.await_count == 0


async def test_dashboard_settings_keep_layout_and_capacity_bounds():
    from pydantic import ValidationError

    for config in ({"dashboard_item_limit": 21}, {"dashboard_limit": 0}, {"dashboard_recovery_days": 0}):
        with pytest.raises(ValidationError):
            Settings(**config)


async def test_fresh_firestore_client_retains_dashboard_pages_and_evidence(storage_adapter):
    if storage_adapter != "firestore":
        pytest.skip("Durability requires the opt-in Firestore emulator.")
    from google.auth.credentials import AnonymousCredentials
    from google.cloud import firestore

    store = MemoryStore()
    artifact = await saved(store)
    service = Dashboards(store, Settings())
    pinned = await pin(service, await create(service))
    namespace, project = store.client.prefix, store.client.project
    wrapper = type(store.client)
    await store.close()
    store.client = wrapper(
        firestore.Client(project=project, database="(default)", credentials=AnonymousCredentials()),
        namespace,
    )
    reopened = await Dashboards(store, Settings()).detail(pinned["dashboard"]["id"])
    assert reopened["items"][0]["artifact_id"] == artifact["id"]
    assert await store.get("artifacts", artifact["id"]) == artifact
    assert (await store.get(f"artifacts/{artifact['id']}/pages", "0"))["rows"][0]["revenue"] == "10.20"
