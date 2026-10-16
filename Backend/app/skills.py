"""Public, versioned instruction playbooks. Skills never add executable tools."""

import re
import time
import uuid
from datetime import UTC, datetime
from typing import Literal

import yaml
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import PlainTextResponse
from google.genai.errors import APIError
from pydantic import Field, ValidationError, field_validator

from app.errors import AppError
from app.models import StrictModel
from app.repository import now_iso


class SkillContent(StrictModel):
    name: str = Field(min_length=1, max_length=80)
    description: str = Field(min_length=1, max_length=300)
    when_to_use: str = Field(min_length=1, max_length=500)
    source: Literal["all", "bigquery", "postgres"] = "all"
    tags: list[str] = Field(default_factory=list, max_length=8)
    instructions: str = Field(min_length=1, max_length=16384)

    @field_validator("name", "description", "when_to_use", "instructions")
    @classmethod
    def meaningful(cls, value):
        if not value.strip():
            raise ValueError("Enter non-blank skill fields.")
        if len(value.encode("utf-8")) > 16384:
            raise ValueError("Instructions must fit within 16 KiB of UTF-8 text.")
        return value.strip()

    @field_validator("tags")
    @classmethod
    def clean_tags(cls, values):
        if any(not tag.strip() or len(tag.strip()) > 30 for tag in values):
            raise ValueError("Tags must contain 1–30 characters.")
        return list(dict.fromkeys(tag.strip() for tag in values))


class SkillPatch(StrictModel):
    expected_revision: int = Field(ge=1)
    name: str | None = None
    description: str | None = None
    when_to_use: str | None = None
    source: Literal["all", "bigquery", "postgres"] | None = None
    tags: list[str] | None = None
    instructions: str | None = None
    enabled: bool | None = None


class RevisionCheck(StrictModel):
    expected_revision: int = Field(ge=1)


class SkillAttachments(StrictModel):
    skill_ids: list[str] = Field(max_length=3)
    expected_revision: int = Field(default=0, ge=0)

    @field_validator("skill_ids")
    @classmethod
    def distinct_ids(cls, values):
        if len(set(values)) != len(values) or any(
            not re.fullmatch(r"[a-zA-Z0-9_-]{1,80}", v) for v in values
        ):
            raise ValueError("Choose distinct valid skill IDs.")
        return values


class SkillImport(StrictModel):
    markdown: str = Field(max_length=24576)


class SkillChoice(StrictModel):
    skill_ids: list[str] = Field(default_factory=list, max_length=3)


SUMMARY_FIELDS = [field for field in SkillContent.model_fields if field != "instructions"] + [
    "id",
    "enabled",
    "deleted",
    "revision",
    "created_at",
    "updated_at",
]


def public_skill(value):
    return {key: item for key, item in value.items() if key not in {"created_by", "updated_by"}}


def skill_reference(value, mode):
    return {key: value[key] for key in ("id", "name", "description", "revision")} | {"mode": mode}


def compatible(skill, source):
    return skill["source"] == "all" or source == "all" or skill["source"] == source


