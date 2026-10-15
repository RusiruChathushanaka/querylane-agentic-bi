from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, create_autospec

from google.cloud.firestore_v1 import CollectionReference

from app.adk_sessions import FirestoreSessionService
from app.ai import AI
from app.config import Settings
from app.connectors import Connectors
from app.storage import MemoryStore


async def test_vector_query_uses_pinned_sdk_signature_and_dimensions():
    settings = Settings()
    store = MemoryStore()
    ai = AI(settings, FirestoreSessionService(store), Connectors(settings), store)
    settings.ai_backend = "gemini"
    collection = create_autospec(CollectionReference, instance=True)
    collection.find_nearest.return_value.get.return_value = [
        Mock(
            to_dict=Mock(
                return_value={
                    "source": "bigquery",
                    "table": "orders",
                    "embedding_model": settings.embedding_model,
                    "embedding_dimensions": 768,
                }
            )
        )
    ]
    store.client = SimpleNamespace(collection=Mock(return_value=collection))
    ai.embedding_client = SimpleNamespace(
        aio=SimpleNamespace(
            models=SimpleNamespace(
                embed_content=AsyncMock(
                    return_value=SimpleNamespace(embeddings=[SimpleNamespace(values=[0.1] * 768)])
                )
            )
        )
    )
    schema, mode = await ai.retrieve("Monthly revenue", ["bigquery"])
    assert mode == "gemini-embedding + full-schema"
    assert schema[0]["table"] == "orders"
    assert collection.find_nearest.call_args.kwargs["limit"] == 8
    assert collection.find_nearest.call_args.kwargs["vector_field"] == "embedding"
