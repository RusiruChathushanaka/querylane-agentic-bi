"""Opt-in real Gemini Live/tool integration check; no microphone is recorded.

Run from Backend: python -m scripts.smoke_voice
"""

import asyncio
import json
from types import SimpleNamespace

from app.adk_sessions import FirestoreSessionService
from app.admin import operator_credentials
from app.ai import AI
from app.analysis import AnalysisService
from app.config import Settings
from app.connectors import Connectors
from app.repository import Repository
from app.storage import MemoryStore
from app.voice import voice_session


class VoiceHarness:
    def __init__(self):
        self.incoming = asyncio.Queue()
        self.events = []

    async def receive_json(self):
        return await self.incoming.get()

    async def send_json(self, event):
        self.events.append(event)
        if event["type"] == "ready":
            await self.incoming.put(
                {
                    "type": "text",
                    "text": "What is total gross retail revenue? Please query the data and answer briefly.",
                }
            )
        if event["type"] == "turn_complete" and all(
            any(item["type"] == required for item in self.events)
            for required in ["artifact", "audio", "transcript"]
        ):
            await self.incoming.put({"type": "stop"})


async def main():
    credentials = operator_credentials()
    settings = Settings(ai_backend="gemini", voice_max_seconds=100)
    store = MemoryStore()
    repo = Repository(store, settings)
    connectors = Connectors(settings)
    sessions = FirestoreSessionService(store)
    ai = AI(settings, sessions, connectors, store, credentials=credentials)
    analysis = AnalysisService(repo, connectors, ai, settings)
    services = SimpleNamespace(
        settings=settings,
        store=store,
        repo=repo,
        connectors=connectors,
        sessions=sessions,
        ai=ai,
        analysis=analysis,
        credentials=credentials,
    )
    conversation = await repo.create_conversation("Live integration smoke", "all")
    harness = VoiceHarness()
    try:
        await voice_session(harness, services, "smoke-guest", conversation["id"])
        types = [event["type"] for event in harness.events]
        result = {
            "ready": "ready" in types,
            "artifact": "artifact" in types,
            "audio": "audio" in types,
            "transcript": "transcript" in types,
            "turn_complete": "turn_complete" in types,
            "errors": [event for event in harness.events if event["type"] == "error"],
            "audio_recorded": False,
            "input": "text sent through the live transport; microphone hardware not tested",
        }
        print(json.dumps(result, indent=2))
        return (
            all(result[key] for key in ["ready", "artifact", "audio", "transcript", "turn_complete"])
            and not result["errors"]
        )
    finally:
        await analysis.close()
        await ai.close()


if __name__ == "__main__":
    raise SystemExit(0 if asyncio.run(main()) else 1)