class Skills:
    def __init__(self, repo, settings):
        self.repo, self.store, self.settings = repo, repo.store, settings

    async def get(self, skill_id, revision=None):
        collection, key = (
            (f"skills/{skill_id}/revisions", str(revision)) if revision is not None else ("skills", skill_id)
        )
        value = await self.store.get(collection, key)
        if not value:
            raise AppError("Skill not found.", 404, "skill_not_found")
        return value

    async def list(self, deleted=False):
        values = await self.store.list(
            "skills",
            limit=10000 if deleted else self.settings.skill_catalog_limit,
            where=("deleted", deleted),
            fields=SUMMARY_FIELDS,
        )
        return sorted(
            [public_skill(v) for v in values if bool(v.get("deleted")) == deleted],
            key=lambda v: (v["updated_at"], v["id"]),
            reverse=True,
        )

    async def mutate(
        self,
        guest_id,
        *,
        content=None,
        skill_id=None,
        patch=None,
        action="create",
        seed=False,
        author_publication: tuple[str, int] | None = None,
    ):
        skill_id = skill_id or uuid.uuid4().hex
        key, capacity_key = ("skills", skill_id), ("system", "skills_capacity")
        stamp = datetime.now(UTC)
        quotas = (
            []
            if seed
            else [
                (f"skill_guest_{guest_id}_{stamp:%Y%m%d%H}", self.settings.skill_guest_hourly_limit),
                (f"skill_workspace_{stamp:%Y%m%d}", self.settings.skill_workspace_daily_limit),
            ]
        )
        keys = [key, capacity_key] + [("quotas", q) for q, _ in quotas]
        author_key = ("skill_author_sessions", author_publication[0]) if author_publication else None
        if author_key:
            keys.append(author_key)

        def update(docs):
            previous = docs[key]
            author = docs.get(author_key) if author_key else None
            if author_key:
                if not author or author["guest_id"] != guest_id:
                    raise AppError("Author session not found.", 404, "author_not_found")
                # A lost HTTP response must not create another skill or consume
                # another quota. Later public edits/deletion are preserved.
                if author.get("published_skill_id") == skill_id and previous:
                    return {}, public_skill(previous)
                if author["expires_at"] <= time.time():
                    raise AppError("This author session expired.", 410, "author_expired")
                if author.get("active_run") and author["lease_until"] > time.time():
                    raise AppError("Pause the voice assistant before publishing.", 409, "author_busy")
                if author["revision"] != author_publication[1]:
                    raise AppError("The draft changed. Reload it before publishing.", 409, "author_conflict")
                if not author.get("draft") or author["draft"] != content.model_dump():
                    raise AppError("Prepare and review a draft first.", 409, "author_draft_required")
            if seed and previous:
                return {}, public_skill(previous)
            if action != "create":
                if not previous:
                    raise AppError("Skill not found.", 404, "skill_not_found")
                if previous["revision"] != patch["expected_revision"]:
                    raise AppError(
                        "Someone changed this skill. Reload the latest version; your draft is preserved.",
                        409,
                        "skill_conflict",
                    )
                if previous["deleted"] != (action == "restore"):
                    raise AppError(
                        "This skill is deleted. Restore it before editing.", 409, "skill_unavailable"
                    )
            elif previous:
                raise AppError("Skill already exists.", 409, "skill_conflict")
            base = (
                {field: previous[field] for field in SkillContent.model_fields}
                if previous
                else content.model_dump()
            )
            edits = {k: v for k, v in (patch or {}).items() if k in SkillContent.model_fields}
            try:
                validated = SkillContent.model_validate(base | edits).model_dump()
            except ValidationError as exc:
                raise AppError(
                    "Check the skill fields: " + exc.errors()[0]["msg"], 422, "validation_error"
                ) from exc
            enabled = (patch or {}).get("enabled", previous["enabled"] if previous else True)
            if not isinstance(enabled, bool):
                raise AppError("Enabled must be true or false.", 422, "validation_error")
            deleted = action == "delete"
            count = (docs[capacity_key] or {}).get("count", 0)
            change = 1 if not previous or action == "restore" else -1 if action == "delete" else 0
            if count + change > self.settings.skill_catalog_limit:
                raise AppError(
                    "The shared library is full. Delete a skill before adding another.", 409, "skill_capacity"
                )
            updates = {}
            for quota, limit in quotas:
                used = (docs[("quotas", quota)] or {}).get("count", 0)
                if used >= limit:
                    raise AppError("Skill editing limit reached. Please return later.", 429, "usage_limit")
                updates[("quotas", quota)] = {"id": quota, "count": used + 1}
            value = validated | {
                "id": skill_id,
                "enabled": enabled,
                "deleted": deleted,
                "revision": previous["revision"] + 1 if previous else 1,
                "created_at": previous["created_at"] if previous else now_iso(),
                "updated_at": now_iso(),
                "created_by": previous["created_by"] if previous else guest_id,
                "updated_by": guest_id,
            }
            updates.update(
                {
                    key: value,
                    capacity_key: {"count": count + change},
                    (f"skills/{skill_id}/revisions", str(value["revision"])): value,
                }
            )
            if author_key:
                updates[author_key] = author | {
                    "published_skill_id": skill_id,
                    "status": "published",
                    "revision": author["revision"] + 1,
                    "updated_at": now_iso(),
                }
            return updates, public_skill(value)

        return await self.store.atomic(keys, update)

    async def attach(self, conversation_id, body):
        conversation_key = ("conversations", conversation_id)
        skill_keys = [("skills", key) for key in body.skill_ids]

        def update(docs):
            chat = docs[conversation_key]
            if not chat:
                raise AppError("Conversation not found.", 404, "not_found")
            if chat.get("active_run") and chat.get("lease_until", 0) > time.time():
                raise AppError(
                    "Wait for this exploration to finish before changing skills.", 409, "conversation_busy"
                )
            if chat.get("skills_revision", 0) != body.expected_revision:
                raise AppError(
                    "Someone changed this chat's skills. Reload and try again.", 409, "skill_conflict"
                )
            for key in skill_keys:
                self.require_available(docs[key], chat["source"])
            chat.update(
                skill_ids=body.skill_ids, skills_revision=body.expected_revision + 1, updated_at=now_iso()
            )
            return {conversation_key: chat}, chat

        return await self.store.atomic([conversation_key, *skill_keys], update)

    @staticmethod
    def require_available(skill, source):
        if not skill or skill.get("deleted") or not skill.get("enabled") or not compatible(skill, source):
            raise AppError(
                "An attached skill is deleted, disabled, or incompatible. Remove it from Attach skills before continuing.",
                409,
                "skill_unavailable",
            )

    async def select(self, question, history, source, pinned_ids, ai, analysis_id):
        selected = []
        for skill_id in pinned_ids:
            skill = await self.store.get("skills", skill_id)
            self.require_available(skill, source)
            selected.append(public_skill(skill) | {"mode": "manual"})
        candidates = [
            s
            for s in await self.list()
            if s["enabled"] and compatible(s, source) and s["id"] not in pinned_ids
        ]
        warnings = []
        if candidates and len(selected) < 3:
            metadata = [
                {k: s[k] for k in ("id", "name", "description", "when_to_use", "source", "tags")}
                for s in candidates
            ]
            try:
                choices = await ai.choose_skills(question, history, metadata, 3 - len(selected), analysis_id)
                if (
                    len(set(choices)) != len(choices)
                    or len(choices) > 3 - len(selected)
                    or any(c not in {s["id"] for s in candidates} for c in choices)
                ):
                    raise ValueError("Invalid skill selection")
                selected.extend(
                    s | {"mode": "automatic"} for key in choices for s in candidates if s["id"] == key
                )
            except (AppError, APIError, ValidationError, ValueError, TimeoutError):
                warnings.append(
                    "Automatic skill selection is unavailable. Valid manual attachments are still applied."
                )
        # Freeze selected revisions atomically before SQL. Deleted/changed automatic candidates are skipped;
        # changed manual content gets its latest valid revision at this snapshot boundary.
        keys = [("skills", s["id"]) for s in selected]

        def snapshot(docs):
            frozen = []
            for item, key in zip(selected, keys):
                current = docs[key]
                if item["mode"] == "manual":
                    self.require_available(current, source)
                elif (
                    not current
                    or current["deleted"]
                    or not current["enabled"]
                    or not compatible(current, source)
                    or current["revision"] != item["revision"]
                ):
                    continue
                frozen.append(public_skill(current) | {"mode": item["mode"]})
            return {}, frozen

        return (await self.store.atomic(keys, snapshot) if keys else []), warnings


