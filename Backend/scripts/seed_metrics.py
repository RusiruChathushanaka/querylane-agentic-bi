"""Explicit operator command: uv run python -m scripts.seed_metrics [--cloud]."""

import argparse
import asyncio

from app.config import Settings
from app.metric_examples import seed_metrics
from app.storage import FirestoreStore, MemoryStore


async def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cloud", action="store_true")
    args = parser.parse_args()
    settings = Settings()
    store = FirestoreStore(settings.google_cloud_project, settings.firestore_database) if args.cloud else MemoryStore()
    try:
        print({"created": await seed_metrics(store, settings), "storage": "firestore" if args.cloud else "ephemeral memory"})
    finally:
        await store.close()


if __name__ == "__main__":
    asyncio.run(main())
