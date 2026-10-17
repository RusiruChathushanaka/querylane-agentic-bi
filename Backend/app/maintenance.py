"""Operator-only, reference-aware cleanup. Failed operations stay fenced for recovery."""

import asyncio
import time
import uuid

from app.errors import AppError
from app.repository import now_iso

MAINTENANCE = ("system", "history_maintenance")


def check_maintenance(value):
    if value and value.get("active"):
        raise AppError("Workspace maintenance is in progress. Retry shortly.", 503, "maintenance")


async def enter_maintenance(store, operation):
    owner = uuid.uuid4().hex

    def claim(docs):
        check_maintenance(docs[MAINTENANCE])
        return {
            MAINTENANCE: {"active": True, "operation": operation, "owner": owner, "started_at": now_iso()}
        }, owner

    return await store.atomic([MAINTENANCE], claim)


async def clear_maintenance(store, owner=None):
    def release(docs):
        current = docs[MAINTENANCE]
        if owner is not None and (not current or current.get("owner") != owner):
            raise AppError("Maintenance ownership changed.", 409, "maintenance_conflict")
        return {MAINTENANCE: {"active": False, "finished_at": now_iso()}}, None

    await store.atomic([MAINTENANCE], release)


async def wait_for_idle(store, timeout=660):
    deadline = time.monotonic() + timeout
    while True:
        active = False
        for collection in ("conversations", "skill_author_sessions", "report_runs"):
            async for _, value in store.iter_documents(collection):
                if (value.get("active_run") or value.get("status") == "running") and value.get(
                    "lease_until", 0
                ) > time.time():
                    active = True
                    break
        if not active:
            return
        if time.monotonic() >= deadline:
            raise AppError(
                "Active work did not drain. Maintenance remains fenced; inspect and recover explicitly.",
                409,
                "maintenance_busy",
            )
        await asyncio.sleep(min(1, max(0, deadline - time.monotonic())))


async def reset_history(store, *, timeout=660):
    owner = await enter_maintenance(store, "reset-history")
    # Do not clear the fence on failure: an operator must inspect an interrupted reset.
    await wait_for_idle(store, timeout)
    kept = set()
    async for artifact_id, ref in store.iter_documents("dashboard_artifact_refs"):
        if ref.get("count", 0) > 0:
            kept.add(artifact_id)
    async for artifact_id, ref in store.iter_documents("report_artifact_refs"):
        if ref.get("count", 0) > 0:
            kept.add(artifact_id)
    async for _, ref in store.iter_documents("planning_retention_refs"):
        if ref.get("expires_at", 0) > time.time():
            kept.add(ref["artifact_id"])
    removed = 0
    async for artifact_id, _ in store.iter_documents("artifacts"):
        if artifact_id not in kept:
            await store.delete_tree(f"artifacts/{artifact_id}")
            removed += 1
    for collection in (
        "conversations",
        "runs",
        "adk_sessions",
        "voice_resumptions",
        "quotas",
        "skill_author_sessions",
    ):
        await store.delete_tree(collection)
    await clear_maintenance(store, owner)
    return {"preserved_artifacts": len(kept), "removed_artifacts": removed}


async def purge_dashboards(store, *, timeout=660, now=None):
    owner = await enter_maintenance(store, "purge-dashboards")
    await wait_for_idle(store, timeout)
    stamp = time.time() if now is None else now
    removed = 0
    async for board_id, board in store.iter_documents("dashboards"):
        expired_board = board.get("deleted") and board.get("recover_until", float("inf")) <= stamp
        async for item_id, item in store.iter_documents(f"dashboards/{board_id}/items"):
            if not expired_board and not (
                item.get("removed") and item.get("recover_until", float("inf")) <= stamp
            ):
                continue
            item_key = (f"dashboards/{board_id}/items", item_id)
            ref_key = ("dashboard_artifact_refs", item["artifact_id"])

            def purge(docs):
                if not docs[MAINTENANCE] or docs[MAINTENANCE].get("owner") != owner:
                    raise AppError("Maintenance ownership changed.", 409)
                if not docs[item_key]:
                    return {}, None
                count = (docs[ref_key] or {}).get("count", 0)
                if count < 1:
                    raise AppError(
                        "Retained artifact references are inconsistent; inspect before purging.", 409
                    )
                return {
                    item_key: None,
                    ref_key: {"id": item["artifact_id"], "count": count - 1} if count > 1 else None,
                }, None

            await store.atomic([MAINTENANCE, item_key, ref_key], purge)
            removed += 1
        if expired_board:
            await store.delete_tree(f"dashboards/{board_id}")
    async for request_id, request in store.iter_documents("dashboard_requests"):
        if request.get("expires_at", float("inf")) <= stamp:
            await store.delete("dashboard_requests", request_id)
    await clear_maintenance(store, owner)
    return {"purged_items": removed}


