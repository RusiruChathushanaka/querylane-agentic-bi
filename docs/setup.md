# Local setup

For Google Cloud Run and supporting cloud services, use the **[Deployment guide](deployment-guide.md)**. It is the primary reference for provisioning, releases, IAM/secrets, seeding, validation, rollback, and cloud troubleshooting. Local setup below does not change deployed services.

## Dependencies and default mode

Use Node 26/npm, Python 3.12, and `uv`. Install from the committed lockfiles.

Backend terminal, from the repository root:

```bash
cd Backend
uv sync --frozen
uv run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend terminal, from the repository root:

```bash
cd Frontend
npm ci
npm run dev
```

Open [localhost:3000](http://localhost:3000). Default local mode uses synthetic fixture sources, deterministic planning, and in-memory history. It needs no cloud credentials and is labeled in the interface.

## Environment files

Copy `Backend/.env.example` to `Backend/.env` and `Frontend/.env.example` to `Frontend/.env.local` only when overrides are needed. Keep real credentials out of the repository. The frontend's server-side `BACKEND_URL` defaults to `http://localhost:8000` and is read through `/api/config` at runtime.

The backend example uses `ENVIRONMENT=local`, `STORAGE_BACKEND=memory`, `DATA_BACKEND=fixture`, and `AI_BACKEND=fixture`. Leave these values for the default local experience.

## Real Gemini preview over local fixtures

With the intended operator signed in to `gcloud`, run this instead of the default backend command:

```bash
cd Backend
uv run uvicorn app.cloud_preview:app --host 127.0.0.1 --port 8000
```

The preview calls real Gemini text/live models with an operator token held in memory, while keeping synthetic sources and memory history. Model calls are billable. Restart the preview after the token expires. This entrypoint is local-only; deploy `app.serve` through the Dockerfile/helper described in the deployment guide.

## Local development with cloud services

Ordinary local SDK access uses ADC:

```bash
gcloud auth application-default login
```

Configure the intended named database, source connections, models, and permitted frontend origins in the backend environment. `STORAGE_BACKEND=firestore`, `DATA_BACKEND=cloud`, and `AI_BACKEND=gemini` use actual cloud resources; writes to the shared demo database appear in the public workspace and consume its quotas. Follow the deployment guide's resource boundaries and configuration reference.

For direct local PostgreSQL, use `DATA_BACKEND=cloud`, configure the real BigQuery source, set `POSTGRES_DSN`, and explicitly set `CLOUD_SQL_INSTANCE` empty so it does not select the Cloud SQL connector. Provide the expected `retail` schema/tables and a restricted reader role. The same SQL validation and result limits apply.

## Verification

Use the commands in the [root README](../README.md#verify) for local checks. Cloud deployment and hosted acceptance use the [Deployment guide](deployment-guide.md#acceptance-checks). Historical results and manual verification limits are recorded in [validation.md](validation.md).

## Voice skill author preview

The standard fixture backend deliberately cannot run a live interview. For a local Gemini preview on synthetic data, authenticate the operator with the documented Google Cloud setup, then run:

```bash
ALLOWED_ORIGINS=http://127.0.0.1:3002 Backend/.venv/bin/python -m uvicorn app.cloud_preview:app --app-dir Backend --host 127.0.0.1 --port 8002
```

Run the frontend with `BACKEND_URL=http://127.0.0.1:8002` and a matching origin. A second standalone preview avoids changing the existing dev server:

```bash
cd Frontend
npm run build
mkdir -p .next/standalone/.next
cp -R .next/static .next/standalone/.next/
cp -R public .next/standalone/
BACKEND_URL=http://127.0.0.1:8002 PORT=3002 HOSTNAME=127.0.0.1 node .next/standalone/server.js
```

Open `http://127.0.0.1:3002/skills` → **Create with voice**. The preview uses temporary in-memory operator credentials; restart the backend after they expire. Its conversations, author drafts, and skills are memory-only and disappear on backend restart. It does not change the hosted library. For persistent hosting, follow the deployment guide rather than deploying `app.cloud_preview`.
