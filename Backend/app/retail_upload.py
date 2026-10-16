"""Operator-only, insert-only ingestion into dedicated time-series source tables."""

import asyncio
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pyarrow.parquet as pq
from google.cloud import bigquery

from app.admin import DATABASE, DATASET, INSTANCE, PROJECT, operator_credentials, secret
from app.retail_generator import read_manifest, record_hash
from app.retail_schema import PG_SCHEMA, TABLES, VERSION
from app.retail_validation import validate_bundle

STATE = "retail_timeseries_state"
MAX_BYTES = 2 * 1024**3


def upload_plan(directory: Path):
    manifest = read_manifest(directory)
    return {
        "project": PROJECT,
        "bigquery_dataset": DATASET,
        "cloud_sql_instance": INSTANCE,
        "postgres_database": DATABASE,
        "postgres_schema": PG_SCHEMA,
        "version": VERSION,
        "configuration_id": manifest["configuration_id"],
        "date_range": [manifest["parameters"]["start"], manifest["parameters"]["end"]],
        "mode": "insert-only; existing IDs with different content are rejected",
        "maximum_bytes_billed_per_operator_query": MAX_BYTES,
        "tables": [
            {
                "source": t.source,
                "table": t.name,
                "rows": manifest["files"][t.name]["rows"],
                "partition": t.partition,
                "cluster": list(t.cluster),
            }
            for t in TABLES
        ],
        "reader": "existing bi_reader receives SELECT/USAGE on retail_timeseries only; existing BigQuery dataset reader ACL is reused",
    }


def bq_schema(table):
    return [
        bigquery.SchemaField(c.name, c.kind, mode="NULLABLE" if c.nullable else "REQUIRED")
        for c in table.columns
    ]


def qualified(name):
    return f"`{PROJECT}.{DATASET}.{name}`"


def parameters(**values):
    return [
        bigquery.ScalarQueryParameter(k, "DATE" if isinstance(v, date) else "STRING", v)
        for k, v in values.items()
    ]


def query(client, sql, **values):
    return client.query(
        sql,
        location="asia-southeast1",
        job_config=bigquery.QueryJobConfig(
            maximum_bytes_billed=MAX_BYTES, query_parameters=parameters(**values)
        ),
    ).result(timeout=600)


def claim(client, manifest, owner):
    schema = [
        bigquery.SchemaField("id", "STRING"),
        bigquery.SchemaField("status", "STRING"),
        bigquery.SchemaField("owner", "STRING"),
        bigquery.SchemaField("expires", "TIMESTAMP"),
        bigquery.SchemaField("configuration_id", "STRING"),
        bigquery.SchemaField("anchor_start", "DATE"),
        bigquery.SchemaField("end_date", "DATE"),
        bigquery.SchemaField("batch_hash", "STRING"),
    ]
    # Atomic CTAS creates exactly one initial fence row. Concurrent first uploads
    # must not independently insert into an unconstrained empty BigQuery table.
    definitions = ",".join(f"{f.name} {f.field_type}" for f in schema)
    initial = ",".join(
        "'current'"
        if f.name == "id"
        else "'empty'"
        if f.name == "status"
        else f"CAST(NULL AS {f.field_type})"
        for f in schema
    )
    query(client, f"CREATE TABLE IF NOT EXISTS {qualified(STATE)} ({definitions}) AS SELECT {initial}")
    query(
        client,
        f"""BEGIN TRANSACTION;
        ASSERT (SELECT COUNT(*)=1 FROM {qualified(STATE)} WHERE id='current') AS 'Invalid ingestion state';
        ASSERT NOT EXISTS(SELECT 1 FROM {qualified(STATE)} WHERE id='current' AND status='loading' AND expires>CURRENT_TIMESTAMP()) AS 'Another upload is active';
        ASSERT NOT EXISTS(SELECT 1 FROM {qualified(STATE)} WHERE id='current' AND configuration_id IS NOT NULL AND (configuration_id<>@config OR anchor_start<>@start OR end_date>@end)) AS 'Use the same generation settings/start and a non-decreasing end date';
        UPDATE {qualified(STATE)} SET status='loading',owner=@owner,expires=TIMESTAMP_ADD(CURRENT_TIMESTAMP(),INTERVAL 45 MINUTE),configuration_id=@config,anchor_start=@start,end_date=@end,batch_hash=@batch WHERE id='current';
        COMMIT TRANSACTION;""",
        owner=owner,
        config=manifest["configuration_id"],
        start=date.fromisoformat(manifest["parameters"]["start"]),
        end=date.fromisoformat(manifest["parameters"]["end"]),
        batch=record_hash(manifest),
    )


