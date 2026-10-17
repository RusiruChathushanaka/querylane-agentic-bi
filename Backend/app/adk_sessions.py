"""Durable ADK session adapter with ordered events and fenced state writes."""

import hashlib
import time
import uuid

from google.adk.events import Event
from google.adk.sessions import BaseSessionService, Session
from google.adk.sessions.base_session_service import GetSessionConfig, ListSessionsResponse

from app.errors import StaleLease
from app.report_repository import active_report_lease
from app.repository import active_lease, check_lease


class FirestoreSessionService(BaseSessionService):
    def __init__(self, store, collection="adk_sessions"):
        self.store, self.collection = store, collection

    @staticmethod
    def key(app_name, user_id, session_id):
        return hashlib.sha256(f"{app_name}:{user_id}:{session_id}".encode()).hexdigest()

    async def create_session(
        self,
        *,
        app_name: str,
        user_id: str,
        state: dict | None = None,
        session_id: str | None = None,
        **kwargs,
    ):
        session = Session(
            id=session_id or uuid.uuid4().hex,
            app_name=app_name,
            user_id=user_id,
            state=state or {},
            last_update_time=time.time(),
        )
        key = self.key(app_name, user_id, session.id)
        keys = [(self.collection, key)]
        lease = active_lease.get()
        report_lease = active_report_lease.get()
        if lease:
            keys.append((lease.get("collection", "conversations"), lease["conversation_id"]))
        if report_lease:
            keys.append(("report_runs", report_lease["run_id"]))

        def mutate(docs):
            if lease:
                check_lease(docs[keys[1]], lease)
            if report_lease:
                current = docs[("report_runs", report_lease["run_id"])]
                if (
                    not current
                    or current["owner"] != report_lease["owner"]
                    or current["generation"] != report_lease["generation"]
                    or (current["status"] == "running" and current["lease_until"] <= time.time())
                ):
                    raise StaleLease()
            existing = docs[keys[0]]
            if existing:
                return {}, existing
            value = session.model_dump(exclude={"events"}, mode="json") | {"sequence": 0}
            return {keys[0]: value}, value

        result = await self.store.atomic(keys, mutate)
        loaded = Session.model_validate({k: v for k, v in result.items() if k != "sequence"})
        object.__setattr__(loaded, "_agentic_revision", result["sequence"])
        return loaded

    async def get_session(
        self, *, app_name: str, user_id: str, session_id: str, config: GetSessionConfig | None = None
    ):
        key = self.key(app_name, user_id, session_id)
        value = await self.store.get(self.collection, key)
        if not value:
            return None
        events = sorted(
            await self.store.list(
                f"{self.collection}/{key}/events",
                limit=config.num_recent_events if config and config.num_recent_events else 1000,
                order_by="sequence",
                descending=True,
            ),
            key=lambda item: item["sequence"],
        )
        if config and config.after_timestamp:
            events = [e for e in events if e["event"].get("timestamp", 0) > config.after_timestamp]
        if config and config.num_recent_events:
            events = events[-config.num_recent_events :]
        loaded = Session.model_validate(
            {k: v for k, v in value.items() if k != "sequence"}
            | {"events": [Event.model_validate(e["event"]) for e in events]}
        )
        object.__setattr__(loaded, "_agentic_revision", value["sequence"])
        return loaded

    async def list_sessions(self, *, app_name: str, user_id: str, **kwargs):
        values = await self.store.list(self.collection)
        sessions = [
            Session.model_validate({k: v for k, v in value.items() if k != "sequence"})
            for value in values
            if value["app_name"] == app_name and value["user_id"] == user_id
        ]
        return ListSessionsResponse(sessions=sessions)

    async def delete_session(self, *, app_name: str, user_id: str, session_id: str):
        key = self.key(app_name, user_id, session_id)
        # Called only by the credentialed administrative reset command.
        for item in await self.store.list(f"{self.collection}/{key}/events"):
            await self.store.delete(f"{self.collection}/{key}/events", f"{item['sequence']:08d}")
        await self.store.delete(self.collection, key)

    async def append_event(self, session: Session, event: Event):
        if event.partial:
            return event
        if (
            event.content
            and event.content.parts
            and all(part.inline_data is not None for part in event.content.parts)
            and not event.actions.state_delta
            and not event.input_transcription
            and not event.output_transcription
        ):
            return event
        key = self.key(session.app_name, session.user_id, session.id)
        # Fence the exact loaded object. A later read through the same adapter
        # must not make an earlier, stale object eligible to overwrite state.
        expected = getattr(session, "_agentic_revision", 0)
        # Let ADK implement state-delta/temp-prefix semantics in the in-memory object.
        event = await super().append_event(session, event)
        payload = event.model_dump(mode="json", exclude_none=True)
        if payload.get("content"):
            payload["content"]["parts"] = [
                part
                for part in payload["content"].get("parts", [])
                if "inline_data" not in part and "inlineData" not in part
            ]
        session.last_update_time = max(session.last_update_time, event.timestamp)
        metadata = session.model_dump(mode="json", exclude={"events"})
        metadata["state"] = {
            key: value for key, value in metadata["state"].items() if not key.startswith("temp:")
        }
        lease = active_lease.get()
        report_lease = active_report_lease.get()
        keys = [(self.collection, key)]
        if lease:
            keys.append((lease.get("collection", "conversations"), lease["conversation_id"]))
        if report_lease:
            keys.append(("report_runs", report_lease["run_id"]))

        def mutate(docs):
            if lease:
                check_lease(docs[keys[1]], lease)
            if report_lease:
                current = docs[("report_runs", report_lease["run_id"])]
                if (
                    not current
                    or current["owner"] != report_lease["owner"]
                    or current["generation"] != report_lease["generation"]
                    or (current["status"] == "running" and current["lease_until"] <= time.time())
                ):
                    raise StaleLease()
            stored = docs[keys[0]]
            if not stored or stored["sequence"] != expected:
                raise StaleLease()
            sequence = expected + 1
            return {
                keys[0]: metadata | {"sequence": sequence},
                (f"{self.collection}/{key}/events", f"{sequence:08d}"): {
                    "sequence": sequence,
                    "event": payload,
                },
            }, sequence

        revision = await self.store.atomic(keys, mutate)
        object.__setattr__(session, "_agentic_revision", revision)
        return event
