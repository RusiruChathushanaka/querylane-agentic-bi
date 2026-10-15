from unittest.mock import AsyncMock

import pytest
from google.adk.events import Event
from google.adk.sessions.base_session_service import GetSessionConfig
from google.genai import types

from app.adk_sessions import FirestoreSessionService
from app.ai import AI
from app.analysis import AnalysisService
from app.config import Settings
from app.connectors import Connectors
from app.errors import AppError
from app.repository import Repository
from app.storage import MemoryStore


async def test_result_survives_interpreter_outage_and_reconnect():
    settings = Settings()
    store = MemoryStore()
    repo = Repository(store, settings)
    connectors = Connectors(settings)
    ai = AI(settings, FirestoreSessionService(store), connectors, store)
    ai.answer = AsyncMock(side_effect=AppError("Model timed out", 504, "model_timeout"))
    analysis = AnalysisService(repo, connectors, ai, settings)
    conversation = await repo.create_conversation("Test", "bigquery")
    run = await analysis.start(conversation["id"], "guest", "What is total revenue?", "recovery-test")
    await analysis.tasks[run["id"]]
    messages = await repo.messages(conversation["id"])
    assert len(messages) == 2
    assert "AI explanation is unavailable" in messages[-1]["text"]
    assert await store.get("artifacts", messages[-1]["artifact_id"])
    assert (await repo.run(run["id"]))["status"] == "complete"


async def test_recent_session_context_uses_newest_events():
    store = MemoryStore()
    service = FirestoreSessionService(store)
    session = await service.create_session(app_name="a", user_id="u", session_id="s")
    for index in range(12):
        await service.append_event(
            session,
            Event(author="user", content=types.Content(role="user", parts=[types.Part(text=str(index))])),
        )
    loaded = await service.get_session(
        app_name="a", user_id="u", session_id="s", config=GetSessionConfig(num_recent_events=3)
    )
    assert [event.content.parts[0].text for event in loaded.events] == ["9", "10", "11"]


async def test_raw_audio_is_not_persisted():
    store = MemoryStore()
    service = FirestoreSessionService(store)
    session = await service.create_session(app_name="a", user_id="u", session_id="audio")
    event = Event(
        author="model",
        content=types.Content(
            role="model", parts=[types.Part(inline_data=types.Blob(data=b"\x00\x00", mime_type="audio/pcm"))]
        ),
    )
    await service.append_event(session, event)
    loaded = await service.get_session(app_name="a", user_id="u", session_id="audio")
    assert loaded.events == []


async def test_unknown_cancellation_does_not_claim_database_completion():
    result = await Connectors(Settings()).cancel("another-instance-run")
    assert result["requested"]
    assert not result["database_jobs_terminal"]


async def test_cancellation_failure_still_releases_conversation():
    settings = Settings()
    store = MemoryStore()
    repo = Repository(store, settings)
    connectors = Connectors(settings)
    ai = AI(settings, FirestoreSessionService(store), connectors, store)
    ai.plan = AsyncMock(side_effect=AppError("Unavailable", 503, "source_unavailable"))
    connectors.cancel = AsyncMock(side_effect=RuntimeError("Cancellation transport failed"))
    analysis = AnalysisService(repo, connectors, ai, settings)
    conversation = await repo.create_conversation("Test", "bigquery")
    run = await analysis.start(conversation["id"], "guest", "What is total revenue?", "cancel-failure")
    await analysis.tasks[run["id"]]
    assert (await repo.run(run["id"]))["status"] == "failed"
    assert not (await repo.conversation(conversation["id"]))["active_run"]
    assert run["id"] not in analysis.tasks


async def test_transient_model_failure_retried_once_only():
    ai = AI(Settings(), FirestoreSessionService(MemoryStore()), Connectors(Settings()), MemoryStore())
    ai._structured_once = AsyncMock(side_effect=[AppError("temporary", 504, "model_timeout"), "success"])
    assert await ai._structured("test", "", "", None, "conversation") == "success"
    assert ai._structured_once.await_count == 2
    ai._structured_once = AsyncMock(side_effect=AppError("temporary", 504, "model_timeout"))
    with pytest.raises(AppError):
        await ai._structured("test", "", "", None, "conversation")
    assert ai._structured_once.await_count == 2
