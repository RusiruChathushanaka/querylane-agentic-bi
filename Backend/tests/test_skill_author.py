import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from google.adk.events import Event
from google.genai import types
from starlette.websockets import WebSocketDisconnect

from app.adk_sessions import FirestoreSessionService
from app.config import Settings
from app.errors import AppError, StaleLease
from app.main import create_app
from app.repository import Repository, active_lease
from app.skill_author import COLLECTION, AuthorDraft, SkillAuthor
from app.skills import SkillContent, Skills
from app.storage import MemoryStore

BRIEF = dict(
    name="Revenue reporting",
    description="Report retail gross revenue consistently.",
    purpose="Review retail revenue.",
    when_to_use="Monthly revenue or total sales.",
    source="bigquery",
    workflow="Use completed orders at order grain. Preserve the requested filters and USD units.",
    definitions="Gross revenue is before refunds. Use orders.revenue once per order.",
    examples="Show monthly revenue as a line chart.",
    tags="revenue, monthly",
)
ORIGIN = {"Origin": "http://localhost:3000"}


@pytest.fixture
def client():
    with TestClient(create_app(Settings(environment="test"))) as value:
        yield value


def guest(client):
    return {"Authorization": "Bearer " + client.post("/api/v1/guest-sessions").json()["token"]}


def create(client, headers, key="author-session-test"):
    result = client.post("/api/v1/skills/author-sessions", headers=headers, json={"idempotency_key": key})
    assert result.status_code == 201
    return result.json()


def setup_service(**overrides):
    settings = Settings(environment="test", **overrides)
    store = MemoryStore()
    repo = Repository(store, settings)
    services = SimpleNamespace(
        settings=settings, store=store, analysis=SimpleNamespace(skills=Skills(repo, settings))
    )
    return SkillAuthor(services)


async def prepared(author, guest_id="guest", key="author-session-test"):
    value = await author.create(guest_id, key)
    lease, _ = await author.acquire(value["id"], guest_id)
    await author.update_brief(value["id"], guest_id, BRIEF, lease)
    value = await author.prepare(value["id"], guest_id, lease)
    await author.release(lease)
    return value


def test_creation_ownership_recovery_idempotency_and_no_public_listing(client):
    headers = guest(client)
    value = create(client, headers)
    assert value == create(client, headers)
    assert value["status"] == "collecting" and len(value["missing_fields"]) == 6
    path = "/api/v1/skills/author-sessions/" + value["id"]
    assert client.get(path).status_code == 401
    assert client.get(path, headers=guest(client)).status_code == 404
    assert client.get(path, headers=headers).json() == value
    assert not {"guest_id", "active_run", "generation", "lease_until"} & value.keys()
    assert client.get("/api/v1/skills").json() == {"skills": []}


@pytest.mark.asyncio
async def test_create_and_connection_quotas_are_atomic_and_retry_safe():
    author = setup_service(author_guest_hourly_limit=1, author_voice_guest_hourly_limit=1)
    value = await author.create("guest", "key-00001")
    assert await author.create("guest", "key-00001") == value
    with pytest.raises(AppError, match="usage limit"):
        await author.create("guest", "key-00002")
    lease, _ = await author.acquire(value["id"], "guest")
    with pytest.raises(AppError) as busy:
        await author.acquire(value["id"], "guest")
    assert busy.value.code == "author_busy"
    await author.release(lease)
    with pytest.raises(AppError) as limited:
        await author.acquire(value["id"], "guest")
    assert limited.value.code == "author_usage_limit"


@pytest.mark.asyncio
async def test_missing_fields_corrections_invalidate_draft_and_do_not_publish():
    author = setup_service()
    value = await author.create("guest", "key-00001")
    lease, _ = await author.acquire(value["id"], "guest")
    await author.update_brief(value["id"], "guest", {"purpose": "Revenue"}, lease)
    with pytest.raises(AppError) as incomplete:
        await author.prepare(value["id"], "guest", lease)
    assert incomplete.value.code == "author_incomplete"
    await author.update_brief(value["id"], "guest", BRIEF, lease)
    first = await author.prepare(value["id"], "guest", lease)
    assert first["draft"]["instructions"].count("## ") == 4
    assert not await author.store.list("skills")
    revision = first["revision"]
    assert (await author.prepare(value["id"], "guest", lease))["revision"] == revision
    changed = await author.update_brief(
        value["id"], "guest", {"definitions": "Net revenue subtracts refunds."}, lease
    )
    assert changed["draft"] is None and first["draft"] is not None
    assert changed["brief"]["purpose"] == BRIEF["purpose"]
    assert "Net revenue" in (await author.prepare(value["id"], "guest", lease))["draft"]["instructions"]


