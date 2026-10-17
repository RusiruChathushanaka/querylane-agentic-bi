import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from google.genai import types

from app.adk_sessions import FirestoreSessionService
from app.config import Settings
from app.repository import Repository
from app.storage import MemoryStore
from app.voice import voice_session


async def test_live_partial_final_transcripts_persist_once_and_allow_repeated_turns(monkeypatch):
    import app.voice as live

    settings = Settings(ai_backend="gemini")
    store = MemoryStore()
    repo = Repository(store, settings)
    chat = await repo.create_conversation("Voice regression", "bigquery")
    inbound = asyncio.Queue()
    sent = []

    async def send(event):
        sent.append(event)
        if sum(e["type"] == "turn_complete" for e in sent) == 2:
            await inbound.put({"type": "stop"})

    def event(**fields):
        return SimpleNamespace(
            **(
                {
                    "error_code": None,
                    "interrupted": False,
                    "input_transcription": None,
                    "output_transcription": None,
                    "content": None,
                    "live_session_resumption_update": None,
                    "go_away": None,
                    "turn_complete": False,
                    "partial": False,
                }
                | fields
            )
        )

    class Runner:
        def __init__(self, agent, **kwargs):
            self.tool = agent.tools[0]

        async def run_live(self, **kwargs):
            for _ in range(2):
                yield event(input_transcription=types.Transcription(text="How many "), partial=True)
                yield event(input_transcription=types.Transcription(text="How many orders?"))
                await self.tool("How many orders?")
                # Late final replay must not create another public user message.
                yield event(input_transcription=types.Transcription(text="How many orders?"))
                yield event(output_transcription=types.Transcription(text="The count "), partial=True)
                yield event(output_transcription=types.Transcription(text="is two."), partial=True)
                yield event(output_transcription=types.Transcription(text="The count is two."))
                yield event(turn_complete=True)
            await asyncio.Future()

    async def heartbeat(lease):
        await asyncio.Future()

    analysis = SimpleNamespace(
        heartbeat=heartbeat, execute=AsyncMock(return_value={}), save_message=AsyncMock()
    )
    monkeypatch.setattr(live, "Client", lambda **kw: SimpleNamespace(aio=SimpleNamespace(aclose=AsyncMock())))
    monkeypatch.setattr(live, "Gemini", lambda **kw: "fake-live-model")
    monkeypatch.setattr(live, "LlmAgent", lambda **kw: SimpleNamespace(**kw))
    monkeypatch.setattr(live, "Runner", Runner)
    services = SimpleNamespace(
        settings=settings,
        repo=repo,
        analysis=analysis,
        sessions=FirestoreSessionService(store),
        connectors=SimpleNamespace(data_context="synthetic", forget=lambda _: None),
    )
    socket = SimpleNamespace(receive_json=inbound.get, send_json=send)
    await asyncio.wait_for(voice_session(socket, services, "guest", chat["id"]), 5)
    calls = analysis.save_message.await_args_list
    assert [c.args[2] for c in calls if c.args[1] == "user"] == ["How many orders?"] * 2
    assert [c.args[2] for c in calls if c.args[1] == "assistant"] == ["The count is two."] * 2
    assert any(e.get("replace") for e in sent if e["type"] == "transcript")
    assert not any(e["type"] == "error" for e in sent)
