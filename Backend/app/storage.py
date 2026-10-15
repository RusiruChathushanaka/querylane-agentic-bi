"""Small document interface with atomic, retry-safe read/modify/write operations."""

from __future__ import annotations

import asyncio
import copy
from collections.abc import Callable
from typing import Any

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
        self, collection: str, limit: int = 1000, *, order_by: str | None = None, descending: bool = False
    ) -> list[dict]:
        values = [v for (c, _), v in self.documents.items() if c == collection]
        if order_by:
            values.sort(key=lambda value: value[order_by], reverse=descending)
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


class FirestoreStore:
    def __init__(self, project: str, database: str, credentials=None):
        from google.cloud import firestore

        self.client = firestore.Client(project=project, database=database, credentials=credentials)

    async def get(self, collection: str, key: str) -> dict | None:
        snapshot = await asyncio.to_thread(self.client.collection(collection).document(key).get)
        return snapshot.to_dict() if snapshot.exists else None

    async def put(self, collection: str, key: str, value: dict) -> None:
        await asyncio.to_thread(self.client.collection(collection).document(key).set, value)

    async def delete(self, collection: str, key: str) -> None:
        await asyncio.to_thread(self.client.collection(collection).document(key).delete)

    async def list(
        self, collection: str, limit: int = 1000, *, order_by: str | None = None, descending: bool = False
    ) -> list[dict]:
        from google.cloud import firestore

        query = self.client.collection(collection)
        if order_by:
            query = query.order_by(
                order_by, direction=firestore.Query.DESCENDING if descending else firestore.Query.ASCENDING
            )
        return await asyncio.to_thread(
            lambda: [snapshot.to_dict() for snapshot in query.limit(limit).stream()]
        )

    async def atomic(self, keys: list[Key], mutate: Mutation):
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

            return operation(self.client.transaction())

        return await asyncio.to_thread(execute)

    async def close(self):
        await asyncio.to_thread(self.client.close)
