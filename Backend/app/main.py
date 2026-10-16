import asyncio
import contextlib
import hashlib
import json
import logging
import secrets
import time
from contextlib import asynccontextmanager
from datetime import UTC, date, datetime
from types import SimpleNamespace
from typing import Literal

from fastapi import Depends, FastAPI, Header, Query, Request, WebSocket
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from starlette.websockets import WebSocketDisconnect

from app.adk_sessions import FirestoreSessionService
from app.ai import AI
from app.analysis import AnalysisService
from app.chart_presentation import csv_line, present, saved_rows
from app.config import Settings, get_settings
from app.connectors import Connectors
from app.errors import AppError
from app.fixtures import SOURCE_TABLES
from app.model_selection import TEXT_MODELS, resolve_text_model
from app.models import ConversationCreate, TurnCreate
from app.repository import Repository
from app.skill_author import author_router
from app.skill_author_voice import skill_author_voice
from app.skills import skill_router
from app.storage import FirestoreStore, MemoryStore
from app.voice import voice_session

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


def create_app(settings: Settings | None = None, store_override=None, credentials=None):
    settings = settings or get_settings()
    settings.validate_runtime()
    signer = URLSafeTimedSerializer(settings.guest_signing_key, salt="agentic-bi-guest-v1")

    @asynccontextmanager
    async def lifespan(app):
        store = store_override or (
            FirestoreStore(
                settings.google_cloud_project, settings.firestore_database, credentials=credentials
            )
            if settings.storage_backend == "firestore"
            else MemoryStore()
        )
        repo = Repository(store, settings)
        connectors = Connectors(settings, credentials=credentials)
        await connectors.start()
        sessions = FirestoreSessionService(store)
        ai = AI(settings, sessions, connectors, store, credentials=credentials)
        analysis = AnalysisService(repo, connectors, ai, settings)
        app.state.services = SimpleNamespace(
            settings=settings,
            store=store,
            repo=repo,
            connectors=connectors,
            sessions=sessions,
            ai=ai,
            analysis=analysis,
            credentials=credentials,
        )
        try:
            yield
        finally:
            await analysis.close()
            await ai.close()
            await connectors.close()
            await store.close()

    app = FastAPI(title="Agentic BI", version="0.1.0", lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.origins,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Authorization", "Content-Type", "Last-Event-ID"],
        expose_headers=["X-Request-ID"],
    )

    @app.middleware("http")
    async def request_boundary(request: Request, call_next):
        try:
            body_limit = 65_536 if request.url.path.startswith("/api/v1/skills") else 32_768
            if int(request.headers.get("content-length", "0")) > body_limit:
                return JSONResponse(
                    {"error": {"code": "body_too_large", "message": "Request body exceeds the size limit."}},
                    status_code=413,
                )
        except ValueError:
            return JSONResponse(
                {"error": {"code": "invalid_request", "message": "Invalid content length."}}, status_code=400
            )
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.exception_handler(AppError)
    async def app_error(request, exc):
        return JSONResponse({"error": {"code": exc.code, "message": exc.message}}, status_code=exc.status)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        return JSONResponse(
            {"error": {"code": "validation_error", "message": "Check the question and request fields."}},
            status_code=422,
        )

    @app.exception_handler(Exception)
    async def unexpected_error(request, exc):
        logger.exception("Request failed: %s", request.url.path, exc_info=exc)
        return JSONResponse(
            {
                "error": {
                    "code": "internal_error",
                    "message": "The service could not complete this request. Try again later.",
                }
            },
            status_code=500,
        )

    def verify(token: str):
        try:
            data = signer.loads(token, max_age=21600)
            guest_id = data["guest_id"]
            if not isinstance(guest_id, str) or len(guest_id) != 32:
                raise BadSignature("Invalid guest")
            return guest_id
        except (BadSignature, SignatureExpired, KeyError):
            raise AppError("Guest session expired. Refresh to continue.", 401, "guest_expired")

    async def guest(authorization: str | None = Header(default=None)):
        if not authorization or not authorization.startswith("Bearer "):
            raise AppError("Start a guest session to continue.", 401, "guest_required")
        return verify(authorization[7:])

    app.include_router(author_router(guest))
    app.include_router(skill_router(guest))

    @app.get("/health/live")
    async def live():
        return {"status": "ok", "service": "agentic-bi-backend"}

    @app.get("/health/ready")
    async def ready(request: Request):
        services = request.app.state.services
        try:
            await services.store.get("system", "health")
            connections = await asyncio.gather(
                services.connectors.test("bigquery"), services.connectors.test("postgres")
            )
            healthy = all(connection["connected"] for connection in connections)
        except Exception:
            healthy = False
        return JSONResponse(
            {
                "status": "ready" if healthy else "degraded",
                "mode": "local-fixtures" if settings.ai_backend == "fixture" else "gemini",
                "storage": settings.storage_backend,
                "visibility": "public",
            },
            status_code=200 if healthy else 503,
        )

    @app.post("/api/v1/guest-sessions", status_code=201)
    async def guest_session(request: Request):
        origin = request.headers.get("origin")
        if origin and origin.rstrip("/") not in settings.origins:
            raise AppError("This origin is not enabled for the demo.", 403, "origin_denied")
        hour = datetime.now(UTC).strftime("%Y%m%d%H")
        ip = request.client.host if request.client else "unknown"
        ip_hash = hashlib.sha256((ip + settings.guest_signing_key).encode()).hexdigest()[:24]
        await request.app.state.services.repo.quota(
            [(f"session_ip_{ip_hash}_{hour}", 60), (f"sessions_{hour[:8]}", 1000)]
        )
        guest_id = secrets.token_hex(16)
        return {"token": signer.dumps({"guest_id": guest_id}), "expires_in": 21600, "visibility": "public"}

    @app.get("/api/v1/connections")
    async def connections(request: Request):
        services = request.app.state.services
        return {
            "mode": ("local-fixtures" if settings.ai_backend == "fixture" else "gemini-fixtures")
            if settings.data_backend == "fixture"
            else "cloud",
            "data_profile": settings.data_profile,
            "period": "DAILY · MULTI-YEAR" if settings.data_profile == "timeseries" else "JAN–SEP 2026",
            "connections": [
                {
                    "id": source,
                    "name": "Retail warehouse" if source == "bigquery" else "Business operations",
                    "engine": "BigQuery" if source == "bigquery" else "PostgreSQL",
                    "tables": len(services.connectors.source_tables[source]),
                    **await services.connectors.test(source),
                }
                for source in SOURCE_TABLES
            ],
        }

    @app.get("/api/v1/connections/{source}/schema")
    async def connection_schema(source: str, request: Request):
        if source not in SOURCE_TABLES:
            raise AppError("Source not found.", 404, "not_found")
        return {"tables": await request.app.state.services.ai.schema(source)}

    @app.get("/api/v1/conversations")
    async def conversations(request: Request):
        items = await request.app.state.services.store.list(
            "conversations", limit=100, order_by="updated_at", descending=True
        )
        return {"conversations": sorted(items, key=lambda c: c["updated_at"], reverse=True)[:100]}

    @app.post("/api/v1/conversations", status_code=201)
    async def create_conversation(body: ConversationCreate, request: Request, guest_id=Depends(guest)):
        hour = datetime.now(UTC).strftime("%Y%m%d%H")
        await request.app.state.services.repo.quota(
            [(f"new_chats_{guest_id}_{hour}", 20), (f"new_chats_{hour[:8]}", 300)]
        )
        return await request.app.state.services.repo.create_conversation(body.title, body.source)

    @app.get("/api/v1/conversations/{conversation_id}")
    async def get_conversation(conversation_id: str, request: Request):
        repo = request.app.state.services.repo
        return {
            "conversation": await repo.conversation(conversation_id),
            "messages": await repo.messages(conversation_id),
        }

    @app.post("/api/v1/conversations/{conversation_id}/fork", status_code=201)
    async def fork(conversation_id: str, request: Request, guest_id=Depends(guest)):
        hour = datetime.now(UTC).strftime("%Y%m%d%H")
        await request.app.state.services.repo.quota(
            [(f"new_chats_{guest_id}_{hour}", 20), (f"new_chats_{hour[:8]}", 300)]
        )
        return await request.app.state.services.repo.fork(conversation_id)

    @app.get("/api/v1/models")
    async def models():
        return {
            "models": TEXT_MODELS,
            "default_model": settings.text_model,
            "mode": settings.ai_backend,
            "live_model": settings.live_model,
        }

    @app.post("/api/v1/conversations/{conversation_id}/turns", status_code=202)
    async def turn(conversation_id: str, body: TurnCreate, request: Request, guest_id=Depends(guest)):
        run = await request.app.state.services.analysis.start(
            conversation_id, guest_id, body.question, body.idempotency_key, model=body.model
        )
        return {
            "run_id": run["id"],
            "status": run["status"],
            "events_url": f"/api/v1/runs/{run['id']}/events",
        }

    @app.get("/api/v1/runs/{run_id}")
    async def run_status(run_id: str, request: Request):
        run = await request.app.state.services.repo.run(run_id)
        return {k: v for k, v in run.items() if k not in ("guest_id", "fingerprint")}

    @app.post("/api/v1/runs/{run_id}/cancel")
    async def cancel_run(run_id: str, request: Request, guest_id=Depends(guest)):
        return await request.app.state.services.analysis.cancel(run_id, guest_id)

    @app.get("/api/v1/runs/{run_id}/events")
    async def events(run_id: str, request: Request, after: int = Query(default=0, ge=0)):
        repo = request.app.state.services.repo
        await repo.run(run_id)
        try:
            after = max(after, int(request.headers.get("last-event-id", "0")))
        except ValueError:
            raise AppError("Invalid event cursor.")

        async def stream():
            cursor, heartbeat_at = after, time.monotonic()
            while not await request.is_disconnected():
                persisted = sorted(
                    await repo.store.list(f"runs/{run_id}/events"), key=lambda event: event["id"]
                )
                for event in persisted:
                    if event["id"] > cursor:
                        cursor = event["id"]
                        yield f"id: {cursor}\nevent: {event['type']}\ndata: {json.dumps(event['data'])}\n\n"
                run = await repo.run(run_id)
                if run["status"] != "running":
                    # The worker can commit its final events after our list query
                    # and finish before this status read. Drain that committed
                    # sequence before closing, including on reconnect/replay.
                    if cursor < run["sequence"]:
                        continue
                    if run["status"] == "interrupted":
                        yield f"event: error\ndata: {json.dumps({'code': 'interrupted', 'message': run['error']})}\n\n"
                    break
                if time.monotonic() - heartbeat_at > 15:
                    yield ": keepalive\n\n"
                    heartbeat_at = time.monotonic()
                await asyncio.sleep(0.5)

        return StreamingResponse(
            stream(),
            media_type="text/event-stream",
            headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"},
        )

    @app.get("/api/v1/artifacts/{artifact_id}")
    async def artifact(artifact_id: str, request: Request):
        store = request.app.state.services.store
        artifact = await store.get("artifacts", artifact_id)
        if not artifact:
            raise AppError("Result not found.", 404, "not_found")
        rows = []
        for index in range(artifact["page_count"]):
            page = await store.get(f"artifacts/{artifact_id}/pages", str(index))
            rows.extend(page["rows"])
            if len(rows) >= settings.preview_rows:
                break
        return artifact | {"rows": rows[: settings.preview_rows]}

    chart_slots = asyncio.Semaphore(2)

    @app.get("/api/v1/artifacts/{artifact_id}/chart-data")
    async def chart_data(
        artifact_id: str,
        request: Request,
        start: date | None = None,
        end: date | None = None,
        primary: str | None = Query(default=None, max_length=128),
        order: Literal["value_desc", "value_asc", "label", "original"] = "value_desc",
        top: int = Query(default=10, ge=5, le=20),
        view: Literal["line", "area", "bar", "pie", "scatter", "kpi"] | None = None,
    ):
        store = request.app.state.services.store
        artifact = await store.get("artifacts", artifact_id)
        if not artifact:
            raise AppError("Result not found.", 404, "not_found")
        if top not in {5, 10, 20}:
            raise AppError("Choose Top 5, 10, or 20.", 422)
        async with chart_slots:
            rows = [row async for row in saved_rows(store, artifact)]
            return await asyncio.to_thread(
                present,
                artifact,
                rows,
                start=start,
                end=end,
                primary=primary,
                order=order,
                top=top,
                view=view,
            )

    @app.get("/api/v1/artifacts/{artifact_id}/export.csv")
    async def export_csv(artifact_id: str, request: Request):
        store = request.app.state.services.store
        artifact = await store.get("artifacts", artifact_id)
        if not artifact:
            raise AppError("Result not found.", 404, "not_found")
        # Validate all pages before sending headers; never return a successful truncated download.
        async with chart_slots:
            rows = [row async for row in saved_rows(store, artifact)]
        columns = [c["name"] for c in artifact["columns"]]

        async def chunks():
            yield "\ufeff" + csv_line(columns)
            for row in rows:
                yield csv_line([row.get(column) for column in columns])

        suffix = "partial" if not artifact["complete"] else "complete"
        safe_id = hashlib.sha256(artifact_id.encode()).hexdigest()[:12]
        return StreamingResponse(
            chunks(),
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="querylane-{safe_id}-{suffix}.csv"',
                "Cache-Control": "no-store",
            },
        )

    @app.get("/api/v1/artifacts/{artifact_id}/pages/{index}")
    async def artifact_page(artifact_id: str, index: int, request: Request):
        if index < 0:
            raise AppError("Invalid page index.")
        page = await request.app.state.services.store.get(f"artifacts/{artifact_id}/pages", str(index))
        if not page:
            raise AppError("Result page not found.", 404, "not_found")
        return page

    @app.websocket("/api/v1/skills/author-sessions/{session_id}/voice")
    async def author_voice(websocket: WebSocket, session_id: str):
        if websocket.headers.get("origin", "").rstrip("/") not in settings.origins:
            await websocket.close(code=1008)
            return
        await websocket.accept()
        try:
            first = await asyncio.wait_for(websocket.receive_json(), timeout=5)
            if not isinstance(first, dict) or first.get("type") != "authenticate":
                raise AppError("Authenticate the voice connection first.", 401, "guest_required")
            guest_id = verify(str(first.get("token", "")))
            await skill_author_voice(websocket, websocket.app.state.services, guest_id, session_id)
        except AppError as exc:
            with contextlib.suppress(WebSocketDisconnect, RuntimeError):
                await websocket.send_json({"type": "error", "message": exc.message, "code": exc.code})
        except (TimeoutError, ValueError, KeyError):
            with contextlib.suppress(WebSocketDisconnect, RuntimeError):
                await websocket.send_json({"type": "error", "message": "Invalid or expired voice handshake."})
        except WebSocketDisconnect:
            pass
        finally:
            with contextlib.suppress(WebSocketDisconnect, RuntimeError):
                await websocket.close()

    @app.websocket("/api/v1/conversations/{conversation_id}/voice")
    async def voice(websocket: WebSocket, conversation_id: str):
        if websocket.headers.get("origin", "").rstrip("/") not in settings.origins:
            await websocket.close(code=1008)
            return
        await websocket.accept()
        try:
            first = await asyncio.wait_for(websocket.receive_json(), timeout=5)
            if first.get("type") != "authenticate":
                raise AppError("Authenticate the voice connection first.", 401, "guest_required")
            guest_id = verify(str(first.get("token", "")))
            await websocket.app.state.services.repo.conversation(conversation_id)
            requested_model = first.get("model")
            if requested_model is not None and not isinstance(requested_model, str):
                raise AppError("Choose a supported analysis model in Settings.", 400, "unsupported_model")
            resolve_text_model(settings, requested_model)
            await voice_session(
                websocket, websocket.app.state.services, guest_id, conversation_id, model=requested_model
            )
        except AppError as exc:
            await websocket.send_json({"type": "error", "message": exc.message, "code": exc.code})
        except (TimeoutError, ValueError, KeyError):
            await websocket.send_json({"type": "error", "message": "Invalid or expired voice handshake."})
        finally:
            try:
                await websocket.close()
            except (RuntimeError, WebSocketDisconnect):
                pass

    return app


app = create_app()