@asynccontextmanager
async def postgres_connection(credentials, local_dsn=None):
    if local_dsn:
        import asyncpg

        connection = await asyncpg.connect(local_dsn, command_timeout=600)
        try:
            yield connection
        finally:
            await connection.close()
        return
    from google.cloud.sql.connector import create_async_connector

    connector = await create_async_connector(credentials=credentials, refresh_strategy="lazy")
    connection = None
    try:
        password = await asyncio.to_thread(secret, "agentic-bi-postgres-admin")
        connection = await connector.connect_async(
            f"{PROJECT}:asia-southeast1:{INSTANCE}",
            "asyncpg",
            user="postgres",
            password=password,
            db=DATABASE,
        )
        yield connection
    finally:
        if connection:
            await connection.close()
        await connector.close_async()


async def upload_postgres(connection, directory, manifest, grant_reader=True):
    kinds = {
        "STRING": "TEXT",
        "INT64": "BIGINT",
        "NUMERIC": "NUMERIC(18,2)",
        "DATE": "DATE",
        "TIMESTAMP": "TIMESTAMPTZ",
        "BOOL": "BOOLEAN",
    }
    results = []
    async with connection.transaction():
        await connection.execute("SELECT pg_advisory_xact_lock(1842739)")
        await connection.execute("SET LOCAL lock_timeout='5s'")
        await connection.execute("SET LOCAL statement_timeout='120s'")
        await connection.execute(f'CREATE SCHEMA IF NOT EXISTS "{PG_SCHEMA}"')
        await connection.execute(
            f'CREATE TABLE IF NOT EXISTS "{PG_SCHEMA}".ingestion_batches (configuration_id TEXT PRIMARY KEY, anchor_start DATE NOT NULL, end_date DATE NOT NULL, batch_hash TEXT NOT NULL)'
        )
        existing = await connection.fetch(f'SELECT * FROM "{PG_SCHEMA}".ingestion_batches')
        start, end = (date.fromisoformat(manifest["parameters"][k]) for k in ("start", "end"))
        if existing and (
            len(existing) != 1
            or existing[0]["configuration_id"] != manifest["configuration_id"]
            or existing[0]["anchor_start"] != start
            or existing[0]["end_date"] > end
        ):
            raise ValueError("PostgreSQL data settings/start differ, or end date would move backward.")
        for table in (t for t in TABLES if t.source == "postgres"):
            target = f'"{PG_SCHEMA}"."{table.name}"'
            columns = ",".join(
                f'"{c.name}" {kinds[c.kind]}' + ("" if c.nullable else " NOT NULL") for c in table.columns
            )
            keys = ",".join(f'"{k}"' for k in table.key)
            await connection.execute(f"CREATE TABLE IF NOT EXISTS {target} ({columns},PRIMARY KEY({keys}))")
            # Different versions require an explicit migration, never a silent ALTER/overwrite.
            actual = await connection.fetch(
                "SELECT column_name FROM information_schema.columns WHERE table_schema=$1 AND table_name=$2 ORDER BY ordinal_position",
                PG_SCHEMA,
                table.name,
            )
            if [r["column_name"] for r in actual] != [c.name for c in table.columns]:
                raise ValueError(f"Unexpected existing PostgreSQL schema: {table.name}")
            stage = f"stage_{table.name}"
            await connection.execute(
                f'CREATE TEMP TABLE "{stage}" (LIKE {target} INCLUDING DEFAULTS) ON COMMIT DROP'
            )
            parquet = pq.ParquetFile(directory / f"{table.name}.parquet")
            for batch in parquet.iter_batches(batch_size=4096):
                await connection.copy_records_to_table(
                    stage,
                    columns=[c.name for c in table.columns],
                    records=[tuple(row[c.name] for c in table.columns) for row in batch.to_pylist()],
                )
            join = " AND ".join(f't."{k}"=s."{k}"' for k in table.key)
            if await connection.fetchval(
                f'SELECT EXISTS(SELECT 1 FROM {target} t JOIN "{stage}" s ON {join} WHERE t.record_hash<>s.record_hash)'
            ):
                raise ValueError(
                    f"Existing PostgreSQL records differ: {table.name}. Nothing in this transaction was changed."
                )
            names = ",".join(f'"{c.name}"' for c in table.columns)
            status = await connection.execute(
                f'INSERT INTO {target}({names}) SELECT {names} FROM "{stage}" ON CONFLICT({keys}) DO NOTHING'
            )
            count = await connection.fetchval(f"SELECT COUNT(*) FROM {target}")
            if count != manifest["files"][table.name]["rows"]:
                raise ValueError(f"Unexpected PostgreSQL count: {table.name}")
            results.append({"table": table.name, "rows": count, "inserted": int(status.split()[-1])})
        # Real keys and constraints on the operational dimensions.
        for name, definition in (
            ("store_target_store_fk", f'FOREIGN KEY(store_id) REFERENCES "{PG_SCHEMA}".stores(store_id)'),
            (
                "promotion_campaign_fk",
                f'FOREIGN KEY(campaign_id) REFERENCES "{PG_SCHEMA}".campaigns(campaign_id)',
            ),
        ):
            table = "store_targets" if name.startswith("store") else "promotions"
            exists = await connection.fetchval(
                "SELECT EXISTS(SELECT 1 FROM pg_constraint WHERE conname=$1 AND connamespace=(SELECT oid FROM pg_namespace WHERE nspname=$2))",
                name,
                PG_SCHEMA,
            )
            if not exists:
                await connection.execute(
                    f'ALTER TABLE "{PG_SCHEMA}"."{table}" ADD CONSTRAINT "{name}" {definition}'
                )
        for table, columns in (
            ("customer_profiles", "signup_date,region"),
            ("campaigns", "start_date,end_date"),
            ("store_targets", "month,region"),
        ):
            await connection.execute(
                f'CREATE INDEX IF NOT EXISTS "{table}_analytics_idx" ON "{PG_SCHEMA}"."{table}"({columns})'
            )
        if grant_reader:
            if not await connection.fetchval(
                "SELECT EXISTS(SELECT 1 FROM pg_roles WHERE rolname='bi_reader')"
            ):
                raise ValueError("Expected existing demo reader bi_reader; no roles were created.")
            await connection.execute(f'GRANT USAGE ON SCHEMA "{PG_SCHEMA}" TO bi_reader')
            await connection.execute(f'GRANT SELECT ON ALL TABLES IN SCHEMA "{PG_SCHEMA}" TO bi_reader')
        await connection.execute(
            f'INSERT INTO "{PG_SCHEMA}".ingestion_batches VALUES($1,$2,$3,$4) ON CONFLICT(configuration_id) DO UPDATE SET end_date=EXCLUDED.end_date,batch_hash=EXCLUDED.batch_hash',
            manifest["configuration_id"],
            start,
            end,
            record_hash(manifest),
        )
    return results