@pytest.mark.asyncio
async def test_publish_once_uses_reviewed_version_and_normal_skill_controls():
    author = setup_service()
    value = await prepared(author)
    content = SkillContent(**(value["draft"] | {"name": "Reviewed revenue"}))
    edited = await author.edit_draft(
        value["id"], "guest", AuthorDraft(expected_revision=value["revision"], content=content)
    )
    with pytest.raises(AppError) as conflict:
        await author.publish(value["id"], "guest", value["revision"])
    assert conflict.value.code == "author_conflict"
    skill = await author.publish(value["id"], "guest", edited["revision"])
    replay = await author.publish(value["id"], "guest", edited["revision"])
    assert replay == skill and skill["enabled"] and skill["revision"] == 1
    assert len(await author.store.list("skills")) == 1
    assert skill["name"] == "Reviewed revenue"
    assert (await author.store.get("system", "skills_capacity"))["count"] == 1
    changed = await author.services.analysis.skills.mutate(
        "other", skill_id=skill["id"], action="delete", patch={"expected_revision": 1}
    )
    assert (await author.publish(value["id"], "guest", edited["revision"])) == changed
    assert (await author.get(value["id"], "guest"))["status"] == "published"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "setting,code",
    [("skill_catalog_limit", "skill_capacity"), ("skill_workspace_daily_limit", "usage_limit")],
)
async def test_publication_capacity_and_quota_failures_preserve_draft(setting, code):
    author = setup_service(**{setting: 0})
    value = await prepared(author)
    with pytest.raises(AppError) as failure:
        await author.publish(value["id"], "guest", value["revision"])
    assert failure.value.code == code
    assert (await author.get(value["id"], "guest"))["draft"] == value["draft"]
    assert not await author.store.list("skills")


@pytest.mark.asyncio
async def test_one_connection_stale_tools_and_adk_events_cannot_cross_author_fence():
    author = setup_service()
    value = await author.create("guest", "key-00001")
    results = await asyncio.gather(
        author.acquire(value["id"], "guest"), author.acquire(value["id"], "guest"), return_exceptions=True
    )
    assert sum(isinstance(r, tuple) for r in results) == 1
    lease, _ = next(r for r in results if isinstance(r, tuple))
    sessions = FirestoreSessionService(author.store)
    token = active_lease.set(lease)
    old = await sessions.create_session(app_name="skill_author", user_id="guest", session_id="test")
    await sessions.append_event(
        old, Event(author="model", content=types.Content(parts=[types.Part(text="Question")], role="model"))
    )
    await author.release(lease)
    new_lease, _ = await author.acquire(value["id"], "guest")
    with pytest.raises(StaleLease):
        await author.update_brief(value["id"], "guest", BRIEF, lease)
    with pytest.raises(StaleLease):
        await sessions.append_event(
            old, Event(author="model", content=types.Content(parts=[types.Part(text="Stale")], role="model"))
        )
    active_lease.reset(token)
    await author.release(lease)
    assert (await author.get(value["id"], "guest"))["active_run"] == new_lease["run_id"]


@pytest.mark.asyncio
async def test_draft_edit_and_publish_are_blocked_during_voice_and_revision_checked():
    author = setup_service()
    value = await prepared(author)
    lease, _ = await author.acquire(value["id"], "guest")
    with pytest.raises(AppError) as busy:
        await author.publish(value["id"], "guest", value["revision"])
    assert busy.value.code == "author_busy"
    await author.release(lease)
    body = AuthorDraft(expected_revision=value["revision"] - 1, content=SkillContent(**value["draft"]))
    with pytest.raises(AppError) as conflict:
        await author.edit_draft(value["id"], "guest", body)
    assert conflict.value.code == "author_conflict"


