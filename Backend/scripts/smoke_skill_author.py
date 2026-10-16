"""Opt-in conversational author smoke. Run only against an isolated Gemini preview."""

import argparse
import asyncio
import json
import uuid
from datetime import UTC, datetime
from pathlib import Path

import httpx
from websockets.asyncio.client import connect

from app.fixtures import retail_data


async def run(base, origin):
    report = {
        "backend": base,
        "scope": "Real Gemini Live, synthetic local sources, memory storage; no deployed/shared data changed.",
        "checks": {},
        "turns": [],
    }
    checks = report["checks"]
    async with httpx.AsyncClient(base_url=base, timeout=210) as http:
        ready = (await http.get("/health/ready")).json()
        assert ready["mode"] == "gemini" and ready["storage"] == "memory", (
            "Use an isolated Gemini memory preview."
        )
        response = await http.post("/api/v1/guest-sessions", headers={"Origin": origin})
        response.raise_for_status()
        token = response.json()["token"]
        headers = {"Origin": origin, "Authorization": "Bearer " + token}
        response = await http.post(
            "/api/v1/skills/author-sessions", headers=headers, json={"idempotency_key": uuid.uuid4().hex}
        )
        response.raise_for_status()
        session = response.json()
        path = "/api/v1/skills/author-sessions/" + session["id"]
        ws_url = base.replace("http://", "ws://").replace("https://", "wss://") + path + "/voice"

        async def receive_turn(socket):
            seen, texts, state = set(), [], None
            async with asyncio.timeout(120):
                async for raw in socket:
                    event = json.loads(raw)
                    seen.add(event["type"])
                    if event.get("session"):
                        state = event["session"]
                    if event["type"] == "error":
                        raise AssertionError(event)
                    if event["type"] == "transcript" and event["role"] == "assistant":
                        if event.get("replace"):
                            texts = [event["text"]]
                        else:
                            texts.append(event["text"])
                    if event["type"] == "turn_complete":
                        break
            result = {
                "event_types": sorted(seen),
                "assistant": "".join(texts),
                "draft_ready": bool(state and state["draft"]),
            }
            report["turns"].append(result)
            print(json.dumps(result), flush=True)
            return state, seen

        async def pause(socket):
            await socket.send(json.dumps({"type": "stop"}))
            async with asyncio.timeout(20):
                async for raw in socket:
                    event = json.loads(raw)
                    if event["type"] == "stopped":
                        return event["session"]
            raise AssertionError("No pause acknowledgment")

        async with connect(ws_url, origin=origin, max_size=2**20, close_timeout=10) as socket:
            await socket.send(json.dumps({"type": "authenticate", "token": token}))
            greeting, seen = await receive_turn(socket)
            checks["spoken_greeting_and_question"] = {
                "ready",
                "audio",
                "transcript",
                "turn_complete",
            } <= seen and bool(report["turns"][-1]["assistant"])
            messages = [
                "I want a playbook for monthly gross retail sales trends. Please call it Monthly sales coaching.",
                "Use BigQuery orders with status='completed' (lowercase literal exactly), in USD, at order grain. Revenue is before refunds. Preserve date and region filters, sort calendar months chronologically, and do not invent causal explanations.",
                "Use it for monthly sales trend and month-over-month questions. Workflow: check the requested reporting window, sum gross revenue by calendar month, compare adjacent months with zero-safe growth, show a line chart, and explain the observations. Example: Show monthly revenue as a line chart. You may write a concise description and tags from these requirements. That is the complete brief; please prepare the draft now.",
            ]
            for message in messages:
                await socket.send(json.dumps({"type": "text", "text": message}))
                session, seen = await receive_turn(socket)
            if not session["draft"]:
                await socket.send(
                    json.dumps(
                        {
                            "type": "text",
                            "text": "All requirements are provided. Record the remaining fields using my prior answers and prepare the skill draft now. Use source bigquery.",
                        }
                    )
                )
                session, seen = await receive_turn(socket)
            assert session["draft"], session
            first = session["draft"]
            checks["multi_turn_requirements_and_draft"] = (
                not session["missing_fields"] and session["draft"]["source"] == "bigquery"
            )
            checks["no_automatic_publication"] = (await http.get("/api/v1/skills")).json()["skills"] == []
            session = await pause(socket)
            checks["pause_releases_lease"] = not session["connected"]
        recovered = (await http.get(path, headers=headers)).json()
        checks["recovery_retains_brief_draft_transcript"] = (
            recovered["draft"] == first and len(recovered["transcript"]) >= 4
        )
        async with connect(ws_url, origin=origin, max_size=2**20, close_timeout=10) as socket:
            await socket.send(json.dumps({"type": "authenticate", "token": token}))
            await receive_turn(socket)
            await socket.send(
                json.dumps(
                    {
                        "type": "text",
                        "text": "Change the skill to net revenue, defined as gross completed-order sales minus refunds linked at order grain. Rename it Net monthly sales coaching. Use the original order-month cohort because returns have no processing date. Keep the other requirements, adapt the workflow to net revenue, and regenerate the draft. Do not publish.",
                    }
                )
            )
            session, _ = await receive_turn(socket)
            if not session["draft"]:
                await socket.send(
                    json.dumps(
                        {
                            "type": "text",
                            "text": "Yes, please record these corrections and prepare the updated draft.",
                        }
                    )
                )
                session, _ = await receive_turn(socket)
            session = await pause(socket)
        assert session["draft"]
        checks["reconnected_correction_regenerates_draft"] = (
            session["draft"] != first
            and "refund" in session["draft"]["instructions"].lower()
            and session["revision"] > recovered["revision"]
        )
        report["draft_before_correction"] = first
        report["draft_after_correction"] = session["draft"]
        reviewed = session["draft"] | {"name": session["draft"]["name"] + " (reviewed)"}
        response = await http.patch(
            path + "/draft",
            headers=headers,
            json={"expected_revision": session["revision"], "content": reviewed},
        )
        response.raise_for_status()
        session = response.json()
        body = {"expected_revision": session["revision"]}
        response = await http.post(path + "/publish", headers=headers, json=body)
        response.raise_for_status()
        skill = response.json()
        replay = await http.post(path + "/publish", headers=headers, json=body)
        replay.raise_for_status()
        checks["review_and_publish_once"] = (
            skill == replay.json()
            and skill["enabled"]
            and skill["revision"] == 1
            and skill["name"].endswith("(reviewed)")
        )
        response = await http.post(
            "/api/v1/conversations",
            headers=headers,
            json={"title": "Voice-authored skill verification", "source": "bigquery"},
        )
        response.raise_for_status()
        chat = response.json()["id"]
        response = await http.patch(
            "/api/v1/conversations/" + chat + "/skills",
            headers=headers,
            json={"skill_ids": [skill["id"]], "expected_revision": 0},
        )
        response.raise_for_status()
        response = await http.post(
            "/api/v1/conversations/" + chat + "/turns",
            headers=headers,
            json={
                "question": "Calculate total net revenue across all demo months as gross revenue for orders with status = 'completed' (lowercase, exactly as stored) minus all matching refunds. Return a single KPI, alias the result revenue.",
                "idempotency_key": uuid.uuid4().hex,
            },
        )
        response.raise_for_status()
        run_id = response.json()["run_id"]
        response = await http.get("/api/v1/runs/" + run_id + "/events")
        response.raise_for_status()
        events = []
        for block in response.text.split("\n\n"):
            if "event: " in block and "data: " in block:
                events.append(
                    (block.split("event: ", 1)[1].splitlines()[0], json.loads(block.split("data: ", 1)[1]))
                )
        assert any(k == "complete" for k, _ in events), events
        artifact_id = next(d["id"] for k, d in events if k == "artifact")
        artifact = (await http.get("/api/v1/artifacts/" + artifact_id)).json()
        from decimal import Decimal

        data = retail_data()
        expected = sum(x["revenue"] for x in data["orders"]) - sum(
            x["refund_amount"] for x in data["returns"]
        )
        checks["published_skill_guides_analytics_with_correct_provenance"] = any(
            s["id"] == skill["id"] and s["mode"] == "manual" and s["revision"] == 1
            for s in artifact["skills_used"]
        )
        checks["independent_net_revenue"] = (
            len(artifact["rows"]) == 1
            and artifact["rows"][0].get("revenue") is not None
            and Decimal(str(artifact["rows"][0]["revenue"])) == expected
        )
        report["analytics"] = {
            "rows": artifact["rows"],
            "expected_net_revenue": str(expected),
            "skills_used": artifact["skills_used"],
        }
        report["input"] = (
            "Text messages through real Gemini Live; audio output received; microphone hardware not tested."
        )
        report["raw_audio_recorded"] = False
    report.update(verified_at=datetime.now(UTC).isoformat(), passed=all(checks.values()))
    return report


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", default="http://127.0.0.1:8002")
    parser.add_argument("--origin", default="http://127.0.0.1:3001")
    parser.add_argument("--output", default="../docs/evaluation/voice-skill-author-live.json")
    args = parser.parse_args()
    report = await run(args.backend, args.origin)
    Path(args.output).write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"checks": report["checks"], "passed": report["passed"]}), flush=True)
    assert report["passed"], report


if __name__ == "__main__":
    asyncio.run(main())
