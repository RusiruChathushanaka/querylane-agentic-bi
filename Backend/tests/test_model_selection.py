import asyncio
import json
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from google.genai.errors import ClientError

from app.adk_sessions import FirestoreSessionService
from app.ai import AI, fixture_answer, fixture_plan
from app.analysis import AnalysisService
from app.config import Settings
from app.connectors import Connectors
from app.errors import AppError
from app.main import create_app
from app.model_selection import TEXT_MODELS, active_text_model
from app.repository import Repository
from app.storage import MemoryStore

FLASH, LITE = [model["id"] for model in TEXT_MODELS]


@pytest.mark.parametrize("model", [FLASH, LITE, None])
def test_model_catalog_and_selected_run_preserve_numerical_results(model):
    with TestClient(create_app(Settings(environment="test"))) as client:
        catalog = client.get("/api/v1/models").json()
        assert {choice["id"] for choice in catalog["models"]} == {FLASH, LITE}
        assert catalog["mode"] == "fixture"
        headers = {"Authorization": "Bearer " + client.post("/api/v1/guest-sessions").json()["token"]}
        chat = client.post("/api/v1/conversations", headers=headers, json={}).json()
        path = f"/api/v1/conversations/{chat['id']}/turns"
        body = {"question": "What is total revenue?", "idempotency_key": "selected-model", "model": model}
        response = client.post(path, headers=headers, json=body)
        assert response.status_code == 202
        run_id = response.json()["run_id"]
        stream = client.get(f"/api/v1/runs/{run_id}/events").text
        assert "event: complete" in stream
        run = client.get(f"/api/v1/runs/{run_id}").json()
        assert run["text_model"] == (model or FLASH)
        artifact = next(
            json.loads(block.split("data: ", 1)[1])
            for block in stream.split("\n\n")
            if "event: artifact" in block
        )
        assert artifact["ai"] == {
            "backend": "fixture",
            "text_model": None,
            "selected_text_model": model or FLASH,
        }
        rows = client.get(f"/api/v1/artifacts/{artifact['id']}").json()["rows"]
        assert float(rows[0]["revenue"]) == 118951
        assert client.post(path, headers=headers, json=body).json()["run_id"] == run_id
        other = LITE if model != LITE else FLASH
        assert client.post(path, headers=headers, json=body | {"model": other}).status_code == 409
        assert client.post(path, headers=headers, json=body | {"model": "arbitrary-model"}).status_code == 400
        fork = client.post(f"/api/v1/conversations/{chat['id']}/fork", headers=headers).json()
        messages = client.get(f"/api/v1/conversations/{fork['id']}").json()["messages"]
        assert messages[-1]["artifact_id"] == artifact["id"]


async def test_default_retry_reuses_original_model_after_operator_default_changes():
    settings = Settings()
    repo = Repository(MemoryStore(), settings)
    chat = await repo.create_conversation("Test", "all")
    run, _ = await repo.begin(chat["id"], "guest", "Revenue?", "same-key")
    settings.text_model = LITE
    retry, created = await repo.begin(chat["id"], "guest", "Revenue?", "same-key")
    assert not created and retry["text_model"] == run["text_model"] == FLASH


async def test_concurrent_analyses_isolate_models_across_selection_planning_and_answers():
    settings = Settings()
    store = MemoryStore()
    repo = Repository(store, settings)
    connectors = Connectors(settings)
    ai = AI(settings, FirestoreSessionService(store), connectors, store)
    analysis = AnalysisService(repo, connectors, ai, settings)
    observed = []

    def instrument(original, stage):
        async def call(*args, **kwargs):
            selected = active_text_model.get()
            await asyncio.sleep(0.01)
            assert active_text_model.get() == selected
            observed.append((stage, selected))
            return await original(*args, **kwargs)

        return call

    analysis.skills.select = instrument(analysis.skills.select, "skills")
    ai.plan = instrument(ai.plan, "plan")
    ai.answer = instrument(ai.answer, "answer")
    chats = [await repo.create_conversation("Test", "bigquery") for _ in range(2)]
    runs = await asyncio.gather(
        *[
            analysis.start(chat["id"], "guest", "What is total revenue?", f"model-{index}", model=model)
            for index, (chat, model) in enumerate(zip(chats, [FLASH, LITE], strict=True))
        ]
    )
    await asyncio.gather(*(analysis.tasks[run["id"]] for run in runs))
    assert set(observed) == {
        (stage, model) for stage in ["skills", "plan", "answer"] for model in [FLASH, LITE]
    }
    assert active_text_model.get() is None
    assert ai.settings.text_model == FLASH
    finished = await asyncio.gather(*(repo.run(run["id"]) for run in runs))
    assert all(run["status"] == "complete" for run in finished)


