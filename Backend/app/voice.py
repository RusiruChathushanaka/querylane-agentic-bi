import asyncio
import base64
import contextlib
import logging
import time
import uuid
from datetime import UTC, datetime

from google.adk.agents import LiveRequestQueue, LlmAgent
from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.genai import Client, types
from starlette.websockets import WebSocketDisconnect

from app.errors import AppError
from app.repository import active_lease

logger = logging.getLogger(__name__)


async def voice_session(websocket, services, guest_id, conversation_id, model=None):
    settings, repo, analysis, sessions = (
        services.settings,
        services.repo,
        services.analysis,
        services.sessions,
    )
    if settings.ai_backend != "gemini":
        await websocket.send_json(
            {
                "type": "error",
                "message": "Live voice needs Gemini configuration. Local sample mode supports text only.",
            }
        )
        return
    run, _ = await repo.begin(
        conversation_id, guest_id, "Live voice exploration", uuid.uuid4().hex, voice=True, model=model
    )
    lease = {"run_id": run["id"], "conversation_id": conversation_id, "generation": run["generation"]}
    token = active_lease.set(lease)
    heartbeat = asyncio.create_task(analysis.heartbeat(lease))
    queue = LiveRequestQueue()
    send_lock = asyncio.Lock()
    client = None
    try:
        client = Client(
            vertexai=True,
            project=settings.google_cloud_project,
            location=settings.live_model_location,
            credentials=getattr(services, "credentials", None),
        )
        observed_transcript = {"user": "", "assistant": ""}
        persisted_transcript = {"user": "", "assistant": ""}

        async def flush_transcript(role):
            text = observed_transcript[role].strip()
            if text and text != persisted_transcript[role]:
                await analysis.save_message(conversation_id, role, text[:12000])
                persisted_transcript[role] = text

        async def send(payload):
            async with send_lock:
                await websocket.send_json(payload)

        async def analyze_data(question: str) -> dict:
            """Analyze a retail data question; execute controlled read-only queries and return charts plus evidence."""
            hour = datetime.now(UTC).strftime("%Y%m%d%H")
            await repo.quota(
                [
                    (f"guest_{guest_id}_{hour}", settings.guest_hourly_limit),
                    (f"workspace_{hour[:8]}", settings.workspace_daily_limit),
                ]
            )
            await flush_transcript("user")
            # Tool-created text and chart answers use the same fenced conversation as live events.
            result = await analysis.execute(question[:4000], conversation_id)
            if result.get("artifact_id"):
                artifact = await repo.store.get("artifacts", result["artifact_id"])
                await send({"type": "artifact", "data": artifact})
            return result

        agent = LlmAgent(
            name="retail_voice_analyst",
            model=Gemini(model=settings.live_model, client=client),
            instruction="You are a concise English retail analyst in a public demo workspace. Use analyze_data for EVERY question about data, even follow-ups; never invent numbers. Explain important inferred relationship assumptions. "
            + services.connectors.data_context
            + " Speak briefly and refer to charts shown in the workspace. You cannot change databases or reveal credentials. On tool errors explain the limitation. Do not expose hidden reasoning.",
            tools=[analyze_data],
        )
        session_id = f"{conversation_id}_voice_{guest_id}"
        if not await sessions.get_session(
            app_name="agentic_bi", user_id="public-demo", session_id=session_id
        ):
            await sessions.create_session(app_name="agentic_bi", user_id="public-demo", session_id=session_id)
        runner = Runner(agent=agent, app_name="agentic_bi", session_service=sessions)
        resume_key = f"{conversation_id}_{guest_id}"
        resume = await repo.store.get("voice_resumptions", resume_key)
        handle = resume.get("handle") if resume and resume.get("expires", 0) > time.time() else None
        config = RunConfig(
            streaming_mode=StreamingMode.BIDI,
            response_modalities=["AUDIO"],
            input_audio_transcription=types.AudioTranscriptionConfig(),
            output_audio_transcription=types.AudioTranscriptionConfig(),
            session_resumption=types.SessionResumptionConfig(handle=handle),
            context_window_compression=types.ContextWindowCompressionConfig(
                sliding_window=types.SlidingWindow()
            ),
            max_llm_calls=8,
            save_live_blob=False,
        )

    except BaseException:
        heartbeat.cancel()
        await asyncio.gather(heartbeat, return_exceptions=True)
        if client is not None:
            await client.aio.aclose()
        with contextlib.suppress(AppError):
            await repo.finish("failed")
        active_lease.reset(token)
        raise

    async def receive():
        await send(
            {
                "type": "ready",
                "run_id": run["id"],
                "input_rate": 16000,
                "output_rate": 24000,
                "max_seconds": settings.voice_max_seconds,
            }
        )
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "audio":
                encoded = data.get("data", "")
                if not isinstance(encoded, str) or len(encoded) > 44_000:
                    raise AppError("Audio frame exceeds the limit.")
                audio = base64.b64decode(encoded, validate=True)
                if len(audio) % 2:
                    raise AppError("Invalid PCM frame.")
                queue.send_realtime(types.Blob(data=audio, mime_type="audio/pcm;rate=16000"))
            elif data.get("type") == "text":
                text = str(data.get("text", ""))[:4000]
                queue.send_content(types.Content(role="user", parts=[types.Part(text=text)]))
            elif data.get("type") == "stop":
                break
            elif data.get("type") == "ping":
                await send({"type": "pong"})

    async def respond():
        async for event in runner.run_live(
            user_id="public-demo", session_id=session_id, live_request_queue=queue, run_config=config
        ):
            if event.error_code:
                raise AppError(
                    "The live model could not complete the conversation.", 502, "voice_model_error"
                )
            if event.interrupted:
                await send({"type": "interrupted"})
            for role, transcription in [
                ("user", event.input_transcription),
                ("assistant", event.output_transcription),
            ]:
                if transcription and transcription.text:
                    observed_transcript[role] = (
                        observed_transcript[role] + transcription.text
                        if event.partial
                        else transcription.text
                    )
                    await send(
                        {
                            "type": "transcript",
                            "role": role,
                            "text": transcription.text,
                            "replace": not event.partial,
                        }
                    )
            if event.content:
                for part in event.content.parts or []:
                    if (
                        part.inline_data
                        and part.inline_data.mime_type
                        and part.inline_data.mime_type.startswith("audio/")
                    ):
                        await send(
                            {
                                "type": "audio",
                                "data": base64.b64encode(part.inline_data.data).decode(),
                                "rate": 24000,
                            }
                        )
            if event.live_session_resumption_update and event.live_session_resumption_update.new_handle:
                await repo.write(
                    "voice_resumptions",
                    resume_key,
                    {
                        "handle": event.live_session_resumption_update.new_handle,
                        "expires": time.time() + 7200,
                    },
                )
            if event.go_away:
                await send(
                    {"type": "reconnect", "message": "Live connection is rotating. Reconnect to resume."}
                )
            if event.turn_complete:
                for role in ("user", "assistant"):
                    await flush_transcript(role)
                    observed_transcript[role] = ""
                    persisted_transcript[role] = ""
                await send({"type": "turn_complete"})

    tasks = []
    status = "complete"
    try:
        tasks = [asyncio.create_task(receive()), asyncio.create_task(respond()), heartbeat]
        done, _ = await asyncio.wait(
            tasks, timeout=settings.voice_max_seconds, return_when=asyncio.FIRST_COMPLETED
        )
        for task in done:
            task.result()
        if not done:
            await send(
                {
                    "type": "session_limit",
                    "message": "Voice session time limit reached. Your conversation is saved.",
                }
            )
    except WebSocketDisconnect:
        status = "interrupted"
    except Exception:
        status = "failed"
        logger.exception("Live session failed", extra={"run_id": run["id"]})
        with contextlib.suppress(Exception):
            await send(
                {
                    "type": "error",
                    "message": "Live voice is unavailable. Check model access or reconnect; text chat is still available.",
                }
            )
    finally:
        queue.close()
        for task in tasks:
            task.cancel()
        heartbeat.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        with contextlib.suppress(AppError):
            await repo.finish(status)
        if status != "complete":
            try:
                await services.connectors.cancel(run["id"])
            except Exception:
                logger.exception(
                    "Voice query cancellation could not be confirmed", extra={"run_id": run["id"]}
                )
        services.connectors.forget(run["id"])
        await client.aio.aclose()
        active_lease.reset(token)
