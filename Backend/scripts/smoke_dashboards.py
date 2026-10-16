"""Opt-in API check using existing immutable artifacts; never runs an analysis or history reset."""

import argparse
import asyncio
import json
import uuid
from datetime import datetime
from pathlib import Path

import httpx


async def run(args):
    report = {
        "verified_at": datetime.now().astimezone().isoformat(),
        "backend": args.backend,
        "checks": {},
        "created_dashboards": [],
        "source_queries_requested": False,
        "model_calls_requested": False,
    }
    checks = report["checks"]
    async with httpx.AsyncClient(base_url=args.backend.rstrip("/"), timeout=60) as client:
        token = (await client.post("/api/v1/guest-sessions")).json()["token"]
        headers = {"Authorization": "Bearer " + token}

        async def mutate(path, method, body, key=None):
            payload = body | {"request_id": key or uuid.uuid4().hex}
            response = await client.request(
                method,
                "/api/v1" + path,
                headers=headers,
                **({"params": payload} if method == "DELETE" else {"json": payload}),
            )
            response.raise_for_status()
            return response.json(), payload

        async def get(path):
            response = await client.get("/api/v1" + path)
            response.raise_for_status()
            return response.json()

        first, _ = await mutate(
            "/dashboards",
            "POST",
            {
                "name": "Verification: saved results",
                "description": "Opt-in API verification; no new analyses.",
            },
        )
        second, _ = await mutate(
            "/dashboards",
            "POST",
            {
                "name": "Verification: shared result",
                "description": "Same immutable artifact, another dashboard.",
            },
        )
        boards = [first["dashboard"], second["dashboard"]]
        report["created_dashboards"] = [b["id"] for b in boards]
        artifact = await get(f"/artifacts/{args.artifact_id}?metadata_only=true")
        checks["metadata_has_no_preview_rows"] = artifact["rows"] == []
        view = {"version": 1, "view": "table", "visible_measures": [], "highlights": True, "decimals": 2}
        response, payload = await mutate(
            f"/dashboards/{boards[0]['id']}/items",
            "POST",
            {"expected_revision": boards[0]["revision"], "artifact_id": artifact["id"], "view": view},
        )
        board, item = response["dashboard"], response["item"]
        again, _ = await mutate(
            f"/dashboards/{board['id']}/items",
            "POST",
            {k: v for k, v in payload.items() if k != "request_id"},
            payload["request_id"],
        )
        checks["idempotent_pin"] = again == response
        other, _ = await mutate(
            f"/dashboards/{boards[1]['id']}/items",
            "POST",
            {"expected_revision": boards[1]["revision"], "artifact_id": artifact["id"], "view": view},
        )
        boards[1] = other["dashboard"]
        checks["shared_public_result"] = (await get(f"/dashboards/{boards[1]['id']}"))["items"][0][
            "artifact_id"
        ] == artifact["id"]
        stale = await client.patch(
            f"/api/v1/dashboards/{board['id']}",
            headers=headers,
            json={"name": "Stale edit", "expected_revision": 1, "request_id": uuid.uuid4().hex},
        )
        checks["stale_revision_denied"] = stale.status_code == 409
        removed, _ = await mutate(
            f"/dashboards/{board['id']}/items/{item['id']}",
            "DELETE",
            {"expected_revision": board["revision"]},
        )
        board = removed["dashboard"]
        checks["unpin_only_one_board"] = (await get(f"/dashboards/{board['id']}"))["card_count"] == 0 and (
            await get(f"/dashboards/{boards[1]['id']}")
        )["card_count"] == 1
        replay, _ = await mutate(
            f"/dashboards/{board['id']}/items",
            "POST",
            {k: v for k, v in payload.items() if k != "request_id"},
            payload["request_id"],
        )
        checks["old_pin_retry_cannot_resurrect"] = (
            replay == response and (await get(f"/dashboards/{board['id']}"))["card_count"] == 0
        )
        restored, _ = await mutate(
            f"/dashboards/{board['id']}/items/{item['id']}/restore",
            "POST",
            {"expected_revision": board["revision"]},
        )
        board = restored["dashboard"]
        checks["restore_card"] = board["card_count"] == 1
        after = await get(f"/artifacts/{artifact['id']}?metadata_only=true")
        checks["artifact_evidence_unchanged"] = after == artifact
        csv = await client.get(f"/api/v1/artifacts/{artifact['id']}/export.csv")
        checks["saved_csv_available"] = csv.status_code == 200 and "text/csv" in csv.headers.get(
            "content-type", ""
        )
        deleted, _ = await mutate(
            f"/dashboards/{board['id']}", "DELETE", {"expected_revision": board["revision"]}
        )
        back, _ = await mutate(
            f"/dashboards/{board['id']}/restore",
            "POST",
            {"expected_revision": deleted["dashboard"]["revision"]},
        )
        checks["dashboard_restore_keeps_card"] = (await get(f"/dashboards/{board['id']}"))["card_count"] == 1
        boards[0] = back["dashboard"]
        for value in boards:
            await mutate(f"/dashboards/{value['id']}", "DELETE", {"expected_revision": value["revision"]})
        report["cleanup"] = (
            "Verification dashboards soft-deleted; recovery references remain until an authorized expiry purge."
        )
    report["passed"] = all(checks.values())
    return report


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", required=True)
    parser.add_argument(
        "--artifact-id",
        required=True,
        help="An existing saved artifact; this script never creates an analysis.",
    )
    parser.add_argument("--output", type=Path, default=Path("../docs/evaluation/dashboards-api.json"))
    args = parser.parse_args()
    report = await run(args)
    args.output.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return report["passed"]


if __name__ == "__main__":
    raise SystemExit(0 if asyncio.run(main()) else 1)
