"""Public saved plans, guest-owned proposals, explicit publication and adjustment versions."""

import copy
import hashlib
import json
import time
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response

from app.dashboards import artifact_summary, item_identity
from app.errors import AppError
from app.hierarchy import adjust_plan
from app.maintenance import MAINTENANCE, check_maintenance
from app.planning_engine import plan_artifact, plan_report
from app.planning_models import PlanAdjustment, PlanningAction, PlanningCreate, ProposalWrite
from app.report_exports import FORMATS, render
from app.report_repository import public
from app.repository import now_iso
from app.timesfm import digest


def root_public(value):
    return {k: v for k, v in value.items() if k not in {"guest_id", "previous_dashboard", "fingerprint"}}


class Planning:
    def __init__(self, services):
        self.s, self.store, self.repo = services, services.store, services.reports

    async def create(self, kind, guest, body):
        if (
            not self.s.settings.planning_enabled
            or not self.s.settings.reports_enabled
            or self.s.settings.report_dispatch == "disabled"
        ):
            raise AppError("Background analysis is disabled.", 503, "reports_disabled")
        run_id = digest([kind, guest, body.request_id])[:32]
        existing = await self.store.get("report_runs", run_id)
        if existing:
            if existing["fingerprint"] != digest(body.model_dump(mode="json")):
                raise AppError("Request ID already used.", 409, "idempotency_conflict")
            return public(existing)
        captures = {}
        if body.dashboard_id:
            if kind != "dashboard":
                raise AppError("Choose a forecast planning scope.", 422, "planning_invalid")
            board = await self.s.dashboards.detail(body.dashboard_id)
            if board["deleted"] or board["revision"] != body.expected_revision:
                raise AppError("Dashboard changed. Reload before building.", 409, "dashboard_conflict")
            captures["base_dashboard"] = board
        if kind == "forecast":
            if self.s.settings.data_profile != "timeseries" or not body.metric or body.source == "postgres":
                raise AppError(
                    "Choose a published revenue metric and the timeseries BigQuery source.",
                    422,
                    "hierarchy_metric",
                )
            captures["metric_snapshot"] = await self.s.metrics.snapshot(body.metric.id, body.metric.version)
        captures["metric_snapshots"] = await self.s.metrics.resolve(body.objective, body.source)
        # Resolve and validate attachments before charging admission; immutable bodies are captured.
        skills = []
        for sid in body.skill_ids:
            skill = await self.s.analysis.skills.get(sid)
            if (
                skill.get("deleted")
                or not skill.get("enabled")
                or (body.source != "all" and skill["source"] not in {"all", body.source})
            ):
                raise AppError(
                    "Remove unavailable or incompatible attached skills.", 409, "skill_unavailable"
                )
            skills.append(skill | {"mode": "manual"})
        captures["manual_skills"] = skills
        if len(json.dumps(captures).encode()) > 196608:
            raise AppError(
                "Selected definitions and skills exceed the captured context budget.", 422, "planning_context"
            )
        run = await self.repo.create_job(kind, guest, body, captures)
        await self.s.report_dispatcher.enqueue(run["id"])
        return public(run)

    async def build(self, run_id, guest):
        run = await self.repo.owned(run_id, guest)
        if run.get("kind") != "dashboard":
            raise AppError("Dashboard build not found.", 404, "planning_not_found")
        root = await self.repo.get("dashboard_builds", run["root_id"])
        if root.get("expires_at", float("inf")) <= time.time() and root["status"] != "published":
            raise AppError("Unpublished proposal expired after seven days.", 410, "proposal_expired")
        return root

    async def save_proposal(self, run_id, guest, body):
        req = ("planning_requests", digest([guest, body.request_id]))
        fingerprint = digest(["proposal", run_id, body.model_dump()])
        prior = await self.store.get(*req)
        if prior:
            if prior["fingerprint"] != fingerprint:
                raise AppError("Request ID already used.", 409, "idempotency_conflict")
            return prior["result"]
        root = await self.build(run_id, guest)
        run = await self.repo.get("report_runs", run_id)
        if run["status"] != "complete":
            raise AppError("Wait for the saved proposal to finish.", 409, "planning_busy")
        board = (
            await self.s.dashboards.detail(root["dashboard_id"])
            if body.rebase and root.get("dashboard_id")
            else None
        )
        cards = [c.model_dump(mode="json") for c in body.cards]
        if board:
            by_id = {c["artifact_id"]: c for c in cards}
            current = [
                {k: i[k] for k in ("artifact_id", "title", "note", "width", "view")} | {"reused": True}
                for i in board["items"]
            ]
            cards = [by_id.pop(c["artifact_id"], c) for c in current] + list(by_id.values())
        if len(cards) > 20 or len({c["artifact_id"] for c in cards}) != len(cards):
            raise AppError("Use at most twenty distinct saved artifacts.", 422, "proposal_invalid")
        for card in cards:
            from app.dashboard_models import ChartViewState

            await self.s.dashboards.validated(
                card["artifact_id"], ChartViewState.model_validate(card["view"])
            )
        key = ("dashboard_builds", run_id)

        def update(docs):
            check_maintenance(docs[MAINTENANCE])
            if docs[req]:
                if docs[req]["fingerprint"] != fingerprint:
                    raise AppError("Request ID already used.", 409, "idempotency_conflict")
                return {}, docs[req]["result"]
            value = docs[key]
            if value["revision"] != body.expected_revision or value["status"] != "review":
                raise AppError("Proposal changed. Your draft is preserved.", 409, "planning_conflict")
            value.update(
                proposal={
                    "name": body.name,
                    "description": body.description,
                    "cards": cards,
                    "omitted": value["proposal"]["omitted"],
                },
                revision=value["revision"] + 1,
                updated_at=now_iso(),
            )
            if board:
                value["base_revision"] = board["revision"]
                value["base_cards"] = current
            result = root_public(value)
            return {key: value, req: {"fingerprint": fingerprint, "result": result}}, result

        return await self.store.atomic([key, req, MAINTENANCE], update)

    async def publish(self, run_id, guest, body, undo=False):
        root = await self.build(run_id, guest)
        run = await self.repo.get("report_runs", run_id)
        if run["status"] != "complete":
            raise AppError("Wait for the proposal worker to finish.", 409, "planning_busy")
        request_key = ("dashboard_build_requests", digest([guest, body.request_id]))
        fingerprint = digest([run_id, body.model_dump(), undo])
        prior = await self.store.get(*request_key)
        if prior:
            if prior["fingerprint"] != fingerprint:
                raise AppError("Request ID already used.", 409, "idempotency_conflict")
            return prior["result"]
        board_id = root.get("dashboard_id") or run_id
        old_items = await self.store.list(f"dashboards/{board_id}/items", limit=40)
        old_by_id = {i["id"]: i for i in old_items}
        proposal = root["previous_dashboard"] if undo else root["proposal"]
        cards = proposal["cards"]
        validated = {}
        from app.dashboard_models import ChartViewState

        for card in cards:
            artifact, view = await self.s.dashboards.validated(
                card["artifact_id"], ChartViewState.model_validate(card["view"])
            )
            validated[card["artifact_id"]] = (artifact, view)
        key, bkey, capacity = (
            ("dashboard_builds", run_id),
            ("dashboards", board_id),
            ("system", "dashboards_capacity"),
        )
        stamp = datetime.now(UTC).strftime("%Y%m%d%H")
        quota_keys = [
            ("quotas", f"dashboard_guest_{guest}_{stamp}"),
            ("quotas", f"dashboard_workspace_{stamp[:8]}"),
        ]
        itemkeys = {(f"dashboards/{board_id}/items", item_identity(c["artifact_id"])) for c in cards} | {
            (f"dashboards/{board_id}/items", i["id"]) for i in old_items
        }
        refkeys = {("dashboard_artifact_refs", c["artifact_id"]) for c in cards}
        artifactkeys = {("artifacts", c["artifact_id"]) for c in cards}

        def commit(docs):
            if docs[request_key]:
                if docs[request_key]["fingerprint"] != fingerprint:
                    raise AppError("Request ID already used.", 409, "idempotency_conflict")
                return {}, docs[request_key]["result"]
            check_maintenance(docs[MAINTENANCE])
            value, current = docs[key], docs[bkey]
            if value["revision"] != body.expected_revision or value["status"] != (
                "published" if undo else "review"
            ):
                raise AppError("Proposal changed. Reload it before publishing.", 409, "planning_conflict")
            expected = value.get("published_dashboard_revision") if undo else value.get("base_revision")
            if (current and (current["deleted"] or current["revision"] != expected)) or (
                not current and expected is not None
            ):
                raise AppError(
                    "Dashboard changed. Rebase the proposal before publishing or restoring.",
                    409,
                    "dashboard_conflict",
                )
            updates = {}
            for q, limit in zip(
                quota_keys,
                (
                    self.s.settings.dashboard_guest_hourly_limit,
                    self.s.settings.dashboard_workspace_daily_limit,
                ),
            ):
                count = (docs[q] or {}).get("count", 0)
                if count >= limit:
                    raise AppError("Dashboard mutation limit reached.", 429, "dashboard_usage_limit")
                updates[q] = {"count": count + 1}
            if not current:
                count = (docs[capacity] or {}).get("count", 0)
                if count >= self.s.settings.dashboard_limit:
                    raise AppError("Dashboard library is full.", 409, "dashboard_capacity")
                updates[capacity] = {"count": count + 1}
                current = {
                    "id": board_id,
                    "revision": 0,
                    "item_ids": [],
                    "created_at": now_iso(),
                    "created_by": guest,
                    "deleted": False,
                    "visibility": "public",
                }
            if not undo:
                value["previous_dashboard"] = {
                    "name": current.get("name", "Before AI build"),
                    "description": current.get("description", ""),
                    "cards": [
                        {k: old_by_id[i][k] for k in ("artifact_id", "title", "note", "width", "view")}
                        for i in current["item_ids"]
                    ],
                }
            chosen = [item_identity(c["artifact_id"]) for c in cards]
            for item_id in current["item_ids"]:
                if item_id not in chosen:
                    ik = (f"dashboards/{board_id}/items", item_id)
                    item = docs[ik]
                    item.update(
                        removed=True,
                        previous_position=current["item_ids"].index(item_id),
                        recover_until=time.time() + 30 * 86400,
                    )
                    updates[ik] = item
            sources = {}
            for card in cards:
                aid, item_id = card["artifact_id"], item_identity(card["artifact_id"])
                artifact, view = validated[aid]
                if docs[("artifacts", aid)] != artifact:
                    raise AppError("Saved evidence changed during publication.", 409, "artifact_unavailable")
                ik, ref = (f"dashboards/{board_id}/items", item_id), ("dashboard_artifact_refs", aid)
                previous = docs[ik]
                if not previous:
                    updates[ref] = {"id": aid, "count": (docs[ref] or {}).get("count", 0) + 1}
                item = {
                    "id": item_id,
                    "artifact_id": aid,
                    "conversation_id": artifact["conversation_id"],
                    "summary": artifact_summary(artifact),
                    "title": card["title"],
                    "note": card.get("note", ""),
                    "width": card.get("width", "standard"),
                    "view": view,
                    "created_at": (previous or {}).get("created_at", now_iso()),
                    "pinned_at": now_iso(),
                    "updated_at": now_iso(),
                    "created_by": guest,
                    "removed": False,
                    "recover_until": None,
                }
                updates[ik] = item
                for source in item["summary"]["sources"]:
                    sources[source] = sources.get(source, 0) + 1
            current.update(
                name=proposal["name"],
                description=proposal["description"],
                item_ids=chosen,
                card_count=len(chosen),
                sources=list(sources),
                source_counts=sources,
                revision=current["revision"] + 1,
                updated_at=now_iso(),
                updated_by=guest,
            )
            value.update(
                status="undone" if undo else "published",
                dashboard_id=board_id,
                published_dashboard_revision=current["revision"],
                revision=value["revision"] + 1,
            )
            result = {
                "dashboard_id": board_id,
                "dashboard_revision": current["revision"],
                "build": root_public(value),
            }
            updates.update(
                {key: value, bkey: current, request_key: {"fingerprint": fingerprint, "result": result}}
            )
            return updates, result

        return await self.store.atomic(
            [key, bkey, capacity, request_key, MAINTENANCE, *itemkeys, *refkeys, *artifactkeys, *quota_keys],
            commit,
        )

    async def version(self, plan_id, version=None):
        root = await self.repo.get("forecast_plans", plan_id)
        version = version or root.get("latest_version")
        if not version or version not in root["versions"]:
            raise AppError("Forecast plan version not found.", 404, "plan_version_not_found")
        return await self.repo.get(f"forecast_plans/{plan_id}/revisions", str(version))

    async def metadata(self, plan_id, guest, body, action):
        key = ("forecast_plans", plan_id)
        req = ("planning_requests", digest([guest, body.request_id]))
        fingerprint = digest([plan_id, action, body.model_dump()])
        quota = ("quotas", f"planning_metadata_{guest}_{int(time.time() // 3600)}")

        def update(docs):
            check_maintenance(docs[MAINTENANCE])
            if docs[req]:
                if docs[req]["fingerprint"] != fingerprint:
                    raise AppError("Request ID already used.", 409, "idempotency_conflict")
                return {}, docs[req]["result"]
            count = (docs[quota] or {}).get("count", 0)
            if count >= 30:
                raise AppError("Planning metadata limit reached.", 429, "usage_limit")
            root = docs[key]
            if not root or root["revision"] != body.expected_revision:
                raise AppError("Plan changed. Your draft is preserved.", 409, "planning_conflict")
            if root.get("active_run"):
                run = docs.get(("report_runs", root["active_run"]))
                if run and run["status"] in {"failed", "cancelled", "complete"}:
                    root["active_run"] = None
                else:
                    raise AppError(
                        "Cancel or finish active computation before changing the library.",
                        409,
                        "planning_busy",
                    )
            if action == "restore":
                if not root["deleted"] or root.get("recover_until", 0) <= time.time():
                    raise AppError("Plan recovery expired.", 410, "planning_expired")
                root.update(deleted=False, recover_until=None)
            elif root["deleted"]:
                raise AppError("Restore the plan before editing.", 409, "planning_deleted")
            elif action == "delete":
                root.update(deleted=True, recover_until=time.time() + 30 * 86400)
            else:
                if not body.name or not body.name.strip():
                    raise AppError("Enter a plan name.", 422, "planning_invalid")
                root["name"] = body.name.strip()
            root.update(revision=root["revision"] + 1, updated_at=now_iso())
            result = root_public(root)
            return {
                key: root,
                req: {"fingerprint": fingerprint, "result": result},
                quota: {"count": count + 1},
            }, result

        captured = await self.repo.get("forecast_plans", plan_id)
        return await self.store.atomic(
            [
                key,
                req,
                quota,
                MAINTENANCE,
                *([("report_runs", captured["active_run"])] if captured.get("active_run") else []),
            ],
            update,
        )

    async def adjustment(self, plan_id, guest, body):
        root = await self.repo.get("forecast_plans", plan_id)
        base = await self.version(plan_id, body.base_version)
        request_key = ("planning_requests", digest([guest, body.request_id]))
        fingerprint = digest([plan_id, body.model_dump()])
        prior = await self.store.get(*request_key)
        if prior:
            if prior["fingerprint"] != fingerprint:
                raise AppError("Request ID already used.", 409, "idempotency_conflict")
            return prior["result"]
        doc = adjust_plan(base["document"], body.node_id, body.operation, body.value, body.reason)
        doc.update(version=root["next_version"], created_at=now_iso())
        doc["artifact_ids"] = []
        doc["company_artifact_id"] = None
        doc["base_version"] = body.base_version
        key, revkey = (
            ("forecast_plans", plan_id),
            (f"forecast_plans/{plan_id}/revisions", str(doc["version"])),
        )

        # Publish immutable data first; exports are generated lazily from this exact version.
        def commit(docs):
            check_maintenance(docs[MAINTENANCE])
            if docs[request_key]:
                if docs[request_key]["fingerprint"] != fingerprint:
                    raise AppError("Request ID already used.", 409, "idempotency_conflict")
                return {}, docs[request_key]["result"]
            current = docs[key]
            if (
                current["revision"] != body.expected_revision
                or current.get("active_run")
                or current["deleted"]
                or docs[revkey]
            ):
                raise AppError(
                    "Plan changed. Reload before saving your adjustment.", 409, "planning_conflict"
                )
            if len(current["versions"]) >= 20:
                raise AppError("Plan version limit reached.", 409, "planning_capacity")
            current.update(
                versions=current["versions"] + [doc["version"]],
                latest_version=doc["version"],
                next_version=doc["version"] + 1,
                revision=current["revision"] + 1,
                updated_at=now_iso(),
            )
            value = {"version": doc["version"], "document": doc, "exports": {}}
            return {
                key: current,
                revkey: value,
                request_key: {"fingerprint": fingerprint, "result": {"version": doc["version"]}},
            }, {"version": doc["version"]}

        return await self.store.atomic([key, revkey, request_key, MAINTENANCE], commit)

    async def node_artifact(self, plan_id, version, node_id):
        doc = (await self.version(plan_id, version))["document"]
        if node_id not in doc["history"]["nodes"]:
            raise AppError("Hierarchy node not found.", 404, "planning_node")
        artifact, rows = plan_artifact(doc, node_id)
        key, page = ("artifacts", artifact["id"]), (f"artifacts/{artifact['id']}/pages", "0")
        ref = ("report_artifact_refs", artifact["id"])
        artifact.update(page_count=1, report_run_id=doc["run_id"])

        def commit(docs):
            check_maintenance(docs[MAINTENANCE])
            if docs[key]:
                return {}, docs[key]
            return {
                key: artifact,
                page: {"index": 0, "rows": rows},
                ref: {"id": artifact["id"], "run_id": doc["run_id"], "count": 1},
            }, artifact

        return await self.store.atomic([key, page, ref, MAINTENANCE], commit)

    async def download(self, plan_id, version, fmt):
        if fmt not in {"pdf", "data", "json"}:
            raise AppError("Choose PDF, CSV ZIP or JSON.", 422, "planning_format")
        saved = await self.version(plan_id, version)
        if fmt in saved["exports"]:
            metadata = saved["exports"][fmt]
            return await self.s.report_exports.read(metadata), metadata["content_type"]
        doc = copy.deepcopy(saved["document"])
        artifact, rows = plan_artifact(doc, "company")
        full, all_rows = plan_artifact(doc)
        doc.update(artifact_ids=[artifact["id"], full["id"]], company_artifact_id=artifact["id"])
        # Bounded renderer process, saved observations only. Concurrent downloads share admission.
        async with self.s.dashboards.slots:
            files = await render(
                plan_report(doc), {artifact["id"]: (artifact, rows), full["id"]: (full, all_rows)}
            )
        if fmt == "json":
            manifest = doc | {
                "export_checksums": {
                    name: hashlib.sha256(files[name]).hexdigest() for name in ("pdf", "data")
                },
                "checksum_note": "The manifest does not recursively embed its own checksum.",
            }
            return json.dumps(manifest, sort_keys=True, indent=2).encode(), "application/json"
        return files[fmt], FORMATS[fmt][0]


