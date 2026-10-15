# Querylane backend

FastAPI, Google ADK, Gemini, and controlled BigQuery/PostgreSQL analysis, with named Firestore persistence in cloud mode.

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

## Deployment

Use the **[Deployment guide](../docs/deployment-guide.md)** before deploying, provisioning supporting resources, changing secrets/IAM, seeding data, or troubleshooting Cloud Run. It documents the production entrypoint, dedicated identity, source permissions, model locations, verification tools, and rollback.

Follow [repository instructions](../AGENTS.md). Administrative seed/reset commands are separate from routine releases and have the data effects described in the guide.
