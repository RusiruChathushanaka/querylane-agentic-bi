"""Small document interface with atomic, retry-safe read/modify/write operations."""

from __future__ import annotations

import asyncio
import copy
import random
import time
from collections.abc import Callable
from typing import Any

from app.errors import AppError
from app.read_performance import record_read

Key = tuple[str, str]
Mutation = Callable[[dict[Key, dict | None]], tuple[dict[Key, dict | None], Any]]


class MemoryStore:
    def __init__(self):
        self.documents: dict[Key, dict] = {}
        self.lock = asyncio.Lock()

    async def get(self, collection: str, key: str) -> dict | None:
        return copy.deepcopy(self.documents.get((collection, key)))

    async def put(self, collection: str, key: str, value: dict) -> None:
        async with self.lock:
            self.documents[(collection, key)] = copy.deepcopy(value)

    async def delete(self, collection: str, key: str) -> None:
        async with self.lock:
            self.documents.pop((collection, key), None)

    async def list(
        self,
        collection: str,
        limit: int = 1000,
        *,
        order_by: str | None = None,
        descending: bool = False,
        where: tuple[str, object] | tuple[str, str, object] | None = None,
        fields: list[str] | None = None,
    ) -> list[dict]:
        values = [v for (c, _), v in self.documents.items() if c == collection]
        if where:
            field, op, value = (where[0], "==", where[1]) if len(where) == 2 else where
            if op == "==":
                values = [v for v in values if v.get(field) == value]
            elif op == ">":
                values = [v for v in values if v.get(field) is not None and v[field] > value]
            else:
                raise ValueError("Unsupported storage filter.")
        if order_by:
            values.sort(key=lambda value: value[order_by], reverse=descending)
        if fields is not None:
            values = [{key: value[key] for key in fields if key in value} for value in values]
        return copy.deepcopy(values[:limit])

    async def atomic(self, keys: list[Key], mutate: Mutation):
        async with self.lock:
            updates, result = mutate({k: copy.deepcopy(self.documents.get(k)) for k in keys})
            for key, value in updates.items():
                if value is None:
                    self.documents.pop(key, None)
                else:
                    self.documents[key] = copy.deepcopy(value)
            return copy.deepcopy(result)

    async def close(self):
        pass

    async def iter_documents(self, collection):
        # Snapshot the identifiers; maintenance fences prevent new owned writes.
        keys = [key for col, key in self.documents if col == collection]
        for key in keys:
            value = await self.get(collection, key)
            if value is not None:
                yield key, value

    async def delete_tree(self, path):
        async with self.lock:
            for key in list(self.documents):
                full = f"{key[0]}/{key[1]}"
                if full == path or full.startswith(path + "/"):
                    del self.documents[key]


class FirestoreStore:
    def __init__(self, project: str, database: str, credentials=None):
        from google.cloud import firestore

        self.client = firestore.Client(project=project, database=database, credentials=credentials)

    async def get(self, collection: str, key: str) -> dict | None:
        started = time.perf_counter()
        try:
            snapshot = await asyncio.to_thread(self.client.collection(collection).document(key).get)
            return snapshot.to_dict() if snapshot.exists else None
        finally:
            record_read("firestore", time.perf_counter() - started)

    async def put(self, collection: str, key: str, value: dict) -> None:
        await asyncio.to_thread(self.client.collection(collection).document(key).set, value)

    async def delete(self, collection: str, key: str) -> None:
        await asyncio.to_thread(self.client.collection(collection).document(key).delete)

    async def iter_documents(self, collection):
        # Separate bounded RPCs: deleting a page may take longer than a stream's
        # deadline. Snapshot cursors remain valid after deleting that document.
        query = self.client.collection(collection).order_by("__name__").limit(100)
        while batch := await asyncio.to_thread(lambda: list(query.stream())):
            for snapshot in batch:
                yield snapshot.id, snapshot.to_dict()
            query = query.start_after(batch[-1])

    async def delete_tree(self, path):
        ref = self.client.collection(path) if len(path.split("/")) % 2 else self.client.document(path)
        await asyncio.to_thread(self.client.recursive_delete, ref)

    async def list(
        self,
        collection: str,
        limit: int = 1000,
        *,
        order_by: str | None = None,
        descending: bool = False,
        where: tuple[str, object] | tuple[str, str, object] | None = None,
        fields: list[str] | None = None,
    ) -> list[dict]:
        from google.cloud import firestore

        query = self.client.collection(collection)
        if where:
            from google.cloud.firestore_v1.base_query import FieldFilter

            field, op, value = (where[0], "==", where[1]) if len(where) == 2 else where
            if op not in {"==", ">"}:
                raise ValueError("Unsupported storage filter.")
            query = query.where(filter=FieldFilter(field, op, value))
        if fields is not None:
            query = query.select(fields)
        if order_by:
            query = query.order_by(
                order_by, direction=firestore.Query.DESCENDING if descending else firestore.Query.ASCENDING
            )
        started = time.perf_counter()
        try:
            return await asyncio.to_thread(
                lambda: [snapshot.to_dict() for snapshot in query.limit(limit).stream()]
            )
        finally:
            record_read("firestore", time.perf_counter() - started)

    async def atomic(self, keys: list[Key], mutate: Mutation):
        from google.api_core.exceptions import Aborted
        from google.cloud import firestore

        def execute():
            refs = {key: self.client.collection(key[0]).document(key[1]) for key in keys}

            @firestore.transactional
            def operation(transaction):
                snapshots = {key: ref.get(transaction=transaction) for key, ref in refs.items()}
                updates, result = mutate(
                    {key: snap.to_dict() if snap.exists else None for key, snap in snapshots.items()}
                )
                for key, value in updates.items():
                    ref = self.client.collection(key[0]).document(key[1])
                    if value is None:
                        transaction.delete(ref)
                    else:
                        transaction.set(ref, value)
                return result

            # The SDK retries aborted commits, but an Aborted raised by a read
            # in the callback escapes that retry loop. Re-read in a fresh
            # transaction so a competing request observes the committed winner.
            for attempt in range(3):
                try:
                    return operation(self.client.transaction())
                except Aborted as exc:
                    if attempt == 2:
                        raise AppError(
                            "The workspace is busy. Retry this action shortly.", 409, "transaction_busy"
                        ) from exc
                    time.sleep(random.uniform(0.025, 0.075) * 2**attempt)
                except ValueError as exc:
                    # Commit retries are already bounded by the SDK. Do not
                    # multiply that budget or hide unrelated callback errors.
                    if not isinstance(exc.__cause__, Aborted):
                        raise
                    raise AppError(
                        "The workspace is busy. Retry this action shortly.", 409, "transaction_busy"
                    ) from exc

        return await asyncio.to_thread(execute)

    async def close(self):
        await asyncio.to_thread(self.client.close)
