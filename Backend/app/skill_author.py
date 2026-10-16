"""Durable, guest-scoped interviews. Drafts become shared skills only on review/publication."""

import hashlib
import json
import time
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Request
from pydantic import Field

from app.errors import AppError
from app.models import StrictModel
from app.repository import check_lease, now_iso
from app.skills import SkillContent

COLLECTION = "skill_author_sessions"
REQUIRED = ("purpose", "when_to_use", "source", "workflow", "definitions", "examples")


class AuthorCreate(StrictModel):
    idempotency_key: str = Field(min_length=8, max_length=80, pattern=r"^[a-zA-Z0-9_-]+$")


class AuthorBrief(StrictModel):
    name: str = Field(default="", max_length=80)
    description: str = Field(default="", max_length=300)
    purpose: str = Field(default="", max_length=1000)
    when_to_use: str = Field(default="", max_length=500)
    source: str = Field(default="", pattern=r"^(all|bigquery|postgres)?$")
    workflow: str = Field(default="", max_length=4000)
    definitions: str = Field(default="", max_length=4000)
    examples: str = Field(default="", max_length=2000)
    tags: str = Field(default="", max_length=240)


class AuthorDraft(StrictModel):
    expected_revision: int = Field(ge=1)
    content: SkillContent


class AuthorPublish(StrictModel):
    expected_revision: int = Field(ge=1)


def owned(value, guest_id):
    if not value or value["guest_id"] != guest_id:
        raise AppError("Author session not found in this browser session.", 404, "author_not_found")
    if value["expires_at"] <= time.time() and not value.get("published_skill_id"):
        raise AppError("This author session expired. Start a new interview.", 410, "author_expired")
    return value


def snapshot(value):
    return {
        k: value[k]
        for k in (
            "id",
            "revision",
            "status",
            "brief",
            "draft",
            "transcript",
            "published_skill_id",
            "expires_at",
        )
    } | {
        "missing_fields": [k for k in REQUIRED if not value["brief"][k].strip()],
        "connected": bool(value.get("active_run") and value["lease_until"] > time.time()),
        "turns": value["turns"],
    }


