import json

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.config import Settings
from app.main import create_app


@pytest.fixture
def client():
    with TestClient(create_app(Settings(environment="test"))) as value:
        yield value


def guest(client):
    return {"Authorization": "Bearer " + client.post("/api/v1/guest-sessions").json()["token"]}


def test_guest_scope_and_no_administrative_routes(client):
    assert client.post("/api/v1/conversations", json={}).status_code == 401
    assert client.post("/api/v1/admin/reset", headers=guest(client)).status_code == 404
    assert client.get("/api/v1/conversations").status_code == 200
    assert client.get("/health/ready").json()["mode"] == "local-fixtures"


def test_origin_and_payload_validation(client):
    assert (
        client.post("/api/v1/guest-sessions", headers={"Origin": "https://untrusted.example"}).status_code
        == 403
    )
    headers = guest(client)
    assert (
        client.post(
            "/api/v1/conversations", headers=headers, json={"credentials": "must-not-be-accepted"}
        ).status_code
        == 422
    )
    assert client.post("/api/v1/conversations", headers=headers, content="x" * 40_000).status_code == 413


def test_analysis_replay_fork_and_provenance(client):
    headers = guest(client)
    conversation = client.post("/api/v1/conversations", headers=headers, json={"source": "all"}).json()
    path = f"/api/v1/conversations/{conversation['id']}"
    body = {"question": "Compare regional revenue with targets", "idempotency_key": "api-test-request"}
    run = client.post(path + "/turns", headers=headers, json=body).json()
    with client.stream("GET", f"/api/v1/runs/{run['run_id']}/events") as response:
        stream = "".join(response.iter_text())
    assert "event: artifact" in stream and "event: complete" in stream
    artifact_event = next(
        json.loads(block.split("data: ", 1)[1])
        for block in stream.split("\n\n")
        if "event: artifact" in block
    )
    assert "rows" not in artifact_event
    same = client.post(path + "/turns", headers=headers, json=body).json()
    assert same["run_id"] == run["run_id"]
    messages = client.get(path).json()["messages"]
    assert len(messages) == 2
    artifact = client.get(f"/api/v1/artifacts/{messages[1]['artifact_id']}").json()
    assert artifact["complete"] and len(artifact["provenance"]) == 2
    assert artifact["join_diagnostics"]["cardinality"] == "one-to-one"
    assert sum(float(row["revenue"]) for row in artifact["rows"]) == 118951
    assert client.get(f"/api/v1/runs/{run['run_id']}/events?after=999").text == ""
    fork = client.post(path + "/fork", headers=headers).json()
    assert fork["parent_id"] == conversation["id"]
    assert (
        client.get(f"/api/v1/conversations/{fork['id']}").json()["messages"][1]["artifact_id"]
        == messages[1]["artifact_id"]
    )


@pytest.mark.parametrize("origin", [None, "https://untrusted.example", "null"])
def test_voice_rejects_unapproved_origin(client, origin):
    headers = guest(client)
    conversation = client.post("/api/v1/conversations", headers=headers, json={}).json()
    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect(
            f"/api/v1/conversations/{conversation['id']}/voice", headers={"Origin": origin} if origin else {}
        ):
            pass


@pytest.mark.parametrize(
    "first",
    [
        {},
        {"type": "audio", "data": "bad"},
        {"type": "authenticate", "token": "wrong"},
        {"type": "authenticate"},
        [],
        None,
    ],
)
def test_voice_rejects_invalid_handshake(client, first):
    headers = guest(client)
    conversation = client.post("/api/v1/conversations", headers=headers, json={}).json()
    with client.websocket_connect(
        f"/api/v1/conversations/{conversation['id']}/voice", headers={"Origin": "http://localhost:3000"}
    ) as socket:
        socket.send_json(first)
        assert socket.receive_json()["type"] == "error"


