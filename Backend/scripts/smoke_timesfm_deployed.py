"""Opt-in hosted forecast/scenario acceptance. Public reports; read-only retail sources.

Makes real billed model/query calls, consumes three report admissions, and retains
labeled report/dashboard examples. Never resets quotas, uploads data or changes IAM.
"""

import argparse
import asyncio
import csv
import hashlib
import io
import json
import math
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
        "reports": [],
        "source_writes": 0,
        "quota_reset": False,
        "limitations": [],
    }
    if args.resume:
        evidence = json.loads(args.output.read_text())
        assert evidence["backend"] == args.backend and evidence["frontend"] == args.frontend
        assert len(evidence["reports"]) == 2
        evidence.pop("error", None)
        evidence.pop("passed", None)
        evidence["resumed_at"] = datetime.now(UTC).isoformat()
    checks = evidence["checks"]
    args.output.parent.mkdir(parents=True, exist_ok=True)

    def save():
        args.output.write_text(json.dumps(evidence, indent=2) + "\n")

    async with httpx.AsyncClient(base_url=args.backend, timeout=210) as http:
        token = (await http.post("/api/v1/guest-sessions", headers={"Origin": args.frontend})).json()["token"]
        headers = {"Origin": args.frontend, "Authorization": "Bearer " + token}

        async def request(method, path, body=None):
            response = await http.request(method, "/api/v1" + path, json=body, headers=headers)
            response.raise_for_status()
            return response.json()

        async def wait(run_id, *, scenario=False):
            previous, deadline, clarifications = None, time.monotonic() + 720, 0
            while time.monotonic() < deadline:
                state = await request("GET", f"/report-runs/{run_id}")
                marker = (state["status"], state.get("stage"))
                if marker != previous:
                    print(run_id[:8], marker, flush=True)
                    previous = marker
                if state["status"] == "waiting_input" and scenario and clarifications < 2:
                    inputs = {}
                    for requirement in state.get("clarification_requirements") or []:
                        assert requirement["grain"] == "day"
                        assert all("promotion" in key.lower() for key in requirement["drivers"])
                        horizon = requirement.get("horizon") or 14
                        inputs[requirement["target"]] = {
                            "baseline": [{key: 0 for key in requirement["drivers"]} for _ in range(horizon)],
                            "scenario": [{key: 1 for key in requirement["drivers"]} for _ in range(horizon)],
                        }
                    evidence["supplied_future_paths"] = inputs
                    await request(
                        "POST",
                        f"/report-runs/{run_id}/clarifications",
                        {
                            "expected_revision": state["revision"],
                            "forecast_inputs": inputs,
                            "answer": "Use daily merchandise revenue, January 2023 through September 2026; exactly one numeric promotion_day driver from the calendar. My explicit next-14-day assumptions: baseline promotion_day=0 every day; alternative promotion_day=1 every day. These are hypothetical schedules, not guaranteed lift. No other future business drivers. Keep one evidence task and compare eligible managed and statistical methods.",
                        },
                    )
                    clarifications += 1
                elif state["status"] in {"complete", "failed", "cancelled", "waiting_input"}:
                    return state
                await asyncio.sleep(3)
            raise RuntimeError("Report did not finish within the bounded acceptance window.")

        async def start(kind, question):
            if args.resume:
                return next(record for record in evidence["reports"] if record["kind"] == kind)
            chat = await request(
                "POST",
                "/conversations",
                {"title": "TimesFM release verification: " + kind, "source": "bigquery"},
            )
            body = {
                "question": question,
                "style": "technical",
                "model": "gemini-3.8-flash",
                "idempotency_key": uuid.uuid4().hex,
            }
            active = await request("POST", f"/conversations/{chat['id']}/reports", body)
            same = await request("POST", f"/conversations/{chat['id']}/reports", body)
            checks[kind + "_idempotent_admission"] = same["id"] == active["id"]
            record = {
                "kind": kind,
                "conversation_id": chat["id"],
                "report_id": active["report_id"],
                "run_id": active["id"],
            }
            evidence["reports"].append(record)
            save()
            return record

        try:
            config = await request("GET", "/reports/config")
            evidence["configuration"] = config
            checks["enabled_managed_timesfm"] = config["timesfm"]["enabled"] and config["timesfm"]["preview"]
            sources = await request("GET", "/connections")
            checks["larger_sources_active"] = (
                sources["data_profile"] == "timeseries" and sources["mode"] == "cloud"
            )
            monthly = await start(
                "forecast",
                "Create a technical revenue forecast report. Use exactly one evidence task: complete monthly merchandise revenue (after discounts, before refunds/tax/shipping) and completed order counts, January 2023 through September 2026 inclusive. Use explicit aliases month and revenue. Include three future monthly revenue periods, no business drivers. Compare available TimesFM with statistical methods on the same three chronological full-horizon folds; publish the method supported by validation. Do not force TimesFM to win. Explain cutoff, errors, assumptions and unavailable intervals. No other breakdown queries.",
            )
            scenario = await start(
                "scenario",
                "Create a technical conditional-scenario report. Use exactly one evidence task: daily merchandise revenue (after discounts, before refunds/tax/shipping) January 2023 through September 2026 inclusive, with numeric promotion_day = calendar.is_promotion_day cast to 0/1. Join calendar to daily preaggregated sales with equality on calendar_date/order_date and retain genuine zero-sales days. Use aliases date, revenue, promotion_day. Forecast 14 days using this single explicit future-known driver; ask me to provide structured baseline and alternative paths. Compare available conditional TimesFM and driver regression using chronological full-horizon backtests. Publish separate ordinary forecast and same-method scenario comparison if validated, otherwise explain the limitation. Do not infer causality or invent future driver values. No other evidence tasks.",
            )
            outcomes = await asyncio.gather(wait(monthly["run_id"]), wait(scenario["run_id"], scenario=True))
            for record, state in zip(evidence["reports"], outcomes):
                kind, rid = record["kind"], record["report_id"]
                record["outcome"] = state
                checks[kind + "_worker_complete"] = state["status"] == "complete"
                if state["status"] != "complete":
                    raise RuntimeError(
                        f"{kind} report outcome: {state.get('error') or state.get('clarification')}"
                    )
                revision = await request("GET", f"/reports/{rid}/revisions/1")
                doc = revision["document"]
                record["artifacts"], record["predictions"] = [], []
                for aid in doc["artifact_ids"]:
                    artifact = await request("GET", f"/artifacts/{aid}")
                    record["artifacts"].append(aid)
                    prediction = artifact.get("prediction")
                    if not prediction:
                        if kind == "forecast" and artifact["row_count"] == 45:
                            data = await request("GET", f"/artifacts/{aid}/chart-data")
                            checks["45_month_revenue_reconciliation"] = sum(
                                Decimal(str(r["revenue"])) for r in data["rows"]
                            ) == Decimal("354425112.20")
                        if kind == "scenario":
                            checks["1369_day_complete_evidence"] = (
                                artifact["row_count"] == 1369 and artifact["complete"]
                            )
                        continue
                    record["predictions"].append({"artifact_id": aid, **prediction})
                    comparison = prediction.get("comparison", {})
                    checks[kind + "_managed_comparison_evaluated"] = comparison.get("status") == "evaluated"
                    if "timesfm_3" in prediction.get("scores", {}):
                        observed = {
                            r["date"][:10]: float(r["observed"])
                            for r in artifact["rows"]
                            if r.get("observed") is not None
                        }
                        # Full CSV contains all 1,369 observations, beyond the preview.
                        response = await http.get(f"/api/v1/artifacts/{aid}/export.csv")
                        response.raise_for_status()
                        full = list(csv.DictReader(io.StringIO(response.text.lstrip("\ufeff"))))
                        observed = {r["date"][:10]: float(r["observed"]) for r in full if r.get("observed")}
                        errors = [
                            observed[r["date"]] - r["value"]
                            for fold in comparison["native_backtest_intervals"].values()
                            for r in fold
                        ]
                        score = prediction["scores"]["timesfm_3"]
                        checks[kind + "_independent_remote_score"] = math.isclose(
                            sum(abs(e) for e in errors) / len(errors), score["mae"], rel_tol=1e-9
                        ) and math.isclose(
                            math.sqrt(sum(e * e for e in errors) / len(errors)), score["rmse"], rel_tol=1e-9
                        )
                predictions = record["predictions"]
                checks[kind + "_forecast_published"] = any(p.get("kind") == "forecast" for p in predictions)
                if kind == "scenario":
                    checks["scenario_published_or_explicit_validation_limitation"] = any(
                        p.get("kind") == "scenario" for p in predictions
                    ) or any("scenario" in s.lower() for s in doc["limitations"])
                    record["scenario_published"] = any(p.get("kind") == "scenario" for p in predictions)
                checks[kind + "_immutable_source_profile"] = doc["data_profile"] == "timeseries"
                for fmt, magic in (("pdf", b"%PDF"), ("docx", b"PK"), ("data", b"PK")):
                    response = await http.get(f"/api/v1/reports/{rid}/revisions/1/downloads/{fmt}")
                    response.raise_for_status()
                    checks[kind + "_download_" + fmt] = (
                        response.content.startswith(magic)
                        and hashlib.sha256(response.content).hexdigest()
                        == revision["downloads"][fmt]["sha256"]
                    )
                    if fmt == "data":
                        archive = zipfile.ZipFile(io.BytesIO(response.content))
                        manifest = json.loads(archive.read("manifest.json"))
                        checks[kind + "_matching_saved_prediction_manifest"] = all(
                            next(d for d in manifest["datasets"] if d["file"] == p["artifact_id"] + ".csv")[
                                "prediction"
                            ]
                            == {k: v for k, v in p.items() if k != "artifact_id"}
                            for p in predictions
                        )
                replay = await http.get(f"/api/v1/report-runs/{record['run_id']}/events")
                checks[kind + "_comparison_progress_replay"] = (
                    "Comparing forecasting methods" in replay.text and "event: complete" in replay.text
                )
                save()
            # Presentation revision must reuse saved predictions, without inference.
            rid = monthly["report_id"]
            report = await request("GET", f"/reports/{rid}")
            if args.resume and evidence.get("presentation_run_id"):
                revised = {"id": evidence["presentation_run_id"]}
            else:
                revised = await request(
                    "POST",
                    f"/reports/{rid}/revisions",
                    {
                        "question": "Present the same saved evidence in business style; reuse every saved prediction without new analysis.",
                        "style": "business",
                        "mode": "presentation",
                        "base_version": 1,
                        "expected_revision": report["revision"],
                        "model": "gemini-3.8-flash",
                        "idempotency_key": uuid.uuid4().hex,
                    },
                )
            state = await wait(revised["id"])
            checks["presentation_revision_complete"] = state["status"] == "complete"
            revised_doc = (await request("GET", f"/reports/{rid}/revisions/2"))["document"]
            checks["presentation_reuses_artifacts"] = revised_doc["artifact_ids"] == monthly["artifacts"]
            evidence["presentation_run_id"] = revised["id"]
            selected = monthly["predictions"][0]["artifact_id"]
            existing_board = args.resume_dashboard or evidence.get("dashboard_id")
            if args.resume and existing_board:
                board = await request("GET", f"/dashboards/{existing_board}")
            else:
                board = (
                    await request(
                        "POST",
                        "/dashboards",
                        {"name": "TimesFM verification — saved predictions", "request_id": uuid.uuid4().hex},
                    )
                )["dashboard"]
            evidence["dashboard_id"] = board["id"]
            save()
            pin = await request(
                "POST",
                f"/dashboards/{board['id']}/items",
                {
                    "expected_revision": board["revision"],
                    "request_id": uuid.uuid4().hex,
                    "artifact_id": selected,
                    "view": {
                        "version": 1,
                        "view": "line",
                        "primary": "forecast",
                        "visible_measures": ["observed", "forecast"],
                    },
                },
            )
            checks["prediction_dashboard_pin"] = pin["item"]["artifact_id"] == selected
            evidence["dashboard_id"] = board["id"]
            checks["saved_dashboard_read"] = (await request("GET", f"/dashboards/{board['id']}"))[
                "id"
            ] == board["id"]
        except Exception as exc:
            evidence["error"] = {"type": type(exc).__name__, "message": str(exc)[:1400]}
            evidence["passed"] = False
            raise
        finally:
            evidence.setdefault("passed", bool(checks) and all(checks.values()))
            save()
    if not evidence["passed"]:
        raise RuntimeError("Some hosted checks did not pass; inspect the saved evidence.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", required=True)
    parser.add_argument("--frontend", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Revalidate captured completed reports, reusing their saved artifacts and presentation revision.",
    )
    parser.add_argument(
        "--resume-dashboard",
        default="",
        help="Existing verification dashboard to finish pinning after a rejected operator payload.",
    )
    asyncio.run(run(parser.parse_args()))