class FrontmatterLoader(yaml.SafeLoader):
    def compose_node(self, parent, index):
        if self.check_event(yaml.AliasEvent):
            raise ValueError("YAML aliases are not supported.")
        return super().compose_node(parent, index)

    def construct_mapping(self, node, deep=False):
        pairs = self.construct_pairs(node, deep=deep)
        result = {}
        for key, value in pairs:
            if not isinstance(key, str) or key in result:
                raise ValueError("Frontmatter requires unique text keys.")
            result[key] = value
        return result


def import_skill(markdown):
    if len(markdown.encode("utf-8")) > 24576:
        raise AppError("SKILL.md must fit within 24 KiB, including frontmatter.", 422, "invalid_skill_file")
    parts = markdown.removeprefix("\ufeff").replace("\r\n", "\n").split("\n")
    if not parts or parts[0] != "---":
        raise AppError(
            "SKILL.md needs YAML frontmatter with name and description.", 422, "invalid_skill_file"
        )
    try:
        end = parts.index("---", 1)
        header = "\n".join(parts[1:end])
        if len(header.encode()) > 8192:
            raise ValueError("Frontmatter exceeds 8 KiB.")
        metadata = yaml.load(header, Loader=FrontmatterLoader)
        if not isinstance(metadata, dict):
            raise ValueError("Frontmatter must be a mapping.")
        if not isinstance(metadata.get("name"), str) or not isinstance(metadata.get("description"), str):
            raise ValueError("Name and description must be text.")
        extra = metadata.get("metadata", {})
        extra = extra.get("querylane", {}) if isinstance(extra, dict) else {}
        if not isinstance(extra, dict):
            raise ValueError("metadata.querylane must be a mapping.")
        value = SkillContent.model_validate(
            {
                "name": extra.get("display_name", metadata["name"]),
                "description": metadata["description"],
                "when_to_use": extra.get("when_to_use", metadata["description"]),
                "source": extra.get("source", "all"),
                "tags": extra.get("tags", []),
                "instructions": "\n".join(parts[end + 1 :]).strip(),
            }
        )
        return value
    except (ValueError, yaml.YAMLError, RecursionError) as exc:
        raise AppError(
            "Invalid SKILL.md frontmatter or fields. Use name, description, and a non-empty Markdown body.",
            422,
            "invalid_skill_file",
        ) from exc


