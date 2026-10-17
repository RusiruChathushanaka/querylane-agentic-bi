"""Transient requester-only Google Search. Never uses the public Firestore ADK service."""

import asyncio
from contextlib import aclosing
from datetime import UTC, datetime

from google.adk.agents import LlmAgent
from google.adk.agents.run_config import RunConfig
from google.adk.apps import App
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types

from app.errors import AppError
from app.model_selection import resolve_text_model


async def research_panel(services, guest_id, body):
    if not services.settings.report_research_enabled or not services.ai.client:
        raise AppError(
            "External research is not enabled. Reports continue using database evidence.",
            503,
            "research_disabled",
        )
    day = datetime.now(UTC).strftime("%Y%m%d")
    await services.repo.quota(
        [(f"report_research_guest_{guest_id}_{day}", 3), (f"report_research_workspace_{day}", 12)]
    )
    model = resolve_text_model(services.settings, body.model)
    agent = LlmAgent(
        name="retail_research",
        model=Gemini(model=model, client=services.ai.client),
        instruction="Research the supplied public retail topic using Google Search. No database access, private context, or report writing is available. Cite supporting sources. Keep the answer concise.",
        tools=[google_search],
        generate_content_config=types.GenerateContentConfig(
            max_output_tokens=2048,
            http_options=types.HttpOptions(timeout=45000, retry_options=types.HttpRetryOptions(attempts=1)),
        ),
    )
    sessions = InMemorySessionService()
    await sessions.create_session(app_name="querylane_research", user_id="requester", session_id="panel")
    runner = Runner(app=App(name="querylane_research", root_agent=agent), session_service=sessions)
    text, grounding = "", None
    # No raw question/rows/schema/history enter this request. Topic is an allowlisted enum.
    async with (
        asyncio.timeout(55),
        aclosing(
            runner.run_async(
                user_id="requester",
                session_id="panel",
                new_message=types.Content(role="user", parts=[types.Part(text=body.topic)]),
                run_config=RunConfig(max_llm_calls=1),
            )
        ) as events,
    ):
        async for event in events:
            if event.error_code:
                raise AppError(
                    "Search is unavailable for the selected model or location. The report is unaffected.",
                    502,
                    "research_unavailable",
                )
            if event.is_final_response() and event.content:
                text = "".join(p.text or "" for p in event.content.parts if not p.thought)
            if event.grounding_metadata:
                grounding = event.grounding_metadata.model_dump(mode="json", exclude_none=True)
    if not text or not grounding:
        raise AppError(
            "Search returned no grounded result. The report is unaffected.", 502, "research_unavailable"
        )
    return {"text": text, "grounding": grounding, "visibility": "requester-only", "persistent": False}
