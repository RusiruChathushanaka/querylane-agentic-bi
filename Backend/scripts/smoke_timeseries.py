"""Opt-in hosted time-series/chart acceptance. Creates public demo chats; never resets data."""

import argparse
import asyncio
import csv
import io
import json
import uuid
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import duckdb
import httpx
from websockets.asyncio.client import connect
from websockets.exceptions import InvalidStatus

from app.retail_generator import read_manifest


def reference(bundle):
    manifest = read_manifest(bundle)
    monthly = {month: Decimal(value["revenue_cents"]) / 100 for month, value in manifest["monthly"].items()}
    db = duckdb.connect(config={"threads": 2, "memory_limit": "256MB"})
    try:
        db.from_parquet(str(bundle / "sales_orders.parquet")).create_view("orders")
        db.from_parquet(str(bundle / "customer_profiles.parquet")).create_view("profiles")
        segments = dict(
            db.execute(
                "SELECT p.segment,SUM(o.revenue) FROM orders o JOIN profiles p ON o.customer_id=p.customer_id GROUP BY p.segment"
            ).fetchall()
        )
    finally:
        db.close()
    return manifest, monthly, segments


def equal_amount(actual, expected):
    return actual is not None and abs(Decimal(str(actual)) - Decimal(str(expected))) <= Decimal("0.02")


