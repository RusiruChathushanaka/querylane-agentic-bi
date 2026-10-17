"""Private Cloud Run entrypoint. Deploy with --no-allow-unauthenticated and timeout 660.

Cloud Run verifies task/scheduler OIDC before these handlers; never mount them on the public API.
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import Field

from app.errors import AppError
from app.main import create_app
from app.models import StrictModel

base = create_app()
app = FastAPI(title="Querylane private report worker", lifespan=base.router.lifespan_context)


class TaskBody(StrictModel):
    run_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    delivery: int = Field(ge=0)


@app.exception_handler(AppError)
async def error(request, exc):
    return JSONResponse({"error": {"code": exc.code, "message": exc.message}}, status_code=exc.status)


@app.post("/internal/reports/execute")
async def execute(body: TaskBody):
    await app.state.services.report_engine.work(body.run_id, body.delivery)
    return {"acknowledged": True}


@app.post("/internal/reports/reconcile")
async def reconcile():
    return await app.state.services.report_dispatcher.reconcile()


@app.get("/health/live")
async def live():
    return {"status": "ok", "service": "agentic-bi-report-worker"}
