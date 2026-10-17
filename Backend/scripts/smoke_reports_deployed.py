"""Opt-in hosted report acceptance; creates public verification reports/chat/dashboard.

Uses existing analytical sources read-only. Never uploads data or resets history/quotas.
"""

import argparse
import asyncio
import csv
import hashlib
import io
import json
import time
import uuid
import zipfile
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

import httpx


async def run(args):
    evidence = {
        "verified_at": datetime.now(UTC).isoformat(),
        "backend": args.backend,
        "frontend": args.frontend,
        "checks": {},
        "source_upload_or_reset": False,
    }
    checks = evidence["checks"]
    async with httpx.AsyncClient(base_url=args.backend.rstrip("/"), timeout=210) as client:
        token = (await client.post("/api/v1/guest-sessions", headers={"Origin": args.frontend})).json()[
            "token"
        ]
        headers = {"Authorization": "Bearer " + token, "Origin": args.frontend}

        async def get(path):
            response = await client.get("/api/v1" + path)
            response.raise_for_status()
            return response.json()

        async def mutate(path, body=None, method="POST"):
            response = await client.request(method, "/api/v1" + path, headers=headers, json=body)
            response.raise_for_status()
            return response.json()

        async def wait(run_id):
            deadline, previous = time.monotonic() + 720, None
            while time.monotonic() < deadline:
                state = await get(f"/report-runs/{run_id}")
                marker = (state["status"], state["stage"])
                if marker != previous:
                    print(f"Report {run_id[:8]}: {marker[0]} / {marker[1]}", flush=True)
                    previous = marker
                if state["status"] in {"complete", "failed", "cancelled", "waiting_input"}:
                    return state
                await asyncio.sleep(2)
            raise RuntimeError(
                "Hosted report did not reach a recorded outcome within the acceptance deadline."
            )

        try:
            config = await get("/reports/config")
            checks["production_dispatch_enabled"] = config["enabled"] and config["mode"] == "cloud_tasks"
            sources = await get("/connections")
            checks["larger_profile_preserved"] = (
                sources["data_profile"] == "timeseries" and sources["mode"] == "cloud"
            )
            chat = await mutate(
                "/conversations", {"title": "Verification: advanced retail reporting", "source": "bigquery"}
            )
            evidence["conversation_id"] = chat["id"]
            payload = {
                "question": "Create a concise business report on monthly merchandise revenue and completed order counts for all available months, January 2023 through September 2026. Include a monthly revenue trend, a product category breakdown and key factual comparisons. Forecast monthly revenue for the next three months only if chronological backtests support it. Revenue means after discounts, before refunds, tax and shipping. Explain limitations; do not invent future drivers.",
                "style": "business",
                "model": "gemini-3.8-flash",
                "idempotency_key": uuid.uuid4().hex,
            }
            accepted = await mutate(f"/conversations/{chat['id']}/reports", payload)
            evidence.update(report_id=accepted["report_id"], run_id=accepted["id"])
            args.output.write_text(json.dumps(evidence, indent=2) + "\n")
            repeated = await mutate(f"/conversations/{chat['id']}/reports", payload)
            checks["idempotent_report_admission"] = repeated["id"] == accepted["id"]
            forbidden = await client.post(f"/api/v1/report-runs/{accepted['id']}/cancel")
            checks["mutations_require_guest_credentials"] = forbidden.status_code == 401
            # Ordinary chat acquires its own lease while report work is active.
            normal = await mutate(
                f"/conversations/{chat['id']}/turns",
                {
                    "question": "How many completed orders exist across all available dates? Return a KPI.",
                    "model": "gemini-3.5-flash-lite",
                    "idempotency_key": uuid.uuid4().hex,
                },
            )
            normal_stream = await client.get(f"/api/v1/runs/{normal['run_id']}/events")
            normal_stream.raise_for_status()
            checks["ordinary_chat_during_report"] = "event: complete" in normal_stream.text
            state = await wait(accepted["id"])
            evidence["outcome"] = state
            checks["private_worker_completes_report"] = state["status"] == "complete"
            if state["status"] != "complete":
                raise RuntimeError(state.get("error") or state.get("clarification") or "Report failed.")
            rid = accepted["report_id"]
            version = await get(f"/reports/{rid}/revisions/1")
            doc = version["document"]
            checks["report_profile_and_evidence"] = (
                doc["data_profile"] == "timeseries" and bool(doc["claims"]) and bool(doc["artifact_ids"])
            )
            checks["reviewed_narrative"] = doc["reviewed"]
            artifacts = {aid: await get(f"/artifacts/{aid}") for aid in doc["artifact_ids"]}
            evidence["artifact_ids"] = list(artifacts)
            matches = []
            forecasts = []
            for aid, artifact in artifacts.items():
                if artifact.get("prediction"):
                    predictions = artifact["prediction"]
                    forecasts.append({key: value for key, value in predictions.items() if key != "rows"})
                    continue
                if artifact["row_count"] != 45:
                    continue
                for measure in artifact["visualization"].get("measures", []):
                    if measure.get("unit") == "currency" and "revenue" in measure["field"].lower():
                        data = await get(f"/artifacts/{aid}/chart-data")
                        actual = sum(Decimal(str(row[measure["field"]])) for row in data["rows"])
                        matches.append(
                            {
                                "artifact_id": aid,
                                "field": measure["field"],
                                "rows": len(data["rows"]),
                                "total": str(actual),
                                "matches": actual == Decimal("354425112.20"),
                            }
                        )
            evidence["independent_reconciliation"], evidence["predictions"] = matches, forecasts
            checks["monthly_revenue_matches_independent_ledger"] = bool(matches) and all(
                m["matches"] for m in matches
            )
            checks["prediction_or_explicit_limitation"] = bool(forecasts) or any(
                "forecast" in item.lower() or "prediction" in item.lower() for item in doc["limitations"]
            )
            files = {}
            for format, signature in (("pdf", b"%PDF"), ("docx", b"PK"), ("data", b"PK")):
                response = await client.get(f"/api/v1/reports/{rid}/revisions/1/downloads/{format}")
                response.raise_for_status()
                files[format] = response.content
                checks["download_" + format] = (
                    response.content.startswith(signature)
                    and hashlib.sha256(response.content).hexdigest() == version["downloads"][format]["sha256"]
                )
                if args.download_dir:
                    args.download_dir.mkdir(parents=True, exist_ok=True)
                    (args.download_dir / f"report-v1.{'zip' if format == 'data' else format}").write_bytes(
                        response.content
                    )
            archive = zipfile.ZipFile(io.BytesIO(files["data"]))
            manifest = json.loads(archive.read("manifest.json"))
            checks["data_manifest_version_and_claims"] = (
                manifest["report_id"] == rid
                and manifest["version"] == 1
                and manifest["claims"] == doc["claims"]
            )
            checks["full_csv_checksums_and_row_counts"] = all(
                hashlib.sha256(archive.read(dataset["file"])).hexdigest() == dataset["sha256"]
                and len(list(csv.DictReader(io.StringIO(archive.read(dataset["file"]).decode("utf-8-sig")))))
                == dataset["rows"]
                for dataset in manifest["datasets"]
            )
            word = zipfile.ZipFile(io.BytesIO(files["docx"]))
            checks["word_is_editable_document"] = b"<w:p" in word.read(
                "word/document.xml"
            ) and b"<w:tbl" in word.read("word/document.xml")
            current = await get(f"/reports/{rid}")
            renamed = await mutate(
                f"/reports/{rid}",
                {"name": "Retail performance — verified report", "expected_revision": current["revision"]},
                "PATCH",
            )
            stale = await client.patch(
                f"/api/v1/reports/{rid}",
                headers=headers,
                json={"name": "stale", "expected_revision": current["revision"]},
            )
            checks["stale_metadata_edit_rejected"] = stale.status_code == 409
            revised = await mutate(
                f"/reports/{rid}/revisions",
                {
                    "question": "Present the saved findings in technical style with a clear methodology and limitations. Reuse all saved evidence.",
                    "style": "technical",
                    "model": "gemini-3.8-flash",
                    "idempotency_key": uuid.uuid4().hex,
                    "expected_revision": renamed["revision"],
                    "base_version": 1,
                    "mode": "presentation",
                },
            )
            revision_state = await wait(revised["id"])
            checks["presentation_revision_complete"] = revision_state["status"] == "complete"
            updated = await get(f"/reports/{rid}/revisions/2")
            checks["revision_reuses_immutable_artifacts"] = (
                updated["document"]["artifact_ids"] == doc["artifact_ids"]
                and updated["document"]["style"] == "technical"
            )
            checks["original_revision_unchanged"] = (await get(f"/reports/{rid}/revisions/1")) == version
            replay = await client.get(f"/api/v1/report-runs/{accepted['id']}/events")
            replay.raise_for_status()
            checks["persisted_event_replay"] = (
                "event: complete" in replay.text and "event: progress" in replay.text
            )
            board = (
                await mutate(
                    "/dashboards", {"name": "Verification: report evidence", "request_id": uuid.uuid4().hex}
                )
            )["dashboard"]
            selected = matches[0]["artifact_id"] if matches else doc["artifact_ids"][0]
            pinned = await mutate(
                f"/dashboards/{board['id']}/items",
                {
                    "expected_revision": board["revision"],
                    "request_id": uuid.uuid4().hex,
                    "artifact_id": selected,
                    "view": {"version": 1, "view": "table", "visible_measures": []},
                },
            )
            evidence["dashboard_id"] = board["id"]
            checks["report_chart_can_be_pinned"] = pinned["item"]["artifact_id"] == selected
            current = await get(f"/reports/{rid}")
            deleted = await mutate(f"/reports/{rid}?expected_revision={current['revision']}", method="DELETE")
            checks["dashboard_retains_deleted_report_evidence"] = (await get(f"/artifacts/{selected}"))[
                "id"
            ] == selected
            await mutate(f"/reports/{rid}/restore", {"expected_revision": deleted["revision"]})
            checks["recoverable_report_deletion"] = not (await get(f"/reports/{rid}"))["deleted"]
            # Confirm non-owner cancellation using another actual guest.
            cancelled = await mutate(
                f"/conversations/{chat['id']}/reports",
                {
                    "question": "Verification cancellation request; stop before analysis.",
                    "idempotency_key": uuid.uuid4().hex,
                },
            )
            another_token = (await client.post("/api/v1/guest-sessions")).json()["token"]
            denied = await client.post(
                f"/api/v1/report-runs/{cancelled['id']}/cancel",
                headers={"Authorization": "Bearer " + another_token},
            )
            checks["cancellation_requires_initiating_guest"] = denied.status_code == 403
            await mutate(f"/report-runs/{cancelled['id']}/cancel")
            checks["cancellation_confirmed"] = (await wait(cancelled["id"]))["status"] == "cancelled"
            evidence["cancellation_run_id"] = cancelled["id"]
        except Exception as exc:
            evidence["error"] = str(exc)
            raise
        finally:
            evidence["passed"] = bool(checks) and all(checks.values()) and "error" not in evidence
            args.output.write_text(json.dumps(evidence, indent=2) + "\n")
            print(
                json.dumps(
                    {
                        "passed": evidence["passed"],
                        "checks": checks,
                        "report_id": evidence.get("report_id"),
                        "error": evidence.get("error"),
                    },
                    indent=2,
                ),
                flush=True,
            )
    return evidence["passed"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", required=True)
    parser.add_argument("--frontend", required=True)
    parser.add_argument("--output", type=Path, default=Path("../docs/evaluation/reports-deployed.json"))
    parser.add_argument("--download-dir", type=Path)
    args = parser.parse_args()
    raise SystemExit(0 if asyncio.run(run(args)) else 1)


if __name__ == "__main__":
    main()
