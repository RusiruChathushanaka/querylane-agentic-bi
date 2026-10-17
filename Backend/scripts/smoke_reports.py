"""Local-only report smoke; --gemini opts into billable model calls, never cloud data writes.

Run from Backend with PYTHONPATH=. .venv/bin/python scripts/smoke_reports.py.
The source bundle, history and exports remain local; only --gemini uses Google Cloud.
"""

import argparse
import asyncio
import json
import tempfile
from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path

from app.admin import operator_credentials
from app.chart_presentation import saved_rows
from app.config import Settings
from app.main import create_app
from app.report_models import ReportCreate


async def run(args):
    bundle = args.bundle.resolve()
    manifest = json.loads((bundle / "manifest.json").read_text())
    with tempfile.TemporaryDirectory(prefix="querylane-report-smoke-") as directory:
        # Explicit arguments isolate this check from any .env production configuration.
        settings = Settings(
            _env_file=None,
            environment="test",
            storage_backend="memory",
            data_backend="fixture",
            data_profile="timeseries",
            retail_bundle_path=str(bundle),
            source_row_limit=30000,
            ai_backend="gemini" if args.gemini else "fixture",
            text_model=args.model,
            reports_enabled=True,
            report_dispatch="disabled",
            report_bucket="",
            report_research_enabled=False,
            report_local_directory=directory,
        )
        app = create_app(settings, credentials=operator_credentials() if args.gemini else None)
        async with app.router.lifespan_context(app):
            services = app.state.services
            chat = await services.repo.create_conversation("Local report compatibility check", "bigquery")
            request = await services.reports.create(
                chat["id"],
                "local-verification",
                ReportCreate(
                    question=(
                        "Create a concise business report on monthly merchandise revenue and completed order counts for all available months. Include a revenue trend and product category breakdown. Forecast monthly revenue for the next three months only if chronological backtests support it. Explain limitations."
                        if args.gemini
                        else "Show monthly revenue for all available months as a line chart"
                    ),
                    idempotency_key="local-report-compatibility",
                    model=args.model,
                ),
            )
            await services.report_engine.work(request["id"])
            state = await services.reports.get("report_runs", request["id"])
            result = {
                "verified_at": datetime.now(UTC).isoformat(),
                "status": state["status"],
                "stage": state["stage"],
                "error": state.get("error"),
                "clarification": state.get("clarification"),
                "budgets": state["budgets"],
                "data_profile": "timeseries",
                "model": args.model if args.gemini else "deterministic fixture",
                "cloud_data_writes": False,
                "production_dispatch_verified": False,
            }
            if state["status"] == "complete":
                revision = await services.reports.get(f"reports/{request['report_id']}/revisions", "1")
                document = revision["document"]
                result.update(
                    reviewed=document["reviewed"],
                    artifact_count=len(document["artifact_ids"]),
                    claims=len(document["claims"]),
                    downloads={
                        key: {"size": value["size"], "sha256": value["sha256"]}
                        for key, value in revision["exports"].items()
                    },
                )
                comparisons = []
                for artifact_id in document["artifact_ids"]:
                    artifact = await services.reports.get("artifacts", artifact_id)
                    if artifact.get("prediction") or artifact["row_count"] != len(manifest["monthly"]):
                        continue
                    for measure in artifact["visualization"].get("measures", []):
                        if measure["unit"] == "currency" and "revenue" in measure["field"].lower():
                            rows = [row async for row in saved_rows(services.store, artifact)]
                            actual = sum(Decimal(str(row[measure["field"]])) for row in rows)
                            expected = Decimal(manifest["summary_cents"]["revenue"]) / 100
                            comparisons.append(
                                {
                                    "field": measure["field"],
                                    "rows": len(rows),
                                    "actual": str(actual),
                                    "independent_ledger": str(expected),
                                    "matches": actual == expected,
                                }
                            )
                result["independent_reconciliation"] = comparisons
                result["passed"] = bool(comparisons) and all(value["matches"] for value in comparisons)
            else:
                result["passed"] = False
            return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--bundle", type=Path, default=Path(__file__).resolve().parents[2] / "data/retail-timeseries-20260930"
    )
    parser.add_argument(
        "--gemini",
        action="store_true",
        help="Opt in to bounded, billable Vertex model calls using operator credentials.",
    )
    parser.add_argument(
        "--model", choices=["gemini-3.8-flash", "gemini-3.5-flash-lite"], default="gemini-3.8-flash"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Write a metadata-only verification record; contains no credentials or research text.",
    )
    args = parser.parse_args()
    result = asyncio.run(run(args))
    payload = json.dumps(result, indent=2)
    if args.output:
        args.output.write_text(payload + "\n")
    print(payload)
    raise SystemExit(0 if result["passed"] else 1)


if __name__ == "__main__":
    main()
