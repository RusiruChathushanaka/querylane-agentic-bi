"""Transactional report lifecycle, budgets, leases, event replay, and immutable evidence."""

import hashlib
import json
import time
import uuid
from contextvars import ContextVar
from datetime import UTC, datetime

from app.errors import AppError
from app.maintenance import MAINTENANCE, check_maintenance
from app.model_selection import resolve_text_model
from app.repository import now_iso
from app.timesfm import policy as forecast_policy

active_report_lease = ContextVar("active_report_lease", default=None)

TERMINAL = {"complete", "failed", "cancelled"}
REGISTRY = ("system", "report_workers")


def public(value):
    return {
        k: v
        for k, v in value.items()
        if k
        not in {
            "guest_id",
            "fingerprint",
            "owner",
            "brief",
            "budgets",
            "lease_until",
            "tick_at",
            "active_run",
        }
    }


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()


class ReportRepository:
    def __init__(self, store, settings):
        self.store, self.settings = store, settings

    async def get(self, collection, key):
        value = await self.store.get(collection, key)
        if not value:
            raise AppError("Report or report run not found.", 404, "report_not_found")
        return value

    async def create_job(self, kind, guest_id, body, captures):
        """Same admission/lease/outbox as reports; no synthetic public conversation."""
        payload = body.model_dump(mode="json")
        run_id = digest([kind, guest_id, body.request_id])[:32]
        fingerprint = digest(payload)
        key, meta_key = ("report_runs", run_id), ("reports", run_id)
        collection = "dashboard_builds" if kind == "dashboard" else "forecast_plans"
        root_id = body.base_plan_id if kind == "forecast" and body.base_plan_id else run_id
        rootkey = (collection, root_id)
        capacity = ("system", collection + "_capacity")
        day = datetime.now(UTC).strftime("%Y%m%d")
        quotas = [("report_quotas", f"guest_{guest_id}_{day}"), ("report_quotas", f"workspace_{day}")]
        stamp = now_iso()

        def create(docs):
            if docs[key]:
                if docs[key]["fingerprint"] != fingerprint:
                    raise AppError("Request ID already used.", 409, "idempotency_conflict")
                return {}, docs[key]
            check_maintenance(docs[MAINTENANCE])
            root = docs[rootkey]
            if body.base_plan_id and not root:
                raise AppError("Forecast plan not found.", 404, "planning_not_found")
            if root and (
                root["revision"] != body.expected_revision or root.get("active_run") or root.get("deleted")
            ):
                raise AppError("Plan changed or already has active work.", 409, "planning_conflict")
            updates = {}
            if not root:
                count = (docs[capacity] or {}).get("count", 0)
                if count >= 100:
                    raise AppError("This library reached its 100-entry capacity.", 409, "planning_capacity")
                updates[capacity] = {"count": count + 1}
            elif len(root["versions"]) >= 20:
                raise AppError("Plan version limit reached. Create another plan.", 409, "planning_capacity")
            for q, limit in zip(
                quotas, (self.settings.report_guest_daily_limit, self.settings.report_workspace_daily_limit)
            ):
                n = (docs[q] or {}).get("count", 0)
                if n >= limit:
                    raise AppError(
                        "Shared advanced-analysis daily limit reached. Try after the UTC daily reset.",
                        429,
                        "report_usage_limit",
                    )
                updates[q] = {"count": n + 1}
            root = root or {
                "id": root_id,
                "kind": kind,
                "name": body.objective[:80],
                "expires_at": time.time() + 7 * 86400 if kind == "dashboard" else None,
                "revision": 0,
                "versions": [],
                "next_version": 1,
                "deleted": False,
                "created_at": stamp,
            }
            version = root["next_version"]
            root.update(
                active_run=run_id,
                status="queued",
                updated_at=stamp,
                revision=root["revision"] + 1,
                next_version=version + 1,
            )
            run = {
                "id": run_id,
                "report_id": run_id,
                "root_id": root_id,
                "kind": kind,
                "version": version,
                "workflow_version": 3,
                "conversation_id": run_id,
                "guest_id": guest_id,
                "fingerprint": fingerprint,
                "status": "queued",
                "stage": "Preparing scope",
                "sequence": 0,
                "revision": 1,
                "generation": 0,
                "delivery": 0,
                "attempts": 0,
                "lease_until": 0,
                "owner": None,
                "cancel_requested": False,
                "created_at": stamp,
                "updated_at": stamp,
                "expires_at": time.time() + 21600,
                "clarifications": [],
                "clarification": None,
                "budgets": {
                    k: 0
                    for k in (
                        "model_calls",
                        "output_tokens",
                        "queries",
                        "scan_bytes",
                        "fits",
                        "fit_seconds",
                        "seconds",
                    )
                },
                "brief": {
                    **payload,
                    **captures,
                    "job_kind": kind,
                    "planning_policy": {
                        "version": 1,
                        "fit_limit": self.settings.forecast_plan_fit_limit if kind == "forecast" else 0,
                        "max_nodes": 500,
                        "allocation_months": 12,
                        "score_improvement": 0.05,
                        "max_level_degradation": 0.10,
                    },
                    "question": body.objective,
                    "text_model": resolve_text_model(self.settings, body.model),
                    "data_profile": self.settings.data_profile,
                    "history": [],
                    "mode": "reanalyze",
                    "forecast_policy": forecast_policy(self.settings),
                },
            }
            meta = {
                "id": run_id,
                "kind": kind,
                "name": body.objective[:80],
                "active_run": run_id,
                "status": "queued",
                "conversation_id": run_id,
                "revision": 1,
                "versions": [],
                "latest_version": None,
                "deleted": False,
                "created_at": stamp,
                "updated_at": stamp,
            }
            updates.update(
                {
                    key: run,
                    meta_key: meta,
                    rootkey: root,
                    ("report_outbox", run_id): {"id": run_id, "delivery": 0, "pending": True},
                    ("report_conversations", run_id): {"run_id": run_id},
                }
            )
            return updates, run

        return await self.store.atomic([key, meta_key, rootkey, capacity, MAINTENANCE, *quotas], create)

    async def create(self, conversation_id, guest_id, body, report_id=None):
        payload = body.model_dump(mode="json")
        for optional in ("forecast_plan_id", "forecast_plan_version"):
            if payload.get(optional) is None:
                payload.pop(optional, None)
        run_id = digest([conversation_id, guest_id, body.idempotency_key])[:32]
        request_key = ("report_runs", run_id)
        fingerprint = digest([report_id, payload])
        existing = await self.store.get(*request_key)
        if existing:
            if existing["fingerprint"] != fingerprint:
                raise AppError("This request key belongs to another report.", 409, "idempotency_conflict")
            return existing
        conversation = await self.store.get("conversations", conversation_id)
        base_document = None
        if report_id:
            saved_version = await self.get(f"reports/{report_id}/revisions", str(body.base_version))
            base_document = saved_version["document"]
            original = await self.get("report_runs", saved_version["run_id"])
        if conversation is None:
            if not base_document:
                raise AppError("Conversation not found.", 404, "report_not_found")
            conversation = {"source": original["brief"]["source"], "skills_revision": 0, "skill_ids": []}
        history = await self.store.list(
            f"conversations/{conversation_id}/messages", order_by="created_at", descending=True, limit=12
        )
        history = [
            {"role": m["role"], "text": m["text"][:3000]}
            for m in reversed(history)
            if m.get("status") == "complete"
        ]
        captured_plan = None
        if body.forecast_plan_id:
            if not body.forecast_plan_version:
                raise AppError("Select an immutable forecast plan version.", 422, "planning_version")
            captured_plan = await self.get(
                f"forecast_plans/{body.forecast_plan_id}/revisions", str(body.forecast_plan_version)
            )
            captured_plan = captured_plan["document"]
            if not captured_plan.get("artifact_ids"):
                from app.planning_engine import plan_artifact

                company, _ = plan_artifact(captured_plan, "company")
                if not await self.store.get("artifacts", company["id"]):
                    raise AppError(
                        "Prepare the saved company chart before requesting a report.",
                        422,
                        "planning_artifact",
                    )
                captured_plan.update(artifact_ids=[company["id"]], company_artifact_id=company["id"])
        from app.repository import Repository
        from app.skills import Skills

        if base_document:
            history = history + [
                {"role": "user", "text": original["brief"]["question"][:3000]},
                {
                    "role": "assistant",
                    "text": json.dumps(
                        {"scope": base_document["scope"], "definitions": base_document["definitions"]}
                    )[:3000],
                },
            ]
        library = Skills(Repository(self.store, self.settings), self.settings)
        manual = []
        for skill_id in (
            [] if getattr(body, "mode", None) == "presentation" else conversation.get("skill_ids", [])
        ):
            skill = await library.get(skill_id)
            if (
                skill.get("deleted")
                or not skill.get("enabled")
                or (
                    skill["source"] not in {"all", conversation["source"]} and conversation["source"] != "all"
                )
            ):
                raise AppError(
                    "Remove unavailable or incompatible attached skills before creating this report.",
                    409,
                    "skill_unavailable",
                )
            manual.append(skill | {"mode": "manual"})
        report_id = report_id or run_id
        report_key, slot = ("reports", report_id), ("report_conversations", conversation_id)
        day = datetime.now(UTC).strftime("%Y%m%d")
        quotas = [
            (f"guest_{guest_id}_{day}", self.settings.report_guest_daily_limit),
            (f"workspace_{day}", self.settings.report_workspace_daily_limit),
        ]
        keys = [
            MAINTENANCE,
            request_key,
            report_key,
            slot,
            ("conversations", conversation_id),
            ("system", "report_capacity"),
        ] + [("report_quotas", q) for q, _ in quotas]
        stamp = now_iso()
        text_model = resolve_text_model(self.settings, body.model)

        def create(docs):
            prior = docs[request_key]
            if prior:
                if prior["fingerprint"] != fingerprint:
                    raise AppError("This request key belongs to another report.", 409, "idempotency_conflict")
                return {}, prior
            check_maintenance(docs[MAINTENANCE])
            current = docs[("conversations", conversation_id)]
            if (not current and not base_document) or (
                current and current.get("skills_revision", 0) != conversation.get("skills_revision", 0)
            ):
                raise AppError(
                    "Conversation changed. Reload before requesting a report.", 409, "report_conflict"
                )
            if docs[slot] and docs[slot].get("run_id"):
                raise AppError(
                    "A report is already active in this conversation. Open it from Reports; ordinary chat remains available.",
                    409,
                    "report_busy",
                )
            report = docs[report_key]
            if report:
                if report["deleted"] or report["active_run"] or report["revision"] != body.expected_revision:
                    raise AppError("Report changed or has active work. Reload it.", 409, "report_conflict")
                if body.base_version not in report["versions"]:
                    raise AppError("Select an existing base version.", 422, "report_version_invalid")
                if len(report["versions"]) >= 20:
                    raise AppError(
                        "This report reached its version limit. Create another report.",
                        409,
                        "report_capacity",
                    )
                report["revision"] += 1
            else:
                if hasattr(body, "base_version"):
                    raise AppError("Report not found.", 404, "report_not_found")
                report = {
                    "id": report_id,
                    "name": body.question[:120],
                    "revision": 1,
                    "versions": [],
                    "latest_version": None,
                    "created_at": stamp,
                    "deleted": False,
                    "visibility": "public",
                    "conversation_id": conversation_id,
                }
            updates = {}
            if not docs[report_key]:
                capacity_key = ("system", "report_capacity")
                count = (docs[capacity_key] or {}).get("count", 0)
                if count >= self.settings.report_catalog_limit:
                    raise AppError(
                        "The report library is full. Move an unused report to Recently deleted.",
                        409,
                        "report_capacity",
                    )
                updates[capacity_key] = {"count": count + 1}
            if current and current["title"] == "New exploration" and not current.get("active_run"):
                current.update(title=body.question[:90], updated_at=stamp)
                updates[("conversations", conversation_id)] = current
            for q, limit in quotas:
                key = ("report_quotas", q)
                count = (docs[key] or {}).get("count", 0)
                if count >= limit:
                    raise AppError(
                        "Advanced report usage limit reached. Try again tomorrow.", 429, "report_usage_limit"
                    )
                updates[key] = {"count": count + 1}
            version = max(report["versions"], default=0) + 1
            # Failed candidates also receive unique numbers; a later success never changes an old URL.
            version = max(version, report.get("next_version", 1))
            report.update(active_run=run_id, status="queued", updated_at=stamp, next_version=version + 1)
            run = {
                "id": run_id,
                "report_id": report_id,
                "version": version,
                "workflow_version": 2,
                "conversation_id": conversation_id,
                "guest_id": guest_id,
                "fingerprint": fingerprint,
                "status": "queued",
                "stage": "Preparing scope",
                "sequence": 0,
                "revision": 1,
                "generation": 0,
                "delivery": 0,
                "attempts": 0,
                "lease_until": 0,
                "owner": None,
                "cancel_requested": False,
                "created_at": stamp,
                "expires_at": time.time() + 21600,
                "updated_at": stamp,
                "clarifications": [],
                "clarification": None,
                "budgets": {
                    "model_calls": 0,
                    "output_tokens": 0,
                    "queries": 0,
                    "scan_bytes": 0,
                    "fits": 0,
                    "fit_seconds": 0,
                    "seconds": 0,
                },
                "brief": {
                    "question": body.question,
                    "style": body.style,
                    "text_model": text_model,
                    "source": conversation["source"],
                    "data_profile": base_document["data_profile"]
                    if base_document and body.mode == "presentation"
                    else self.settings.data_profile,
                    "history": history,
                    "manual_skills": manual,
                    "mode": getattr(body, "mode", "reanalyze"),
                    "base_version": getattr(body, "base_version", None),
                    "forecast_policy": forecast_policy(self.settings),
                    "forecast_plan_snapshot": captured_plan,
                },
            }
            updates.update(
                {
                    request_key: run,
                    report_key: report,
                    slot: {"run_id": run_id},
                    ("report_outbox", run_id): {
                        "id": run_id,
                        "delivery": 0,
                        "pending": True,
                        "created_at": stamp,
                    },
                }
            )
            if captured_plan:
                updates[("plan_report_refs", report_id)] = {
                    "id": report_id,
                    "plan_id": captured_plan["id"],
                    "version": captured_plan["version"],
                    "artifact_ids": captured_plan["artifact_ids"],
                }
            return updates, run

        return await self.store.atomic(keys, create)

    def _lease(self, run, lease):
        if (
            not run
            or run["status"] != "running"
            or run["owner"] != lease["owner"]
            or run["generation"] != lease["generation"]
            or run["lease_until"] <= time.time()
        ):
            raise AppError("This report worker no longer owns the run.", 409, "report_stale_lease")
        if run.get("cancel_requested"):
            raise AppError("Report cancellation requested.", 409, "cancelled")

    async def received(self, run_id, delivery):
        key, outkey = ("report_runs", run_id), ("report_outbox", run_id)

        def acknowledge(docs):
            run = docs[key]
            if not run or run["status"] in TERMINAL or (delivery is not None and run["delivery"] != delivery):
                return {}, False
            outbox = docs[outkey]
            if outbox and outbox["delivery"] == run["delivery"]:
                outbox["received_at"] = time.time()
                return {outkey: outbox}, True
            return {}, True

        return await self.store.atomic([key, outkey], acknowledge)

    async def claim(self, run_id, delivery=None):
        key = ("report_runs", run_id)
        snapshot = await self.get("report_runs", run_id)
        report_key = ("reports", snapshot["report_id"])
        owner, stamp = uuid.uuid4().hex, time.time()

        def claim(docs):
            run = docs[key]
            if not run:
                raise AppError("Run not found.", 404, "report_not_found")
            if (
                run["status"] in TERMINAL
                or run["status"] == "waiting_input"
                or (delivery is not None and run["delivery"] != delivery)
            ):
                return {}, None
            check_maintenance(docs[MAINTENANCE])
            slots = {k: v for k, v in (docs[REGISTRY] or {}).get("slots", {}).items() if v > stamp}
            if run["status"] == "running" and run["lease_until"] > stamp:
                raise AppError("Report is already running.", 503, "report_worker_busy")
            if len(slots) >= self.settings.report_concurrency and run_id not in slots:
                raise AppError("Report workers are occupied. Retrying shortly.", 503, "report_worker_busy")
            if run["attempts"] >= 3 or run["budgets"]["seconds"] >= self.settings.report_timeout_seconds:
                raise AppError("Report recovery budget exhausted.", 409, "report_budget")
            if run["status"] == "running":
                run["budgets"]["seconds"] += max(0, run["lease_until"] - run["tick_at"])
            run.update(
                status="running",
                owner=owner,
                generation=run["generation"] + 1,
                attempts=run["attempts"] + 1,
                lease_until=stamp + 45,
                tick_at=stamp,
                updated_at=now_iso(),
            )
            slots[run_id] = run["lease_until"]
            report = docs[report_key]
            report.update(status="running", updated_at=now_iso())
            return {key: run, report_key: report, REGISTRY: {"slots": slots}}, {
                "run_id": run_id,
                "owner": owner,
                "generation": run["generation"],
            }

        return await self.store.atomic([key, REGISTRY, MAINTENANCE, report_key], claim)

    async def change(self, lease, mutate, extra=()):
        key = ("report_runs", lease["run_id"])

        def apply(docs):
            run = docs[key]
            self._lease(run, lease)
            updates, result = mutate(run, docs)
            run["updated_at"] = now_iso()
            updates[key] = run
            return updates, result

        return await self.store.atomic([key, *extra], apply)

    async def guard(self, lease):
        run = await self.get("report_runs", lease["run_id"])
        self._lease(run, lease)
        elapsed = run["budgets"]["seconds"] + max(0, time.time() - run["tick_at"])
        if elapsed >= self.settings.report_timeout_seconds:
            raise AppError(
                "Report reached its computation deadline. Narrow the request.", 409, "report_budget"
            )
        return run

    async def heartbeat(self, lease):
        stamp = time.time()

        def renew(run, docs):
            run["budgets"]["seconds"] += max(0, stamp - run["tick_at"])
            if run["budgets"]["seconds"] >= self.settings.report_timeout_seconds:
                raise AppError("Report reached its computation deadline.", 409, "report_budget")
            run.update(tick_at=stamp, lease_until=stamp + 45)
            slots = (docs[REGISTRY] or {}).get("slots", {})
            if slots.get(run["id"], 0) <= stamp:
                raise AppError("Worker slot expired.", 409, "report_stale_lease")
            slots[run["id"]] = run["lease_until"]
            return {REGISTRY: {"slots": slots}}, None

        return await self.change(lease, renew, [REGISTRY])

    async def spend(self, lease, **amounts):
        limits = {
            "model_calls": self.settings.report_model_calls,
            "output_tokens": self.settings.report_output_tokens,
            "queries": self.settings.report_query_limit,
            "scan_bytes": self.settings.report_scan_bytes,
            "fits": self.settings.report_fit_limit,
            "fit_seconds": self.settings.report_fit_seconds,
        }

        def spend(run, _):
            if run.get("kind") == "forecast":
                limits["fits"] = min(128, run["brief"].get("planning_policy", {}).get("fit_limit", 128))
            for name, amount in amounts.items():
                count = max(0, run["budgets"].get(name, 0) + amount)
                if amount > 0 and count > limits[name]:
                    raise AppError(
                        f"Report {name.replace('_', ' ')} budget reached. Narrow the request.",
                        409,
                        "report_budget",
                    )
                run["budgets"][name] = count
            return {}, dict(run["budgets"])

        await self.guard(lease)
        return await self.change(lease, spend)

    def forecast_limits(self, run):
        policy = run["brief"].get("forecast_policy", {})
        return {
            "queries": self.settings.report_query_limit,
            "scan_bytes": self.settings.report_scan_bytes,
            "fits": min(128, run["brief"].get("planning_policy", {}).get("fit_limit", 128))
            if run.get("kind") == "forecast"
            else self.settings.report_fit_limit,
            "fit_seconds": self.settings.report_fit_seconds,
            **{
                "timesfm_" + k: policy.get(k, 0)
                for k in ("targets", "jobs", "input_tokens", "output_tokens", "seconds")
            },
        }

    async def reserve_once(self, lease, name, amounts, value):
        """Operation and conservative budget reservation commit in one fenced transaction."""
        key = (f"report_runs/{lease['run_id']}/checkpoints", name)

        def reserve(run, docs):
            prior = docs[key]
            if prior is not None:
                return {}, prior["value"]
            limits = self.forecast_limits(run)
            for field, amount in amounts.items():
                if amount < 0 or run["budgets"].get(field, 0) + amount > limits[field]:
                    raise AppError(
                        "TimesFM work budget reached; statistical evidence remains available.",
                        422,
                        "timesfm_budget",
                    )
                run["budgets"][field] = run["budgets"].get(field, 0) + amount
            return {key: {"value": value, "created_at": now_iso()}}, value

        await self.guard(lease)
        return await self.change(lease, reserve, [key])

    async def settle_forecast_seconds(self, lease, name, reserved, elapsed):
        key = (f"report_runs/{lease['run_id']}/checkpoints", name + "_settled")

        def settle(run, docs):
            if docs[key] is not None:
                return {}, None
            run["budgets"]["timesfm_seconds"] = max(
                0, run["budgets"].get("timesfm_seconds", 0) - max(0, reserved - elapsed)
            )
            return {key: {"value": True, "created_at": now_iso()}}, None

        return await self.change(lease, settle, [key])

    async def checkpoint(self, lease, name, value):
        key = (f"report_runs/{lease['run_id']}/checkpoints", name)

        def save(_, docs):
            if docs[key] is not None:
                return {}, docs[key]["value"]
            return {key: {"value": value, "created_at": now_iso()}}, value

        return await self.change(lease, save, [key])

    async def read_checkpoint(self, run_id, name):
        value = await self.store.get(f"report_runs/{run_id}/checkpoints", name)
        return value["value"] if value else None

    async def event(self, lease, kind, data):
        def append(run, _):
            run["sequence"] += 1
            if kind == "progress":
                run["stage"] = data["message"]
            return {
                (f"report_runs/{run['id']}/events", str(run["sequence"])): {
                    "id": run["sequence"],
                    "type": kind,
                    "data": data,
                }
            }, None

        await self.change(lease, append)

    async def save_artifact(self, lease, artifact, rows, checkpoint_name):
        artifact_id = artifact["id"]
        existing = await self.read_checkpoint(lease["run_id"], checkpoint_name)
        if existing is not None:
            if existing != artifact_id:
                raise AppError(
                    "A checkpoint already references different immutable evidence.", 409, "report_immutable"
                )
            await self.guard(lease)
            return existing
        # Pages are fenced too. Unpublished pages cannot be discovered until metadata commits.
        page, size, index = [], 0, 0
        for row in rows:
            n = len(json.dumps(row, default=str).encode())
            if n > 180000:
                raise AppError("Result row exceeds storage limits.", 422, "result_too_large")
            if page and (size + n > 180000 or len(page) >= 250):
                await self.change(
                    lease,
                    lambda _, __, p=page, i=index: (
                        {(f"artifacts/{artifact_id}/pages", str(i)): {"rows": p, "index": i}},
                        None,
                    ),
                )
                page, size, index = [], 0, index + 1
            page.append(row)
            size += n
        if page:
            await self.change(
                lease,
                lambda _, __: (
                    {(f"artifacts/{artifact_id}/pages", str(index)): {"rows": page, "index": index}},
                    None,
                ),
            )
        artifact["page_count"] = index + 1 if rows else 0
        artifact["report_run_id"] = lease["run_id"]
        artifact_key, ref_key = ("artifacts", artifact_id), ("report_artifact_refs", artifact_id)
        cp_key = (f"report_runs/{lease['run_id']}/checkpoints", checkpoint_name)

        def commit(run, docs):
            if docs[cp_key]:
                return {}, docs[cp_key]["value"]
            return {
                artifact_key: artifact,
                ref_key: {"id": artifact_id, "run_id": run["id"], "count": 1},
                cp_key: {"value": artifact_id, "created_at": now_iso()},
            }, artifact_id

        return await self.change(lease, commit, [artifact_key, ref_key, cp_key])

    async def finish(
        self, lease, status, *, document=None, exports=None, error=None, clarification=None, requirements=None
    ):
        run = await self.get("report_runs", lease["run_id"])
        report_key = ("reports", run["report_id"])
        slot = ("report_conversations", run["conversation_id"])
        version_key = (f"reports/{run['report_id']}/revisions", str(run["version"]))
        job_key = (
            (
                ("forecast_plans" if run.get("kind") == "forecast" else "dashboard_builds"),
                run.get("root_id", run["id"]),
            )
            if run.get("kind")
            else None
        )

        def finish(run, docs):
            report = docs[report_key]
            updates = {}
            if document:
                if docs[version_key]:
                    raise AppError("A completed report version is immutable.", 409, "report_immutable")
                updates[version_key] = {
                    "version": run["version"],
                    "run_id": run["id"],
                    "created_at": now_iso(),
                    "document": document,
                    "exports": exports,
                    "artifact_ids": document["artifact_ids"],
                }
                report["versions"].append(run["version"])
                report["latest_version"] = run["version"]
            run.update(
                status=status,
                error=error,
                clarification=clarification,
                clarification_requirements=requirements,
                lease_until=0,
            )
            report.update(status=status, updated_at=now_iso(), revision=report["revision"] + 1)
            if status in TERMINAL:
                report["active_run"] = None
                updates[slot] = {"run_id": None}
            if job_key and status != "complete":
                root = docs[job_key]
                root.update(status=status, updated_at=now_iso(), revision=root["revision"] + 1)
                if status in TERMINAL:
                    root["active_run"] = None
                updates[job_key] = root
            slots = (docs[REGISTRY] or {}).get("slots", {})
            slots.pop(run["id"], None)
            updates.update({report_key: report, REGISTRY: {"slots": slots}})
            run["sequence"] += 1
            updates[(f"report_runs/{run['id']}/events", str(run["sequence"]))] = {
                "id": run["sequence"],
                "type": status,
                "data": {
                    "report_id": report["id"],
                    "version": run["version"],
                    "error": error,
                    "clarification": clarification,
                    "clarification_requirements": requirements,
                },
            }
            return updates, public(run)

        # Cancellation is allowed to reach a terminal state, but never to publish.
        if status == "cancelled":
            original = lease.copy()
            key = ("report_runs", lease["run_id"])

            def cancelled(docs):
                value = docs[key]
                if (
                    not value
                    or value["owner"] != original["owner"]
                    or value["generation"] != original["generation"]
                    or value["lease_until"] <= time.time()
                ):
                    raise AppError("Report ownership changed.", 409, "report_stale_lease")
                updates, result = finish(value, docs)
                updates[key] = value
                return updates, result

            return await self.store.atomic(
                [key, report_key, slot, version_key, REGISTRY, *([job_key] if job_key else [])], cancelled
            )
        return await self.change(
            lease, finish, [report_key, slot, version_key, REGISTRY, *([job_key] if job_key else [])]
        )

    async def owned(self, run_id, guest_id):
        run = await self.get("report_runs", run_id)
        if run["guest_id"] != guest_id:
            raise AppError("Only the initiating guest can control this report run.", 403, "forbidden")
        return run

    async def cancel(self, run_id, guest_id):
        await self.owned(run_id, guest_id)
        key = ("report_runs", run_id)

        def request(docs):
            run = docs[key]
            if run["status"] in TERMINAL:
                return {}, public(run)
            run["cancel_requested"] = True
            return {key: run}, public(run)

        return await self.store.atomic([key], request)

    async def clarify(self, run_id, guest_id, body):
        await self.owned(run_id, guest_id)
        key = ("report_runs", run_id)

        def answer(docs):
            check_maintenance(docs[MAINTENANCE])
            run = docs[key]
            if run["status"] != "waiting_input" or run["revision"] != body.expected_revision:
                raise AppError(
                    "Report clarification changed. Reload it; your draft is preserved.",
                    409,
                    "report_conflict",
                )
            if len(run["clarifications"]) >= 3:
                raise AppError("Clarification limit reached. Create a narrower report.", 409, "report_budget")
            run["clarifications"].append(
                {
                    "question": run["clarification"],
                    "answer": body.answer,
                    "forecast_inputs": {
                        key: value.model_dump() for key, value in body.forecast_inputs.items()
                    },
                }
            )
            run.update(
                status="queued",
                clarification=None,
                clarification_requirements=None,
                revision=run["revision"] + 1,
                delivery=run["delivery"] + 1,
                attempts=0,
            )
            return {
                key: run,
                ("report_outbox", run_id): {"id": run_id, "pending": True, "delivery": run["delivery"]},
            }, public(run)

        return await self.store.atomic([key, MAINTENANCE], answer)
