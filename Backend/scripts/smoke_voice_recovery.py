"""Opt-in hosted Live recovery check; creates and soft-deletes one probe skill.

Uses an intentionally disabled attachment to produce a controlled application
error, then reenables only that probe and asks a fresh question in the SAME Live
connection. No provider outage is injected and no source data is changed.
"""

import argparse
import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path

import httpx
from websockets.asyncio.client import connect


async def run(args):
    evidence = {"verified_at": datetime.now(UTC).isoformat(), "checks": {}, "fatal_errors": []}
    checks = evidence["checks"]
    skill = None
    async with httpx.AsyncClient(base_url=args.backend, timeout=60) as client:
        token = (await client.post("/api/v1/guest-sessions")).json()["token"]
        headers = {"Authorization": "Bearer " + token, "Origin": args.frontend}

        async def mutate(path, payload=None, method="POST", **kwargs):
            response = await client.request(method, "/api/v1" + path, headers=headers, json=payload, **kwargs)
            response.raise_for_status()
            return response.json()

        try:
            skill = await mutate(
                "/skills",
                {
                    "name": "Verification: recoverable Live tool error",
                    "description": "Temporary release probe; soft-deleted after verification.",
                    "when_to_use": "Only when explicitly attached for the release verification.",
                    "source": "bigquery",
                    "tags": ["verification"],
                    "instructions": "Use existing approved metrics and preserve all application safeguards.",
                },
            )
            evidence["probe_skill_id"] = skill["id"]
            chat = await mutate(
                "/conversations", {"title": "Verification: Live error recovery", "source": "bigquery"}
            )
            evidence["conversation_id"] = chat["id"]
            await mutate(f"/conversations/{chat['id']}/skills", {"skill_ids": [skill["id"]]}, "PATCH")
            skill = await mutate(
                f"/skills/{skill['id']}", {"expected_revision": skill["revision"], "enabled": False}, "PATCH"
            )
            url = args.backend.replace("https://", "wss://").replace("http://", "ws://")
            artifact, audio, transcript = None, 0, ""
            failed, second = False, False
            async with connect(
                url + f"/api/v1/conversations/{chat['id']}/voice",
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
                            evidence["run_id"] = event["run_id"]
                            await socket.send(
                                json.dumps(
                                    {
                                        "type": "text",
                                        "text": "Use analyze_data to query the count of completed sales_orders across all available history. Return a KPI and speak briefly.",
                                    }
                                )
                            )
                        elif kind == "tool_error":
                            evidence["recoverable_error"] = {
                                "code": event.get("code"),
                                "message": event.get("message"),
                            }
                            failed = event.get("code") == "skill_unavailable"
                            skill = await mutate(
                                f"/skills/{skill['id']}",
                                {"expected_revision": skill["revision"], "enabled": True},
                                "PATCH",
                            )
                        elif kind == "turn_complete" and failed and not second:
                            second = True
                            await socket.send(
                                json.dumps(
                                    {
                                        "type": "text",
                                        "text": "I have enabled the attached skill. Now please run a new analysis of completed sales_orders across all history as completed_orders. Query the data, show the KPI and speak the count briefly.",
                                    }
                                )
                            )
                        elif kind == "artifact":
                            response = await client.get("/api/v1/artifacts/" + event["data"]["id"])
                            response.raise_for_status()
                            artifact, audio, transcript = response.json(), 0, ""
                        elif kind == "audio" and artifact:
                            audio += 1
                        elif kind == "transcript" and artifact and event.get("role") == "assistant":
                            transcript = event["text"] if event.get("replace") else transcript + event["text"]
                        elif kind == "turn_complete" and artifact and audio and transcript:
                            await socket.send(json.dumps({"type": "stop"}))
                            break
                        elif kind == "error":
                            evidence["fatal_errors"].append(event.get("message"))
                            break
            checks["recoverable_tool_error_delivered"] = failed
            checks["same_connection_continued"] = (
                second and artifact is not None and not evidence["fatal_errors"]
            )
            checks["large_dataset_count"] = (
                bool(artifact) and int(next(iter(artifact["rows"][0].values()))) == 573348
            )
            checks["timeseries_query_evidence"] = (
                bool(artifact)
                and artifact["data_profile"] == "timeseries"
                and any(p.get("job_id") for p in artifact["provenance"])
            )
            checks["spoken_recovery_answer"] = bool(audio and transcript)
            if artifact:
                evidence["answer"] = {
                    "artifact_id": artifact["id"],
                    "rows": artifact["rows"],
                    "provenance": artifact["provenance"],
                    "audio_frames": audio,
                    "spoken": transcript,
                }
            for _ in range(30):
                state = (await client.get("/api/v1/runs/" + evidence["run_id"])).json()
                if state["status"] != "running":
                    break
                await asyncio.sleep(0.5)
            checks["run_finalized_after_stop"] = state["status"] == "complete"
        except Exception as exc:
            evidence["fatal_errors"].append(type(exc).__name__ + ": " + str(exc)[:500])
        finally:
            if skill:
                try:
                    removed = await mutate(
                        f"/skills/{skill['id']}",
                        method="DELETE",
                        params={"expected_revision": skill["revision"]},
                    )
                    checks["only_probe_skill_soft_deleted"] = removed["deleted"]
                except Exception as exc:
                    evidence["fatal_errors"].append("Probe cleanup: " + type(exc).__name__)
        evidence["passed"] = bool(checks) and all(checks.values()) and not evidence["fatal_errors"]
        args.output.write_text(json.dumps(evidence, indent=2) + "\n")
        print(
            json.dumps({"passed": evidence["passed"], "checks": checks, "errors": evidence["fatal_errors"]})
        )
        return evidence["passed"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", required=True)
    parser.add_argument("--frontend", required=True)
    parser.add_argument("--output", required=True, type=Path)
    raise SystemExit(0 if asyncio.run(run(parser.parse_args())) else 1)
