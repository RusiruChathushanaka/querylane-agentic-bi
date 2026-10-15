import hashlib
import time
import uuid
from contextvars import ContextVar
from datetime import UTC, datetime

from app.errors import AppError, StaleLease

active_lease: ContextVar[dict | None] = ContextVar("active_lease", default=None)


def now_iso() -> str:
    return datetime.now(UTC).isoformat()


def check_lease(conversation: dict | None, lease: dict):
    if (
        not conversation
        or conversation.get("active_run") != lease["run_id"]
        or conversation.get("generation") != lease["generation"]
        or conversation.get("lease_until", 0) < time.time()
    ):
        raise StaleLease()


class Repository:
    def __init__(self, store, settings):
        self.store, self.settings = store, settings

    async def quota(self, keys: list[tuple[str, int]]):
        doc_keys = [("quotas", key) for key, _ in keys]

        def mutate(docs):
            updates = {}
            for (key, limit), doc_key in zip(keys, doc_keys):
                count = (docs[doc_key] or {}).get("count", 0)
                if count >= limit:
                    raise AppError("Demo usage limit reached. Please return later.", 429, "usage_limit")
                updates[doc_key] = {"id": key, "count": count + 1}
            return updates, None

        await self.store.atomic(doc_keys, mutate)

    async def conversation(self, conversation_id: str):
        result = await self.store.get("conversations", conversation_id)
        if not result:
            raise AppError("Conversation not found.", 404, "not_found")
        return result

    async def create_conversation(self, title: str, source: str, parent: str | None = None):
        conversation_id = uuid.uuid4().hex
        conversation = {
            "id": conversation_id,
            "title": title,
            "source": source,
            "parent_id": parent,
            "created_at": now_iso(),
            "updated_at": now_iso(),
            "generation": 0,
            "active_run": None,
            "lease_until": 0,
            "visibility": "public",
            "skill_ids": [],
            "skills_revision": 0,
        }
        await self.store.put("conversations", conversation_id, conversation)
        return conversation

    async def messages(self, conversation_id: str):
        return sorted(
            await self.store.list(
                f"conversations/{conversation_id}/messages", order_by="created_at", descending=True
            ),
            key=lambda m: (m["created_at"], m["id"]),
        )

    async def fork(self, conversation_id: str):
        original = await self.conversation(conversation_id)
        # Copy a consistent completed prefix. Active runs cannot be forked mid-write.
        if original.get("active_run") and original.get("lease_until", 0) > time.time():
            messages = [m for m in await self.messages(conversation_id) if m.get("status") == "complete"]
        else:
            messages = await self.messages(conversation_id)
        fork = await self.create_conversation(
            f"Fork: {original['title']}"[:100], original["source"], conversation_id
        )
        fork["skill_ids"] = original.get("skill_ids", [])
        await self.store.put("conversations", fork["id"], fork)
        for message in messages:
            await self.store.put(f"conversations/{fork['id']}/messages", message["id"], message)
        return fork

    async def begin(
        self, conversation_id: str, guest_id: str, question: str, idempotency_key: str, voice: bool = False
    ):
        run_id = hashlib.sha256(f"{conversation_id}:{guest_id}:{idempotency_key}".encode()).hexdigest()[:32]
        fingerprint = hashlib.sha256(question.encode()).hexdigest()
        conversation_key, run_key = ("conversations", conversation_id), ("runs", run_id)
        hour = datetime.now(UTC).strftime("%Y%m%d%H")
        day = hour[:8]
        quotas = [
            (f"guest_{guest_id}_{hour}", self.settings.guest_hourly_limit),
            (f"workspace_{day}", self.settings.workspace_daily_limit),
        ]
        if voice:
            quotas.append((f"voice_{day}", self.settings.voice_daily_limit))
        keys = [conversation_key, run_key] + [("quotas", key) for key, _ in quotas]

        def mutate(docs):
            existing = docs[run_key]
            if existing:
                if existing["fingerprint"] != fingerprint:
                    raise AppError(
                        "Idempotency key already belongs to another question.", 409, "idempotency_conflict"
                    )
                return {}, (existing, False)
            conversation = docs[conversation_key]
            if not conversation:
                raise AppError("Conversation not found.", 404, "not_found")
            if conversation.get("active_run") and conversation.get("lease_until", 0) > time.time():
                raise AppError(
                    "Someone is already exploring this chat. Wait or fork it to continue.",
                    409,
                    "conversation_busy",
                )
            updates = {}
            for key, limit in quotas:
                value = (docs[("quotas", key)] or {}).get("count", 0)
                if value >= limit:
                    raise AppError("Demo usage limit reached. Please return later.", 429, "usage_limit")
                updates[("quotas", key)] = {"id": key, "count": value + 1}
            generation = conversation.get("generation", 0) + 1
            run = {
                "id": run_id,
                "conversation_id": conversation_id,
                "guest_id": guest_id,
                "fingerprint": fingerprint,
                "question": question,
                "generation": generation,
                "status": "running",
                "sequence": 0,
                "cancel_requested": False,
                "kind": "voice" if voice else "text",
                "created_at": now_iso(),
                "skill_ids": list(conversation.get("skill_ids", [])),
            }
            conversation.update(
                active_run=run_id,
                generation=generation,
                lease_until=time.time() + self.settings.lease_seconds,
                updated_at=now_iso(),
            )
            if conversation["title"] == "New exploration" and not voice:
                conversation["title"] = question[:90]
            updates.update({conversation_key: conversation, run_key: run})
            if not voice:
                updates[(f"conversations/{conversation_id}/messages", run_id + "_user")] = {
                    "id": run_id + "_user",
                    "run_id": run_id,
                    "role": "user",
                    "text": question,
                    "created_at": now_iso(),
                    "status": "complete",
                }
            return updates, (run, True)

        return await self.store.atomic(keys, mutate)

    async def renew(self, lease: dict):
        key, run_key = ("conversations", lease["conversation_id"]), ("runs", lease["run_id"])

        def mutate(docs):
            check_lease(docs[key], lease)
            if (docs[run_key] or {}).get("cancel_requested"):
                raise AppError("Analysis cancelled.", code="cancelled")
            conversation = docs[key]
            conversation["lease_until"] = time.time() + self.settings.lease_seconds
            return {key: conversation}, None

        await self.store.atomic([key, run_key], mutate)

    async def write(self, collection: str, key: str, value: dict):
        lease = active_lease.get()
        if not lease:
            await self.store.put(collection, key, value)
            return
        conversation_key = ("conversations", lease["conversation_id"])

        def mutate(docs):
            check_lease(docs[conversation_key], lease)
            return {(collection, key): value}, None

        await self.store.atomic([conversation_key], mutate)

    async def emit(self, event_type: str, payload: dict):
        lease = active_lease.get()
        if not lease:
            return
        conversation_key, run_key = ("conversations", lease["conversation_id"]), ("runs", lease["run_id"])

        def mutate(docs):
            check_lease(docs[conversation_key], lease)
            run = docs[run_key]
            run["sequence"] += 1
            event = {"id": run["sequence"], "type": event_type, "data": payload, "created_at": now_iso()}
            return {run_key: run, (f"runs/{lease['run_id']}/events", f"{run['sequence']:08d}"): event}, event

        return await self.store.atomic([conversation_key, run_key], mutate)

    async def finish(self, status: str):
        lease = active_lease.get()
        conversation_key, run_key = ("conversations", lease["conversation_id"]), ("runs", lease["run_id"])

        def mutate(docs):
            check_lease(docs[conversation_key], lease)
            conversation, run = docs[conversation_key], docs[run_key]
            conversation.update(active_run=None, lease_until=0, updated_at=now_iso())
            run.update(status=status, finished_at=now_iso())
            return {conversation_key: conversation, run_key: run}, None

        await self.store.atomic([conversation_key, run_key], mutate)

    async def run(self, run_id: str):
        run = await self.store.get("runs", run_id)
        if not run:
            raise AppError("Analysis not found.", 404, "not_found")
        if run["status"] == "running":
            run_key = ("runs", run_id)
            conversation_key = ("conversations", run["conversation_id"])

            def snapshot(docs):
                current, conversation = docs[run_key], docs[conversation_key]
                if not current:
                    raise AppError("Analysis not found.", 404, "not_found")
                # finish() updates both documents atomically. Read them in one
                # snapshot so completion cannot look like a lost worker lease.
                if current["status"] == "running" and (
                    not conversation
                    or conversation.get("active_run") != run_id
                    or conversation.get("lease_until", 0) < time.time()
                ):
                    current["status"] = "interrupted"
                    current["error"] = (
                        "The worker stopped. Start a new turn; reconnecting will not rerun queries."
                    )
                return {}, current

            return await self.store.atomic([run_key, conversation_key], snapshot)
        return run