def export_skill(skill):
    slug = re.sub(r"[^a-z0-9]+", "-", skill["name"].lower()).strip("-") or "querylane-skill"
    header = {
        "name": slug,
        "description": skill["description"],
        "metadata": {
            "querylane": {
                "display_name": skill["name"],
                "when_to_use": skill["when_to_use"],
                "source": skill["source"],
                "tags": skill["tags"],
            }
        },
    }
    return (
        "---\n"
        + yaml.safe_dump(header, sort_keys=False, allow_unicode=True)
        + "---\n\n"
        + skill["instructions"]
        + "\n"
    )


def skill_router(guest):
    router = APIRouter(prefix="/api/v1")

    def service(request):
        return request.app.state.services.analysis.skills

    @router.get("/skills")
    async def listing(request: Request, deleted: bool = False):
        return {"skills": await service(request).list(deleted)}

    @router.post("/skills/import")
    async def preview(body: SkillImport, guest_id=Depends(guest)):
        return import_skill(body.markdown)

    @router.post("/skills", status_code=201)
    async def create(body: SkillContent, request: Request, guest_id=Depends(guest)):
        return await service(request).mutate(guest_id, content=body)

    @router.get("/skills/{skill_id}")
    async def detail(skill_id: str, request: Request):
        return public_skill(await service(request).get(skill_id))

    @router.get("/skills/{skill_id}/export")
    async def export(skill_id: str, request: Request):
        return PlainTextResponse(
            export_skill(await service(request).get(skill_id)),
            headers={"Content-Disposition": 'attachment; filename="SKILL.md"'},
        )

    @router.get("/skills/{skill_id}/revisions")
    async def revisions(skill_id: str, request: Request):
        await service(request).get(skill_id)
        values = await service(request).store.list(
            f"skills/{skill_id}/revisions",
            order_by="revision",
            descending=True,
            fields=SUMMARY_FIELDS,
        )
        return {"revisions": [public_skill(v) for v in values]}

    @router.get("/skills/{skill_id}/revisions/{revision}")
    async def revision(skill_id: str, revision: int, request: Request):
        return public_skill(await service(request).get(skill_id, revision))

    @router.patch("/skills/{skill_id}")
    async def edit(skill_id: str, body: SkillPatch, request: Request, guest_id=Depends(guest)):
        return await service(request).mutate(
            guest_id, skill_id=skill_id, patch=body.model_dump(exclude_unset=True), action="update"
        )

    @router.delete("/skills/{skill_id}")
    async def delete(
        skill_id: str, request: Request, expected_revision: int = Query(ge=1), guest_id=Depends(guest)
    ):
        return await service(request).mutate(
            guest_id, skill_id=skill_id, patch={"expected_revision": expected_revision}, action="delete"
        )

    @router.post("/skills/{skill_id}/restore")
    async def restore(skill_id: str, body: RevisionCheck, request: Request, guest_id=Depends(guest)):
        return await service(request).mutate(
            guest_id, skill_id=skill_id, patch=body.model_dump(), action="restore"
        )

    @router.patch("/conversations/{conversation_id}/skills")
    async def attach(conversation_id: str, body: SkillAttachments, request: Request, guest_id=Depends(guest)):
        return await service(request).attach(conversation_id, body)

    return router