def prepare_bigquery(client, directory, manifest, owner):
    stages = {}
    for table in (t for t in TABLES if t.source == "bigquery"):
        target = bigquery.Table(f"{PROJECT}.{DATASET}.{table.name}", schema=bq_schema(table))
        target.description = f"{VERSION}. {table.description} record_hash is ingestion metadata."
        if table.partition:
            target.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY, field=table.partition
            )
        if table.cluster:
            target.clustering_fields = list(table.cluster)
        actual = client.create_table(target, exists_ok=True)
        aliases = {"INTEGER": "INT64", "BOOLEAN": "BOOL", "DECIMAL": "NUMERIC"}
        if [(f.name, aliases.get(f.field_type, f.field_type), f.mode) for f in actual.schema] != [
            (f.name, aliases.get(f.field_type, f.field_type), f.mode) for f in target.schema
        ]:
            raise ValueError(f"Unexpected existing BigQuery schema: {table.name}")
        if (actual.time_partitioning.field if actual.time_partitioning else None) != table.partition or list(
            actual.clustering_fields or []
        ) != list(table.cluster):
            raise ValueError(f"Unexpected partitioning/clustering: {table.name}")
        stage_name = f"_retail_ts_stage_{owner}_{table.name}"
        stage = bigquery.Table(f"{PROJECT}.{DATASET}.{stage_name}", schema=bq_schema(table))
        stage.expires = datetime.now(UTC) + timedelta(hours=24)
        client.create_table(stage)
        stages[table.name] = stage_name
        with (directory / f"{table.name}.parquet").open("rb") as stream:
            client.load_table_from_file(
                stream,
                stage.reference,
                location="asia-southeast1",
                job_config=bigquery.LoadJobConfig(
                    source_format=bigquery.SourceFormat.PARQUET,
                    schema=bq_schema(table),
                    write_disposition=bigquery.WriteDisposition.WRITE_EMPTY,
                ),
            ).result(timeout=600)
    return stages