async def test_selected_identifier_reaches_adk_without_mutating_default(monkeypatch):
    settings = Settings()
    store = MemoryStore()
    ai = AI(settings, FirestoreSessionService(store), Connectors(settings), store)
    called = []

    def stop_at_model(**kwargs):
        called.append(kwargs["model"])
        raise RuntimeError("stop before model invocation")

    monkeypatch.setattr("app.ai.Gemini", stop_at_model)
    token = active_text_model.set(LITE)
    try:
        with pytest.raises(RuntimeError, match="stop before"):
            await ai._structured_once("planner", "instruction", "question", None, "chat")
    finally:
        active_text_model.reset(token)
    assert called == [LITE] and settings.text_model == FLASH


async def test_model_access_failure_is_explicit_and_never_falls_back():
    settings = Settings()
    store = MemoryStore()
    ai = AI(settings, FirestoreSessionService(store), Connectors(settings), store)
    ai._structured_once = AsyncMock(side_effect=ClientError(404, {"error": {"message": "not found"}}))
    token = active_text_model.set(LITE)
    try:
        with pytest.raises(AppError, match=LITE) as failure:
            await ai._structured("planner", "instruction", "question", None, "chat")
        assert failure.value.code == "model_unavailable"
        assert ai._structured_once.await_count == 1
    finally:
        active_text_model.reset(token)


def test_voice_rejects_unsupported_model_before_acquiring_a_lease():
    with TestClient(create_app(Settings(environment="test"))) as client:
        token = client.post("/api/v1/guest-sessions").json()["token"]
        chat = client.post(
            "/api/v1/conversations", headers={"Authorization": f"Bearer {token}"}, json={}
        ).json()
        with client.websocket_connect(
            f"/api/v1/conversations/{chat['id']}/voice", headers={"Origin": "http://localhost:3000"}
        ) as socket:
            socket.send_json({"type": "authenticate", "token": token, "model": "unknown"})
            assert socket.receive_json()["code"] == "unsupported_model"
        assert client.get(f"/api/v1/conversations/{chat['id']}").json()["conversation"]["active_run"] is None


@pytest.mark.parametrize("model", [FLASH, LITE])
def test_voice_passes_selected_analysis_model_to_session(monkeypatch, model):
    observed = []

    async def session(socket, services, guest_id, conversation_id, *, model=None):
        observed.append(model)
        await socket.send_json({"type": "ready"})

    monkeypatch.setattr("app.main.voice_session", session)
    with TestClient(create_app(Settings(environment="test"))) as client:
        token = client.post("/api/v1/guest-sessions").json()["token"]
        chat = client.post(
            "/api/v1/conversations", headers={"Authorization": f"Bearer {token}"}, json={}
        ).json()
        with client.websocket_connect(
            f"/api/v1/conversations/{chat['id']}/voice", headers={"Origin": "http://localhost:3000"}
        ) as socket:
            socket.send_json({"type": "authenticate", "token": token, "model": model})
            assert socket.receive_json()["type"] == "ready"
    assert observed == [model]


async def test_sql_repair_keeps_selected_model_and_read_only_guards():
    settings = Settings()
    store = MemoryStore()
    repo = Repository(store, settings)
    connectors = Connectors(settings)
    ai = AI(settings, FirestoreSessionService(store), connectors, store)
    settings.ai_backend = "gemini"  # Fake model functions; actual connector guards remain active.
    observed = []

    async def plan(question, history, source, conversation_id, feedback="", **kwargs):
        observed.append(active_text_model.get())
        value = fixture_plan(question, history, source)
        if len(observed) == 1:
            value.queries[0].sql = "DELETE FROM orders"
        else:
            assert feedback
        return value, "test"

    async def answer(question, plan, rows, diagnostics, conversation_id, **kwargs):
        assert active_text_model.get() == LITE
        return fixture_answer(plan, rows)

    ai.plan, ai.answer = plan, answer
    analysis = AnalysisService(repo, connectors, ai, settings)
    chat = await repo.create_conversation("Guarded repair", "bigquery")
    run = await analysis.start(chat["id"], "guest", "What is total revenue?", "repair-model", model=LITE)
    await analysis.tasks[run["id"]]
    assert observed == [LITE, LITE]
    assert (await repo.run(run["id"]))["status"] == "complete"
    assert active_text_model.get() is None
