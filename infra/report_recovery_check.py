"""Run inside a temporary private job; only creates labeled report-control probes.

No model or analytical query is executed. The probes are cancelled and soft-deleted.
"""

import asyncio
import json
import time
import uuid

import httpx
from itsdangerous import URLSafeTimedSerializer

from app.config import Settings
from app.errors import AppError
from app.main import create_app
from app.report_models import ReportCreate
from app.report_repository import ReportRepository
from app.storage import FirestoreStore


async def main():
    settings = Settings()
    app = create_app(settings)
    checks, probes = {}, []
    guest = uuid.uuid4().hex
    async with app.router.lifespan_context(app):
        services = app.state.services
        other_store = FirestoreStore(settings.google_cloud_project, settings.firestore_database)
        other = ReportRepository(other_store, settings)
        try:
            chat = await services.repo.create_conversation(
                "Verification: report recovery, no source queries", "bigquery"
            )

            async def create(label):
                run = await services.reports.create(
                    chat["id"], guest, ReportCreate(question=label, idempotency_key=uuid.uuid4().hex)
                )
                probes.append(run)
                return run

            run = await create("Verification: fenced recovery control probe; no published analysis")
            repo = services.reports
            checks["atomic_pending_outbox"] = (await services.store.get("report_outbox", run["id"]))[
                "pending"
            ]
            first = await repo.claim(run["id"])
            try:
                await other.claim(run["id"])
                checks["independent_client_exclusion"] = False
            except AppError as exc:
                checks["independent_client_exclusion"] = exc.code == "report_worker_busy"
            await repo.checkpoint(first, "verification", {"no_source_queries": True})
            state = await repo.get("report_runs", run["id"])
            state["lease_until"] = time.time() - 1
            await services.store.put("report_runs", run["id"], state)
            second = await other.claim(run["id"])
            checks["expired_lease_replaced"] = second["generation"] > first["generation"]
            checks["checkpoint_survives_fresh_client"] = await other.read_checkpoint(
                run["id"], "verification"
            ) == {"no_source_queries": True}
            try:
                await repo.checkpoint(first, "forbidden_late_write", {"invalid": True})
                checks["stale_worker_write_rejected"] = False
            except AppError as exc:
                checks["stale_worker_write_rejected"] = exc.code == "report_stale_lease"
            await other.cancel(run["id"], guest)
            await other.finish(
                second, "cancelled", error="Infrastructure probe completed; no analysis executed."
            )
            checks["terminal_duplicate_delivery_no_work"] = not await repo.received(run["id"], 0)

            # An admission interrupted before enqueue is recovered by a separate dispatcher.
            # Waiting input prevents this real queued task from performing analytical work.
            pending = await create(
                "Verification: outbox enqueue recovery control probe; no published analysis"
            )
            lease = await repo.claim(pending["id"])
            await repo.finish(
                lease, "waiting_input", clarification="Infrastructure probe; no visitor input needed."
            )
            await services.report_dispatcher.reconcile()
            checks["outbox_enqueue_recovered"] = not (
                await services.store.get("report_outbox", pending["id"])
            )["pending"]
            for _ in range(30):
                received = (await services.store.get("report_outbox", pending["id"])).get("received_at")
                if received:
                    break
                await asyncio.sleep(1)
            checks["oidc_delivery_on_another_cloud_run_instance"] = bool(received)
            await repo.cancel(pending["id"], guest)
            await services.report_dispatcher.reconcile()
            checks["waiting_cancellation_confirmed"] = (await repo.get("report_runs", pending["id"]))[
                "status"
            ] == "cancelled"
            signer = URLSafeTimedSerializer(settings.guest_signing_key, salt="agentic-bi-guest-v1")
            async with httpx.AsyncClient(
                transport=httpx.ASGITransport(app=app), base_url="http://verification"
            ) as client:
                for probe in probes:
                    current = await repo.get("reports", probe["report_id"])
                    response = await client.delete(
                        f"/api/v1/reports/{current['id']}?expected_revision={current['revision']}",
                        headers={"Authorization": "Bearer " + signer.dumps({"guest_id": guest})},
                    )
                    response.raise_for_status()
            result = {
                "checks": checks,
                "passed": all(checks.values()),
                "data_profile": settings.data_profile,
                "source_queries_or_models": False,
                "probe_reports_soft_deleted": [p["report_id"] for p in probes],
            }
            print("AGENTIC_BI_RUNTIME_CHECK " + json.dumps(result), flush=True)
            if not result["passed"]:
                raise RuntimeError("Report recovery checks failed.")
        finally:
            await other_store.close()


asyncio.run(main())