@pytest.mark.asyncio
async def test_expiry_and_transcript_turn_budgets_do_not_discard_committed_content():
    author = setup_service(author_turn_limit=1)
    value = await author.create("guest", "key-00001")
    lease, _ = await author.acquire(value["id"], "guest")
    await author.transcript(
        value["id"], "guest", [("user", "Revenue"), ("assistant", "Which source?")], lease
    )
    with pytest.raises(AppError) as limit:
        await author.transcript(value["id"], "guest", [("user", "Another question")], lease)
    assert limit.value.code == "author_turn_limit"
    saved = await author.get(value["id"], "guest")
    assert len(saved["transcript"]) == 2
    saved["expires_at"] = 0
    await author.store.put(COLLECTION, value["id"], saved)
    with pytest.raises(AppError) as expired:
        await author.get(value["id"], "guest")
    assert expired.value.status == 410


@pytest.mark.asyncio
async def test_utf8_transcript_and_brief_update_limits():
    author = setup_service(author_transcript_bytes=100, author_update_limit=1)
    value = await author.create("guest", "key-00001")
    lease, _ = await author.acquire(value["id"], "guest")
    with pytest.raises(AppError) as limit:
        await author.transcript(value["id"], "guest", [("user", "é" * 100)], lease)
    assert limit.value.code == "author_transcript_limit"
    await author.update_brief(value["id"], "guest", BRIEF, lease)
    with pytest.raises(AppError) as updates:
        await author.prepare(value["id"], "guest", lease)
    assert updates.value.code == "author_update_limit"


@pytest.mark.parametrize("origin", [None, "https://untrusted.example", "null"])
def test_voice_origin_guard(client, origin):
    headers = guest(client)
    value = create(client, headers)
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(
            f"/api/v1/skills/author-sessions/{value['id']}/voice",
            headers={"Origin": origin} if origin else {},
        ):
            pass


def test_voice_handshake_and_fixture_mode_are_explicit(client):
    headers = guest(client)
    value = create(client, headers)
    url = f"/api/v1/skills/author-sessions/{value['id']}/voice"
    for first in [[], {"type": "audio"}, {"type": "authenticate", "token": "invalid"}]:
        with client.websocket_connect(url, headers=ORIGIN) as socket:
            socket.send_json(first)
            assert socket.receive_json()["type"] == "error"
    with client.websocket_connect(url, headers=ORIGIN) as socket:
        socket.send_json({"type": "authenticate", "token": headers["Authorization"][7:]})
        assert socket.receive_json()["code"] == "author_model_required"


def test_mocked_live_interview_streams_draft_and_keeps_it_unpublished(monkeypatch):
    import app.skill_author_voice as live

    client_closed = AsyncMock()
    monkeypatch.setattr(
        live, "Client", lambda **kw: SimpleNamespace(aio=SimpleNamespace(aclose=client_closed))
    )
    monkeypatch.setattr(live, "Gemini", lambda **kw: "fixture-live")

    class MockRunner:
        def __init__(self, agent, **kwargs):
            self.agent = agent
            assert [f.__name__ for f in agent.tools] == ["update_skill_brief", "prepare_skill_draft"]

        async def run_live(self, live_request_queue, **kwargs):
            count = 0
            while True:
                request = await live_request_queue.get()
                if not request.content:
                    continue
                count += 1
                if count == 1:
                    yield Event(
                        author="model",
                        partial=True,
                        output_transcription=types.Transcription(text="What task should "),
                    )
                    yield Event(
                        author="model",
                        output_transcription=types.Transcription(
                            text="What task should the skill help with?", finished=True
                        ),
                        turn_complete=True,
                    )
                else:
                    await self.agent.tools[0](**BRIEF)
                    result = await self.agent.tools[1]()
                    assert result["draft_ready"]
                    # ADK can finish a tool-only turn or interrupt it before
                    # the actual spoken response arrives.
                    yield Event(author="model", turn_complete=True)
                    yield Event(author="model", interrupted=True, turn_complete=True)
                    yield Event(
                        author="model",
                        content=types.Content(
                            role="model",
                            parts=[
                                types.Part(
                                    inline_data=types.Blob(data=b"\0\0", mime_type="audio/pcm;rate=24000")
                                )
                            ],
                        ),
                        output_transcription=types.Transcription(
                            text="Your draft is ready. Please review it."
                        ),
                        turn_complete=True,
                    )

    monkeypatch.setattr(live, "Runner", MockRunner)
    with TestClient(create_app(Settings(environment="test", ai_backend="gemini"))) as client:
        headers = guest(client)
        value = create(client, headers)
        path = "/api/v1/skills/author-sessions/" + value["id"]
        seen = set()
        with client.websocket_connect(path + "/voice", headers=ORIGIN) as socket:
            socket.send_json({"type": "authenticate", "token": headers["Authorization"][7:]})
            while True:
                event = socket.receive_json()
                seen.add(event["type"])
                if event["type"] == "turn_complete":
                    assert (
                        event["session"]["transcript"][-1]["text"] == "What task should the skill help with?"
                    )
                    break
            socket.send_json(
                {"type": "text", "text": "Help with monthly revenue; use gross revenue before refunds."}
            )
            while True:
                event = socket.receive_json()
                seen.add(event["type"])
                if event["type"] == "turn_complete":
                    break
            socket.send_json({"type": "stop"})
            assert socket.receive_json()["type"] == "stopped"
        assert {"ready", "brief", "draft", "audio", "transcript", "turn_complete", "user_message"} <= seen
        recovered = client.get(path, headers=headers).json()
        assert not recovered["connected"] and recovered["draft"]["name"] == BRIEF["name"]
        assert recovered["turns"] == 1 and not client.get("/api/v1/skills").json()["skills"]
        assert "audio" not in str(recovered).lower()
        skill = client.post(
            path + "/publish", headers=headers, json={"expected_revision": recovered["revision"]}
        ).json()
        assert skill["enabled"] and skill["revision"] == 1
    client_closed.assert_awaited_once()


