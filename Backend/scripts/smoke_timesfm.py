"""Opt-in managed compatibility probe over synthetic parameters; no analytical tables.

Default invocation prints the plan. --live makes at most four billed inference jobs
using ADC, or an explicitly selected existing runtime identity. It creates no IAM,
Firestore, source table, permanent model, service, or production feature flag.
"""

import argparse
import asyncio
import datetime as dt
import json
import uuid
from pathlib import Path
from types import SimpleNamespace

from app.config import Settings
from app.connectors import Connectors
from app.report_forecasting import reserve_candidates
from app.report_models import ForecastSpec, ReportCreate
from app.report_repository import ReportRepository
from app.report_statistics import prepare_series
from app.repository import Repository
from app.storage import MemoryStore
from app.timesfm import TimesFM, batches


async def run(args):
    settings = Settings(
        environment="test",
        data_backend="fixture",
        storage_backend="memory",
        data_profile="legacy",
        ai_backend="fixture",
        report_dispatch="local",
        google_cloud_project=args.project,
        bigquery_location=args.location,
        report_timesfm_enabled=True,
        report_timesfm_verified=True,
    )
    evidence = {
        "verified_at": dt.datetime.now(dt.UTC).isoformat(),
        "scope": "Managed compatibility over synthetic inline parameters; not a production enablement record.",
        "identity": args.impersonate or "operator ADC",
        "model": "TimesFM 3.0",
        "preview": True,
        "project": args.project,
        "location": args.location,
        "source_queries": 0,
        "source_writes": 0,
        "iam_changes": 0,
        "production_feature_enabled": False,
        "checks": {},
        "jobs": [],
    }
    if not args.live:
        print(
            json.dumps(
                {
                    **evidence,
                    "plan": "Pass --live for up to four billed BigQuery inference jobs; --impersonate verifies an existing runtime identity.",
                },
                indent=2,
            )
        )
        return
    import google.auth
    from google.auth import impersonated_credentials
    from google.cloud import bigquery

    try:
        if args.gcloud_credentials:
            import subprocess

            from google.oauth2.credentials import Credentials

            command = ["gcloud", "auth", "print-access-token"]
            if args.impersonate:
                command.append("--impersonate-service-account=" + args.impersonate)
            token = subprocess.check_output(command, text=True, stderr=subprocess.DEVNULL, timeout=30).strip()
            credentials = Credentials(token=token)
        else:
            credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
            if args.impersonate:
                credentials = impersonated_credentials.Credentials(
                    source_credentials=credentials,
                    target_principal=args.impersonate,
                    target_scopes=["https://www.googleapis.com/auth/cloud-platform"],
                    lifetime=600,
                )
    except Exception as exc:
        evidence.update(
            passed=False,
            error={
                "type": type(exc).__name__,
                "message": "Existing credentials could not authenticate this identity; no IAM grants were changed.",
            },
        )
        if args.output:
            Path(args.output).write_text(json.dumps(evidence, indent=2) + "\n")
        print(json.dumps(evidence, indent=2))
        return False
    store = MemoryStore()
    repo = ReportRepository(store, settings)
    chat = await Repository(store, settings).create_conversation("TimesFM compatibility", "all")
    active = await repo.create(
        chat["id"],
        "operator-probe",
        ReportCreate(question="Verify parameterized TimesFM", idempotency_key=uuid.uuid4().hex),
    )
    lease = await repo.claim(active["id"])
    connectors = Connectors(settings)
    connectors.bq = bigquery.Client(project=args.project, location=args.location, credentials=credentials)
    engine = SimpleNamespace(settings=settings, repo=repo)
    import pandas as pd

    monthly = [
        {"date": d.date().isoformat(), "sales": 100 + i * 0.7 + (i % 12) * 2}
        for i, d in enumerate(pd.date_range("2023-01-01", periods=45, freq="MS"))
    ]
    daily = [
        {
            "date": (dt.date(2025, 1, 1) + dt.timedelta(days=i)).isoformat(),
            "sales": 100 + i * 0.2 + (i % 7) + (i % 2) * 4,
            "promotion": i % 2,
        }
        for i in range(140)
    ]
    specs = [
        ForecastSpec(task_id="main", date_column="date", target="sales", grain="month", horizon=3),
        ForecastSpec(
            task_id="main",
            date_column="date",
            target="sales",
            grain="day",
            horizon=7,
            drivers=["promotion"],
            future_drivers=[{"promotion": 0}] * 7,
            scenario_drivers=[{"promotion": 1}] * 7,
            scenario_name="Explicit synthetic schedule",
        ),
    ]
    await reserve_candidates(
        engine, active, lease, {"tasks": [1], "forecasts": [s.model_dump() for s in specs]}
    )

    async def heartbeat():
        while True:
            await asyncio.sleep(5)
            await repo.heartbeat(lease)

    beat = asyncio.create_task(heartbeat())
    try:
        provider = TimesFM(connectors, repo)
        for index, (rows, spec) in enumerate(zip([monthly, daily], specs)):
            for final in (False, True):
                phase = "final" if final else "backtest"
                result = await provider.execute(
                    active, lease, str(index), batches(prepare_series(rows, spec.model_dump()), final=final)
                )
                evidence["jobs"].append({k: v for k, v in result.items() if k != "series"})
                evidence["checks"][f"{index}_{phase}_parameterized_output"] = True
        evidence["passed"] = True
    except Exception as exc:
        evidence["passed"] = False
        evidence["error"] = {
            "type": type(exc).__name__,
            "code": getattr(exc, "code", None),
            "message": getattr(exc, "message", "Managed compatibility probe did not complete."),
        }
        return False
    finally:
        beat.cancel()
        await asyncio.gather(beat, return_exceptions=True)
        await connectors.cancel(active["id"])
        await connectors.close()
        if args.output:
            Path(args.output).write_text(json.dumps(evidence, indent=2) + "\n")
        print(json.dumps(evidence, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument(
        "--gcloud-credentials",
        action="store_true",
        help="Use the existing CLI login's short-lived token in memory; never writes a credential file.",
    )
    parser.add_argument("--project", default="project-e8b1593d-009a-4822-abf")
    parser.add_argument("--location", default="asia-southeast1")
    parser.add_argument("--impersonate", default="")
    parser.add_argument("--output")
    if asyncio.run(run(parser.parse_args())) is False:
        raise SystemExit(1)
