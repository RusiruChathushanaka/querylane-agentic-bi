"""Credentialed CLI only. No administrative endpoint is exposed by FastAPI."""

import argparse
import asyncio
import json
import subprocess
import time
from datetime import date
from decimal import Decimal

from google.cloud import bigquery, firestore
from google.genai import Client, types
from google.oauth2.credentials import Credentials

from app.config import Settings
from app.connectors import json_rows
from app.fixtures import SOURCE_TABLES, retail_data

PROJECT = "project-e8b1593d-009a-4822-abf"
INSTANCE = "agentic-bi-demo-pg"
DATABASE = "agentic_bi"
DATASET = "agentic_bi_demo"


def cli(*args):
    result = subprocess.run(args, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def operator_credentials():
    # Explicit CLI-operator credentials for administrative commands only.
    # The deployed application uses its attached service account via ADC.
    return Credentials(cli("gcloud", "auth", "print-access-token"))


def secret(name):
    return cli("gcloud", "secrets", "versions", "access", "latest", "--secret", name, "--project", PROJECT)


async def seed():
    import httpx
    from google.cloud.sql.connector import create_async_connector

    credentials = operator_credentials()
    data = retail_data()
    bq = bigquery.Client(project=PROJECT, location="asia-southeast1", credentials=credentials)
    dataset = bq.get_dataset(DATASET)
    backend_email = f"agentic-bi-backend@{PROJECT}.iam.gserviceaccount.com"
    entry = bigquery.AccessEntry("READER", "userByEmail", backend_email)
    if entry not in dataset.access_entries:
        dataset.access_entries = list(dataset.access_entries) + [entry]
        bq.update_dataset(dataset, ["access_entries"])
    for name in SOURCE_TABLES["bigquery"]:
        fields = []
        for column, value in data[name][0].items():
            kind = (
                "NUMERIC"
                if isinstance(value, Decimal)
                else "INTEGER"
                if isinstance(value, int)
                else "DATE"
                if isinstance(value, date)
                else "STRING"
            )
            fields.append(bigquery.SchemaField(column, kind))
        config = bigquery.LoadJobConfig(schema=fields, write_disposition="WRITE_TRUNCATE")
        bq.load_table_from_json(
            json_rows(data[name]), f"{PROJECT}.{DATASET}.{name}", job_config=config
        ).result()
        print(f"Seeded BigQuery {name}: {len(data[name])} synthetic rows")
    bq.close()

    # Update only the administrator password of the dedicated demo instance.
    admin_password = secret("agentic-bi-postgres-admin")
    reader_password = secret("agentic-bi-postgres-reader")
    async with httpx.AsyncClient(timeout=30) as http:
        response = await http.put(
            f"https://sqladmin.googleapis.com/sql/v1beta4/projects/{PROJECT}/instances/{INSTANCE}/users",
            params={"name": "postgres"},
            headers={"Authorization": f"Bearer {credentials.token}"},
            json={"name": "postgres", "password": admin_password},
        )
        response.raise_for_status()
        operation = response.json()["name"]
        for _ in range(60):
            current = await http.get(
                f"https://sqladmin.googleapis.com/sql/v1beta4/projects/{PROJECT}/operations/{operation}",
                headers={"Authorization": f"Bearer {credentials.token}"},
            )
            current.raise_for_status()
            if current.json().get("status") == "DONE":
                if current.json().get("error"):
                    raise RuntimeError("Demo PostgreSQL administrator setup failed.")
                break
            await asyncio.sleep(1)
        else:
            raise TimeoutError("Administrator password operation did not complete.")
    existing = subprocess.run(
        ["gcloud", "sql", "databases", "describe", DATABASE, "--instance", INSTANCE, "--project", PROJECT],
        capture_output=True,
    )
    if existing.returncode:
        cli(
            "gcloud",
            "sql",
            "databases",
            "create",
            DATABASE,
            "--instance",
            INSTANCE,
            "--project",
            PROJECT,
            "--quiet",
        )
    connector = await create_async_connector(credentials=credentials, refresh_strategy="lazy")
    connection = await connector.connect_async(
        f"{PROJECT}:asia-southeast1:{INSTANCE}",
        "asyncpg",
        user="postgres",
        password=admin_password,
        db=DATABASE,
    )
    try:
        async with connection.transaction():
            await connection.execute("CREATE SCHEMA IF NOT EXISTS retail")
            for name in SOURCE_TABLES["postgres"]:
                fields = []
                for column, value in data[name][0].items():
                    kind = (
                        "NUMERIC(18,2)"
                        if isinstance(value, Decimal)
                        else "INTEGER"
                        if isinstance(value, int)
                        else "DATE"
                        if isinstance(value, date)
                        else "TEXT"
                    )
                    fields.append(f'"{column}" {kind}')
                await connection.execute(f'CREATE TABLE IF NOT EXISTS retail."{name}" ({", ".join(fields)})')
                await connection.execute(f'TRUNCATE retail."{name}"')
                columns = list(data[name][0])
                placeholders = ",".join(f"${i + 1}" for i in range(len(columns)))
                quoted = ",".join(f'"{column}"' for column in columns)
                await connection.executemany(
                    f'INSERT INTO retail."{name}" ({quoted}) VALUES ({placeholders})',
                    [tuple(row[column] for column in columns) for row in data[name]],
                )
                print(f"Seeded PostgreSQL {name}: {len(data[name])} synthetic rows")
            if not await connection.fetchval("SELECT 1 FROM pg_roles WHERE rolname=$1", "bi_reader"):
                await connection.execute("CREATE ROLE bi_reader LOGIN")
            attributes = await connection.fetchrow(
                "SELECT rolsuper, rolreplication FROM pg_roles WHERE rolname=$1", "bi_reader"
            )
            if attributes["rolsuper"] or attributes["rolreplication"]:
                raise RuntimeError("Existing demo reader has elevated attributes; refusing to use it.")
            password_literal = "'" + reader_password.replace("'", "''") + "'"
            # Cloud SQL's administrator is not a PostgreSQL SUPERUSER. New
            # roles already default to NOSUPERUSER/NOREPLICATION; attempting
            # to ALTER those attributes is itself a superuser-only operation.
            await connection.execute(
                f"ALTER ROLE bi_reader WITH LOGIN NOCREATEDB NOCREATEROLE PASSWORD {password_literal}"
            )
            await connection.execute("GRANT CONNECT ON DATABASE agentic_bi TO bi_reader")
            await connection.execute("GRANT USAGE ON SCHEMA retail TO bi_reader")
            await connection.execute("GRANT SELECT ON ALL TABLES IN SCHEMA retail TO bi_reader")
            await connection.execute("ALTER ROLE bi_reader SET default_transaction_read_only=on")
            await connection.execute("ALTER ROLE bi_reader SET statement_timeout='15s'")
            await connection.execute("ALTER ROLE bi_reader SET lock_timeout='2s'")
            await connection.execute("ALTER ROLE bi_reader SET search_path=pg_catalog,retail")
        print("PostgreSQL reader role configured with SELECT-only access.")
    finally:
        await connection.close()
        await connector.close_async()


async def index_schema():
    from app.adk_sessions import FirestoreSessionService
    from app.ai import AI
    from app.connectors import Connectors
    from app.storage import FirestoreStore

    credentials = operator_credentials()
    settings = Settings(ai_backend="gemini")
    store = FirestoreStore(PROJECT, "agentic-bi-demo", credentials=credentials)
    # The seed defines the same schema in both modes; indexing does not need a
    # privileged PostgreSQL connection or access to any other dataset.
    connectors = Connectors(
        Settings(data_backend="fixture", data_profile=settings.data_profile), catalog_only=True
    )
    ai = AI(settings, FirestoreSessionService(store), connectors, store, credentials=credentials)
    try:
        print(
            json.dumps(
                {
                    "indexed_chunks": await ai.index_schema(),
                    "model": settings.embedding_model,
                    "dimensions": settings.embedding_dimensions,
                }
            )
        )
    finally:
        await ai.close()
        await store.close()


async def reset():
    client = firestore.Client(project=PROJECT, database="agentic-bi-demo", credentials=operator_credentials())
    # Recursive delete is limited to collections owned by this demo database.
    for name in [
        "conversations",
        "runs",
        "artifacts",
        "adk_sessions",
        "voice_resumptions",
        "quotas",
        "skill_author_sessions",
    ]:
        client.recursive_delete(client.collection(name))
    client.close()
    print("Demo history and quotas reset; schemas and source data preserved.")


async def seed_skills():
    from app.repository import Repository
    from app.skill_examples import seed_examples
    from app.storage import FirestoreStore

    settings = Settings()
    store = FirestoreStore(PROJECT, "agentic-bi-demo", credentials=operator_credentials())
    try:
        count = await seed_examples(Repository(store, settings), settings)
        print(f"Checked {count} example skills; existing skills and revisions preserved.")
    finally:
        await store.close()


async def cleanup_skill_authors():
    """Remove only expired, inactive author interviews and their scoped ADK sessions."""
    from app.adk_sessions import FirestoreSessionService
    from app.skill_author import COLLECTION

    client = firestore.Client(project=PROJECT, database="agentic-bi-demo", credentials=operator_credentials())
    removed = 0
    try:
        for document in client.collection(COLLECTION).stream():
            value = document.to_dict()
            if (
                value.get("expires_at", float("inf")) > time.time()
                or value.get("lease_until", 0) > time.time()
            ):
                continue
            for generation in range(1, value.get("generation", 0) + 1):
                key = FirestoreSessionService.key(
                    "skill_author", value["guest_id"], f"{document.id}_g{generation}"
                )
                client.recursive_delete(client.collection("adk_sessions").document(key))
            client.recursive_delete(document.reference)
            removed += 1
    finally:
        client.close()
    print(f"Removed {removed} expired author interviews; published skills/revisions preserved.")


async def check_models():
    from app.model_selection import TEXT_MODELS

    credentials = operator_credentials()
    settings = Settings()
    client = Client(
        vertexai=True, project=PROJECT, location=settings.text_model_location, credentials=credentials
    )
    try:
        for model_id in dict.fromkeys([settings.text_model, *(model["id"] for model in TEXT_MODELS)]):
            response = await client.aio.models.generate_content(
                model=model_id,
                contents="Reply with OK only.",
                config=types.GenerateContentConfig(
                    max_output_tokens=1024,
                    thinking_config=types.ThinkingConfig(thinking_level=types.ThinkingLevel.LOW),
                ),
            )
            if not response.text:
                raise RuntimeError(f"Model {model_id} returned no text response.")
            print(json.dumps({"text_model": model_id, "has_text_response": True}))
    finally:
        await client.aio.aclose()
    embedding = Client(
        vertexai=True, project=PROJECT, location=settings.embedding_location, credentials=credentials
    )
    try:
        result = await embedding.aio.models.embed_content(
            model=settings.embedding_model,
            contents="Retail revenue by region",
            config=types.EmbedContentConfig(output_dimensionality=768),
        )
        print(
            json.dumps(
                {"embedding_model": settings.embedding_model, "dimensions": len(result.embeddings[0].values)}
            )
        )
    finally:
        await embedding.aio.aclose()
    live = Client(
        vertexai=True, project=PROJECT, location=settings.live_model_location, credentials=credentials
    )
    try:
        async with live.aio.live.connect(
            model=settings.live_model, config=types.LiveConnectConfig(response_modalities=["AUDIO"])
        ):
            print(json.dumps({"live_model": settings.live_model, "connection": "verified"}))
    finally:
        await live.aio.aclose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        choices=[
            "seed",
            "seed-skills",
            "index-schema",
            "check-models",
            "cleanup-skill-authors",
            "reset-history",
        ],
    )
    parser.add_argument("--confirm-demo-reset", action="store_true")
    args = parser.parse_args()
    if args.command == "reset-history" and not args.confirm_demo_reset:
        parser.error("Reset requires --confirm-demo-reset and applies only to the named demo database.")
    operations = {
        "seed": seed,
        "seed-skills": seed_skills,
        "index-schema": index_schema,
        "check-models": check_models,
        "cleanup-skill-authors": cleanup_skill_authors,
        "reset-history": reset,
    }
    asyncio.run(operations[args.command]())


if __name__ == "__main__":
    main()
