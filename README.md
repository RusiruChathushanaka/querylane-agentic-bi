# Querylane · Agentic BI

Public retail analytics using Next.js + shadcn/ui, FastAPI, Google ADK, Gemini, Firestore, BigQuery, and PostgreSQL. No registration or sign-in. All conversations are public.

Open the [deployed application](https://agentic-bi-frontend-wekihucn7q-as.a.run.app) or the [validated cross-source example](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/?chat=d0f257e2cd6e4453921990b03a087536).

## Deployment reference

Use the **[Deployment guide](docs/deployment-guide.md)** before deploying to Google Cloud Run or changing the supporting IAM, Firestore, BigQuery, Cloud SQL, Secret Manager, or build resources. It covers first-time provisioning, routine releases, configuration, acceptance checks, rollback, and troubleshooting.

[AGENTS.md](AGENTS.md) directs repository agents to use the same guide for deployment-related tasks. [deployment.json](docs/deployment.json) records the last verified release; inspect live cloud state before relying on it for a new deployment.

## Run locally

Requirements: Node 26, npm, Python 3.12, and uv. The checked-in lockfiles capture compatible versions. FastAPI is pinned below 0.142 because newer releases require telemetry packages incompatible with the installed ADK 2.12.

Terminal 1:

```bash
cd Backend
uv sync --frozen
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2:

```bash
cd Frontend
npm ci
npm run dev
```

Open [the local workspace](http://localhost:3000). Local mode uses deterministic, synthetic fixtures and in-memory history. The interface labels it explicitly; it does not pretend to call AI or hosted databases.

To try **real Gemini text and live voice against synthetic fixtures**, use the currently authenticated gcloud operator in the backend terminal:

```bash
uv run uvicorn app.cloud_preview:app --host 127.0.0.1 --port 8000
```

This preview uses an operator access token only in memory. Restart it when that token expires. Do not deploy `app.cloud_preview`; production uses an attached service account and requires real connectors and Firestore. For normal local access to cloud services, configure ADC with `gcloud auth application-default login` and use the documented environment variables.

## Included behavior

- Shared conversations, follow-ups, immutable result references, forks, and share links.
- ADK planning and interpretation with Gemini; schema embeddings and Firestore vector retrieval.
- Guarded BigQuery/PostgreSQL connectors, independent query evidence, bounded result pages.
- Automatically inferred, type-checked cross-source relationships; duplicate-key and incomplete-input rejection.
- Bar, line, area, pie, scatter, table, and KPI views with accessible table alternatives.
- Gemini Live voice bridge, PCM microphone streaming, transcripts, interruption, mute, and resumption.
- Browser-local [settings](docs/settings.md): light/dark/system themes, accent colors, density, chart defaults, chat shortcuts, and voice preferences.
- Anonymous guest tokens, shared usage counters, fenced conversation leases, and event replay.
- CLI-only seed/reset commands and isolated cloud build/deployment scripts.

## Verify

```bash
cd Backend
uv run pytest -q
uv run ruff check app tests scripts
uv run python -m app.evaluate --mode fixture --output ../docs/evaluation/fixture.json
# Opt-in real model calls, using the current gcloud account:
uv run python -m app.admin check-models
uv run python -m app.evaluate --mode gemini --output ../docs/evaluation/gemini.json
uv run python -m scripts.smoke_voice
```

```bash
cd Frontend
npm run lint
npm test
npx tsc --noEmit
npm run build
```

See [local setup](docs/setup.md), [deployment guide](docs/deployment-guide.md), [architecture](docs/architecture.md), [demo script](docs/demo.md), [validation notes](docs/validation.md), and [domain glossary](CONTEXT.md).

## Cloud status

Both services are deployed in `asia-southeast1` in project `project-e8b1593d-009a-4822-abf`, using dedicated service accounts. The named Firestore database, vector index, BigQuery dataset, Cloud SQL database, secrets, build bucket, and image repository are configured. The scoped IAM grants were explicitly approved and applied.

The deployed smoke test verifies hosted numbers, follow-ups, forks, browser CORS, and Gemini Live audio/transcripts. A separate private runtime check verifies denial on existing data resources and real Firestore concurrency. See `docs/evaluation/deployed.json` and `docs/evaluation/cloud-runtime.json`. The final hosted numerical evaluation passes 31/31 cases, all using vector retrieval. Cloud SQL and Cloud Run are billable resources; instance/query/public usage limits are configured, while billing alerts require the billing administrator.

The existing Firestore databases and `enterprise_*` BigQuery datasets are outside this application's scope.
