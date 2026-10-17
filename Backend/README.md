# Querylane backend

FastAPI, Google ADK, Gemini, and controlled BigQuery/PostgreSQL analysis, with named Firestore persistence in cloud mode.

The public API serves chat/voice analysis, the Skills, Dashboards and Reports libraries, saved chart data and downloads. Advanced reports execute through a separate private ASGI entrypoint, `app.report_worker:app`, using Cloud Tasks and application checkpoints in production. See [architecture and source map](../docs/architecture.md) and [graph references](../docs/graphify/README.md).

From this directory:

```bash
uv sync --frozen
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The default local mode uses deterministic synthetic sources and memory storage. See [local setup](../docs/setup.md) for Gemini preview, ADC, and direct local PostgreSQL configuration.

```bash
uv run pytest -q
uv run ruff check app tests scripts ../infra
```

For emulator-backed transaction and durability checks, set `FIRESTORE_EMULATOR_HOST` to the running local emulator before pytest. Local report files and memory state are ephemeral; durable execution uses the named Firestore database and private report bucket. Consult [reports](../docs/reports.md) for forecasting gates, recovery and export semantics.

Dashboard image/PDF/CSV ZIP/JSON endpoints read saved artifacts only. Their revision checks, completeness validation, process deadlines and input limits are part of the [dashboard contract](../docs/dashboards.md). Keep model/query execution outside that download path.

## Deployment

Use the **[Deployment guide](../docs/deployment-guide.md)** before deploying, provisioning supporting resources, changing secrets/IAM, seeding data, or troubleshooting Cloud Run. It documents the production entrypoint, dedicated identity, source permissions, model locations, verification tools, and rollback.

Follow [repository instructions](../AGENTS.md). Administrative seed/reset commands are separate from routine releases and have the data effects described in the guide.

Preserve the larger `timeseries` profile and existing `REPORT_*` dispatch configuration during routine releases. Report-worker releases follow the guide's separate worker path; skill seeding and analytical data upload remain explicit operator operations.

## Managed forecasting

Advanced Analysis supports optional TimesFM 3.0 Preview comparison through fixed BigQuery queries over saved evidence. Local defaults are disabled; the recorded hosted release enables it after worker-identity verification. See [TimesFM behavior and compatibility probe](../docs/timesfm.md) before enabling it. `uv run python -m scripts.smoke_timesfm` prints a local plan; `--live` is a separate bounded billable probe and never deploys or changes source data.