@pytest.mark.asyncio
async def test_competing_publish_and_review_cannot_silently_publish_a_stale_draft():
    author = setup_service()
    value = await prepared(author)
    edit = AuthorDraft(
        expected_revision=value["revision"],
        content=SkillContent(**(value["draft"] | {"name": "Concurrent edit"})),
    )
    outcomes = await asyncio.gather(
        author.edit_draft(value["id"], "guest", edit),
        author.publish(value["id"], "guest", value["revision"]),
        return_exceptions=True,
    )
    assert sum(isinstance(item, AppError) for item in outcomes) == 1
    stored = await author.get(value["id"], "guest")
    skills = await author.store.list("skills")
    if stored["published_skill_id"]:
        assert len(skills) == 1 and skills[0]["name"] == value["draft"]["name"]
    else:
        assert not skills and stored["draft"]["name"] == "Concurrent edit"


@pytest.mark.asyncio
async def test_tool_call_budget_counts_noops_and_failed_draft_attempts():
    author = setup_service(author_tool_limit=2)
    value = await author.create("guest", "key-00001")
    lease, _ = await author.acquire(value["id"], "guest")
    for _ in range(2):
        await author.consume_tool(value["id"], "guest", lease)
        await author.update_brief(value["id"], "guest", {}, lease)
    with pytest.raises(AppError) as limit:
        await author.consume_tool(value["id"], "guest", lease)
    assert limit.value.code == "author_tool_limit"
    assert (await author.get(value["id"], "guest"))["revision"] == 1


def test_admin_cleanup_is_scoped_to_expired_inactive_authors(monkeypatch):
    import app.admin as admin

    def document(name, expires, lease):
        return SimpleNamespace(
            id=name,
            reference="author/" + name,
            to_dict=lambda: {
                "expires_at": expires,
                "lease_until": lease,
                "guest_id": "guest",
                "generation": 2,
            },
        )

    removed = []

    class Collection:
        def __init__(self, name):
            self.name = name

        def stream(self):
            assert self.name == COLLECTION
            return [
                document("expired", 0, 0),
                document("future", float("inf"), 0),
                document("active", 0, float("inf")),
            ]

        def document(self, key):
            return self.name + "/" + key

    fake = SimpleNamespace(collection=Collection, recursive_delete=removed.append, close=lambda: None)
    monkeypatch.setattr(admin.firestore, "Client", lambda **kwargs: fake)
    monkeypatch.setattr(admin, "operator_credentials", lambda: None)
    asyncio.run(admin.cleanup_skill_authors())
    assert "author/expired" in removed and len(removed) == 3
    assert all(item.startswith("adk_sessions/") or item == "author/expired" for item in removed)
