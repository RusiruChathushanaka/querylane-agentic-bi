"""Public saved-result dashboards. No connector, agent, or executable configuration access."""

import asyncio
import hashlib
import json
import time
import uuid
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request
from fastapi.responses import Response

from app.chart_presentation import NUMERIC, metadata, present, saved_rows
from app.dashboard_models import (
    DashboardAction,
    DashboardCreate,
    DashboardItemPatch,
    DashboardLayout,
    DashboardPatch,
    DashboardPin,
)
from app.errors import AppError
from app.maintenance import MAINTENANCE, check_maintenance
from app.repository import now_iso

DashboardId = Annotated[str, Path(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")]

SUMMARY_FIELDS = [
    "id",
    "name",
    "description",
    "revision",
    "item_ids",
    "card_count",
    "sources",
    "created_at",
    "updated_at",
    "deleted",
    "recover_until",
    "visibility",
]


def public(value):
    return {k: v for k, v in value.items() if k not in {"created_by", "updated_by"}}


def item_identity(artifact_id):
    return hashlib.sha256(artifact_id.encode()).hexdigest()[:32]


def artifact_summary(artifact):
    return {
        key: artifact.get(key)
        for key in [
            "id",
            "title",
            "created_at",
            "row_count",
            "complete",
            "data_profile",
            "question",
            "analysis_id",
        ]
    } | {
        "sources": list(dict.fromkeys(p["source"] for p in artifact["provenance"])),
        "executed_at": [p["executed_at"] for p in artifact["provenance"]],
    }


def validate_view(artifact, rows, view):
    spec = metadata(artifact["visualization"], artifact["columns"], rows)
    numeric = [c["name"] for c in artifact["columns"] if NUMERIC.search(c["type"])]
    value = view.model_dump(mode="json")
    if (
        view.primary
        and view.primary not in numeric
        or not set(view.visible_measures) <= set(numeric)
        or any(field is not None and field not in numeric for field in (view.scatter_x, view.scatter_y))
    ):
        raise AppError(
            "View fields must reference numeric columns in this saved result.", 422, "dashboard_view_invalid"
        )
    if view.view == "kpi" and (artifact["row_count"] != 1 or not numeric):
        raise AppError(
            "KPI view requires one saved row with numeric measures.", 422, "dashboard_view_invalid"
        )
    if view.view == "kpi" and not view.visible_measures:
        raise AppError("Choose at least one KPI measure.", 422, "dashboard_view_invalid")
    if view.view not in {"table", "kpi"}:
        if not rows or not numeric or not spec["x"]:
            raise AppError("This saved result requires table view.", 422, "dashboard_view_invalid")
        fields = set(spec["y"])
        if not view.visible_measures or not set(view.visible_measures) <= fields:
            raise AppError("Choose visible measures from this saved result.", 422, "dashboard_view_invalid")
        if view.primary and view.primary not in fields:
            raise AppError("The primary measure is unavailable.", 422, "dashboard_view_invalid")
        if view.view == "scatter" and (view.scatter_x not in numeric or view.scatter_y not in numeric):
            raise AppError("Choose valid numeric scatter axes.", 422, "dashboard_view_invalid")
        prepared = present(
            artifact,
            rows,
            start=view.start,
            end=view.end,
            primary=view.primary,
            order=view.order,
            top=view.top,
            view=view.view,
        )
        if view.view == "pie" and not prepared["composition"]:
            raise AppError(
                "This view is not a valid complete composition. Choose bars or table.",
                422,
                "dashboard_view_invalid",
            )
        if prepared.get("warning") and not prepared["rows"]:
            raise AppError(prepared["warning"], 422, "dashboard_view_invalid")
        value["primary"] = prepared["primary"]
    elif view.start or view.end:
        # A table export always represents the whole saved result, not a hidden date filter.
        raise AppError("Table and KPI views do not save a chart date filter.", 422, "dashboard_view_invalid")
    return value


class Dashboards:
    def __init__(self, store, settings, slots=None):
        self.store, self.settings = store, settings
        self.slots = slots or asyncio.Semaphore(2)
        self.export_slot = asyncio.Semaphore(1)

    async def get(self, board_id):
        value = await self.store.get("dashboards", board_id)
        if not value:
            raise AppError("Dashboard not found.", 404, "dashboard_not_found")
        return value

    async def list(self, deleted=False):
        values = await self.store.list(
            "dashboards",
            limit=10000 if deleted else self.settings.dashboard_limit,
            where=("recover_until", ">", time.time()) if deleted else ("deleted", False),
            order_by="recover_until" if deleted else None,
            descending=deleted,
            fields=SUMMARY_FIELDS,
        )
        return sorted(
            [public(v) for v in values if not deleted or v.get("recover_until", 0) > time.time()],
            key=lambda v: (v["updated_at"], v["id"]),
            reverse=True,
        )

    async def detail(self, board_id):
        board = await self.get(board_id)
        items = []
        for item_id in board["item_ids"]:
            value = await self.store.get(f"dashboards/{board_id}/items", item_id)
            if value is None or value.get("removed"):
                raise AppError(
                    "Dashboard layout is inconsistent. Reload or contact the administrator.",
                    409,
                    "dashboard_inconsistent",
                )
            items.append(
                public(value)
                | {
                    "conversation_available": bool(
                        await self.store.get("conversations", value["conversation_id"])
                    )
                }
            )
        # Avoid returning an interleaved layout during a concurrent update.
        latest = await self.get(board_id)
        if latest["revision"] != board["revision"]:
            raise AppError("The dashboard changed while loading. Reload it.", 409, "dashboard_conflict")
        return public(board) | {"items": items}

    async def removed(self, board_id, offset=0):
        await self.get(board_id)
        # Range and ordering share one field's automatic index, excluding old tombstones.
        values = await self.store.list(
            f"dashboards/{board_id}/items",
            limit=10000,
            where=("recover_until", ">", time.time()),
            order_by="recover_until",
            descending=True,
        )
        values = sorted(
            [public(v) for v in values if v.get("recover_until", 0) > time.time()],
            key=lambda v: v["updated_at"],
            reverse=True,
        )
        return {
            "items": values[offset : offset + 20],
            "next_offset": offset + 20 if len(values) > offset + 20 else None,
        }

    async def validated(self, artifact_id, view):
        async with self.slots:
            artifact = await self.store.get("artifacts", artifact_id)
            if not artifact:
                raise AppError("This saved result is unavailable.", 404, "artifact_not_found")
            rows = [r async for r in saved_rows(self.store, artifact)]
            normalized = await asyncio.to_thread(validate_view, artifact, rows, view)
            return artifact, normalized

    async def mutate(self, guest_id, action, body, board_id=None, item_id=None):
        payload = body.model_dump(mode="json")
        request_key = (
            "dashboard_requests",
            hashlib.sha256(f"{guest_id}:{body.request_id}".encode()).hexdigest(),
        )
        fingerprint = hashlib.sha256(
            json.dumps([action, board_id, item_id, payload], sort_keys=True).encode()
        ).hexdigest()
        # Short-circuit exact retries before artifact reads; reset may have removed the source chat.
        prior = await self.store.get(*request_key)
        if prior:
            if prior["fingerprint"] != fingerprint:
                raise AppError("Request ID belongs to another dashboard action.", 409, "idempotency_conflict")
            return prior["result"]
        board_id = board_id or uuid.uuid4().hex
        board_key = ("dashboards", board_id)
        capacity_key = ("system", "dashboards_capacity")
        artifact, normalized = None, None
        existing_item = None
        if action == "pin":
            item_id = item_identity(body.artifact_id)
            artifact, normalized = await self.validated(body.artifact_id, body.view)
        elif action == "item_patch" and body.view is not None:
            existing_item = await self.store.get(f"dashboards/{board_id}/items", item_id)
            if not existing_item:
                raise AppError("Dashboard card not found.", 404, "dashboard_item_not_found")
            artifact, normalized = await self.validated(existing_item["artifact_id"], body.view)
        item_key = (f"dashboards/{board_id}/items", item_id) if item_id else None
        ref_key = ("dashboard_artifact_refs", artifact["id"]) if action == "pin" else None
        artifact_key = ("artifacts", artifact["id"]) if artifact else None
        hour = datetime.now(UTC).strftime("%Y%m%d%H")
        quotas = [
            (f"dashboard_guest_{guest_id}_{hour}", self.settings.dashboard_guest_hourly_limit),
            (f"dashboard_workspace_{hour[:8]}", self.settings.dashboard_workspace_daily_limit),
        ]
        keys = [MAINTENANCE, board_key, request_key, capacity_key] + [("quotas", q) for q, _ in quotas]
        keys += [key for key in (item_key, ref_key, artifact_key) if key]
        stamp, epoch = now_iso(), time.time()

        def remembered(board, item=None):
            result = {"dashboard": public(board), "item": public(item) if item else None}
            return {
                request_key: {"fingerprint": fingerprint, "result": result, "expires_at": epoch + 86400}
            }, result

        def update(docs):
            replay = docs[request_key]
            if replay:
                if replay["fingerprint"] != fingerprint:
                    raise AppError(
                        "Request ID belongs to another dashboard action.", 409, "idempotency_conflict"
                    )
                return {}, replay["result"]
            check_maintenance(docs[MAINTENANCE])
            board = docs[board_key]
            capacity = (docs[capacity_key] or {}).get("count", 0)
            if action == "create":
                if capacity >= self.settings.dashboard_limit:
                    raise AppError("The public dashboard library is full.", 409, "dashboard_capacity")
                board = {
                    "id": board_id,
                    "name": body.name,
                    "description": body.description,
                    "revision": 0,
                    "item_ids": [],
                    "card_count": 0,
                    "sources": [],
                    "source_counts": {},
                    "visibility": "public",
                    "deleted": False,
                    "created_at": stamp,
                    "created_by": guest_id,
                }
            else:
                if not board:
                    raise AppError("Dashboard not found.", 404, "dashboard_not_found")
                if board["revision"] != body.expected_revision:
                    raise AppError(
                        "Someone changed this dashboard. Reload latest; your draft is preserved.",
                        409,
                        "dashboard_conflict",
                    )
                if board["deleted"] != (action == "restore"):
                    raise AppError("Restore this dashboard before changing it.", 409, "dashboard_deleted")
            updates = {}
            result_item = None
            if action in {"create", "restore"}:
                if action == "restore" and board.get("recover_until", 0) <= epoch:
                    raise AppError("This dashboard's recovery window expired.", 410, "dashboard_expired")
                if capacity >= self.settings.dashboard_limit:
                    raise AppError("The public dashboard library is full.", 409, "dashboard_capacity")
                updates[capacity_key] = {"count": capacity + 1}
                board.update(deleted=False, recover_until=None)
            elif action == "delete":
                board.update(
                    deleted=True, recover_until=epoch + self.settings.dashboard_recovery_days * 86400
                )
                updates[capacity_key] = {"count": max(0, capacity - 1)}
            elif action == "patch":
                if all(
                    payload.get(field) is None or payload[field] == board[field]
                    for field in ("name", "description")
                ):
                    return remembered(board)
                for field in ("name", "description"):
                    if payload.get(field) is not None:
                        board[field] = payload[field]
            elif action == "layout":
                if len(body.item_ids) != len(set(body.item_ids)) or set(body.item_ids) != set(
                    board["item_ids"]
                ):
                    raise AppError(
                        "Layout must contain each active card exactly once.", 422, "dashboard_layout_invalid"
                    )
                if body.item_ids == board["item_ids"]:
                    return remembered(board)
                board["item_ids"] = list(body.item_ids)
            else:
                item = docs[item_key]
                if action == "pin":
                    if not docs[artifact_key] or docs[artifact_key] != artifact:
                        raise AppError(
                            "The saved result changed or is unavailable. Retry.", 409, "artifact_unavailable"
                        )
                    if item and not item.get("removed"):
                        raise AppError(
                            "This result is already pinned. Open the dashboard to update its saved view.",
                            409,
                            "dashboard_already_pinned",
                        )
                    if len(board["item_ids"]) >= self.settings.dashboard_item_limit:
                        raise AppError("This dashboard is full. Unpin a card first.", 409, "dashboard_full")
                    if not item:
                        updates[ref_key] = {
                            "id": artifact["id"],
                            "count": (docs[ref_key] or {}).get("count", 0) + 1,
                        }
                    item = {
                        "id": item_id,
                        "artifact_id": artifact["id"],
                        "conversation_id": artifact["conversation_id"],
                        "summary": artifact_summary(artifact),
                        "title": body.title.strip() or artifact["title"],
                        "note": "",
                        "view": normalized,
                        "width": "standard",
                        "created_at": item["created_at"] if item else stamp,
                        "pinned_at": stamp,
                        "created_by": guest_id,
                        "removed": False,
                        "recover_until": None,
                    }
                    board["item_ids"].append(item_id)
                else:
                    if not item:
                        raise AppError("Dashboard card not found.", 404, "dashboard_item_not_found")
                    if action == "item_restore":
                        if not item.get("removed") or item.get("recover_until", 0) <= epoch:
                            raise AppError("This card is not recoverable.", 410, "dashboard_item_expired")
                        if len(board["item_ids"]) >= self.settings.dashboard_item_limit:
                            raise AppError(
                                "This dashboard is full. Unpin a card first.", 409, "dashboard_full"
                            )
                        position = min(
                            item.get("previous_position", len(board["item_ids"])), len(board["item_ids"])
                        )
                        board["item_ids"].insert(position, item_id)
                        item.update(removed=False, recover_until=None)
                    elif item.get("removed"):
                        raise AppError(
                            "This card was removed. Restore it first.", 409, "dashboard_item_removed"
                        )
                    elif action == "unpin":
                        item.update(
                            removed=True,
                            previous_position=board["item_ids"].index(item_id),
                            recover_until=epoch + self.settings.dashboard_recovery_days * 86400,
                        )
                        board["item_ids"].remove(item_id)
                    elif action == "item_patch":
                        if all(
                            payload.get(field) is None or payload[field].strip() == item[field]
                            for field in ("title", "note", "width")
                        ) and (normalized is None or normalized == item["view"]):
                            return remembered(board, item)
                        for field in ("title", "note", "width"):
                            if payload.get(field) is not None:
                                item[field] = payload[field].strip()
                        if normalized is not None:
                            if not docs[artifact_key] or docs[artifact_key] != artifact:
                                raise AppError(
                                    "The saved result is unavailable.", 409, "artifact_unavailable"
                                )
                            item["view"] = normalized
                if action in {"pin", "item_restore", "unpin"}:
                    counts = board.setdefault("source_counts", {})
                    for source in item["summary"]["sources"]:
                        counts[source] = max(0, counts.get(source, 0) + (-1 if action == "unpin" else 1))
                    board["sources"] = [source for source, count in counts.items() if count > 0]
                item.update(updated_at=stamp, updated_by=guest_id)
                updates[item_key] = item
                result_item = public(item)
            for quota, limit in quotas:
                key = ("quotas", quota)
                count = (docs[key] or {}).get("count", 0)
                if count >= limit:
                    raise AppError(
                        "Dashboard usage limit reached. Retry later.", 429, "dashboard_usage_limit"
                    )
                updates[key] = {"id": quota, "count": count + 1}
            board.update(
                revision=board["revision"] + 1,
                card_count=len(board["item_ids"]),
                updated_at=stamp,
                updated_by=guest_id,
            )
            result = {"dashboard": public(board), "item": result_item}
            updates.update(
                {
                    board_key: board,
                    request_key: {"fingerprint": fingerprint, "result": result, "expires_at": epoch + 86400},
                }
            )
            return updates, result

        return await self.store.atomic(keys, update)


def dashboard_router(guest):
    router = APIRouter(prefix="/api/v1/dashboards")

    def service(request):
        return request.app.state.services.dashboards

    @router.get("")
    async def listing(request: Request, deleted: bool = False):
        return {"dashboards": await service(request).list(deleted)}

    @router.post("", status_code=201)
    async def create(body: DashboardCreate, request: Request, guest_id=Depends(guest)):
        return await service(request).mutate(guest_id, "create", body)

    @router.get("/{board_id}")
    async def detail(board_id: DashboardId, request: Request):
        return await service(request).detail(board_id)

    @router.patch("/{board_id}")
    async def patch(board_id: DashboardId, body: DashboardPatch, request: Request, guest_id=Depends(guest)):
        return await service(request).mutate(guest_id, "patch", body, board_id)

    @router.get("/{board_id}/downloads/{kind}")
    async def export_dashboard(
        board_id: DashboardId, kind: str, request: Request, expected_revision: int = Query(ge=1)
    ):
        from app.dashboard_exports import FORMATS, download

        if kind not in FORMATS:
            raise AppError("Choose PNG, JPEG, PDF, CSV ZIP or JSON.", 422, "dashboard_export_format")
        content = await download(service(request), board_id, expected_revision, kind)
        mime, extension = FORMATS[kind]
        return Response(
            content,
            media_type=mime,
            headers={
                "Content-Disposition": f'attachment; filename="querylane-dashboard-{board_id}-r{expected_revision}.{extension}"',
                "Cache-Control": "no-store",
                "X-Content-Type-Options": "nosniff",
            },
        )

    @router.delete("/{board_id}")
    async def delete(
        board_id: DashboardId,
        request: Request,
        expected_revision: int = Query(ge=1),
        request_id: str = Query(min_length=8, max_length=100, pattern=r"^[A-Za-z0-9_-]+$"),
        guest_id=Depends(guest),
    ):
        return await service(request).mutate(
            guest_id,
            "delete",
            DashboardAction(expected_revision=expected_revision, request_id=request_id),
            board_id,
        )

    @router.post("/{board_id}/restore")
    async def restore(
        board_id: DashboardId, body: DashboardAction, request: Request, guest_id=Depends(guest)
    ):
        return await service(request).mutate(guest_id, "restore", body, board_id)

    @router.get("/{board_id}/items")
    async def removed(
        board_id: DashboardId,
        request: Request,
        removed: bool = True,
        offset: int = Query(default=0, ge=0, le=10000),
    ):
        if not removed:
            return {"items": (await service(request).detail(board_id))["items"]}
        return await service(request).removed(board_id, offset)

    @router.post("/{board_id}/items")
    async def pin(board_id: DashboardId, body: DashboardPin, request: Request, guest_id=Depends(guest)):
        return await service(request).mutate(guest_id, "pin", body, board_id)

    @router.patch("/{board_id}/items/{item_id}")
    async def edit_item(
        board_id: DashboardId,
        item_id: DashboardId,
        body: DashboardItemPatch,
        request: Request,
        guest_id=Depends(guest),
    ):
        return await service(request).mutate(guest_id, "item_patch", body, board_id, item_id)

    @router.delete("/{board_id}/items/{item_id}")
    async def unpin(
        board_id: DashboardId,
        item_id: DashboardId,
        request: Request,
        expected_revision: int = Query(ge=1),
        request_id: str = Query(min_length=8, max_length=100, pattern=r"^[A-Za-z0-9_-]+$"),
        guest_id=Depends(guest),
    ):
        return await service(request).mutate(
            guest_id,
            "unpin",
            DashboardAction(expected_revision=expected_revision, request_id=request_id),
            board_id,
            item_id,
        )

    @router.post("/{board_id}/items/{item_id}/restore")
    async def restore_item(
        board_id: DashboardId,
        item_id: DashboardId,
        body: DashboardAction,
        request: Request,
        guest_id=Depends(guest),
    ):
        return await service(request).mutate(guest_id, "item_restore", body, board_id, item_id)

    @router.put("/{board_id}/layout")
    async def layout(board_id: DashboardId, body: DashboardLayout, request: Request, guest_id=Depends(guest)):
        return await service(request).mutate(guest_id, "layout", body, board_id)

    return router
