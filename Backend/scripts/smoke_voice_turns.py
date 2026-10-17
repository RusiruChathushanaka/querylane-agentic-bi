"""Opt-in hosted repeated Live analysis; public test chat, read-only source queries.

Text over Live checks multiple tool invocations in ONE connection. Browser synthetic
speech is a separate acceptance check; this does not certify microphone hardware.
"""

import argparse
import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path

import httpx
from websockets.asyncio.client import connect


async def run(args):
    result = {"verified_at": datetime.now(UTC).isoformat(), "checks": {}, "errors": [], "turns": []}
    checks = result["checks"]
    async with httpx.AsyncClient(base_url=args.backend, timeout=60) as client:
        token = (await client.post("/api/v1/guest-sessions")).json()["token"]
        headers = {"Authorization": "Bearer " + token}
        chat_response = await client.post(
            "/api/v1/conversations",
            headers=headers,
            json={"title": "Verification: repeated live analytics", "source": "bigquery"},
        )
        chat_response.raise_for_status()
        chat = chat_response.json()["id"]
        result["conversation_id"] = chat
        url = args.backend.replace("https://", "wss://").replace("http://", "ws://")
        questions = [
            "Query the count of completed sales_orders across all available history as completed_orders. Show a KPI and speak the count briefly.",
            "Now query completed orders only in calendar year 2024 as completed_orders. Show a KPI and speak the count briefly.",
        ]
        phase, artifact, audio, spoken = 0, None, 0, ""
        try:
            async with connect(
                url + f"/api/v1/conversations/{chat}/voice",
                origin=args.frontend,
                max_size=2**20,
                open_timeout=30,
            ) as socket:
                await socket.send(json.dumps({"type": "authenticate", "token": token}))
                async with asyncio.timeout(175):
                    async for raw in socket:
                        event = json.loads(raw)
                        kind = event["type"]
                        if kind == "ready":
                            result["run_id"] = event["run_id"]
                            await socket.send(json.dumps({"type": "text", "text": questions[phase]}))
                        elif kind == "artifact":
                            # Live notifications carry metadata; rows are read
                            # from the saved artifact, never duplicated in events.
                            saved = await client.get("/api/v1/artifacts/" + event["data"]["id"])
                            saved.raise_for_status()
                            artifact, audio, spoken = saved.json(), 0, ""
                        elif kind == "audio" and artifact:
                            audio += 1
                        elif kind == "transcript" and event.get("role") == "assistant" and artifact:
                            spoken = event["text"] if event.get("replace") else spoken + event["text"]
                        elif kind == "error":
                            result["errors"].append(event.get("message"))
                            break
                        elif kind == "turn_complete" and artifact and audio and spoken:
                            result["turns"].append(
                                {
                                    "artifact_id": artifact["id"],
                                    "rows": artifact["rows"],
                                    "provenance": artifact["provenance"],
                                    "spoken": spoken,
                                    "audio_frames": audio,
                                    "data_profile": artifact["data_profile"],
                                }
                            )
                            phase += 1
                            if phase == len(questions):
                                await socket.send(json.dumps({"type": "stop"}))
                                break
                            artifact, audio, spoken = None, 0, ""
                            await socket.send(json.dumps({"type": "text", "text": questions[phase]}))
        except Exception as exc:
            result["errors"].append(str(exc) or type(exc).__name__)
        checks["two_spoken_analyses_same_connection"] = len(result["turns"]) == 2 and not result["errors"]
        if len(result["turns"]) == 2:
            values = [next(iter(t["rows"][0].values())) for t in result["turns"]]
            checks["counts_match_independent_large_dataset"] = list(map(int, values)) == [573348, 152694]
            jobs = [p["job_id"] for t in result["turns"] for p in t["provenance"] if p.get("job_id")]
            checks["query_jobs_distinct_under_one_parent_run"] = len(set(jobs)) == 2 and all(
                j.startswith("abi_" + result["run_id"] + "_") for j in jobs
            )
            checks["timeseries_only"] = all(t["data_profile"] == "timeseries" for t in result["turns"])
    result["passed"] = bool(checks) and all(checks.values())
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return result["passed"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", required=True)
    parser.add_argument("--frontend", required=True)
    parser.add_argument("--output", type=Path, required=True)
    raise SystemExit(0 if asyncio.run(run(parser.parse_args())) else 1)
