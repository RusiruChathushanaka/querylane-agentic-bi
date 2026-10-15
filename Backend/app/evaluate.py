"""Numerical evaluation against independent Python aggregates of the retail seed."""

import argparse
import asyncio
import json
import time
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

from app.adk_sessions import FirestoreSessionService
from app.admin import operator_credentials
from app.ai import AI
from app.analysis import AnalysisService
from app.config import Settings
from app.connectors import Connectors
from app.fixtures import retail_data
from app.repository import Repository
from app.storage import MemoryStore


def cases():
    data = retail_data()
    result = []
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September"]
    for number, name in enumerate(months, 1):
        month = f"2026-{number:02}"
        total = sum(row["revenue"] for row in data["orders"] if row["month"] == month)
        result.append(
            {
                "id": f"revenue-{month}",
                "question": f"What is total revenue in {name} 2026? Alias the result revenue.",
                "expected": [{"revenue": total}],
            }
        )
    for region in ["North", "South", "East", "West"]:
        total = sum(row["revenue"] for row in data["orders"] if row["region"] == region)
        result.append(
            {
                "id": f"region-{region}",
                "question": f"What is total revenue in {region}? Alias the result revenue.",
                "expected": [{"revenue": total}],
            }
        )
    for number, name in enumerate(months, 1):
        month = f"2026-{number:02}"
        expected = []
        for region in ["North", "South", "East", "West"]:
            actual = sum(
                row["revenue"] for row in data["orders"] if row["month"] == month and row["region"] == region
            )
            target = next(
                row["target_revenue"]
                for row in data["regional_targets"]
                if row["month"] == month and row["region"] == region
            )
            expected.append({"region": region, "revenue": actual, "target_revenue": target})
        result.append(
            {
                "id": f"targets-{month}",
                "question": f"Compare regional revenue with targets in {name} 2026. Return region, revenue, target_revenue.",
                "expected": expected,
            }
        )
    totals = defaultdict(Decimal)
    for row in data["orders"]:
        totals[row["month"]] += row["revenue"]
    result.append(
        {
            "id": "monthly-trend",
            "question": "Show monthly revenue as a line chart. Return month and revenue.",
            "expected": [{"month": key, "revenue": value} for key, value in totals.items()],
        }
    )
    categories = {row["product_id"]: row["category"] for row in data["products"]}
    totals = defaultdict(Decimal)
    for row in data["order_items"]:
        totals[categories[row["product_id"]]] += row["line_revenue"]
    expected = [{"category": key, "revenue": value} for key, value in totals.items()]
    result.extend(
        [
            {
                "id": "categories",
                "question": "Break down revenue by product category. Return category and revenue.",
                "expected": expected,
            },
            {
                "id": "categories-table",
                "question": "Show revenue by product category in a table. Return category and revenue.",
                "expected": expected,
            },
        ]
    )
    customer_segment = {row["customer_id"]: row["segment"] for row in data["customer_profiles"]}
    totals = defaultdict(Decimal)
    for row in data["orders"]:
        totals[customer_segment[row["customer_id"]]] += row["revenue"]
    result.append(
        {
            "id": "customer-segments",
            "question": "What is revenue by customer segment? Return segment and revenue.",
            "expected": [{"segment": key, "revenue": value} for key, value in totals.items()],
        }
    )
    result.append(
        {
            "id": "refunds",
            "question": "What is the total refund amount? Alias it refund_amount.",
            "expected": [{"refund_amount": sum(row["refund_amount"] for row in data["returns"])}],
        }
    )
    total = sum(row["revenue"] for row in data["orders"])
    result.extend(
        [
            {
                "id": "total-revenue",
                "question": "What is total gross revenue? Alias it revenue.",
                "expected": [{"revenue": total}],
            },
            {
                "id": "revenue-kpi",
                "question": "Show a KPI for total gross sales revenue. Alias it revenue.",
                "expected": [{"revenue": total}],
            },
        ]
    )
    counts = defaultdict(int)
    for row in data["customer_profiles"]:
        counts[row["segment"]] += 1
    result.extend(
        [
            {
                "id": "customers-table",
                "source": "postgres",
                "question": "Count customers by segment. Return segment and customers.",
                "expected": [{"segment": key, "customers": value} for key, value in counts.items()],
            },
            {
                "id": "customers-chart",
                "source": "postgres",
                "question": "Show customer counts by segment in a chart. Return segment and customers.",
                "expected": [{"segment": key, "customers": value} for key, value in counts.items()],
            },
        ]
    )
    return result