class SkillAuthor:
    def __init__(self, services):
        self.services = services
        self.store, self.settings = services.store, services.settings

    async def create(self, guest_id, key):
        session_id = hashlib.sha256(f"{guest_id}:{key}".encode()).hexdigest()[:32]
        doc_key = (COLLECTION, session_id)
        hour = datetime.now(UTC).strftime("%Y%m%d%H")
        quotas = [
            (f"author_create_guest_{guest_id}_{hour}", self.settings.author_guest_hourly_limit),
            (f"author_create_workspace_{hour[:8]}", self.settings.author_workspace_daily_limit),
        ]
        keys = [doc_key] + [("quotas", name) for name, _ in quotas]

        def mutate(docs):
            if docs[doc_key]:
                return {}, snapshot(owned(docs[doc_key], guest_id))
            updates = self.quota_updates(docs, quotas)
            value = {
                "id": session_id,
                "guest_id": guest_id,
                "status": "collecting",
                "revision": 1,
                "brief": AuthorBrief().model_dump(),
                "draft": None,
                "transcript": [],
                "turns": 0,
                "updates": 0,
                "published_skill_id": None,
                "expires_at": time.time() + self.settings.author_lifetime_seconds,
                "created_at": now_iso(),
                "updated_at": now_iso(),
                "generation": 0,
                "active_run": None,
                "lease_until": 0,
            }
            return updates | {doc_key: value}, snapshot(value)

        return await self.store.atomic(keys, mutate)

    @staticmethod
    def quota_updates(docs, quotas):
        updates = {}
        for name, limit in quotas:
            count = (docs[("quotas", name)] or {}).get("count", 0)
            if count >= limit:
                raise AppError(
                    "Voice author usage limit reached. Try again later.", 429, "author_usage_limit"
                )
            updates[("quotas", name)] = {"id": name, "count": count + 1}
        return updates

    async def get(self, session_id, guest_id):
        return owned(await self.store.get(COLLECTION, session_id), guest_id)

    async def acquire(self, session_id, guest_id):
        key = (COLLECTION, session_id)
        hour = datetime.now(UTC).strftime("%Y%m%d%H")
        quotas = [
            (f"author_live_guest_{guest_id}_{hour}", self.settings.author_voice_guest_hourly_limit),
            (f"author_live_workspace_{hour[:8]}", self.settings.author_voice_workspace_daily_limit),
        ]

        def mutate(docs):
            value = owned(docs[key], guest_id)
            self.editable(value)
            self.idle(value)
            self.turn_budget(value)
            updates = self.quota_updates(docs, quotas)
            value.update(
                active_run=uuid.uuid4().hex,
                generation=value["generation"] + 1,
                lease_until=time.time() + self.settings.lease_seconds,
            )
            lease = {
                "collection": COLLECTION,
                "conversation_id": session_id,
                "run_id": value["active_run"],
                "generation": value["generation"],
            }
            return updates | {key: value}, (lease, value)

        return await self.store.atomic([key] + [("quotas", q) for q, _ in quotas], mutate)

    @staticmethod
    def idle(value):
        if value.get("active_run") and value["lease_until"] > time.time():
            raise AppError(
                "The assistant is connected. Pause it before reviewing or publishing.", 409, "author_busy"
            )

    @staticmethod
    def editable(value):
        if value.get("published_skill_id"):
            raise AppError(
                "This session already published a skill. Start a new interview.", 409, "author_published"
            )

    def turn_budget(self, value):
        if value["turns"] >= self.settings.author_turn_limit:
            raise AppError(
                "Interview turn limit reached. Review your draft or start a new session.",
                429,
                "author_turn_limit",
            )

    @staticmethod
    def revision(value, expected):
        if value["revision"] != expected:
            raise AppError(
                "The draft changed. Reload it; your local edits are preserved.", 409, "author_conflict"
            )

    async def change(self, session_id, guest_id, mutate, lease=None):
        key = (COLLECTION, session_id)

        def operation(docs):
            value = owned(docs[key], guest_id)
            self.editable(value)
            if lease:
                check_lease(value, lease)
            else:
                self.idle(value)
            mutate(value)
            value["updated_at"] = now_iso()
            return {key: value}, snapshot(value)

        return await self.store.atomic([key], operation)

    def update_budget(self, value):
        if value["updates"] >= self.settings.author_update_limit:
            raise AppError(
                "Draft update limit reached. Review the existing draft or start a new session.",
                429,
                "author_update_limit",
            )
        value["updates"] += 1
        value["revision"] += 1

    async def update_brief(self, session_id, guest_id, changes, lease):
        def mutate(value):
            brief = AuthorBrief.model_validate(
                value["brief"]
                | {k: v.strip() for k, v in changes.items() if isinstance(v, str) and v.strip()}
            ).model_dump()
            if brief == value["brief"]:
                return
            self.update_budget(value)
            value.update(brief=brief, draft=None, status="collecting")

        return await self.change(session_id, guest_id, mutate, lease)

    async def prepare(self, session_id, guest_id, lease):
        def mutate(value):
            brief = value["brief"]
            missing = [k for k in (*REQUIRED, "name", "description") if not brief[k].strip()]
            if missing:
                raise AppError(
                    "Ask about these missing details first: " + ", ".join(missing), 409, "author_incomplete"
                )
            content = SkillContent(
                name=brief["name"],
                description=brief["description"],
                when_to_use=brief["when_to_use"],
                source=brief["source"],
                tags=[t.strip() for t in brief["tags"].split(",") if t.strip()],
                instructions=(
                    f"## Purpose\n{brief['purpose']}\n\n## Workflow\n{brief['workflow']}\n\n"
                    f"## Business definitions\n{brief['definitions']}\n\n## Examples\n{brief['examples']}\n"
                ),
            ).model_dump()
            if value["draft"] != content:
                self.update_budget(value)
                value.update(draft=content, status="draft_ready")

        return await self.change(session_id, guest_id, mutate, lease)

    async def edit_draft(self, session_id, guest_id, body):
        def mutate(value):
            self.revision(value, body.expected_revision)
            if not value["draft"]:
                raise AppError("Prepare a draft in the conversation first.", 409, "author_draft_required")
            if value["draft"] != body.content.model_dump():
                self.update_budget(value)
                value.update(draft=body.content.model_dump(), status="draft_ready")

        return await self.change(session_id, guest_id, mutate)

    async def transcript(self, session_id, guest_id, messages, lease):
        def mutate(value):
            additions = [
                {"role": role, "text": text.strip(), "created_at": now_iso()}
                for role, text in messages
                if text.strip()
            ]
            if any(m["role"] == "user" for m in additions):
                self.turn_budget(value)
                value["turns"] += 1
            transcript = value["transcript"] + additions
            if (
                len(json.dumps(transcript, ensure_ascii=False).encode())
                > self.settings.author_transcript_bytes
            ):
                raise AppError(
                    "Transcript limit reached. Review the saved draft or start another interview.",
                    429,
                    "author_transcript_limit",
                )
            value["transcript"] = transcript

        return await self.change(session_id, guest_id, mutate, lease)

    async def consume_tool(self, session_id, guest_id, lease):
        def mutate(value):
            count = value.get("tool_calls", 0)
            if count >= self.settings.author_tool_limit:
                raise AppError(
                    "Interview tool limit reached. Review the saved draft or start a new interview.",
                    429,
                    "author_tool_limit",
                )
            value["tool_calls"] = count + 1

        return await self.change(session_id, guest_id, mutate, lease)

    async def renew(self, session_id, guest_id, lease):
        await self.change(
            session_id,
            guest_id,
            lambda v: v.update(lease_until=time.time() + self.settings.lease_seconds),
            lease,
        )

    async def release(self, lease):
        key = (COLLECTION, lease["conversation_id"])

        def mutate(docs):
            value = docs[key]
            if (
                value
                and value["active_run"] == lease["run_id"]
                and value["generation"] == lease["generation"]
            ):
                value.update(active_run=None, lease_until=0)
                return {key: value}, snapshot(value)
            return {}, None

        return await self.store.atomic([key], mutate)

    async def publish(self, session_id, guest_id, expected_revision):
        value = await self.get(session_id, guest_id)
        if not value.get("draft"):
            raise AppError("Prepare a draft before publishing.", 409, "author_draft_required")
        return await self.services.analysis.skills.mutate(
            guest_id,
            skill_id="author_" + session_id,
            content=SkillContent(**value["draft"]),
            author_publication=(session_id, expected_revision),
        )


def author_router(guest):
    router = APIRouter(prefix="/api/v1/skills/author-sessions")

    def service(request):
        return SkillAuthor(request.app.state.services)

    @router.post("", status_code=201)
    async def create(body: AuthorCreate, request: Request, guest_id=Depends(guest)):
        return await service(request).create(guest_id, body.idempotency_key)

    @router.get("/{session_id}")
    async def get(session_id: str, request: Request, guest_id=Depends(guest)):
        return snapshot(await service(request).get(session_id, guest_id))

    @router.patch("/{session_id}/draft")
    async def edit(session_id: str, body: AuthorDraft, request: Request, guest_id=Depends(guest)):
        return await service(request).edit_draft(session_id, guest_id, body)

    @router.post("/{session_id}/publish")
    async def publish(session_id: str, body: AuthorPublish, request: Request, guest_id=Depends(guest)):
        return await service(request).publish(session_id, guest_id, body.expected_revision)

    return router