def planning_router(guest):
    router = APIRouter(prefix="/api/v1")

    def service(request):
        return request.app.state.services.planning

    @router.post("/dashboard-builds", status_code=202)
    async def create_build(body: PlanningCreate, request: Request, guest_id=Depends(guest)):
        return await service(request).create("dashboard", guest_id, body)

    @router.get("/dashboard-builds")
    async def builds(request: Request, guest_id=Depends(guest)):
        runs = await request.app.state.services.store.list(
            "report_runs", where=("guest_id", guest_id), limit=1000
        )
        return {"builds": [public(r) for r in runs if r.get("kind") == "dashboard"]}

    @router.get("/dashboard-builds/{run_id}")
    async def build(run_id: str, request: Request, guest_id=Depends(guest)):
        root = await service(request).build(run_id, guest_id)
        run = await request.app.state.services.reports.get("report_runs", run_id)
        return root_public(root) | {"run": public(run)}

    @router.patch("/dashboard-builds/{run_id}")
    async def save(run_id: str, body: ProposalWrite, request: Request, guest_id=Depends(guest)):
        return await service(request).save_proposal(run_id, guest_id, body)

    @router.post("/dashboard-builds/{run_id}/publish")
    async def publish(run_id: str, body: PlanningAction, request: Request, guest_id=Depends(guest)):
        return await service(request).publish(run_id, guest_id, body)

    @router.post("/dashboard-builds/{run_id}/undo")
    async def undo(run_id: str, body: PlanningAction, request: Request, guest_id=Depends(guest)):
        return await service(request).publish(run_id, guest_id, body, undo=True)

    @router.post("/forecast-plans", status_code=202)
    async def create_plan(body: PlanningCreate, request: Request, guest_id=Depends(guest)):
        return await service(request).create("forecast", guest_id, body)

    @router.get("/forecast-plans")
    async def plans(request: Request, deleted: bool = False):
        s = request.app.state.services
        roots = await s.store.list("forecast_plans", where=("deleted", deleted), limit=1000)
        values = []
        for root in roots:
            if deleted and root.get("recover_until", 0) <= time.time():
                continue
            run = await s.store.get("report_runs", root["active_run"]) if root.get("active_run") else None
            values.append(root_public(root) | {"run": public(run) if run else None})
        return {"plans": sorted(values, key=lambda v: v["updated_at"], reverse=True)}

    @router.get("/forecast-plans/{plan_id}")
    async def plan(plan_id: str, request: Request):
        s = request.app.state.services
        root = await s.reports.get("forecast_plans", plan_id)
        run = await s.store.get("report_runs", root["active_run"]) if root.get("active_run") else None
        return root_public(root) | {"run": public(run) if run else None}

    @router.patch("/forecast-plans/{plan_id}")
    async def rename(plan_id: str, body: PlanningAction, request: Request, guest_id=Depends(guest)):
        return await service(request).metadata(plan_id, guest_id, body, "rename")

    @router.delete("/forecast-plans/{plan_id}")
    async def delete(plan_id: str, body: PlanningAction, request: Request, guest_id=Depends(guest)):
        return await service(request).metadata(plan_id, guest_id, body, "delete")

    @router.post("/forecast-plans/{plan_id}/restore")
    async def restore(plan_id: str, body: PlanningAction, request: Request, guest_id=Depends(guest)):
        return await service(request).metadata(plan_id, guest_id, body, "restore")

    @router.get("/forecast-plans/{plan_id}/revisions")
    async def revisions(plan_id: str, request: Request):
        root = await request.app.state.services.reports.get("forecast_plans", plan_id)
        return {"versions": root["versions"]}

    @router.get("/forecast-plans/{plan_id}/revisions/{version}")
    async def version(plan_id: str, version: int, request: Request):
        saved = await service(request).version(plan_id, version)
        return {
            "version": saved["version"],
            "document": saved["document"],
            "downloads": {k: {f: v for f, v in m.items() if f != "key"} for k, m in saved["exports"].items()},
        }

    @router.post("/forecast-plans/{plan_id}/revisions", status_code=202)
    async def recompute(plan_id: str, body: PlanningCreate, request: Request, guest_id=Depends(guest)):
        return await service(request).create(
            "forecast", guest_id, body.model_copy(update={"base_plan_id": plan_id})
        )

    @router.post("/forecast-plans/{plan_id}/adjustments")
    async def adjust(plan_id: str, body: PlanAdjustment, request: Request, guest_id=Depends(guest)):
        return await service(request).adjustment(plan_id, guest_id, body)

    @router.post("/forecast-plans/{plan_id}/revisions/{version}/artifacts/{node_id}")
    async def artifact(plan_id: str, version: int, node_id: str, request: Request, guest_id=Depends(guest)):
        return await service(request).node_artifact(plan_id, version, node_id)

    @router.get("/forecast-plans/{plan_id}/revisions/{version}/downloads/{fmt}")
    async def download(plan_id: str, version: int, fmt: str, request: Request):
        content, mime = await service(request).download(plan_id, version, fmt)
        extension = "zip" if fmt == "data" else fmt
        return Response(
            content,
            media_type=mime,
            headers={"Content-Disposition": f'attachment; filename="forecast-plan-{version}.{extension}"'},
        )

    return router