def test_voice_does_not_fake_model_in_fixture_mode(client):
    headers = guest(client)
    conversation = client.post("/api/v1/conversations", headers=headers, json={}).json()
    with client.websocket_connect(
        f"/api/v1/conversations/{conversation['id']}/voice", headers={"Origin": "http://localhost:3000"}
    ) as socket:
        socket.send_json({"type": "authenticate", "token": headers["Authorization"][7:]})
        message = socket.receive_json()
        assert message["type"] == "error" and "Gemini" in message["message"]


def test_voice_unknown_conversation(client):
    token = guest(client)["Authorization"][7:]
    with client.websocket_connect(
        "/api/v1/conversations/not-found/voice", headers={"Origin": "http://localhost:3000"}
    ) as socket:
        socket.send_json({"type": "authenticate", "token": token})
        assert socket.receive_json()["code"] == "not_found"


def test_production_cannot_start_with_fixture_backends():
    with pytest.raises(ValueError, match="Production requires"):
        create_app(Settings(environment="production"))


@pytest.mark.parametrize("terminal", ["complete", "failed", "cancelled"])
def test_stream_drains_events_committed_between_poll_and_terminal_read(client, monkeypatch, terminal):
    """A worker may finish after the event query but before the status read."""
    repo = client.app.state.services.repo
    calls = 0
    listed = 0
    final_type = "complete" if terminal == "complete" else "error"

    async def status(run_id):
        nonlocal calls
        calls += 1
        return {"id": run_id, "status": "running" if calls == 1 else terminal, "sequence": 2}

    async def events(collection):
        nonlocal listed
        listed += 1
        prefix = [{"id": 1, "type": "progress", "data": {"stage": "query"}}]
        return prefix if listed == 1 else prefix + [{"id": 2, "type": final_type, "data": {}}]

    monkeypatch.setattr(repo, "run", status)
    monkeypatch.setattr(repo.store, "list", events)
    response = client.get("/api/v1/runs/finishing/events")
    assert f"event: {final_type}" in response.text
    assert response.text.count("id: 1\n") == 1
    assert response.text.count("id: 2\n") == 1
    replay = client.get("/api/v1/runs/finishing/events?after=2")
    assert replay.text == ""


def test_voice_setup_storage_failure_returns_safe_error(client, monkeypatch):
    from unittest.mock import AsyncMock

    headers = guest(client)
    conversation = client.post("/api/v1/conversations", headers=headers, json={}).json()
    monkeypatch.setattr(
        client.app.state.services.repo,
        "conversation",
        AsyncMock(side_effect=RuntimeError("private storage error")),
    )
    with client.websocket_connect(
        f"/api/v1/conversations/{conversation['id']}/voice", headers={"Origin": "http://localhost:3000"}
    ) as socket:
        socket.send_json({"type": "authenticate", "token": headers["Authorization"].split()[1]})
        event = socket.receive_json()
        assert event["type"] == "error" and event["code"] == "voice_unavailable"
        assert "private" not in event["message"]


def test_source_checks_overlap_and_keep_individual_results_and_order(client, monkeypatch):
    import asyncio

    entered = []
    both_started = None

    async def check(source):
        nonlocal both_started
        if both_started is None:
            both_started = asyncio.Event()
        entered.append(source)
        if len(entered) == 2:
            both_started.set()
        # Sequential checks cannot pass this barrier.
        await asyncio.wait_for(both_started.wait(), timeout=1)
        return {"connected": source == "bigquery", "mode": "cloud", **({"error": "Source unavailable"} if source == "postgres" else {})}

    monkeypatch.setattr(client.app.state.services.connectors, "test", check)
    response = client.get("/api/v1/connections")
    assert response.status_code == 200
    values = response.json()["connections"]
    assert [v["id"] for v in values] == ["bigquery", "postgres"]
    assert values[0]["connected"] is True
    assert values[1]["connected"] is False
    assert values[1]["error"] == "Source unavailable"