def matches(actual, expected):
    if len(actual) != len(expected):
        return False
    keys = list(expected[0]) if expected else []

    def normalize(rows):
        output = []
        for row in rows:
            values = []
            for key in keys:
                value = row.get(key)
                if value is None:
                    values.append("NULL")
                    continue
                try:
                    values.append(str(Decimal(str(value)).quantize(Decimal("0.01"))))
                except Exception:
                    values.append(str(value))
            output.append(tuple(values))
        return sorted(output)

    return normalize(actual) == normalize(expected)


async def evaluate(mode, limit, output):
    settings = Settings(
        environment="test", ai_backend=mode, guest_hourly_limit=1000, workspace_daily_limit=1000
    )
    store = MemoryStore()
    repo = Repository(store, settings)
    connectors = Connectors(settings)
    credentials = operator_credentials() if mode == "gemini" else None
    ai = AI(settings, FirestoreSessionService(store), connectors, store, credentials=credentials)
    analysis = AnalysisService(repo, connectors, ai, settings)
    report = {
        "mode": mode,
        "text_model": settings.text_model if mode == "gemini" else "deterministic local planner",
        "data": "synthetic fixtures; reference values independently aggregated in Python",
        "cases": [],
    }
    semaphore = asyncio.Semaphore(3)

    async def evaluate_one(case):
        async with semaphore:
            started = time.monotonic()
            conversation = await repo.create_conversation(case["id"], case.get("source", "all"))
            run = await analysis.start(conversation["id"], "evaluator", case["question"], case["id"])
            await analysis.tasks[run["id"]]
            artifacts = await store.list("artifacts")
            artifact = next((a for a in artifacts if a["conversation_id"] == conversation["id"]), None)
            rows = []
            if artifact:
                for page in sorted(
                    await store.list(f"artifacts/{artifact['id']}/pages"), key=lambda p: p["index"]
                ):
                    rows.extend(page["rows"])
            passed = bool(artifact and artifact["complete"] and matches(rows, case["expected"]))
            item = {
                "id": case["id"],
                "question": case["question"],
                "passed": passed,
                "elapsed_seconds": round(time.monotonic() - started, 2),
            }
            if not passed:
                item["expected"] = case["expected"]
                item["actual"] = rows
                item["events"] = await store.list(f"runs/{run['id']}/events")
            print(json.dumps({k: v for k, v in item.items() if k not in ("expected", "actual", "events")}))
            return item

    try:
        report["cases"] = await asyncio.gather(*(evaluate_one(case) for case in cases()[:limit]))
    finally:
        await analysis.close()
        await ai.close()
    report["passed"] = sum(item["passed"] for item in report["cases"])
    report["total"] = len(report["cases"])
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    Path(output).write_text(json.dumps(report, indent=2, default=str))
    print(json.dumps({"passed": report["passed"], "total": report["total"], "output": output}))
    return report["passed"] == report["total"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["fixture", "gemini"], default="fixture")
    parser.add_argument("--limit", type=int, default=31)
    parser.add_argument("--output", default="../docs/evaluation/latest.json")
    args = parser.parse_args()
    if not 1 <= args.limit <= 31:
        parser.error("--limit must be between 1 and 31.")
    raise SystemExit(0 if asyncio.run(evaluate(args.mode, args.limit, args.output)) else 1)


if __name__ == "__main__":
    main()