async def purge_reports(store, exports, *, timeout=660, now=None):
    """Explicit operator purge after recovery expires; preserve dashboard references."""
    owner = await enter_maintenance(store, "purge-reports")
    await wait_for_idle(store, timeout)
    stamp, removed = time.time() if now is None else now, 0
    async for report_id, report in store.iter_documents("reports"):
        if report.get("kind"):
            continue  # Planning envelopes are purged by their own reference-aware maintenance.
        if not report.get("deleted") or report.get("recover_until", float("inf")) > stamp:
            continue
        if report.get("active_run"):
            raise AppError("Deleted report has active work. Inspect before purging.", 409)
        async for _, revision in store.iter_documents(f"reports/{report_id}/revisions"):
            for metadata in revision.get("exports", {}).values():
                await exports.delete(metadata)
        runs = await store.list("report_runs", where=("report_id", report_id), limit=1000)
        for run in runs:
            references = await store.list("report_artifact_refs", where=("run_id", run["id"]), limit=1000)
            for reference in references:
                artifact_id = reference["id"]
                ref_key = ("report_artifact_refs", artifact_id)

                def release(docs):
                    if not docs[MAINTENANCE] or docs[MAINTENANCE].get("owner") != owner:
                        raise AppError("Maintenance ownership changed.", 409)
                    current = docs[ref_key]
                    if current and current.get("run_id") != run["id"]:
                        raise AppError("Report evidence ownership is inconsistent.", 409)
                    return {ref_key: None}, None

                await store.atomic([MAINTENANCE, ref_key], release)
                dashboard_ref = await store.get("dashboard_artifact_refs", artifact_id)
                if not dashboard_ref or dashboard_ref.get("count", 0) < 1:
                    await store.delete_tree(f"artifacts/{artifact_id}")
            async for key, session in store.iter_documents("report_adk_sessions"):
                if session.get("id", "").startswith(f"report_{run['id']}_"):
                    await store.delete_tree(f"report_adk_sessions/{key}")
            await store.delete("report_outbox", run["id"])
            await store.delete_tree(f"report_runs/{run['id']}")
        await store.delete_tree(f"reports/{report_id}")
        await store.delete("plan_report_refs", report_id)
        removed += 1
    await clear_maintenance(store, owner)
    return {"purged_reports": removed}


async def purge_planning(store, exports, *, timeout=660, now=None):
    """Operator-only expiry; keep whole plan families referenced by saved public evidence."""
    owner = await enter_maintenance(store, "purge-planning")
    await wait_for_idle(store, timeout)
    stamp = time.time() if now is None else now
    retained_plans = set()
    async for _, ref in store.iter_documents("plan_report_refs"):
        retained_plans.add(ref["plan_id"])
    async for artifact_id, ref in store.iter_documents("dashboard_artifact_refs"):
        if ref.get("count", 0) > 0:
            artifact = await store.get("artifacts", artifact_id)
            if artifact and artifact.get("forecast_plan_id"):
                retained_plans.add(artifact["forecast_plan_id"])
    removed = {"dashboard_builds": 0, "forecast_plans": 0}
    for collection in removed:
        async for root_id, root in store.iter_documents(collection):
            expired = (
                root.get("deleted") and (root.get("recover_until") or float("inf")) <= stamp
                if collection == "forecast_plans"
                else root.get("status") != "published" and root.get("expires_at", float("inf")) <= stamp
            )
            if not expired or root_id in retained_plans:
                continue
            runs = await store.list("report_runs", where=("root_id", root_id), limit=1000)
            if any(r["status"] == "running" and r.get("lease_until", 0) > time.time() for r in runs):
                raise AppError("Planning work has not drained; maintenance remains fenced.", 409)
            async for _, revision in store.iter_documents(f"{collection}/{root_id}/revisions"):
                for metadata in revision.get("exports", {}).values():
                    await exports.delete(metadata)
            for run in runs:
                async for ref_id, ref in store.iter_documents("planning_retention_refs"):
                    if ref.get("run_id") == run["id"]:
                        await store.delete("planning_retention_refs", ref_id)
                refs = await store.list("report_artifact_refs", where=("run_id", run["id"]), limit=1000)
                for ref in refs:
                    aid = ref["id"]
                    dashboard = await store.get("dashboard_artifact_refs", aid)
                    other = await store.list(
                        "planning_retention_refs", where=("artifact_id", aid), limit=1000
                    )
                    await store.delete("report_artifact_refs", aid)
                    if not (dashboard and dashboard.get("count", 0) > 0) and not any(
                        r.get("expires_at", 0) > stamp for r in other
                    ):
                        await store.delete_tree(f"artifacts/{aid}")
                await store.delete("report_outbox", run["id"])
                await store.delete("report_conversations", run["id"])
                await store.delete_tree(f"reports/{run['id']}")
                await store.delete_tree(f"report_runs/{run['id']}")
            key, capacity = (collection, root_id), ("system", collection + "_capacity")

            def release(docs):
                if not docs[MAINTENANCE] or docs[MAINTENANCE].get("owner") != owner:
                    raise AppError("Maintenance ownership changed.", 409)
                if not docs[key]:
                    return {}, None
                return {
                    key: None,
                    capacity: {"count": max(0, (docs[capacity] or {}).get("count", 0) - 1)},
                }, None

            await store.atomic([key, capacity, MAINTENANCE], release)
            await store.delete_tree(f"{collection}/{root_id}")
            removed[collection] += 1
    await clear_maintenance(store, owner)
    return removed
