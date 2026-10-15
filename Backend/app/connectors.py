import asyncio
import datetime as dt
import json
import time
from decimal import Decimal
from typing import Any

import pyarrow as pa

from app.config import Settings
from app.errors import AppError
from app.fixtures import DESCRIPTIONS, SOURCE_TABLES, retail_data
from app.models import QueryResult
from app.sql_guard import validate_sql


def json_value(value: Any):
    if isinstance(value, (dt.datetime, dt.date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, bytes):
        return value.hex()
    return value


def json_rows(rows: list[dict]) -> list[dict]:
    return [{key: json_value(value) for key, value in row.items()} for row in rows]


class Connectors:
    def __init__(self, settings: Settings, credentials=None):
        self.settings = settings
        self.credentials = credentials
        self.jobs: dict[str, list[Any]] = {}
        self.cancelled: set[str] = set()
        self.pg_pool = None
        self.sql_connector = None
        self.bq = None
        self.fixtures = retail_data()

    async def start(self):
        if self.settings.data_backend == "cloud":
            import asyncpg
            from google.cloud import bigquery

            self.bq = bigquery.Client(
                project=self.settings.google_cloud_project,
                location=self.settings.bigquery_location,
                credentials=self.credentials,
            )
            if self.settings.cloud_sql_instance:
                from google.cloud.sql.connector import create_async_connector

                self.sql_connector = await create_async_connector(
                    refresh_strategy="lazy", credentials=self.credentials
                )

                async def connect(*args, **kwargs):
                    return await self.sql_connector.connect_async(
                        self.settings.cloud_sql_instance,
                        "asyncpg",
                        user=self.settings.postgres_user,
                        password=self.settings.postgres_password,
                        db=self.settings.postgres_database,
                        ip_type="public",
                    )

                self.pg_pool = await asyncpg.create_pool(connect=connect, min_size=0, max_size=3)
            else:
                self.pg_pool = await asyncpg.create_pool(self.settings.postgres_dsn, min_size=0, max_size=3)

    async def close(self):
        if self.pg_pool:
            await self.pg_pool.close()
        if self.sql_connector:
            await self.sql_connector.close_async()
        if self.bq:
            self.bq.close()

    async def test(self, source: str) -> dict:
        if self.settings.data_backend == "fixture":
            return {"connected": True, "mode": "local-fixtures"}
        try:
            if source == "bigquery":
                await asyncio.to_thread(self.bq.get_dataset, self.settings.bigquery_dataset)
            else:
                async with self.pg_pool.acquire(timeout=5) as connection:
                    await connection.fetchval("SELECT 1", timeout=5)
            return {"connected": True, "mode": "cloud"}
        except Exception:
            return {
                "connected": False,
                "mode": "cloud",
                "error": "Connection unavailable; administrator configuration is required.",
            }

    async def schema(self, source: str) -> list[dict]:
        tables = []
        for name in SOURCE_TABLES[source]:
            if self.settings.data_backend == "fixture":
                arrow = pa.Table.from_pylist(self.fixtures[name])
                columns = [{"name": field.name, "type": str(field.type)} for field in arrow.schema]
            elif source == "bigquery":
                table = await asyncio.to_thread(
                    self.bq.get_table,
                    f"{self.settings.google_cloud_project}.{self.settings.bigquery_dataset}.{name}",
                )
                columns = [{"name": field.name, "type": field.field_type} for field in table.schema]
            else:
                async with self.pg_pool.acquire(timeout=5) as connection:
                    fields = await connection.fetch(
                        "SELECT column_name, data_type FROM information_schema.columns WHERE table_schema=$1 AND table_name=$2 ORDER BY ordinal_position",
                        "retail",
                        name,
                        timeout=5,
                    )
                columns = [{"name": field["column_name"], "type": field["data_type"]} for field in fields]
            tables.append(
                {"source": source, "table": name, "description": DESCRIPTIONS[name], "columns": columns}
            )
        return tables

    async def query(self, source: str, sql: str, run_id: str, leg: int = 0) -> QueryResult:
        if run_id in self.cancelled:
            raise asyncio.CancelledError()
        normalized = validate_sql(
            sql, source, self.settings.google_cloud_project, self.settings.bigquery_dataset
        )
        started = time.monotonic()
        job_id, billed = None, None
        if self.settings.data_backend == "fixture":
            rows, columns = await asyncio.to_thread(self._fixture_query, normalized, source)
        elif source == "bigquery":
            rows, columns, job_id, billed = await asyncio.to_thread(self._bigquery, normalized, run_id, leg)
        else:
            async with self.pg_pool.acquire(timeout=5) as connection:
                async with connection.transaction(readonly=True):
                    await connection.execute("SET LOCAL statement_timeout = '15s'")
                    await connection.execute("SET LOCAL lock_timeout = '2s'")
                    await connection.execute("SET LOCAL search_path = pg_catalog, retail")
                    statement = await connection.prepare(
                        f"SELECT * FROM ({normalized}) AS bounded_result LIMIT {self.settings.source_row_limit + 1}",
                        timeout=15,
                    )
                    fields = statement.get_attributes()
                    records = await statement.fetch(timeout=15)
                    rows = [dict(row) for row in records]
                    columns = [{"name": field.name, "type": field.type.name} for field in fields]
        if run_id in self.cancelled:
            raise asyncio.CancelledError()
        complete = len(rows) <= self.settings.source_row_limit
        rows = rows[: self.settings.source_row_limit]
        if len(json.dumps(json_rows(rows)).encode()) > self.settings.source_byte_limit:
            raise AppError(
                "Source result exceeds the byte budget. Narrow the question.", code="result_too_large"
            )
        return QueryResult(
            source=source,
            sql=normalized,
            columns=columns,
            rows=rows,
            row_count=len(rows),
            complete=complete,
            elapsed_ms=round((time.monotonic() - started) * 1000),
            executed_at=dt.datetime.now(dt.UTC).isoformat(),
            job_id=job_id,
            bytes_processed=billed,
        )

    def _fixture_query(self, sql: str, source: str):
        import duckdb
        import sqlglot
        from sqlglot import exp

        tree = sqlglot.parse_one(sql, read="bigquery" if source == "bigquery" else "postgres")
        for table in tree.find_all(exp.Table):
            table.set("db", None)
            table.set("catalog", None)
        with duckdb.connect(":memory:", config={"enable_external_access": False, "threads": 1}) as connection:
            for name in SOURCE_TABLES[source]:
                connection.register(name, pa.Table.from_pylist(self.fixtures[name]))
            result = connection.execute(
                f"SELECT * FROM ({tree.sql(dialect='duckdb')}) AS bounded_result LIMIT {self.settings.source_row_limit + 1}"
            )
            columns = [{"name": c[0], "type": str(c[1])} for c in result.description]
            rows = [dict(zip([c["name"] for c in columns], row)) for row in result.fetchall()]
        return rows, columns

    def _bigquery(self, sql: str, run_id: str, leg: int):
        from google.cloud import bigquery

        bounded = f"SELECT * FROM ({sql}) AS bounded_result LIMIT {self.settings.source_row_limit + 1}"
        dry = self.bq.query(bounded, job_config=bigquery.QueryJobConfig(dry_run=True, use_query_cache=False))
        if (dry.total_bytes_processed or 0) > self.settings.bigquery_max_bytes:
            raise AppError(
                "Estimated BigQuery scan exceeds 1 GiB. Narrow the date range or columns.", code="scan_budget"
            )
        job_id = f"abi_{run_id}_{leg}"
        config = bigquery.QueryJobConfig(
            maximum_bytes_billed=self.settings.bigquery_max_bytes,
            job_timeout_ms=self.settings.query_timeout_seconds * 1000,
            labels={"application": "agentic-bi-demo"},
        )
        try:
            job = self.bq.query(bounded, job_config=config, job_id=job_id)
        except Exception as exc:
            from google.api_core.exceptions import Conflict

            if not isinstance(exc, Conflict):
                raise
            job = self.bq.get_job(job_id)
        self.jobs.setdefault(run_id, []).append(job)
        if run_id in self.cancelled:
            job.cancel()
            raise AppError("Cancellation requested.", code="cancelled")
        try:
            result = job.result(timeout=self.settings.query_timeout_seconds)
            rows = [dict(row) for row in result]
            columns = [{"name": f.name, "type": f.field_type} for f in result.schema]
            return rows, columns, job_id, job.total_bytes_processed
        except Exception:
            job.cancel()
            raise

    async def cancel(self, run_id: str) -> dict:
        self.cancelled.add(run_id)
        jobs = self.jobs.get(run_id, [])
        confirmed = bool(jobs)
        for job in jobs:
            await asyncio.to_thread(job.cancel)
            await asyncio.to_thread(job.reload)
            confirmed = confirmed and job.state == "DONE"
        return {"requested": True, "database_jobs_terminal": confirmed}

    def forget(self, run_id: str):
        self.jobs.pop(run_id, None)
        self.cancelled.discard(run_id)
