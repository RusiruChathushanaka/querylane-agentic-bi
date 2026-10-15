"""Opt-in public deployment checks. Creates visible demo conversations; never stores audio."""

import argparse
import asyncio
import json
import uuid
from pathlib import Path

import httpx
from websockets.asyncio.client import connect
from websockets.exceptions import InvalidStatus

from app.evaluate import cases, matches


async def run(backend: str, frontend: str, voice: bool):
    report = {"backend": backend, "frontend": frontend, "checks": {}}
    checks = report["checks"]
    async with httpx.AsyncClient(timeout=210) as http:

        async def get(path):
            response = await http.get(backend + path)
            response.raise_for_status()
            return response.json()

        async def post(path, body=None):
            response = await http.post(backend + path, json=body, headers=headers)
            response.raise_for_status()
            return response.json()

        checks["live"] = (await get("/health/live"))["status"] == "ok"
        checks["ready"] = (await get("/health/ready"))["status"] == "ready"
        response = await http.get(frontend + "/api/health")
        checks["frontend_backend"] = response.status_code == 200 and response.json()["backend"] == 200
        checks["runtime_config"] = (await http.get(frontend + "/api/config")).json()["backend_url"] == backend
        response = await http.options(
            backend + "/api/v1/conversations",
            headers={"Origin": frontend, "Access-Control-Request-Method": "POST"},
        )
        checks["cors"] = response.headers.get("access-control-allow-origin") == frontend
        token = (await http.post(backend + "/api/v1/guest-sessions", headers={"Origin": frontend})).json()[
            "token"
        ]
        headers = {"Authorization": "Bearer " + token, "Origin": frontend}
        connections = await get("/api/v1/connections")
        checks["real_connectors"] = connections["mode"] == "cloud" and all(
            item["connected"] for item in connections["connections"]
        )

        async def question(chat, text):
            body = {"question": text, "idempotency_key": uuid.uuid4().hex}
            run = await post(f"/api/v1/conversations/{chat}/turns", body)
            events_response = await http.get(backend + f"/api/v1/runs/{run['run_id']}/events")
            events_response.raise_for_status()
            events = []
            for block in events_response.text.split("\n\n"):
                if "data: " in block and "event: " in block:
                    kind = block.split("event: ", 1)[1].splitlines()[0]
                    events.append((kind, json.loads(block.split("data: ", 1)[1])))
            failures = [data for kind, data in events if kind == "error"]
            if failures:
                raise RuntimeError(json.dumps(failures))
            assert any(kind == "complete" for kind, _ in events), "Run did not complete"
            same = await post(f"/api/v1/conversations/{chat}/turns", body)
            assert same["run_id"] == run["run_id"], "Idempotency failed"
            artifact_id = next(data["id"] for kind, data in events if kind == "artifact")
            artifact = await get(f"/api/v1/artifacts/{artifact_id}")
            assert artifact["complete"], "Incomplete input"
            return artifact

        all_cases = {case["id"]: case for case in cases()}
        conversation = await post(
            "/api/v1/conversations", {"title": "Demo: regional performance", "source": "all"}
        )
        chat = conversation["id"]
        artifact = await question(chat, all_cases["targets-2026-08"]["question"])
        checks["cross_source_numbers"] = matches(artifact["rows"], all_cases["targets-2026-08"]["expected"])
        checks["hosted_query_evidence"] = any(p.get("job_id") for p in artifact["provenance"])
        checks["join_diagnostics"] = artifact["join_diagnostics"]["cardinality"] == "one-to-one"
        artifact = await question(
            chat, "Only September 2026, please. Return region, revenue, target_revenue."
        )
        checks["followup_numbers"] = matches(artifact["rows"], all_cases["targets-2026-09"]["expected"])
        fork = await post(f"/api/v1/conversations/{chat}/fork")
        forked = await get(f"/api/v1/conversations/{fork['id']}")
        checks["fork_context"] = any(m.get("artifact_id") == artifact["id"] for m in forked["messages"])
        single = await post(
            "/api/v1/conversations", {"title": "Demo: total retail revenue", "source": "bigquery"}
        )
        total = await question(single["id"], all_cases["total-revenue"]["question"])
        checks["bigquery_numbers"] = matches(total["rows"], all_cases["total-revenue"]["expected"])
        single = await post(
            "/api/v1/conversations", {"title": "Demo: customer segments", "source": "postgres"}
        )
        customers = await question(single["id"], all_cases["customers-table"]["question"])
        checks["postgres_numbers"] = matches(customers["rows"], all_cases["customers-table"]["expected"])

        ws_base = backend.replace("https://", "wss://").replace("http://", "ws://")
        voice_chat = await post("/api/v1/conversations", {"title": "Demo: voice analytics", "source": "all"})
        ws_url = ws_base + f"/api/v1/conversations/{voice_chat['id']}/voice"
        try:
            async with connect(ws_url, origin="https://untrusted.example", open_timeout=20):
                checks["voice_origin_denied"] = False
        except InvalidStatus as exc:
            checks["voice_origin_denied"] = exc.response.status_code == 403
        async with connect(ws_url, origin=frontend, open_timeout=20) as socket:
            await socket.send(json.dumps({"type": "authenticate", "token": "invalid"}))
            checks["voice_bad_token_denied"] = json.loads(await socket.recv())["type"] == "error"
        if voice:
            seen, errors = set(), []
            async with connect(
                ws_url, origin=frontend, open_timeout=30, close_timeout=10, max_size=2**20
            ) as socket:
                await socket.send(json.dumps({"type": "authenticate", "token": token}))
                async with asyncio.timeout(165):
                    async for raw in socket:
                        event = json.loads(raw)
                        seen.add(event["type"])
                        if event["type"] == "ready":
                            await socket.send(
                                json.dumps(
                                    {
                                        "type": "text",
                                        "text": "What is total gross retail revenue? Query the data and answer briefly.",
                                    }
                                )
                            )
                        if event["type"] == "error":
                            errors.append(event.get("message"))
                            break
                        if event["type"] == "turn_complete" and {"artifact", "audio", "transcript"} <= seen:
                            await socket.send(json.dumps({"type": "stop"}))
                            break
            checks["live_tool_audio_transcript"] = {
                "ready",
                "artifact",
                "audio",
                "transcript",
                "turn_complete",
            } <= seen and not errors
            report["voice"] = {
                "event_types": sorted(seen),
                "errors": errors,
                "raw_audio_recorded": False,
                "input": "text through live transport; microphone hardware not tested",
            }
        report["conversation_id"] = chat
    report["passed"] = all(checks.values())
    return report


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", required=True)
    parser.add_argument("--frontend", required=True)
    parser.add_argument("--voice", action="store_true")
    parser.add_argument("--output", default="../docs/evaluation/deployed.json")
    args = parser.parse_args()
    result = await run(args.backend.rstrip("/"), args.frontend.rstrip("/"), args.voice)
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return result["passed"]


if __name__ == "__main__":
    raise SystemExit(0 if asyncio.run(main()) else 1)
