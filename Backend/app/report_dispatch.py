"""Cloud Tasks outbox, reconciliation and an explicitly local-only development pump."""

import asyncio
import contextlib
import hashlib
import json
import logging
import time

from app.errors import AppError
from app.maintenance import MAINTENANCE
from app.report_repository import REGISTRY, TERMINAL

logger = logging.getLogger(__name__)


class ReportDispatcher:
    def __init__(self, repository, engine, credentials=None):
        self.repo, self.engine = repository, engine
        self.settings = repository.settings
        self.credentials = credentials
        self.pump = None
        self.tasks = set()

    async def enqueue(self, run_id):
        if self.settings.report_dispatch != "cloud_tasks":
            return
        outbox = await self.repo.store.get("report_outbox", run_id)
        if not outbox or not outbox["pending"]:
            return
        from google.api_core.exceptions import AlreadyExists
        from google.cloud import tasks_v2
        from google.protobuf.duration_pb2 import Duration

        def dispatch():
            client = tasks_v2.CloudTasksClient(credentials=self.credentials)
            parent = client.queue_path(
                self.settings.google_cloud_project, self.settings.report_region, self.settings.report_queue
            )
            identity = hashlib.sha256(f"{run_id}:{outbox['delivery']}".encode()).hexdigest()
            try:
                client.create_task(
                    parent=parent,
                    task={
                        "name": f"{parent}/tasks/report-{identity}",
                        "dispatch_deadline": Duration(seconds=665),
                        "http_request": {
                            "http_method": tasks_v2.HttpMethod.POST,
                            "url": self.settings.report_worker_url.rstrip("/") + "/internal/reports/execute",
                            "headers": {"Content-Type": "application/json"},
                            "oidc_token": {
                                "service_account_email": self.settings.report_dispatch_service_account,
                                "audience": self.settings.report_worker_url.rstrip("/"),
                            },
                            "body": json.dumps({"run_id": run_id, "delivery": outbox["delivery"]}).encode(),
                        },
                    },
                    timeout=15,
                )
            except AlreadyExists:
                pass
            finally:
                client.transport.close()

        try:
            await asyncio.to_thread(dispatch)
        except Exception as exc:
            logger.warning("Report enqueue pending recovery (%s)", type(exc).__name__)
            return
        key = ("report_outbox", run_id)

        def acknowledge(docs):
            current = docs[key]
            if current and current["delivery"] == outbox["delivery"]:
                current["pending"] = False
                current["enqueued_at"] = time.time()
                return {key: current}, None
            return {}, None

        await self.repo.store.atomic([key], acknowledge)

    async def reconcile(self):
        if (await self.repo.store.get(*MAINTENANCE) or {}).get("active"):
            return {"maintenance": True}
        count = 0
        candidates = []
        for status in ("queued", "running", "waiting_input"):
            candidates.extend(await self.repo.store.list("report_runs", where=("status", status), limit=1000))
        for snapshot in candidates:
            run_id = snapshot["id"]
            key = ("report_runs", run_id)
            report_key = ("reports", snapshot["report_id"])
            slot = ("report_conversations", snapshot["conversation_id"])
            outkey = ("report_outbox", run_id)

            def recover(docs):
                run = docs[key]
                if not run or run["status"] in TERMINAL:
                    return {}, None
                stamp = time.time()
                abandoned = run["status"] == "running" and run["lease_until"] <= stamp
                exhausted = (
                    run["attempts"] >= 3 or run["budgets"]["seconds"] >= self.settings.report_timeout_seconds
                )
                expired = run.get("expires_at", float("inf")) <= stamp and run["status"] != "running"
                if (
                    (run["cancel_requested"] and (run["status"] != "running" or abandoned))
                    or ((abandoned or run["status"] == "queued") and exhausted)
                    or expired
                ):
                    run.update(
                        status="cancelled" if run["cancel_requested"] else "failed",
                        error="Cancelled."
                        if run["cancel_requested"]
                        else "Report expired or recovery budget exhausted; saved evidence is preserved.",
                        owner=None,
                        lease_until=0,
                    )
                    run["sequence"] += 1
                    report = docs[report_key]
                    report.update(active_run=None, status=run["status"], revision=report["revision"] + 1)
                    return {
                        key: run,
                        report_key: report,
                        slot: {"run_id": None},
                        outkey: {"id": run_id, "pending": False, "delivery": run["delivery"]},
                        (f"report_runs/{run_id}/events", str(run["sequence"])): {
                            "id": run["sequence"],
                            "type": run["status"],
                            "data": {"error": run["error"], "report_id": run["report_id"]},
                        },
                    }, None
                outbox = docs[outkey] or {}
                stranded = (
                    run["status"] == "queued"
                    and not outbox.get("pending", True)
                    and outbox.get("received_at", stamp) < stamp - 180
                )
                if stranded:
                    run["queue_recoveries"] = run.get("queue_recoveries", 0) + 1
                    if run["queue_recoveries"] >= 3:
                        run["expires_at"] = (
                            stamp  # Terminalized by the next sweep without consuming model quota.
                        )
                    run["delivery"] += 1
                    return {
                        key: run,
                        outkey: {"id": run_id, "pending": True, "delivery": run["delivery"]},
                    }, None
                if abandoned:
                    # Conservatively charge the remainder of the abandoned lease. Persisted work stays cached.
                    run["budgets"]["seconds"] += max(0, run["lease_until"] - run["tick_at"])
                    run.update(status="queued", delivery=run["delivery"] + 1, owner=None, lease_until=0)
                    return {
                        key: run,
                        outkey: {"id": run_id, "pending": True, "delivery": run["delivery"]},
                    }, None
                return {}, None

            await self.repo.store.atomic([key, report_key, slot, outkey, REGISTRY], recover)
            await self.enqueue(run_id)
            count += 1
        return {"checked": count}

    async def start(self):
        if self.settings.reports_enabled and self.settings.report_dispatch == "local":
            if self.settings.environment == "production":
                raise AppError("Local report dispatch is forbidden in production.", 503)
            self.pump = asyncio.create_task(self._local_loop(), name="local-report-pump")

    async def _local_loop(self):
        # Explicit application-lifetime development worker. Memory mode is intentionally ephemeral.
        tick = 0
        while True:
            try:
                if tick % 20 == 0:
                    await self.reconcile()
                async for run_id, run in self.repo.store.iter_documents("report_runs"):
                    if len(self.tasks) >= self.settings.report_concurrency:
                        break
                    if run["status"] == "queued" and not run["cancel_requested"]:
                        task = asyncio.create_task(self.engine.work(run_id, run["delivery"]))
                        self.tasks.add(task)

                        def finished(task):
                            self.tasks.discard(task)
                            if not task.cancelled() and task.exception():
                                logger.warning(
                                    "Local report worker awaiting recovery (%s)",
                                    type(task.exception()).__name__,
                                )

                        task.add_done_callback(finished)
                tick += 1
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                logger.warning("Local report pump (%s)", type(exc).__name__)
            await asyncio.sleep(0.5)

    async def close(self):
        if self.pump:
            self.pump.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.pump
        tasks = list(self.tasks)
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