def merge_bigquery(client, stages, owner):
    sql = [
        "BEGIN TRANSACTION;",
        f"ASSERT EXISTS(SELECT 1 FROM {qualified(STATE)} WHERE id='current' AND owner=@owner AND status='loading' AND expires>CURRENT_TIMESTAMP()) AS 'Upload lease lost';",
    ]
    for table in (t for t in TABLES if t.source == "bigquery"):
        target, stage = qualified(table.name), qualified(stages[table.name])
        join = " AND ".join(f"t.`{k}`=s.`{k}`" for k in table.key)
        names = ",".join(f"`{c.name}`" for c in table.columns)
        values = ",".join(f"s.`{c.name}`" for c in table.columns)
        sql += [
            f"ASSERT NOT EXISTS(SELECT 1 FROM {target} t JOIN {stage} s ON {join} WHERE t.record_hash<>s.record_hash) AS 'Existing {table.name} records differ';",
            f"MERGE {target} t USING {stage} s ON {join} WHEN NOT MATCHED THEN INSERT({names}) VALUES({values});",
        ]
    sql.append("COMMIT TRANSACTION;")
    query(client, "\n".join(sql), owner=owner)


async def upload_cloud(directory: Path, progress=lambda message: None):
    validation = await asyncio.to_thread(validate_bundle, directory)
    if not validation["passed"]:
        raise ValueError("Bundle reconciliation failed; nothing was uploaded.")
    manifest = read_manifest(directory, verify_hashes=False)
    credentials = operator_credentials()
    client = bigquery.Client(project=PROJECT, location="asia-southeast1", credentials=credentials)
    owner = uuid.uuid4().hex
    stages, claimed = {}, False
    try:
        dataset = await asyncio.to_thread(client.get_dataset, DATASET)
        if dataset.location.lower() != "asia-southeast1":
            raise ValueError("Unexpected demo dataset location.")
        await asyncio.to_thread(claim, client, manifest, owner)
        claimed = True
        progress("Upload fence acquired; loading dedicated BigQuery staging tables")
        stages = await asyncio.to_thread(prepare_bigquery, client, directory, manifest, owner)
        async with postgres_connection(credentials) as connection:
            progress("Copying and reconciling PostgreSQL dimensions transactionally")
            pg = await upload_postgres(connection, directory, manifest)
        progress("Merging BigQuery history in one insert-only transaction")
        await asyncio.to_thread(merge_bigquery, client, stages, owner)
        bq = []
        for table in (t for t in TABLES if t.source == "bigquery"):
            rows = await asyncio.to_thread(
                query, client, f"SELECT COUNT(*) AS row_count FROM {qualified(table.name)}"
            )
            count = next(iter(rows))["row_count"]
            if count != manifest["files"][table.name]["rows"]:
                raise ValueError(f"Unexpected BigQuery count: {table.name}")
            bq.append({"table": table.name, "rows": count})
        rows = await asyncio.to_thread(
            query, client, f"SELECT SUM(revenue) revenue FROM {qualified('sales_orders')}"
        )
        revenue = next(iter(rows))["revenue"] or Decimal(0)
        if int(revenue * 100) != manifest["summary_cents"]["revenue"]:
            raise ValueError("Cloud revenue did not reconcile the local ledger.")
        await asyncio.to_thread(
            query,
            client,
            f"BEGIN TRANSACTION; ASSERT EXISTS(SELECT 1 FROM {qualified(STATE)} WHERE id='current' AND owner=@owner AND status='loading' AND expires>CURRENT_TIMESTAMP()) AS 'Upload lease lost'; UPDATE {qualified(STATE)} SET status='ready',expires=NULL WHERE id='current' AND owner=@owner; COMMIT TRANSACTION;",
            owner=owner,
        )
        return {
            "version": VERSION,
            "status": "ready",
            "configuration_id": manifest["configuration_id"],
            "bigquery": bq,
            "postgres": pg,
            "revenue": str(revenue),
            "batch_hash": record_hash(manifest),
            "activation": {
                "DATA_PROFILE": "timeseries",
                "SOURCE_ROW_LIMIT": "30000",
                "postgres_schema": PG_SCHEMA,
            },
        }
    except BaseException:
        if claimed:
            try:
                await asyncio.to_thread(
                    query,
                    client,
                    f"UPDATE {qualified(STATE)} SET status='failed',expires=NULL WHERE id='current' AND owner=@owner",
                    owner=owner,
                )
            except Exception:
                pass
        raise
    finally:
        # Only staging tables owned by this exact upload are deleted; failed loads also expire.
        for name in stages.values():
            await asyncio.to_thread(client.delete_table, f"{PROJECT}.{DATASET}.{name}", not_found_ok=True)
        client.close()
