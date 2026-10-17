"""Public report library and guest-owned controls; downloads never invoke analysis."""

import asyncio
import json
import time
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request
from fastapi.responses import StreamingResponse

from app.errors import AppError
from app.maintenance import MAINTENANCE, check_maintenance
from app.report_models import (
    ReportClarification,
    ReportCreate,
    ReportMutation,
    ReportPatch,
    ReportRevisionCreate,
    ResearchRequest,
)
from app.report_repository import TERMINAL, public
from app.repository import now_iso

ReportId = Annotated[str, Path(pattern=r"^[a-f0-9]{32}$")]


def report_router(guest):
    router = APIRouter(prefix="/api/v1")

    def service(request):
        services = request.app.state.services
        if not services.settings.reports_enabled or services.settings.report_dispatch == "disabled":
            raise AppError("Advanced reports are not enabled in this environment.", 503, "reports_disabled")
        return services

    @router.get("/reports/config")
    async def configuration(request: Request):
        s = request.app.state.services.settings
        return {
            "enabled": s.reports_enabled and s.report_dispatch != "disabled",
            "research_enabled": s.report_research_enabled and s.ai_backend == "gemini",
            "mode": "cloud_tasks" if s.report_dispatch == "cloud_tasks" else "local-ephemeral",
            "target_minutes": "3–8",
            "timesfm": {
                "enabled": s.report_timesfm_enabled and s.report_timesfm_verified,
                "model": "TimesFM 3.0",
                "preview": True,
            },
        }

    @router.post("/conversations/{conversation_id}/reports", status_code=202)
    async def create(
        conversation_id: ReportId, body: ReportCreate, request: Request, guest_id=Depends(guest)
    ):
        s = service(request)
        run = await s.reports.create(conversation_id, guest_id, body)
        await s.report_dispatcher.enqueue(run["id"])
        return public(run)

    @router.get("/reports")
    async def listing(
        request: Request,
        deleted: bool = False,
        conversation_id: str | None = Query(default=None, pattern=r"^[a-f0-9]{32}$"),
    ):
        s = service(request)
        values = await s.store.list(
            "reports",
            limit=1000,
            where=("conversation_id", conversation_id)
            if conversation_id
            else ("recover_until", ">", time.time())
            if deleted
            else ("deleted", False),
            order_by="recover_until" if deleted and not conversation_id else None,
            descending=deleted and not conversation_id,
        )
        values = [
            public(v)
            for v in values
            if not v.get("kind")
            and v["deleted"] == deleted
            and (not deleted or v.get("recover_until", 0) > time.time())
        ]
        return {"reports": sorted(values, key=lambda v: v["updated_at"], reverse=True)[:1000]}

    @router.get("/reports/{report_id}")
    async def detail(report_id: ReportId, request: Request):
        s = service(request)
        value = await s.reports.get("reports", report_id)
        if value.get("kind"):
            raise AppError("Open this job from its planning library.", 404, "report_not_found")
        current = await s.reports.get("report_runs", value["active_run"]) if value["active_run"] else None
        return public(value) | {
            "active_run_id": value["active_run"],
            "run": public(current) if current else None,
        }

    @router.get("/reports/{report_id}/revisions")
    async def versions(report_id: ReportId, request: Request):
        s = service(request)
        report = await s.reports.get("reports", report_id)
        return {"versions": report["versions"]}

    @router.get("/reports/{report_id}/revisions/{version}")
    async def revision(report_id: ReportId, version: int, request: Request):
        value = await service(request).reports.get(f"reports/{report_id}/revisions", str(version))
        return {k: v for k, v in value.items() if k != "exports"} | {
            "downloads": {
                name: {k: v for k, v in meta.items() if k != "key"} for name, meta in value["exports"].items()
            }
        }

    @router.post("/reports/{report_id}/revisions", status_code=202)
    async def revise(
        report_id: ReportId, body: ReportRevisionCreate, request: Request, guest_id=Depends(guest)
    ):
        s = service(request)
        report = await s.reports.get("reports", report_id)
        run = await s.reports.create(report["conversation_id"], guest_id, body, report_id)
        await s.report_dispatcher.enqueue(run["id"])
        return public(run)

    async def mutate(s, report_id, expected, action, name=None):
        key = ("reports", report_id)
        capacity_key = ("system", "report_capacity")

        def update(docs):
            check_maintenance(docs[MAINTENANCE])
            report = docs[key]
            if not report:
                raise AppError("Report not found.", 404, "report_not_found")
            if report["revision"] != expected:
                raise AppError(
                    "Someone changed this report. Reload latest; your draft is preserved.",
                    409,
                    "report_conflict",
                )
            if report["active_run"]:
                raise AppError(
                    "Wait for this report to finish before changing library metadata.", 409, "report_busy"
                )
            capacity = (docs[capacity_key] or {}).get("count", 0)
            if action == "restore":
                if capacity >= s.settings.report_catalog_limit:
                    raise AppError(
                        "The report library is full. Delete an unused report before restoring.",
                        409,
                        "report_capacity",
                    )
                if not report["deleted"] or report.get("recover_until", 0) <= time.time():
                    raise AppError("This report is no longer recoverable.", 410, "report_expired")
                report.update(deleted=False, recover_until=None)
            elif report["deleted"]:
                raise AppError("Restore this report first.", 409, "report_deleted")
            elif action == "delete":
                report.update(deleted=True, recover_until=time.time() + 30 * 86400)
            else:
                report["name"] = name
            report.update(revision=report["revision"] + 1, updated_at=now_iso())
            updates = {key: report}
            if action in {"delete", "restore"}:
                updates[capacity_key] = {"count": max(0, capacity + (1 if action == "restore" else -1))}
            return updates, public(report)

        return await s.store.atomic([key, MAINTENANCE, capacity_key], update)

    @router.patch("/reports/{report_id}")
    async def rename(report_id: ReportId, body: ReportPatch, request: Request, guest_id=Depends(guest)):
        s = service(request)
        await s.repo.quota([(f"report_metadata_{guest_id}_{int(time.time() // 3600)}", 30)])
        return await mutate(s, report_id, body.expected_revision, "rename", body.name)

    @router.delete("/reports/{report_id}")
    async def delete(
        report_id: ReportId, request: Request, expected_revision: int = Query(ge=1), guest_id=Depends(guest)
    ):
        s = service(request)
        await s.repo.quota([(f"report_metadata_{guest_id}_{int(time.time() // 3600)}", 30)])
        return await mutate(s, report_id, expected_revision, "delete")

    @router.post("/reports/{report_id}/restore")
    async def restore(report_id: ReportId, body: ReportMutation, request: Request, guest_id=Depends(guest)):
        s = service(request)
        await s.repo.quota([(f"report_metadata_{guest_id}_{int(time.time() // 3600)}", 30)])
        return await mutate(s, report_id, body.expected_revision, "restore")

    @router.get("/report-runs/{run_id}")
    async def status(run_id: ReportId, request: Request):
        return public(await service(request).reports.get("report_runs", run_id))

    @router.get("/report-runs/{run_id}/controls")
    async def controls(run_id: ReportId, request: Request, guest_id=Depends(guest)):
        run = await service(request).reports.get("report_runs", run_id)
        return {"can_control": run["guest_id"] == guest_id, "clarifications": run["clarifications"]}

    @router.post("/report-runs/{run_id}/cancel")
    async def cancel(run_id: ReportId, request: Request, guest_id=Depends(guest)):
        s = service(request)
        result = await s.reports.cancel(run_id, guest_id)
        await s.report_dispatcher.reconcile()
        return result

    @router.post("/report-runs/{run_id}/clarifications", status_code=202)
    async def clarification(
        run_id: ReportId, body: ReportClarification, request: Request, guest_id=Depends(guest)
    ):
        s = service(request)
        value = await s.reports.clarify(run_id, guest_id, body)
        await s.report_dispatcher.enqueue(run_id)
        return value

    @router.get("/report-runs/{run_id}/events")
    async def events(run_id: ReportId, request: Request, after: int = Query(default=0, ge=0)):
        s = service(request)
        await s.reports.get("report_runs", run_id)
        try:
            after = max(after, int(request.headers.get("last-event-id", "0")))
        except ValueError:
            raise AppError("Invalid report event cursor.", 422)

        async def stream():
            cursor, heartbeat = after, time.monotonic()
            while not await request.is_disconnected():
                run = await s.reports.get("report_runs", run_id)
                for index in range(cursor + 1, run["sequence"] + 1):
                    event = await s.store.get(f"report_runs/{run_id}/events", str(index))
                    if not event:
                        raise AppError("Report event sequence is incomplete.", 409, "report_event_missing")
                    yield f"id: {index}\nevent: {event['type']}\ndata: {json.dumps(event['data'])}\n\n"
                    cursor = index
                if run["status"] in TERMINAL or run["status"] == "waiting_input":
                    break
                if time.monotonic() - heartbeat >= 15:
                    yield ": keepalive\n\n"
                    heartbeat = time.monotonic()
                await asyncio.sleep(0.5)

        return StreamingResponse(
            stream(),
            media_type="text/event-stream",
            headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
        )

    @router.get("/reports/{report_id}/revisions/{version}/downloads/{format}")
    async def download(report_id: ReportId, version: int, format: str, request: Request):
        s = service(request)
        revision = await s.reports.get(f"reports/{report_id}/revisions", str(version))
        metadata = revision["exports"].get(format)
        if not metadata:
            raise AppError("Choose PDF, Word, or all-data ZIP.", 404, "report_export_not_found")
        content = await s.report_exports.read(metadata)
        suffix = {"pdf": "pdf", "docx": "docx", "data": "zip"}[format]

        async def chunks():
            for offset in range(0, len(content), 65536):
                yield content[offset : offset + 65536]

        return StreamingResponse(
            chunks(),
            media_type=metadata["content_type"],
            headers={
                "Content-Disposition": f'attachment; filename="querylane-{report_id[:12]}-v{version}.{suffix}"',
                "X-Content-SHA256": metadata["sha256"],
                "Content-Length": str(len(content)),
            },
        )

    @router.post("/reports/research")
    async def research(body: ResearchRequest, request: Request, guest_id=Depends(guest)):
        from app.report_research import research_panel

        s = service(request)
        return await research_panel(s, guest_id, body)

    return router
