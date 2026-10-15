import asyncio
import time

import pytest
from google.adk.events import Event
from google.genai import types

from app.adk_sessions import FirestoreSessionService
from app.config import Settings
from app.errors import AppError, StaleLease
from app.repository import Repository, active_lease
from app.storage import MemoryStore


async def setup_run():
    store = MemoryStore()
    repo = Repository(store, Settings())
    conversation = await repo.create_conversation("New exploration", "all")
    run, _ = await repo.begin(conversation["id"], "guest", "Revenue?", "request-1")
    lease = {"run_id": run["id"], "conversation_id": conversation["id"], "generation": run["generation"]}
    return store, repo, conversation, run, lease


async def test_idempotent_start_charges_once():
    store, repo, conversation, run, _ = await setup_run()
    same, created = await repo.begin(conversation["id"], "guest", "Revenue?", "request-1")
    assert same["id"] == run["id"] and not created
    quotas = await store.list("quotas")
    assert all(value["count"] == 1 for value in quotas)
    with pytest.raises(AppError, match="another question"):
        await repo.begin(conversation["id"], "guest", "Different?", "request-1")


async def test_simultaneous_turns_have_one_winner():
    store = MemoryStore()
    repo = Repository(store, Settings())
    conversation = await repo.create_conversation("Test", "all")
    results = await asyncio.gather(
        repo.begin(conversation["id"], "guest1", "Question A", "request-a"),
        repo.begin(conversation["id"], "guest2", "Question B", "request-b"),
        return_exceptions=True,
    )
    assert sum(isinstance(result, tuple) for result in results) == 1
    assert sum(isinstance(result, AppError) and result.code == "conversation_busy" for result in results) == 1


async def test_completion_between_status_reads_is_not_reported_as_interrupted():
    store, repo, conversation, run, lease = await setup_run()
    original_get = store.get
    finished = False

    async def finish_during_read(collection, key):
        nonlocal finished
        value = await original_get(collection, key)
        if collection == "runs" and key == run["id"] and not finished:
            finished = True
            token = active_lease.set(lease)
            try:
                await repo.finish("complete")
            finally:
                active_lease.reset(token)
        return value

    store.get = finish_during_read
    assert (await repo.run(run["id"]))["status"] == "complete"


async def test_expired_worker_cannot_append_or_release_successor():
    store, repo, conversation, run, lease = await setup_run()
    value = await store.get("conversations", conversation["id"])
    value["lease_until"] = time.time() - 1
    await store.put("conversations", conversation["id"], value)
    successor, _ = await repo.begin(conversation["id"], "guest2", "Another", "request-2")
    token = active_lease.set(lease)
    try:
        with pytest.raises(StaleLease):
            await repo.emit("answer", {"text": "stale"})
        with pytest.raises(StaleLease):
            await repo.finish("complete")
    finally:
        active_lease.reset(token)
    assert (await store.get("conversations", conversation["id"]))["active_run"] == successor["id"]


async def test_session_round_trip_order_state_and_partial_events():
    store, repo, conversation, run, lease = await setup_run()
    token = active_lease.set(lease)
    service = FirestoreSessionService(store)
    try:
        session = await service.create_session(
            app_name="agentic_bi", user_id="public-demo", session_id="test"
        )
        await service.append_event(
            session,
            Event(author="user", content=types.Content(role="user", parts=[types.Part(text="Revenue?")])),
        )
        final = Event(
            author="analyst", content=types.Content(role="model", parts=[types.Part(text="A result")])
        )
        final.actions.state_delta = {"metric": "revenue", "temp:secret": "ephemeral"}
        await service.append_event(session, final)
        await service.append_event(session, Event(author="analyst", partial=True))
        # A new adapter simulates a different Cloud Run instance.
        loaded = await FirestoreSessionService(store).get_session(
            app_name="agentic_bi", user_id="public-demo", session_id="test"
        )
        assert len(loaded.events) == 2
        assert loaded.events[0].author == "user"
        assert loaded.state["metric"] == "revenue"
        assert "temp:secret" not in loaded.state
        other = await service.create_session(
            app_name="agentic_bi", user_id="public-demo", session_id="another"
        )
        assert not other.state
    finally:
        active_lease.reset(token)


async def test_stale_session_revision_is_rejected():
    store, repo, conversation, run, lease = await setup_run()
    token = active_lease.set(lease)
    a, b = FirestoreSessionService(store), FirestoreSessionService(store)
    try:
        first = await a.create_session(app_name="a", user_id="u", session_id="s")
        second = await b.get_session(app_name="a", user_id="u", session_id="s")
        await a.append_event(first, Event(author="user"))
        with pytest.raises(StaleLease):
            await b.append_event(second, Event(author="user"))
    finally:
        active_lease.reset(token)


async def test_fresh_read_does_not_upgrade_stale_session_object():
    store = MemoryStore()
    service = FirestoreSessionService(store)
    stale = await service.create_session(app_name="a", user_id="u", session_id="s")
    writer = await service.get_session(app_name="a", user_id="u", session_id="s")
    await service.append_event(writer, Event(author="user"))
    fresh = await service.get_session(app_name="a", user_id="u", session_id="s")
    with pytest.raises(StaleLease):
        await service.append_event(stale, Event(author="user"))
    await service.append_event(fresh, Event(author="user"))
    loaded = await service.get_session(app_name="a", user_id="u", session_id="s")
    assert len(loaded.events) == 2
    assert "_agentic_revision" not in loaded.model_dump()


async def test_shared_limit_applies_across_repository_instances():
    store = MemoryStore()
    repos = [Repository(store, Settings()), Repository(store, Settings())]
    await repos[0].quota([("global-limit", 1)])
    with pytest.raises(AppError) as exc:
        await repos[1].quota([("global-limit", 1)])
    assert exc.value.status == 429


async def test_fork_keeps_immutable_artifact_references():
    store, repo, conversation, run, lease = await setup_run()
    await store.put(
        f"conversations/{conversation['id']}/messages",
        "answer",
        {
            "id": "answer",
            "role": "assistant",
            "text": "Result",
            "artifact_id": "immutable-artifact",
            "created_at": "2026-01-01",
            "status": "complete",
        },
    )
    fork = await repo.fork(conversation["id"])
    assert fork["id"] != conversation["id"]
    assert fork["parent_id"] == conversation["id"]
    assert any(
        message.get("artifact_id") == "immutable-artifact" for message in await repo.messages(fork["id"])
    )
