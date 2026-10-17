# Querylane · Agentic BI

Public retail analytics using Next.js + shadcn/ui, FastAPI, Google ADK, Gemini, Firestore, BigQuery, and PostgreSQL. No registration or sign-in. All conversations are public.

Open the [landing page](https://agentic-bi-frontend-wekihucn7q-as.a.run.app), enter the [workspace](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/app), or inspect the latest verified [daily chart](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/app?chat=3cec5989c73d4cbab583d52d09e7e452) and [cross-source example](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/app?chat=acec63b2f1ef461bbbba797b3d123a7b).

Personalize the workspace in [Settings](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/settings). Appearance, chart, conversation, and voice preferences are saved per browser.

Explore the public [Dashboards](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/dashboards), [Reports](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/reports), and [Skills](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/skills) libraries. Dashboards have View/Edit modes, public share links, and PNG, JPEG, PDF, full-data CSV ZIP, and JSON downloads. Reports provide immutable versions and PDF, Word, and data downloads. Questions, saved results, skills, dashboards and reports are public; guest tokens provide request attribution rather than private accounts.

The deployed [public landing page](docs/landing-page.md) is at `/`; the workspace is at `/app`. **Open Querylane** enters directly without authentication; legacy root conversation links remain compatible. The [latest deployed assessment](docs/evaluation/e2e-fixes-deployed.md) verifies the landing page, corrected analytics, multi-turn voice, reports, predictions and dashboards against the unchanged larger data profile.

## Repository map

| Path | Responsibility |
| --- | --- |
| [`Frontend/`](Frontend/README.md) | Next.js landing page, `/app` workspace, shared libraries, chart exploration, settings and browser voice transport |
| [`Backend/`](Backend/README.md) | Public FastAPI API, controlled analytics, versioned libraries and private report-worker entrypoint |
| [`Backend/app/skill_library/`](Backend/app/skill_library/) | Source-controlled analytics and prediction playbooks; publication is a separate operator action |
| [`infra/`](infra/) | Scoped cloud provisioning, release and runtime-verification helpers |
| [`docs/architecture.md`](docs/architecture.md) | Component boundaries, data flows, persistence and source-code map |
| [`graphify-out/`](graphify-out/README.md) | Generated code/documentation graph, interactive viewer, analysis and source-hash validation |
| [`docs/graphify/`](docs/graphify/README.md) | Curated Mermaid graph references exported from the architecture document |
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

- [Expanded retail history](docs/retail-timeseries.md): 573,348 orders from January 2023 through September 2026, 1,317,941 line items, dated refunds, stores, promotions, and a daily calendar. Reproducible Parquet generation, validation, insert-only cloud upload, and date-range extension scripts preserve the original demo tables.

- Shared conversations, follow-ups, immutable result references, forks, and share links.
- Conversational [voice skill author](docs/voice-skill-author-plan.md): interview, requirements checklist, recoverable draft, review, and explicit publication. See [implementation validation](docs/validation.md#conversational-voice-skill-author--2026-10-16) and the current deployment record for verification scope.
- Public [skills library](docs/skills.md): versioned Markdown playbooks, import/export, automatic discovery, chat attachments, and recoverable deletion. Open the [deployed skills library](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/skills).
- [Analytics and prediction playbooks](docs/analytics-skills.md): twelve skills for quality checks, weighted KPIs, change diagnostics, cohorts, margin, campaigns, stores, seasonality, validated forecasts and conditional scenarios, with sample questions and reproducible insert-only seeding.
- ADK planning and interpretation with Gemini; schema embeddings and Firestore vector retrieval.
- Guarded BigQuery/PostgreSQL connectors, explicit-key SQL join validation (including nested queries), independent per-analysis query evidence, and bounded result pages. The guard rejects unsupported joins; it does not establish business-grain correctness by itself.
- Automatically inferred, type-checked cross-source relationships; duplicate-key and incomplete-input rejection.
- Bar, line, area, pie, scatter, table, and KPI views with accessible table alternatives.
- Gemini Live voice bridge, PCM microphone streaming, replace-aware transcripts, interruption, mute, and resumption. Repeated analyses in one connection have distinct query/job identities; intentional repeated questions remain separate turns.
- [Interactive charts](docs/charts.md): full saved-result coverage, factual highlights, per-measure tooltips, range and series controls, chart-to-chat drafts, and PNG/CSV exports.
- Browser-local [settings](docs/settings.md): Gemini Flash/Flash-Lite analysis model selection, light/dark/system themes, accent colors, density, chart defaults, chat shortcuts, and voice preferences.
- [Motion and feedback](docs/motion-and-feedback.md) using Framer Motion, beUI, and Sonner, with shared reduced-motion support and reader-aware result scrolling.
- Anonymous guest tokens, shared usage counters, fenced conversation leases, and event replay.
- CLI-only seed/reset commands and isolated cloud build/deployment scripts.

## Error handling and recovery

See [the retry and recovery policy](docs/error-handling.md) for Gemini, voice, source cancellation, streams and durable reports. The [local fault-injection audit](docs/evaluation/error-resilience-20261017.md) and [deployed resilience assessment](docs/evaluation/resilience-deployed.md) distinguish deterministic failure coverage from real hosted AI/voice verification.

## Verify

```bash
cd Backend
uv run pytest -q
uv run ruff check app tests scripts
# The fixture evaluator targets the original legacy seed, not hosted timeseries data:
uv run python -m app.evaluate --mode fixture --output ../docs/evaluation/fixture.json
```

```bash
cd Frontend
npm run lint
npm test
npx tsc --noEmit
npm run build
```

See [local setup](docs/setup.md), [deployment guide](docs/deployment-guide.md), [architecture](docs/architecture.md), [database schema guide](docs/database-schema.md), [demo script](docs/demo.md), [validation notes](docs/validation.md), and [domain glossary](CONTEXT.md).

Run Ruff from `Backend/` so it uses the configured first-party import classification. For explicitly requested hosted verification, follow the [deployment runbook](docs/deployment-guide.md), including the profile-aware `scripts.smoke_timeseries`, repeated-tool `scripts.smoke_voice_turns` and controlled `scripts.smoke_voice_recovery` checks. These invoke real models/queries, consume quotas, and create public test evidence; they are not part of a documentation refresh.

For Firestore transaction and durability coverage, run the backend suite with `FIRESTORE_EMULATOR_HOST` pointing to a running local emulator, as described in the deployment guide. Plain local tests use memory storage. Real model calls, hosted smoke tests and example-skill seeding are separate, opt-in operations. For documentation-only changes, check local links and regenerate the [graph references](docs/graphify/README.md#refresh) instead of rerunning application or billable cloud checks.

## Cloud status

The latest verified release is dated **17 October 2026**: frontend **`agentic-bi-frontend-00014-8p8`**, public backend **`agentic-bi-backend-00019-kwg`**, and private report worker **`agentic-bi-report-worker-00008-xwl`**, each at 100% traffic. See [the deployed resilience assessment](docs/evaluation/resilience-deployed.md) and [deployment.json](docs/deployment.json) for image digests, preserved configuration and rollback references. These are dated observations; inspect live state before a new release.

This release hardens bounded Gemini retries, recoverable Live tool errors, source cancellation, cleanup and browser HTTP/event recovery. Local verification passed **340 backend tests with one existing skip**, **44 frontend tests**, Ruff, lint, TypeScript and production build. Hosted checks passed **40/40 analytics**, **4/4 repeated Live-tool**, **7/7 same-session voice recovery**, **5/5 conversational skill author**, **9/9 synthetic spoken-browser**, **3/3 browser reconnect/permission**, and **26/26 report** checks. The report reader passed its seven browser assertions and an axe scan with zero automated violations. The report suite also verifies dashboard pinning and retained evidence; the [previous dashboard-specific acceptance](docs/evaluation/e2e-fixes-deployed.md) remains a separate dated record.

The deployed application continues to use the **larger synthetic dataset**: **573,348 orders**, **1,317,941 line items**, **25,000 customers**, **45 months** and **1,369 calendar days** from January 2023 through September 2026. Daily and monthly revenue reconcile independently to **USD 354,425,112.20**. BigQuery source counts, bytes, schemas and modification timestamps were identical before and after this release ([preservation evidence](docs/evaluation/resilience-source-preservation.json)). Preserve **`DATA_PROFILE=timeseries`** and **`SOURCE_ROW_LIMIT=30000`** on both analytical runtimes; use the runbook's `--data-profile timeseries` release path. Generated bundles stay outside Git and Cloud Build.

Inspect the verified [Business report](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/reports/4cdb492ffa39d745be7c53c00ebc25c1?version=1), its [Technical revision](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/reports/4cdb492ffa39d745be7c53c00ebc25c1?version=2), and [saved forecast dashboard](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/dashboards/4e1c7b1bea5c48b283542c66b1da3762). The new report has a reviewed narrative and validated ETS prediction; unsupported narratives can still fall back to verified summaries, and forecasts can be withheld when history or backtests are insufficient.

The public frontend/backend and separate private worker use dedicated identities in `asia-southeast1`, project `project-e8b1593d-009a-4822-abf`. Reports dispatch through Cloud Tasks with a scheduled reconciler and private file bucket. Firestore is backend-only. Search research remains disabled. No source-data upload, seed, IAM change or history/usage reset was part of the fix release.

The [assessment's boundaries](docs/evaluation/resilience-deployed.md#boundaries) distinguish real browser/runtime verification with synthetic speech from untested physical microphone/speaker quality, Safari/Firefox, full screen-reader use and other manual checks. The emulator-dependent durability variant remains skipped. One reconciler capacity rejection recovered at the next scheduled minute; three ERROR entries were expected owner-cancellation traces ([log assessment](docs/evaluation/resilience-runtime-logs.json)). Historical failed assessments remain preserved rather than rewritten as successes. Cloud services and models are billable; limits and alerts are not hard spending caps. Existing Firestore databases and `enterprise_*` BigQuery datasets remain outside this application's scope.
