"""Evaluate the public, hosted API against independent seed reference values."""

import argparse
import asyncio
import json
import time
import uuid
from pathlib import Path

import httpx

from app.evaluate import cases, matches


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", required=True)
    parser.add_argument("--output", default="../docs/evaluation/deployed-31.json")
    args = parser.parse_args()
    backend = args.backend.rstrip("/")
    semaphore = asyncio.Semaphore(2)
    async with httpx.AsyncClient(base_url=backend, timeout=210) as http:
        # Each evaluator stays within the public per-guest allowance; the
        # shared workspace budget remains enforced across both guests.
        tokens = []
        for _ in range(2):
            response = await http.post("/api/v1/guest-sessions")
            response.raise_for_status()
            tokens.append(response.json()["token"])

        async def evaluate(index, case):
            async with semaphore:
                started = time.monotonic()
                item = {"id": case["id"], "question": case["question"], "passed": False}
                headers = {"Authorization": "Bearer " + tokens[index // 16]}
                try:
                    response = await http.post(
                        "/api/v1/conversations",
                        headers=headers,
                        json={"title": "Evaluation: " + case["id"], "source": case.get("source", "all")},
                    )
                    response.raise_for_status()
                    chat = response.json()["id"]
                    item["conversation_id"] = chat
                    response = await http.post(
                        f"/api/v1/conversations/{chat}/turns",
                        headers=headers,
                        json={"question": case["question"], "idempotency_key": uuid.uuid4().hex},
                    )
                    response.raise_for_status()
                    run = response.json()["run_id"]
                    response = await http.get(f"/api/v1/runs/{run}/events")
                    response.raise_for_status()
                    events = [
                        (
                            block.split("event: ", 1)[1].splitlines()[0],
                            json.loads(block.split("data: ", 1)[1]),
                        )
                        for block in response.text.split("\n\n")
                        if "event: " in block and "data: " in block
                    ]
                    errors = [data for kind, data in events if kind == "error"]
                    if errors:
                        item["errors"] = errors
                    artifact_id = next((data["id"] for kind, data in events if kind == "artifact"), None)
                    if artifact_id:
                        response = await http.get(f"/api/v1/artifacts/{artifact_id}")
                        response.raise_for_status()
                        artifact = response.json()
                        item["artifact_id"] = artifact_id
                        item["passed"] = bool(
                            not errors
                            and artifact["complete"]
                            and matches(artifact["rows"], case["expected"])
                        )
                        item["retrieval"] = artifact["retrieval"]
                        if not item["passed"]:
                            item["expected"], item["actual"] = case["expected"], artifact["rows"]
                except Exception as exc:
                    item["error"] = str(exc)
                item["elapsed_seconds"] = round(time.monotonic() - started, 2)
                print(json.dumps(item, default=str), flush=True)
                return item

        results = await asyncio.gather(*(evaluate(index, case) for index, case in enumerate(cases())))
    report = {
        "backend": backend,
        "data": "hosted BigQuery and PostgreSQL; independent Python seed references",
        "cases": results,
        "passed": sum(item["passed"] for item in results),
        "total": len(results),
    }
    Path(args.output).write_text(json.dumps(report, indent=2, default=str) + "\n")
    print(json.dumps({key: value for key, value in report.items() if key != "cases"}), flush=True)
    return report["passed"] == report["total"]


if __name__ == "__main__":
    raise SystemExit(0 if asyncio.run(main()) else 1)
