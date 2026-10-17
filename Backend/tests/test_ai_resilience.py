"""Fault injection at the real structured-call and Live transport seams."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest
from google.genai.errors import ClientError, ServerError

from app.adk_sessions import FirestoreSessionService
from app.ai import AI
from app.config import Settings
from app.connectors import Connectors
from app.errors import AppError
from app.repository import Repository, active_lease
from app.storage import MemoryStore
from app.voice import voice_session


def ai_service():
    store = MemoryStore()
    return AI(Settings(), FirestoreSessionService(store), Connectors(Settings()), store)


@pytest.mark.parametrize(
    "failure",
    [
        ClientError(429, {"error": {"message": "provider detail must stay private"}}),
        ServerError(503, {"error": {"message": "unavailable"}}),
        httpx.ReadTimeout("provider detail must stay private"),
        httpx.ConnectError("provider detail must stay private"),
    ],
)
async def test_transient_ai_failures_retry_once_and_exhaust_as_public_errors(monkeypatch, failure):
    ai = ai_service()
    monkeypatch.setattr("app.ai.asyncio.sleep", AsyncMock())
    ai._structured_once = AsyncMock(side_effect=[failure, "ok"])
    assert await ai._structured("test", "", "", None, "chat") == "ok"
    assert ai._structured_once.await_count == 2
    ai._structured_once = AsyncMock(side_effect=failure)
    with pytest.raises(AppError) as error:
        await ai._structured("test", "", "", None, "chat")
    assert error.value.code in {"model_timeout", "model_transient", "model_rate_limited"}
    assert "provider detail" not in error.value.message
    assert ai._structured_once.await_count == 2


@pytest.mark.parametrize("code", [400, 401, 403, 404])
async def test_permanent_model_errors_are_public_and_never_retried(code):
    ai = ai_service()
    ai._structured_once = AsyncMock(side_effect=ClientError(code, {"error": {"message": "private detail"}}))
    with pytest.raises(AppError) as error:
        await ai._structured("test", "", "", None, "chat")
    assert error.value.code in {"model_unavailable", "model_error"}
    assert "private detail" not in error.value.message
    assert ai._structured_once.await_count == 1


async def test_model_cancellation_and_programming_errors_are_not_retried():
    ai = ai_service()
    for error in [asyncio.CancelledError(), RuntimeError("implementation bug")]:
        ai._structured_once = AsyncMock(side_effect=error)
        with pytest.raises(type(error)):
            await ai._structured("test", "", "", None, "chat")
        assert ai._structured_once.await_count == 1


async def live_harness(monkeypatch, *, tool_error=None, close_error=None):
    import app.voice as live

    settings = Settings(ai_backend="gemini")
    store = MemoryStore()
    repo = Repository(store, settings)
    chat = await repo.create_conversation("Failure injection", "bigquery")
    inbound = asyncio.Queue()
    sent, results = [], []
    analysis = SimpleNamespace(execute=AsyncMock(side_effect=tool_error), save_message=AsyncMock())

    async def heartbeat(lease):
        await asyncio.Future()

    analysis.heartbeat = heartbeat

    async def script(tool):
        if tool_error:
            results.append(await tool("Revenue?"))
            yield SimpleNamespace(
                error_code=None,
                interrupted=False,
                input_transcription=None,
                output_transcription=None,
                content=None,
                live_session_resumption_update=None,
                go_away=None,
                turn_complete=False,
            )
        await inbound.put({"type": "stop"})
        await asyncio.Future()

    class Runner:
        def __init__(self, agent, **kwargs):
            self.tool = agent.tools[0]

        def run_live(self, **kwargs):
            return script(self.tool)

    close = AsyncMock(side_effect=close_error)
    monkeypatch.setattr(live, "Client", lambda **kw: SimpleNamespace(aio=SimpleNamespace(aclose=close)))
    monkeypatch.setattr(live, "Gemini", lambda **kw: "fake")
    monkeypatch.setattr(live, "LlmAgent", lambda **kw: SimpleNamespace(**kw))
    monkeypatch.setattr(live, "Runner", Runner)
    connectors = SimpleNamespace(data_context="", cancel=AsyncMock(), forget=lambda _: None)
    services = SimpleNamespace(
        settings=settings,
        repo=repo,
        analysis=analysis,
        sessions=FirestoreSessionService(store),
        connectors=connectors,
    )

    async def send(payload):
        sent.append(payload)

    socket = SimpleNamespace(receive_json=inbound.get, send_json=send)
    await voice_session(socket, services, "guest", chat["id"])
    return sent, results, connectors, repo, chat


async def test_expected_voice_tool_failure_is_recoverable_without_reexecuting_query(monkeypatch):
    sent, results, _, repo, chat = await live_harness(
        monkeypatch, tool_error=AppError("Source timed out. Narrow the question.", 503, "source_transient")
    )
    assert results and results[0]["error"]["code"] == "source_transient"
    assert any(e["type"] == "tool_error" for e in sent)
    assert not any(e["type"] == "error" for e in sent)
    assert not (await repo.conversation(chat["id"]))["active_run"]


async def test_normal_voice_stop_also_requests_database_cancellation(monkeypatch):
    _, _, connectors, _, _ = await live_harness(monkeypatch)
    connectors.cancel.assert_awaited_once()


async def test_voice_client_close_failure_does_not_leak_active_lease(monkeypatch):
    before = active_lease.get()
    await live_harness(monkeypatch, close_error=RuntimeError("close transport failed"))
    assert active_lease.get() == before


async def test_cancel_then_forget_during_bigquery_dry_run_prevents_late_submission(monkeypatch):
    import contextlib
    import threading

    connectors = Connectors(Settings())
    connectors.settings.data_backend = "cloud"
    entered, release, finished = threading.Event(), threading.Event(), threading.Event()
    submitted = []

    def query(sql, job_config=None, **kwargs):
        if job_config.dry_run:
            entered.set()
            assert release.wait(5)
            return SimpleNamespace(total_bytes_processed=0)
        submitted.append(sql)
        return SimpleNamespace(result=lambda **kw: [], cancel=lambda: True, total_bytes_processed=0)

    connectors.bq = SimpleNamespace(query=query)
    original = connectors._bigquery

    def wrapped(*args, **kwargs):
        try:
            return original(*args, **kwargs)
        finally:
            finished.set()

    monkeypatch.setattr(connectors, "_bigquery", wrapped)
    task = asyncio.create_task(connectors.query("bigquery", "SELECT COUNT(*) AS n FROM orders", "late-query"))
    assert await asyncio.to_thread(entered.wait, 5)
    task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await task
    await connectors.cancel("late-query")
    connectors.forget("late-query")
    release.set()
    assert await asyncio.to_thread(finished.wait, 5)
    assert not submitted, "Cancelled dry-run worker must not start a billed query after registry cleanup"


async def test_long_retry_after_does_not_retry_earlier_than_provider_requests():
    ai = ai_service()
    failure = ClientError(
        429, {"error": {"message": "busy"}}, httpx.Response(429, headers={"Retry-After": "120"})
    )
    ai._structured_once = AsyncMock(side_effect=failure)
    with pytest.raises(AppError) as error:
        await ai._structured("test", "", "", None, "chat")
    assert error.value.code == "model_rate_limited"
    assert ai._structured_once.await_count == 1


async def test_analysis_finish_storage_failure_still_clears_local_task_registry():
    from app.analysis import AnalysisService

    store = MemoryStore()
    settings = Settings()
    repo = Repository(store, settings)
    connectors = Connectors(settings)
    analysis = AnalysisService(repo, connectors, ai_service(), settings)
    analysis.execute = AsyncMock(return_value={})
    repo.finish = AsyncMock(side_effect=RuntimeError("storage outage"))
    chat = await repo.create_conversation("Cleanup", "bigquery")
    run = await analysis.start(chat["id"], "guest", "Count orders", "finalization-outage")
    await analysis.tasks[run["id"]]
    assert run["id"] not in analysis.tasks