async def run(args):
    manifest, monthly, segments = reference(args.bundle)
    total = sum(monthly.values())
    report = {
        "verified_at": datetime.now().astimezone().isoformat(),
        "backend": args.backend,
        "frontend": args.frontend,
        "reference": "Independent deterministic bundle ledger and local Parquet SQL",
        "checks": {},
        "analyses": [],
    }
    checks = report["checks"]
    async with httpx.AsyncClient(base_url=args.backend, timeout=210) as http:

        async def get(path):
            response = await http.get(path)
            response.raise_for_status()
            return response.json()

        token_response = await http.post("/api/v1/guest-sessions", headers={"Origin": args.frontend})
        token_response.raise_for_status()
        token = token_response.json()["token"]
        headers = {"Authorization": "Bearer " + token, "Origin": args.frontend}

        async def post(path, body):
            response = await http.post(path, json=body, headers=headers)
            response.raise_for_status()
            return response.json()

        async def analyze(title, question, model="gemini-3.8-flash", chat=None):
            if chat is None:
                chat = (await post("/api/v1/conversations", {"title": title, "source": "all"}))["id"]
            body = {"question": question, "model": model, "idempotency_key": uuid.uuid4().hex}
            run = await post(f"/api/v1/conversations/{chat}/turns", body)
            response = await http.get(f"/api/v1/runs/{run['run_id']}/events")
            response.raise_for_status()
            events = [
                (block.split("event: ", 1)[1].splitlines()[0], json.loads(block.split("data: ", 1)[1]))
                for block in response.text.split("\n\n")
                if "event: " in block and "data: " in block
            ]
            errors = [value for kind, value in events if kind == "error"]
            if errors:
                raise RuntimeError(json.dumps(errors))
            assert any(kind == "complete" for kind, _ in events), "Missing completion"
            artifact_id = next(value["id"] for kind, value in events if kind == "artifact")
            artifact = await get(f"/api/v1/artifacts/{artifact_id}")
            checks[f"complete_{title}"] = artifact["complete"] and artifact["data_profile"] == "timeseries"
            checks[f"gemini_{title}"] = (
                artifact["ai"]["backend"] == "gemini" and artifact["ai"]["text_model"] == model
            )
            checks[f"evidence_{title}"] = all(p["sql"] for p in artifact["provenance"]) and any(
                p.get("job_id") for p in artifact["provenance"]
            )
            same = await post(f"/api/v1/conversations/{chat}/turns", body)
            checks[f"idempotent_{title}"] = same["run_id"] == run["run_id"]
            replay = await http.get(f"/api/v1/runs/{run['run_id']}/events?after=999999")
            checks[f"replay_{title}"] = replay.status_code == 200 and not replay.text
            report["analyses"].append(
                {
                    "title": title,
                    "conversation_id": chat,
                    "artifact_id": artifact_id,
                    "run_id": run["run_id"],
                    "model": artifact["ai"]["text_model"],
                    "rows": artifact["row_count"],
                    "sql": [p["sql"] for p in artifact["provenance"]],
                }
            )
            return chat, artifact

        checks["live"] = (await get("/health/live"))["status"] == "ok"
        checks["ready"] = (await get("/health/ready"))["status"] == "ready"
        connections = await get("/api/v1/connections")
        checks["cloud_sources"] = connections["mode"] == "cloud" and all(
            c["connected"] for c in connections["connections"]
        )
        checks["timeseries_profile"] = connections["data_profile"] == "timeseries" and [
            c["tables"] for c in connections["connections"]
        ] == [5, 6]
        checks["frontend_health"] = (await http.get(args.frontend + "/api/health")).json()["backend"] == 200
        checks["runtime_url"] = (await http.get(args.frontend + "/api/config")).json()[
            "backend_url"
        ] == args.backend
        preflight = await http.options(
            "/api/v1/conversations",
            headers={"Origin": args.frontend, "Access-Control-Request-Method": "POST"},
        )
        checks["cors"] = preflight.headers.get("access-control-allow-origin") == args.frontend

        chat, artifact = await analyze(
            "Release: monthly sales",
            "Show monthly after-discount merchandise revenue across ALL available dates as a line chart. Use sales_orders.revenue, not gross_sales. Return exactly month (YYYY-MM text) and revenue (SUM).",
        )
        actual = {r["month"][:7]: r["revenue"] for r in artifact["rows"]}
        checks["monthly_numbers"] = actual.keys() == monthly.keys() and all(
            equal_amount(actual[k], v) for k, v in monthly.items()
        )
        chart = await get(f"/api/v1/artifacts/{artifact['id']}/chart-data")
        checks["monthly_chart"] = chart["coverage"]["plotted_rows"] == len(monthly) and equal_amount(
            chart["stats"]["sum"], total
        )
        checks["measure_units"] = any(
            m["unit"] == "currency" and m["currency"] == "USD" for m in chart["visualization"]["measures"]
        )
        csv_response = await http.get(f"/api/v1/artifacts/{artifact['id']}/export.csv")
        csv_response.raise_for_status()
        csv_rows = list(csv.DictReader(io.StringIO(csv_response.text.lstrip("\ufeff"))))
        checks["csv_full_result"] = len(csv_rows) == len(monthly) and equal_amount(
            sum(Decimal(r["revenue"]) for r in csv_rows), total
        )
        _, followup = await analyze(
            "Release: 2024 follow-up",
            "Only 2024, please. Keep the same measure and return exactly month and revenue.",
            chat=chat,
        )
        expected_2024 = {m: v for m, v in monthly.items() if m.startswith("2024-")}
        values = {r["month"][:7]: r["revenue"] for r in followup["rows"]}
        checks["followup_numbers"] = values.keys() == expected_2024.keys() and all(
            equal_amount(values[k], v) for k, v in expected_2024.items()
        )
        fork = await post(f"/api/v1/conversations/{chat}/fork", {})
        checks["fork_evidence"] = any(
            m.get("artifact_id") == followup["id"]
            for m in (await get(f"/api/v1/conversations/{fork['id']}"))["messages"]
        )

        _, daily = await analyze(
            "Release: daily history",
            "Show daily after-discount merchandise revenue for ALL available history. Include zero-sales dates using the calendar spine. Return exactly order_date (ISO business date) and revenue. One row per date, as a line chart.",
            "gemini-3.5-flash-lite",
        )
        daily_chart = await get(f"/api/v1/artifacts/{daily['id']}/chart-data")
        checks["daily_full_chart"] = daily_chart["coverage"]["plotted_rows"] == manifest["files"]["calendar"][
            "rows"
        ] and equal_amount(daily_chart["stats"]["sum"], total)
        checks["daily_zero_sales"] = any(
            str(r["order_date"])[:10] == "2024-02-29" and equal_amount(r["revenue"], 0)
            for r in daily_chart["rows"]
        )

        _, segment = await analyze(
            "Release: cross-source segments",
            "What is total after-discount merchandise revenue by customer segment for ALL available dates? Join BigQuery customer-level sales to PostgreSQL customer_profiles by customer_id. Return exactly segment and revenue, with a bar chart. Do not limit the customer population.",
        )
        actual_segments = {r["segment"]: r["revenue"] for r in segment["rows"]}
        checks["cross_source_numbers"] = actual_segments.keys() == segments.keys() and all(
            equal_amount(actual_segments[k], v) for k, v in segments.items()
        )
        checks["cross_source_evidence"] = {p["source"] for p in segment["provenance"]} == {
            "bigquery",
            "postgres",
        } and bool(segment["join_diagnostics"])

        voice_chat = (
            await post("/api/v1/conversations", {"title": "Release: voice connection", "source": "all"})
        )["id"]
        ws_url = (
            args.backend.replace("https://", "wss://").replace("http://", "ws://")
            + f"/api/v1/conversations/{voice_chat}/voice"
        )
        try:
            async with connect(ws_url, origin="https://untrusted.example", open_timeout=20):
                checks["voice_origin_denied"] = False
        except InvalidStatus as exc:
            checks["voice_origin_denied"] = exc.response.status_code == 403
        async with connect(ws_url, origin=args.frontend, open_timeout=20) as socket:
            await socket.send(json.dumps({"type": "authenticate", "token": "invalid"}))
            checks["voice_token_denied"] = json.loads(await socket.recv())["type"] == "error"
        if args.voice:
            seen, errors = set(), []
            async with connect(
                ws_url, origin=args.frontend, open_timeout=30, close_timeout=10, max_size=2**20
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
                                        "text": "Query total after-discount merchandise revenue across all available sales_orders dates. Answer briefly and show a KPI.",
                                    }
                                )
                            )
                        if event["type"] == "error":
                            errors.append(event.get("message"))
                            break
                        if event["type"] == "turn_complete" and {"artifact", "audio", "transcript"} <= seen:
                            await socket.send(json.dumps({"type": "stop"}))
                            break
            checks["live_analysis_audio_transcript"] = {
                "ready",
                "artifact",
                "audio",
                "transcript",
                "turn_complete",
            } <= seen and not errors
            report["voice"] = {
                "events": sorted(seen),
                "errors": errors,
                "raw_audio_recorded": False,
                "input": "text through live transport; microphone hardware not tested",
            }
        report["reference_total"] = str(total)
    report["passed"] = all(checks.values())
    return report


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", required=True)
    parser.add_argument("--frontend", required=True)
    parser.add_argument("--bundle", type=Path, default=Path("../data/retail-timeseries-20260930"))
    parser.add_argument("--voice", action="store_true")
    parser.add_argument("--output", type=Path, default=Path("../docs/evaluation/charts-deployed.json"))
    args = parser.parse_args()
    args.backend, args.frontend = args.backend.rstrip("/"), args.frontend.rstrip("/")
    result = await run(args)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return result["passed"]


if __name__ == "__main__":
    raise SystemExit(0 if asyncio.run(main()) else 1)
