# Querylane · Agentic BI

Public retail analytics using Next.js + shadcn/ui, FastAPI, Google ADK, Gemini, Firestore, BigQuery, and PostgreSQL. No registration or sign-in. All conversations are public.

Open the [landing page](https://agentic-bi-frontend-wekihucn7q-as.a.run.app), enter the [workspace](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/app), or inspect the latest verified [daily chart](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/app?chat=3cec5989c73d4cbab583d52d09e7e452) and [cross-source example](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/app?chat=acec63b2f1ef461bbbba797b3d123a7b).

Personalize the workspace in [Settings](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/settings). Appearance, chart, conversation, and voice preferences are saved per browser.

Explore the public [Metrics](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/metrics), [Forecast Plans](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/forecast-plans), [Dashboards](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/dashboards), [Reports](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/reports), and [Skills](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/skills) libraries. Dashboards have View/Edit modes, public share links, and PNG, JPEG, PDF, full-data CSV ZIP, and JSON downloads. Reports provide immutable versions and PDF, Word, and data downloads. Questions, saved results, skills, dashboards and reports are public; guest tokens provide request attribution rather than private accounts.

The deployed [public landing page](docs/landing-page.md) is at `/`; the workspace is at `/app`. **Open Querylane** enters directly without authentication; legacy root conversation links remain compatible. The four-tab guided preview demonstrates Reports, Forecasts, Scenarios and Voice BI from packaged content. Forecast points, measured model comparisons and explicit conditional paths link to verified report versions; browsing the preview makes no backend, microphone or model calls. See [the landing-specific acceptance](docs/evaluation/landing-timesfm-deployed.md) and [TimesFM analytical acceptance](docs/evaluation/timesfm-deployed.md) for their distinct verification scopes.

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

### Metrics, AI dashboards and Forecast Plans

- [Business Metrics Catalog](docs/business-metrics.md): `/metrics` provides public versioned calculations, controlled compilation, numerical previews and saved-definition evidence.
- [AI Dashboard Builder](docs/ai-dashboard-builder.md): `/dashboards/build` reuses matching evidence, analyzes missing questions, and supports reviewed creation/edits, atomic publication, rebase and conditional Undo.
- [Hierarchical Forecast Plans](docs/forecast-plans.md): `/forecast-plans` reconciles company/region/store and category/product revenue, labels allocations, saves separate planning adjustments and supplies PDF/CSV ZIP/JSON downloads and versioned dashboard pins.

These reuse the existing private worker and shared expensive-job quotas. Forecast Plans alone allow up to 128 fits; report and TimesFM ceilings are unchanged. No analytical migration/upload or IAM expansion is required. These features are deployed; see the [18 October release verification](docs/evaluation/planning-release-20261018.md). Fresh builder/plan execution remains unverified at the existing shared daily quota; the release does not reset or raise it.


- [TimesFM forecasting](docs/timesfm.md): agent-proposed forecasts with measured comparison against statistical methods, explicit driver scenarios and saved model evidence. Enabled in the recorded Cloud Run release after worker-identity verification; [forecast/scenario acceptance](docs/evaluation/timesfm-deployed.md) retains numerical and data-preservation evidence. Local defaults remain disabled.
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

The latest deployment is dated **18 October 2026**: frontend, API and private worker each serve their verified release image at 100% traffic; exact revision/digest and rollback references are in `docs/deployment.json`. It adds Metrics, reviewed AI dashboards and Forecast Plans. [Release verification](docs/evaluation/planning-release-20261018.md) records **121 passing core hosted checks**, 442 backend tests (one existing skip), 53 frontend tests and lint/types/build. Fresh builder/plan execution remains unverified at the existing 12/12 shared daily allowance; no quota was reset or increased. See [deployment.json](docs/deployment.json) for digests, preserved configuration and rollback targets. These are dated observations; inspect live state before another release.

**TimesFM 3.0 Preview is enabled** after actual worker-identity verification without IAM changes. Gemini/ADK proposes relevant forecasts and priorities; chronological backtests select the published method. Hosted acceptance passed **31 checks**, including a three-month forecast, an explicit fourteen-day promotion scenario, saved-score reconciliation, immutable downloads, presentation reuse and dashboard pinning. Both tested reports selected TimesFM on measured errors; future accuracy and causal promotion lift are not guaranteed. Unsupported uncertainty bands were omitted and disclosed.

The TimesFM analytical release’s local verification passed **385 backend tests with one existing skip**, **47 frontend tests**, Ruff, lint, TypeScript and production build. Actual worker compatibility, runtime persistence/reader/model access, repeated spoken Live analysis and browser checks passed. Chromium found no page overflow or uncaught errors; axe reported zero violations and one incomplete SVG-contrast rule. The preceding [resilience release](docs/evaluation/resilience-deployed.md) retains its earlier retry, voice-recovery and accessibility evidence.

The subsequent landing update passed **49 frontend tests**, lint, TypeScript and production build; hosted checks covered the four preview tabs, saved report links, mobile/keyboard interaction, direct workspace entry and health. It made no new inference calls.

The larger synthetic dataset remains **573,348 orders**, **1,317,941 line items**, **25,000 customers**, **45 months** and **1,369 calendar days** from January 2023 through September 2026. Monthly saved revenue reconciles to **USD 354,425,112.20**. All five BigQuery table counts/content fingerprints matched before and after release ([preservation evidence](docs/evaluation/timesfm-data-preservation.json)); PostgreSQL reader verification retained 25,000 customers. Preserve **`DATA_PROFILE=timeseries`** and **`SOURCE_ROW_LIMIT=30000`** on both analytical runtimes. Generated bundles stay outside Git and Cloud Build.

Inspect the [monthly forecast](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/reports/2ed05089e9a86e1ef3046fa6c6728680?version=1), [conditional scenario](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/reports/f0853cca9462ee293ddaf45e6627e843?version=1), and [saved prediction dashboard](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/dashboards/7d213e6c777244fb99c9bc363ff42f22). Presentation revisions, downloads and dashboard views reuse immutable predictions without inference. Insufficient history, poor backtests or provider failures retain supported findings and explicit limitations.

The services retain dedicated identities in `asia-southeast1`, project `project-e8b1593d-009a-4822-abf`, Cloud Tasks dispatch, scheduled reconciliation and private report storage. Firestore is backend-only, the worker remains private, and Search research remains disabled. No source upload, seed, migration, IAM change or history/quota reset occurred. Local defaults remain disabled for unverified environments.

[Verification boundaries](docs/evaluation/timesfm-deployed.md#interface-and-regression-checks) distinguish actual hosted/browser checks and Live spoken output from physical microphone/speaker testing, exhaustive screen-reader/cross-browser coverage and production crash injection. Historical failed/local assessments remain dated evidence. Cloud services and models are billable; budgets and alerts are not hard spending caps. Existing unrelated databases and `enterprise_*` datasets remain outside scope.
