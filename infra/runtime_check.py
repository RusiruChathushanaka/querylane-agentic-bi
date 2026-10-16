"""Run inside a temporary Cloud Run job under the demo backend identity.

Checks out-of-scope resource denial with metadata/transaction requests only.
Only the authorized synthetic demo sources are queried for aggregate checks.
"""

import asyncio
import json
import uuid

import google.auth
import httpx
from google.adk.events import Event
from google.auth.transport.requests import Request
from google.genai import types

from app.adk_sessions import FirestoreSessionService
from app.config import Settings
from app.connectors import Connectors
from app.errors import AppError, StaleLease
from app.repository import Repository, active_lease
from app.storage import FirestoreStore


async def main():
    settings = Settings()
    project = settings.google_cloud_project
    checks = {}
    credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    await asyncio.to_thread(credentials.refresh, Request())
    async with httpx.AsyncClient(
        headers={"Authorization": "Bearer " + credentials.token}, timeout=30
    ) as http:
        for database in ["agentic-bi-demo", "(default)", "cards-acceptance", "commercial-staging"]:
            base = f"https://firestore.googleapis.com/v1/projects/{project}/databases/{database}/documents"
            response = await http.post(base + ":beginTransaction", json={"options": {"readOnly": {}}})
            if database == "agentic-bi-demo":
                checks["demo_firestore_allowed"] = response.status_code == 200
            else:
                checks["firestore_denied_" + database] = response.status_code == 403
            if response.status_code == 200:
                await http.post(base + ":rollback", json={"transaction": response.json()["transaction"]})
        for dataset in [
            "agentic_bi_demo",
            "enterprise_bi",
            "enterprise_commercial",
            "enterprise_commercial_staging",
        ]:
            response = await http.get(
                f"https://bigquery.googleapis.com/bigquery/v2/projects/{project}/datasets/{dataset}"
            )
            checks["bq_allowed" if dataset == "agentic_bi_demo" else "bq_denied_" + dataset] = (
                response.status_code == (200 if dataset == "agentic_bi_demo" else 403)
            )
        response = await http.get(
            f"https://secretmanager.googleapis.com/v1/projects/{project}/secrets/agentic-bi-postgres-admin"
        )
        checks["admin_secret_metadata_denied"] = response.status_code == 403

    # Two independent clients emulate different Cloud Run instances using the
    # real named database rather than sharing an in-process lock.
    stores = [FirestoreStore(project, settings.firestore_database) for _ in range(2)]
    repos = [Repository(store, settings) for store in stores]
    connectors = Connectors(settings)
    try:
        await connectors.start()
        async with connectors.pg_pool.acquire(timeout=15) as connection:
            attrs = await connection.fetchrow(
                "SELECT rolsuper, rolcreatedb, rolcreaterole, rolreplication FROM pg_roles WHERE rolname=current_user"
            )
            checks["postgres_reader_restricted"] = not any(attrs.values())
            checks["postgres_reader_select_only"] = await connection.fetchval(
                "SELECT has_table_privilege(current_user,$1,'SELECT') AND NOT has_table_privilege(current_user,$1,'INSERT,UPDATE,DELETE,TRUNCATE')",
                f"{settings.postgres_schema}.customer_profiles",
            )
        await connectors.ensure_data_ready()
        if settings.data_profile == "timeseries":
            from google.genai import Client

            from app.model_selection import TEXT_MODELS

            schemas = {source: await connectors.schema(source) for source in ("bigquery", "postgres")}
            checks["timeseries_schema"] = (
                len(schemas["bigquery"]) == 5
                and len(schemas["postgres"]) == 6
                and all(table["columns"] for tables in schemas.values() for table in tables)
            )
            result = await connectors.query(
                "bigquery",
                "SELECT COUNT(*) orders, SUM(revenue) revenue, MIN(order_date) start_date, MAX(order_date) end_date FROM sales_orders",
                "release-runtime-" + uuid.uuid4().hex,
            )
            row = result.rows[0]
            checks["timeseries_orders"] = (
                int(row["orders"]) >= 573348
                and str(row["start_date"]) == "2023-01-01"
                and str(row["end_date"]) >= "2026-09-30"
            )
            async with connectors.pg_pool.acquire(timeout=15) as connection:
                checks["timeseries_customers"] = (
                    await connection.fetchval("SELECT COUNT(*) FROM retail_timeseries.customer_profiles")
                    == 25000
                )
            model_client = Client(vertexai=True, project=project, location=settings.text_model_location)
            try:
                for model in TEXT_MODELS:
                    response = await model_client.aio.models.generate_content(
                        model=model["id"],
                        contents="Reply OK only.",
                        config=types.GenerateContentConfig(
                            max_output_tokens=1024,
                            thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.LOW),
                        ),
                    )
                    checks["runtime_model_" + model["id"]] = bool(response.text)
            finally:
                await model_client.aio.aclose()
        conversation = await repos[0].create_conversation("Cloud persistence verification", "all")
        outcomes = await asyncio.gather(
            repos[0].begin(conversation["id"], "runtime-check-a", "Concurrency probe", uuid.uuid4().hex),
            repos[1].begin(conversation["id"], "runtime-check-b", "Concurrency probe", uuid.uuid4().hex),
            return_exceptions=True,
        )
        concurrency_outcomes = [
            {
                "type": type(item).__name__,
                "code": getattr(item, "code", None),
                "message": str(item)[:300] if isinstance(item, Exception) else "acquired",
            }
            for item in outcomes
        ]
        checks["transactional_single_winner"] = (
            sum(isinstance(item, tuple) for item in outcomes) == 1
            and sum(isinstance(item, AppError) and item.code == "conversation_busy" for item in outcomes) == 1
        )
        winner = next(item[0] for item in outcomes if isinstance(item, tuple))
        checks["running_status_snapshot"] = (await repos[1].run(winner["id"]))["status"] == "running"
        lease = {
            "run_id": winner["id"],
            "conversation_id": conversation["id"],
            "generation": winner["generation"],
        }
        token = active_lease.set(lease)
        try:
            a, b = [FirestoreSessionService(store) for store in stores]
            session_id = "runtime-check-" + uuid.uuid4().hex
            session = await a.create_session(
                app_name="agentic_bi", user_id="public-demo", session_id=session_id
            )
            stale = await b.get_session(app_name="agentic_bi", user_id="public-demo", session_id=session_id)
            await a.append_event(
                session,
                Event(
                    author="user",
                    content=types.Content(role="user", parts=[types.Part(text="Persistence probe")]),
                ),
            )
            loaded = await b.get_session(app_name="agentic_bi", user_id="public-demo", session_id=session_id)
            checks["adk_cross_client_persistence"] = len(loaded.events) == 1
            try:
                await b.append_event(stale, Event(author="user"))
                checks["stale_adk_revision_denied"] = False
            except StaleLease:
                checks["stale_adk_revision_denied"] = True
            await repos[0].finish("complete")
            checks["completed_run_survives_new_client"] = (await repos[1].run(winner["id"]))[
                "status"
            ] == "complete"
        finally:
            active_lease.reset(token)
    finally:
        await connectors.close()
        for store in stores:
            await store.close()
    result = {
        "checks": checks,
        "data_profile": settings.data_profile,
        "postgres_schema": settings.postgres_schema,
        "passed": all(checks.values()),
        "existing_business_data_requested": False,
        "concurrency_outcomes": concurrency_outcomes,
    }
    print("AGENTIC_BI_RUNTIME_CHECK " + json.dumps(result), flush=True)
    return result["passed"]


if __name__ == "__main__":
    raise SystemExit(0 if asyncio.run(main()) else 1)
