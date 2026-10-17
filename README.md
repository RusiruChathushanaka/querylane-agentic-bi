# Querylane · Agentic BI

Public retail analytics using Next.js + shadcn/ui, FastAPI, Google ADK, Gemini, Firestore, BigQuery, and PostgreSQL. No registration or sign-in. All conversations are public.

Open the [deployed application](https://agentic-bi-frontend-wekihucn7q-as.a.run.app), [full daily chart](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/?chat=b13399e915de46d78f950d08345f0893), or [validated cross-source example](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/?chat=92b4d70a61414b8e9e77a2bcd5c97d45).

Personalize the workspace in [Settings](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/settings). Appearance, chart, conversation, and voice preferences are saved per browser.

Explore the public [Dashboards](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/dashboards), [Reports](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/reports), and [Skills](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/skills) libraries. Dashboards have View/Edit modes, public share links, and PNG, JPEG, PDF, full-data CSV ZIP, and JSON downloads. Reports provide immutable versions and PDF, Word, and data downloads. Questions, saved results, skills, dashboards and reports are public; guest tokens provide request attribution rather than private accounts.

The current source adds a [public landing page](docs/landing-page.md) at `/` and moves the workspace to `/app`. Open Querylane enters directly without authentication; legacy root conversation links remain compatible. This landing-page change is locally verified and awaiting a separately requested release; the cloud records below describe the previous release.

## Repository map

| Path | Responsibility |
| --- | --- |
| [`Frontend/`](Frontend/README.md) | Next.js landing page, `/app` workspace, shared libraries, chart exploration, settings and browser voice transport |
| [`Backend/`](Backend/README.md) | Public FastAPI API, controlled analytics, versioned libraries and private report-worker entrypoint |
| [`Backend/app/skill_library/`](Backend/app/skill_library/) | Source-controlled analytics and prediction playbooks; publication is a separate operator action |
| [`infra/`](infra/) | Scoped cloud provisioning, release and runtime-verification helpers |
| [`docs/architecture.md`](docs/architecture.md) | Component boundaries, data flows, persistence and source-code map |
| [`docs/graphify/`](docs/graphify/README.md) | Standalone Mermaid graph references exported from the architecture document |
| [`docs/evaluation/`](docs/evaluation/) | Dated numerical, reliability, browser and deployed verification evidence |
| `data/` | Ignored generated analytical bundles; uploaded independently from application releases |

Start with [AGENTS.md](AGENTS.md) for contributor constraints and [CONTEXT.md](CONTEXT.md) for domain terminology.

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

Open [the local landing page](http://localhost:3000), then select **Open Querylane**, or go directly to [the workspace](http://localhost:3000/app). Local mode uses deterministic, synthetic fixtures and in-memory history. The interface labels it explicitly; it does not pretend to call AI or hosted databases.

To try **real Gemini text and live voice against synthetic fixtures**, use the currently authenticated gcloud operator in the backend terminal:

```bash
uv run uvicorn app.cloud_preview:app --host 127.0.0.1 --port 8000
```

This preview uses an operator access token only in memory. Restart it when that token expires. Do not deploy `app.cloud_preview`; production uses an attached service account and requires real connectors and Firestore. For normal local access to cloud services, configure ADC with `gcloud auth application-default login` and use the documented environment variables.

## Included behavior

- [Advanced Analysis reports](docs/reports.md): ADK specialist workflow, concurrent chat, public versioned Reports library, validated forecasts/scenarios, PDF/Word/CSV downloads, dashboard pins and optional requester-only research. Enable **Advanced Analysis** beside the composer to create a public report. Production uses the private Cloud Run report worker and Cloud Tasks; see the release and validation records.

- Public [dashboard library](docs/dashboards.md): create shared dashboards, pin saved chart/KPI/table views, arrange cards, and recover removed items. View/Edit modes, sharing, and whole-dashboard PNG/JPEG/PDF/CSV ZIP/JSON downloads are deployed. Pinning/viewing/downloading runs no new analysis. Images/PDF use published card scopes; CSVs retain full saved results. JSON contains metadata, not a restorable data backup.

- [Expanded retail history](docs/retail-timeseries.md): 573,348 orders across 2023–2026, 1.3 million line items, dated refunds, stores, promotions, and a daily calendar. Reproducible Parquet generation, validation, insert-only cloud upload, and date-range extension scripts preserve the original demo tables.

- Shared conversations, follow-ups, immutable result references, forks, and share links.
- Conversational [voice skill author](docs/voice-skill-author-plan.md): interview, requirements checklist, recoverable draft, review, and explicit publication. See [implementation validation](docs/validation.md#conversational-voice-skill-author--2026-10-16) and the current deployment record for verification scope.
- Public [skills library](docs/skills.md): versioned Markdown playbooks, import/export, automatic discovery, chat attachments, and recoverable deletion. Open the [deployed skills library](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/skills).
- [Analytics and prediction playbooks](docs/analytics-skills.md): twelve skills for quality checks, weighted KPIs, change diagnostics, cohorts, margin, campaigns, stores, seasonality, validated forecasts and conditional scenarios, with sample questions and reproducible insert-only seeding.
- ADK planning and interpretation with Gemini; schema embeddings and Firestore vector retrieval.
- Guarded BigQuery/PostgreSQL connectors, independent query evidence, bounded result pages.
- Automatically inferred, type-checked cross-source relationships; duplicate-key and incomplete-input rejection.
- Bar, line, area, pie, scatter, table, and KPI views with accessible table alternatives.
- Gemini Live voice bridge, PCM microphone streaming, transcripts, interruption, mute, and resumption.
- [Interactive charts](docs/charts.md): full saved-result coverage, factual highlights, per-measure tooltips, range and series controls, chart-to-chat drafts, and PNG/CSV exports.
- Browser-local [settings](docs/settings.md): Gemini Flash/Flash-Lite analysis model selection, light/dark/system themes, accent colors, density, chart defaults, chat shortcuts, and voice preferences.
- [Motion and feedback](docs/motion-and-feedback.md) using Framer Motion, beUI, and Sonner, with shared reduced-motion support and reader-aware result scrolling.
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

See [local setup](docs/setup.md), [deployment guide](docs/deployment-guide.md), [architecture](docs/architecture.md), [database schema guide](docs/database-schema.md), [demo script](docs/demo.md), [validation notes](docs/validation.md), and [domain glossary](CONTEXT.md).

For Firestore transaction and durability coverage, run the backend suite with `FIRESTORE_EMULATOR_HOST` pointing to a running local emulator, as described in the deployment guide. Plain local tests use memory storage. Real model calls, hosted smoke tests and example-skill seeding are separate, opt-in operations. For documentation-only changes, check local links and regenerate the [graph references](docs/graphify/README.md#refresh) instead of rerunning application or billable cloud checks.

## Cloud status

The last verified release is dated **17 October 2026**. The public frontend and backend, plus a separate **private report worker**, are deployed in `asia-southeast1` in project `project-e8b1593d-009a-4822-abf`, using dedicated service accounts. Reports dispatch through Cloud Tasks; a scheduled reconciler recovers pending work and report files stay in a private bucket. The named Firestore database, vector index, BigQuery dataset, Cloud SQL database, secrets, build bucket, and image repository are configured. Search research remains disabled in the recorded production configuration.

The deployed application uses the **larger generated dataset**: 573,348 orders and 25,000 customers from January 2023 through September 2026. Its 45-month and 1,369-day charts reconcile to **$354,425,112.20** in merchandise revenue. Keep `--data-profile timeseries` on future backend releases; generated files are excluded from Git and Cloud Build uploads.

The [latest dashboard-actions release](docs/validation.md#dashboard-actions-cloud-release--2026-10-17) records **400 backend tests passed / 1 skipped**, **28 frontend tests**, **26 hosted API checks**, and **21 runtime-identity checks**. Lint, types, production build and desktop/mobile browser checks passed. Seven accessibility scans found zero automated violations, with manual-review limitations recorded. All five dashboard formats were checked; browser PNG/PDF/CSV downloads and stale-revision recovery were exercised. [deployment.json](docs/deployment.json) records backend `00017-cnf`, frontend `00011-vr4`, and private worker `00006-sk6`, with digests and rollback references. These are dated observations; inspect live state for a new release.

Earlier [chart acceptance](docs/evaluation/charts-deployed.json) covers 40 time-series/voice checks. [Report-release evidence](docs/evaluation/reports-deployed.json) covers the durable report workflow; the latest recorded sample explicitly uses verified evidence summaries when its AI narrative fails review. Forecasts can be withheld when data or backtests are insufficient. Historical evaluation files retain their original scope and are not rerun claims for the latest release. Cloud SQL, Cloud Run, models and supporting services are billable; configured limits and billing alerts are not a hard spending cap.

The existing Firestore databases and `enterprise_*` BigQuery datasets are outside this application's scope.
