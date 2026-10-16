# Deployment guide: Google Cloud Run and supporting services

This is the primary deployment runbook for Querylane. Read it before deploying, changing cloud configuration, provisioning resources, updating secrets, or troubleshooting a release. Use the existing scripts and keep this guide synchronized with changes to them.

Last reviewed: **2026-10-16**. [deployment.json](deployment.json) is the last recorded deployment, not live cloud state. [validation.md](validation.md) explains what has been verified and which manual checks remain.

| Task | Start here |
| --- | --- |
| Update the existing application | [Routine release](#routine-release) |
| Set up the cloud foundation for the first time | [First-time foundation](#first-time-foundation) |
| Understand settings and credentials | [Configuration and secrets](#configuration-and-secrets) |
| Validate a deployment | [Acceptance checks](#acceptance-checks) |
| Restore a previous release | [Rollback](#rollback) |
| Diagnose a failure | [Troubleshooting](#troubleshooting) |
| Reuse this process for another project | [Another environment or project](#another-environment-or-project) |

All commands run from the repository root unless a block explicitly changes directory. Commands in this guide are instructions for an authorized operator; reading the guide does not itself authorize cloud changes, seeding, or history deletion.

## Deployment target

| Component | Current resource |
| --- | --- |
| Google Cloud project | `project-e8b1593d-009a-4822-abf` |
| Application/data region | `asia-southeast1` |
| Next.js service | `agentic-bi-frontend` |
| FastAPI service | `agentic-bi-backend` |
| Firestore | Named database `agentic-bi-demo`, Standard edition, Native mode |
| Firestore vector index | Collection `schema_chunks`, field `embedding`, 768 dimensions, flat index |
| BigQuery | Dataset `agentic_bi_demo` |
| Cloud SQL | Instance `agentic-bi-demo-pg`, PostgreSQL 17, Enterprise, `db-f1-micro`, zonal, 10 GB SSD |
| PostgreSQL database / schema / reader | `agentic_bi` / `retail` / `bi_reader` |
| Artifact Registry | Docker repository `agentic-bi-demo` |
| Build sources and logs | Bucket `project-e8b1593d-009a-4822-abf-agentic-bi-build` |
| Secret Manager | `agentic-bi-guest-signing`, `agentic-bi-postgres-reader`, `agentic-bi-postgres-admin` |

Both application services are public. Guest tokens attribute requests and enforce ownership/quotas; they do not make conversations private. Firestore and database credentials remain backend-only. Firebase Authentication is not part of this deployment.

The existing `(default)`, `cards-acceptance`, and `commercial-staging` Firestore databases and `enterprise_*` BigQuery datasets are outside this application's scope. Preserve their data, configuration, and IAM bindings.

Set these shell variables for the commands below:

```bash
export BI_PROJECT_ID='project-e8b1593d-009a-4822-abf'
export BI_REGION='asia-southeast1'
export BI_BACKEND_URL='https://agentic-bi-backend-wekihucn7q-as.a.run.app'
export BI_FRONTEND_URL='https://agentic-bi-frontend-wekihucn7q-as.a.run.app'
```

These variables help with CLI commands only. **The Python scripts contain project/resource constants; changing shell variables does not retarget them.** See [Another environment or project](#another-environment-or-project).

### Skills library release

See [skills.md](skills.md) for behavior, APIs, and limits. Release the backend before the frontend: the UI needs the skills routes and authenticated `PATCH`/`DELETE` CORS support. This feature uses the existing named `agentic-bi-demo` Firestore database and runtime identity; it requires no additional service, IAM grant, secret, or vector index. Keep default single-field indexing available for the `deleted` field. Do not reset history or reseed analytical tables as part of this release.

New collections are `skills` with immutable `revisions`, run-scoped `skill_snapshots`, and the `system/skills_capacity` document. Existing chats and artifacts need no migration: missing attachments/provenance default to empty. Optional backend environment values are `SKILL_CATALOG_LIMIT=100`, `SKILL_GUEST_HOURLY_LIMIT=20`, and `SKILL_WORKSPACE_DAILY_LIMIT=100`.

After an authorized deployment, check create/edit/delete/restore, CORS preflight for `PATCH` and `DELETE`, skill attachments, one automatic selection, an answer's revision link, and history after restarting/scaling the backend. Test against the named database rather than accepting local memory mode as persistence evidence. For optional non-destructive example seeding, run `cd Backend` then `uv run python -m app.admin seed-skills` using operator credentials. It preserves existing examples, including public edits/deletions; routine deploy scripts do not run it.

Rollback uses the previous frontend/backend revisions through the routine runbook. Keep the additive skills collections and revision documents; older application versions ignore these fields. `reset-history` explicitly preserves skills and their capacity counter. Update deployment records only after actually deploying and verifying serving revisions.

### Voice skill author release

See [the voice-author plan](voice-skill-author-plan.md) and [skills usage](skills.md#conversational-voice-author). This implementation is not deployed by editing these documents. When release is requested, deploy backend before frontend with the normal helpers. It reuses the existing live model/location, dedicated backend identity, and named database; no new secret, IAM grant, or Firebase/browser access is needed. Its additive collection is `skill_author_sessions`; ADK sessions remain under `adk_sessions` with an explicit author lease scope.

The optional `AUTHOR_*` variables and defaults are in `Backend/.env.example`. Author connection timeout defaults to 600 seconds, within the backend Cloud Run timeout. Guest session expiry is six hours. `max_llm_calls` is not a Live budget: retain the application's turn/tool/update/transcript limits and connection quotas. CORS and WebSocket origin checks must both accept the actual frontend origin.

Before release run backend tests, frontend lint/tests/types/build, the browser loop, and the opt-in `python -m scripts.smoke_skill_author` against an isolated Gemini/memory preview. It intentionally refuses production persistence. After deployment verify owner-checked recovery, real microphone/audio, pause/reconnect, explicit draft publication, idempotent retries, skill provenance, and persistence across a new revision. Existing cloud reports do not verify these new endpoints.

Expired author records are not automatically deleted. For authorized maintenance, `cd Backend` then `uv run python -m app.admin cleanup-skill-authors` removes only expired/inactive author records and their scoped ADK sessions. Published skill revisions are retained. History reset now also removes draft author interviews; published skills remain preserved. Rollback keeps additive author documents and uses the recorded prior revisions.

### Analysis model selection release

See [workspace settings](settings.md#analysis-model-selection). Deploy backend before frontend so `GET /api/v1/models`, optional turn `model`, and analyst voice handshake `model` are supported before the selector is exposed. Pinned choices are Gemini 3.8 Flash and Gemini 3.5 Flash-Lite; both use `TEXT_MODEL_LOCATION` (currently `global`). `TEXT_MODEL` remains the operator's default. This change needs no new IAM binding, secret, database, or index. Additive run/artifact model fields require no migration; older revisions ignore them.

Before an authorized release, run `cd Backend && uv run python -m app.admin check-models` to verify the default and every selectable text model, then the existing embedding/live compatibility checks. This operator command makes billable model calls but does not deploy or seed data. Also verify access using the dedicated runtime identity after deployment: operator access alone does not prove its permissions. Do not fix an unavailable model by silently substituting one or expanding IAM without authorization.

Verify both choices in Settings, reload persistence, a new question/follow-up with model evidence, voice data analysis, and unchanged active-run/replay behavior. Local fixture mode must disclose that it does not call models. Rollback uses the normal routine-release steps; retain historical model evidence and do not reset shared history.

### Expanded time-series sources

Follow [the retail data workflow](retail-timeseries.md) and [column dictionary](retail-timeseries-schema.md). Generation, validation, and data upload are separate from an application release. The new data uses additional `sales_*`/`calendar` tables in `agentic_bi_demo` and the separate PostgreSQL schema `retail_timeseries`. It preserves the original tables, shares the existing dataset ACL, and grants only SELECT/USAGE on the new SQL schema to the existing reader. No project IAM or secret changes are needed.

Use `python -m scripts.retail_data upload --bundle PATH` to review a local-only plan; `--apply` performs the explicitly authorized data load. Never use the legacy destructive `app.admin seed` command to extend this history. Keep the same generation settings/start date and use `extend` to move the as-of end forward, including delayed refunds. An import failure marks the new source profile unavailable until a repeat of the same bundle completes. Quiesce this profile's traffic before importing; there is no cross-service distributed snapshot for queries already running.

After upload and verification, an authorized backend release opts in with `python3 infra/deploy.py --service backend --frontend-url "$BI_FRONTEND_URL" --data-profile timeseries`. That flag sets `DATA_PROFILE=timeseries` and `SOURCE_ROW_LIMIT=30000` for the 25,000-customer dimension. It derives SQL schema `retail_timeseries`; SQL allowlists, byte/scan budgets, 50,000-row fusion output bound, and incomplete-input rejection remain active. The helper defaults to `legacy`, so retain the explicit profile flag on later releases. Deploy the frontend label change as part of the normal release.

`DATA_PROFILE=timeseries uv run python -m app.admin index-schema` from `Backend/` optionally refreshes profile-tagged schema embeddings in the existing named Firestore database. It is a separate billable operator action; existing legacy chunks are retained and full-schema retrieval remains available. Verify live queries, readiness/import failure behavior, date coverage, month/year boundaries, YoY/rolling calculations, reader permissions, and source counts. Existing fixed nine-month evaluation fixtures remain valid for the legacy profile; use the new independent reconciliation report for time-series acceptance. Rollback selects `legacy` and leaves the additional data intact.

## Prerequisites

Install Google Cloud CLI including `gcloud` and `bq`, Node/npm, Python 3.12, and `uv`. The current frontend uses Node 26. Local Docker is optional: Cloud Build builds the Dockerfiles remotely. Use the committed dependency lockfiles.

```bash
gcloud version
bq version
node --version
npm --version
uv --version
gcloud auth list --filter=status:ACTIVE --format='value(account)'
gcloud projects describe "$BI_PROJECT_ID" --format='value(projectId)'
```

If the intended operator is not signed in, use `gcloud auth login`. Select the intended account with `gcloud config set account ACCOUNT_EMAIL`. Every cloud command below specifies the project explicitly; do not rely on a global default project.

There are three credential contexts:

| Context | Credential source |
| --- | --- |
| Deployment and administrative scripts | Current authenticated `gcloud` operator; admin tools capture a short-lived token in memory |
| Ordinary local SDK access to cloud services | ADC configured with `gcloud auth application-default login` |
| Deployed services and verification job | Attached dedicated service account through ADC |

Operator CLI login and local ADC are separate. Do not download service-account keys, put credentials in shell commands, or deploy `app.cloud_preview` (it is a local preview using operator credentials).

The operator needs delegated permissions to submit builds, upload to the build bucket, deploy/update Cloud Run and its public invoker policy, and act as the designated build/runtime identities. Foundation setup additionally needs API enablement, service-account/custom-role/IAM administration, and administration of the named data resources and secrets. Seeding needs demo BigQuery and Cloud SQL administration. Readiness/diagnostics need relevant metadata and log access. Use the organization's approved roles; do not solve a permission error by granting Owner/Editor to runtime or build accounts.

## Routine release

Use this path for changes to the already provisioned application. Do not rerun foundation provisioning, seeding, schema indexing, or history reset for a normal code release unless the change actually requires them.

### 1. Verify the change and capture the current release

Run the checks for the changed application. Stop on failures.

```bash
cd Backend
uv sync --frozen
uv run ruff check app tests scripts ../infra
uv run pytest -q
cd ..

cd Frontend
npm ci
npm run lint
npm test
npx tsc --noEmit
npm run build
cd ..
```

Read `infra/deploy.py`, the relevant Dockerfile, and `Backend/app/config.py` for configuration changes. Capture the current serving revisions, traffic, image references, and non-secret configuration before replacing them:

```bash
gcloud run services describe agentic-bi-backend \
  --project "$BI_PROJECT_ID" --region "$BI_REGION" \
  --format='yaml(status.latestReadyRevisionName,status.traffic,spec.template)'

gcloud run services describe agentic-bi-frontend \
  --project "$BI_PROJECT_ID" --region "$BI_REGION" \
  --format='yaml(status.latestReadyRevisionName,status.traffic,spec.template)'
```

Secret Manager entries appear as references, not secret contents; ordinary environment values are visible, so review/redact sensitive overrides before sharing a description. Keep the previous working image/revisions available for rollback. For a first-ever deployment, the services will not exist yet; continue after completing the foundation steps.

### 2. Build and deploy the changed service

Backend only:

```bash
python3 infra/deploy.py --service backend --frontend-url "$BI_FRONTEND_URL"
```

Frontend only:

```bash
python3 infra/deploy.py --service frontend --backend-url "$BI_BACKEND_URL"
```

If both change, deploy the backward-compatible backend first, verify it, then deploy the frontend. Avoid changing revisions while acceptance tests are running.

The helper uploads the repository with `.gcloudignore`, builds the chosen directory using `infra/cloudbuild.yaml`, pushes a timestamp-tagged image to the dedicated repository, and deploys it using the operator's existing permissions. It prints the service URL and image. It does not use a default Cloud Build identity or deploy from source using a broad project-wide builder role. Build logs go to the dedicated GCS bucket. See Google's [user-specified build identity guide](https://docs.cloud.google.com/build/docs/securing-builds/configure-user-specified-service-accounts).

**Configuration behavior:** the helper applies the environment and secret references declared in `infra/deploy.py`. It is not a patch that preserves every custom setting: `--env-vars-file` and `--set-secrets` can replace existing configuration in those categories. Review and incorporate intentional overrides before using the helper. Backend model/dataset/limit overrides that exist only in the console can otherwise be lost on a later release.

Always pass the **actual deployed frontend origin** for routine backend releases. Passing `http://localhost:3000` would replace the production CORS/voice allowlist.

### 3. Verify and record the release

Run [Acceptance checks](#acceptance-checks). Update [deployment.json](deployment.json) from the real service descriptions: date, URLs, serving revisions, images, identities, and readiness. Update the affected evaluation reports and [validation.md](validation.md). Do not mark a deployment ready based only on a successful build or container startup.

## First-time foundation

This section is for missing resources in an authorized target environment. It is not part of every release. The current environment is already provisioned.

### 1. Enable required APIs and inspect resources

Billing must be enabled for the selected project. Enable APIs only within the intended scope:

```bash
gcloud services enable \
  run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com \
  firestore.googleapis.com bigquery.googleapis.com sqladmin.googleapis.com \
  secretmanager.googleapis.com aiplatform.googleapis.com \
  iam.googleapis.com logging.googleapis.com storage.googleapis.com \
  --project "$BI_PROJECT_ID"

gcloud firestore databases describe \
  --database agentic-bi-demo --project "$BI_PROJECT_ID"

gcloud sql instances describe agentic-bi-demo-pg \
  --project "$BI_PROJECT_ID"
```

Create a resource only when the response establishes that it is missing. An authentication, permission, or network error is not proof of absence. For existing Firestore, confirm the named database's edition/location; do not switch the application to the default database.

### 2. Create missing Firestore and Cloud SQL instances

`infra/provision.py` does **not** create either of these instances. For this application's current configuration:

```bash
gcloud firestore databases create \
  --database agentic-bi-demo --edition standard --type firestore-native \
  --location "$BI_REGION" --project "$BI_PROJECT_ID"

gcloud sql instances create agentic-bi-demo-pg \
  --database-version POSTGRES_17 --edition enterprise --tier db-f1-micro \
  --storage-type SSD --storage-size 10 --availability-type zonal \
  --assign-ip --region "$BI_REGION" --project "$BI_PROJECT_ID"

gcloud sql instances describe agentic-bi-demo-pg \
  --project "$BI_PROJECT_ID" --format='value(state,connectionName)'
```

Wait for the SQL instance to be `RUNNABLE`. This small zonal instance is the demo baseline; production sizing, failover, backups/PITR, and recovery objectives need a separate design decision.

The backend uses the Cloud SQL Python Connector with `asyncpg`, public IP, lazy credential refresh, and a database username/password. Connector IAM authorization and PostgreSQL role privileges are separate checks. Do not open the database to `0.0.0.0/0` authorized networks. The connector handles the authenticated encrypted connection; private IP would also require actual VPC reachability. See the [connector documentation](https://github.com/GoogleCloudPlatform/cloud-sql-python-connector).

### 3. Provision dedicated identities, artifacts, dataset, and secrets

Review the intended grants, then run within the user's authorized scope:

```bash
python3 infra/provision.py --foundation
```

The script creates missing dedicated resources and adds bindings; it preserves existing bindings. It creates secrets with generated values supplied through stdin, without printing them. It is an idempotent foundation helper, not a full reconciliation tool: it does not repair arbitrary drift in existing custom roles or resource properties.

| Identity | Intended access |
| --- | --- |
| `agentic-bi-frontend@PROJECT_ID.iam.gserviceaccount.com` | No application data or secret roles |
| `agentic-bi-backend@PROJECT_ID.iam.gserviceaccount.com` | Prediction-only custom role; BigQuery job submission; demo dataset reader ACL; conditioned access to the named Firestore database and SQL instance; access to the reader/signing secrets |
| `agentic-bi-builder@PROJECT_ID.iam.gserviceaccount.com` | Artifact Registry Writer on the demo repository; Storage Object User and Legacy Bucket Reader on the demo source/log bucket |

The custom role `agenticBiModelInvoker` contains `aiplatform.endpoints.predict` and `serviceusage.services.use`. The backend has project-level `roles/bigquery.jobUser`, but dataset read access is granted separately only on `agentic_bi_demo` by the seed command. `roles/datastore.user` is conditioned on the exact demo database. `roles/cloudsql.client` is conditioned on the exact demo instance and SQL Admin service. The runtime account has no access to the PostgreSQL administrator secret.

The bucket metadata role is required because `roles/storage.objectUser` alone lacks `storage.buckets.get`; Cloud Build checks source/log bucket access before building. Keep this binding on the dedicated bucket.

### 4. Seed the synthetic data and configure the reader

**This command overwrites the demo tables and sets the dedicated instance's administrator password from its existing secret.** Use it for authorized initial seeding or an intentional source-data reset, never as a routine release step.

```bash
cd Backend
uv sync --frozen
uv run python -m app.admin seed
cd ..
```

The command grants the backend demo dataset read access, loads synthetic BigQuery tables, creates the PostgreSQL database/schema/tables, and configures `bi_reader` with SELECT privileges and read-only/time-limit defaults. It verifies that the reader has neither superuser nor replication attributes. Cloud SQL's managed administrator is not a PostgreSQL superuser; do not reintroduce superuser-only `ALTER ROLE ... NOSUPERUSER/NOREPLICATION` operations.

Credentials are stored in Secret Manager, not in connection metadata or browser configuration.

### 5. Validate Gemini and create schema embeddings/index

```bash
cd Backend
uv run python -m app.admin check-models
uv run python -m app.admin index-schema
cd ..

gcloud firestore indexes composite list \
  --database agentic-bi-demo --project "$BI_PROJECT_ID"
```

If the matching index is missing, create it:

```bash
gcloud firestore indexes composite create \
  --database agentic-bi-demo --project "$BI_PROJECT_ID" \
  --collection-group schema_chunks --query-scope collection \
  --field-config '[{"field-path":"embedding","vector-config":{"dimension":768,"flat":{}}}]'

gcloud firestore indexes composite list \
  --database agentic-bi-demo --project "$BI_PROJECT_ID" \
  --format='table(name,state)'
```

Wait for `READY` and verify an analysis artifact reports `gemini-embedding + full-schema`. The application explicitly records a full-schema fallback if retrieval is unavailable; a successful analytical answer alone does not establish that the vector index works. Google documents [named databases](https://docs.cloud.google.com/firestore/native/docs/manage-databases) and [vector indexes](https://docs.cloud.google.com/firestore/native/docs/vector-search).

The current indexing command uses the deterministic seed's schema descriptions. It skips unchanged schema/model versions. If the source schema changes beyond the seed, update schema discovery, the indexing path, embedding metadata, and evaluation fixtures together rather than assuming this admin command discovers arbitrary new tables.

### 6. Bootstrap both application URLs

For the first deployment only, use a temporary local frontend origin while obtaining the backend URL:

```bash
python3 infra/deploy.py --service backend --frontend-url http://localhost:3000
```

Set `BI_BACKEND_URL` to the URL actually printed by that deployment. Then:

```bash
python3 infra/deploy.py --service frontend --backend-url "$BI_BACKEND_URL"
```

Set `BI_FRONTEND_URL` to the printed frontend URL, then replace the temporary backend allowlist:

```bash
gcloud run services update agentic-bi-backend \
  --project "$BI_PROJECT_ID" --region "$BI_REGION" \
  --update-env-vars "ALLOWED_ORIGINS=$BI_FRONTEND_URL"
```

The origin must match what the browser actually opens, including scheme and host. An alternative Cloud Run hostname or custom domain must also be intentionally configured if it will be used. For multiple origins, account for gcloud's comma-separated flag parsing; use an escaped value or a complete environment configuration file rather than accidentally splitting the allowlist into separate variables. Reload a browser that opened before the allowlist became active. Continue with acceptance checks after the configuration revision is ready.

## Configuration and secrets

### Container/runtime contract

| Setting | Backend | Frontend |
| --- | --- | --- |
| Build context | `Backend/` | `Frontend/` |
| Entrypoint | `python -m app.serve` | `node server.js` in standalone output |
| Listen address / port | `0.0.0.0`, injected `PORT` | `HOSTNAME=0.0.0.0`, injected `PORT` |
| CPU / memory | 1 CPU / 2 GiB | Cloud Run default CPU / 512 MiB |
| Concurrency | 8 | 40 |
| Minimum / maximum instances | 0 / 2 per revision | 0 / 2 per revision |
| Request timeout | 3600 seconds | Cloud Run default |
| CPU outside requests | Allocated (`--no-cpu-throttling`) | Default request-based behavior |

Keep Next.js `output: "standalone"` and the runtime image's standalone/static/public copies aligned. Keep the backend's single-worker entrypoint and injected port support. Backend CPU allocation permits background analysis to continue if an HTTP stream disconnects; durable leases still handle worker loss. The application separately limits analysis to 180 seconds and voice sessions to 180 seconds. WebSockets remain subject to Cloud Run request timeouts and need reconnect/resumption handling. See the [container contract](https://docs.cloud.google.com/run/docs/container-contract) and [WebSocket guidance](https://docs.cloud.google.com/run/docs/triggering/websockets).

### Backend configuration

| Variable | Current production value/source |
| --- | --- |
| `ENVIRONMENT` | `production` |
| `DATA_PROFILE` | Original demo by default; `--data-profile timeseries` selects the additional sources |
| `SOURCE_ROW_LIMIT` | 10,000 for legacy; helper explicitly sets 30,000 for the time-series customer dimension |
| `RETAIL_BUNDLE_PATH` | Local Parquet previews only; unused for cloud source access |
| `STORAGE_BACKEND`, `DATA_BACKEND`, `AI_BACKEND` | `firestore`, `cloud`, `gemini` |
| `GOOGLE_CLOUD_PROJECT`, `FIRESTORE_DATABASE` | Selected project / `agentic-bi-demo` |
| `BIGQUERY_DATASET`, `BIGQUERY_LOCATION` | `agentic_bi_demo` / `asia-southeast1` |
| `CLOUD_SQL_INSTANCE` | `PROJECT_ID:asia-southeast1:agentic-bi-demo-pg` |
| `POSTGRES_DATABASE`, `POSTGRES_USER` | `agentic_bi`, `bi_reader` (settings defaults) |
| `POSTGRES_PASSWORD` | Secret `agentic-bi-postgres-reader:latest` |
| `GUEST_SIGNING_KEY` | Secret `agentic-bi-guest-signing:latest` |
| `ALLOWED_ORIGINS` | Exact permitted frontend origin(s); comma-separated in application settings |
| `TEXT_MODEL`, `TEXT_MODEL_LOCATION` | `gemini-3.8-flash`, `global` |
| `EMBEDDING_MODEL`, `EMBEDDING_LOCATION`, `EMBEDDING_DIMENSIONS` | `gemini-embedding-001`, `us-central1`, `768` (settings defaults) |
| `LIVE_MODEL`, `LIVE_MODEL_LOCATION` | `gemini-live-2.5-flash-native-audio`, `us-central1` |

Model locations are independent of the Cloud Run/data region. Validate access when changing accounts, models, or regions. Do not silently substitute another model after a failed compatibility check. Limits and fallback behavior are defined in `Backend/app/config.py`; treat changes as deployment configuration changes and keep the helper aligned.

### Frontend configuration

`BACKEND_URL` is a server-side runtime environment variable. `/api/config` exposes only its public URL to the browser. `/api/health` checks backend reachability. Do not bake environment-specific API URLs into the frontend image or place secret values in `NEXT_PUBLIC_*` variables.

### Secret updates

Use a trusted administrator/Secret Manager workflow that does not echo secret material. The helper currently references `latest`; new instances can resolve a newer version at startup. For reproducible rollback, record and pin approved numeric secret versions in the deployment configuration and keep the helper synchronized. Google recommends [secret configuration and version selection](https://docs.cloud.google.com/run/docs/configuring/services/secrets) appropriate to the deployment.

PostgreSQL rotation must coordinate the database role password and Secret Manager value, followed by a backend rollout and connection check. Changing the secret alone is insufficient. Do not use the destructive seed command just to rotate a password. Plan the transition so old/new instances and existing pools are accounted for. Signing-key rotation invalidates existing guest tokens; visitors will need fresh sessions.

Do not disable/delete the previous secret version while a serving revision still depends on it. Never include secret contents in deployment records or evaluation reports.

## Acceptance checks

### Basic health and service readiness

```bash
curl --fail --silent --show-error "$BI_BACKEND_URL/health/live"
curl --fail --silent --show-error "$BI_BACKEND_URL/health/ready"
curl --fail --silent --show-error "$BI_FRONTEND_URL/api/health"
curl --fail --silent --show-error "$BI_FRONTEND_URL/api/config"
```

Expected: backend live `ok`; ready `ready` with Firestore; frontend health reports backend HTTP 200; configuration points to the intended backend. `/health/ready` checks storage and both source connections, not full Gemini/live/vector functionality. A failed readiness request normally returns HTTP 503.

### Identity, persistence, and hosted application checks

```bash
python3 infra/verify_runtime.py

cd Backend
uv run python -m scripts.smoke_deployed \
  --backend "$BI_BACKEND_URL" --frontend "$BI_FRONTEND_URL" --voice
uv run python -m scripts.evaluate_deployed --backend "$BI_BACKEND_URL"
cd ..
```

The runtime verifier creates `agentic-bi-demo-check`, a temporary private Cloud Run job using the current backend image and existing backend identity. It copies only non-secret environment values, mounts the reader secret, checks permissions/real Firestore transactions, and removes its job and temporary config in cleanup. It requires no new token-creator/impersonation role. Inspect cleanup after an interrupted operator process; never delete unrelated jobs.

The smoke test covers CORS, runtime URLs, hosted numerical answers, source query evidence, follow-ups, forks, idempotency, rejected voice origins/tokens, and real Gemini Live tool/audio/transcript output. The numerical evaluation checks 31 questions against independently calculated seed references. These commands make billed model/query calls, create visible public conversations, and consume configured quotas. They write reports under `docs/evaluation/`; preserve earlier reports when comparing a regression.

In a browser, confirm both sources connect, ask a cross-source question, inspect SQL/assumptions/cardinality, switch chart/table, follow up, fork, and reconnect. Manually test microphone permission, actual spoken input/output, mute, interruption, and resumption over HTTPS. The automated voice test injects text into the live transport and does not certify microphone hardware.

For a frontend-only [browser settings](settings.md) release, rerun the frontend checks and basic health checks, confirm the backend revision/configuration is unchanged, and verify the deployed settings controls, reload persistence, theme switching, and an existing public result. Check the settings page on desktop and mobile and confirm returning to the workspace retains the chosen appearance. These checks need no new model calls or public conversations. Rerun the broader hosted analysis/voice and private runtime checks when backend, connector, model, persistence, IAM, or protocol changes affect those paths. Preserve their existing reports when those components have not changed.

Do not reset quotas to conceal a usage-limit failure. Record actual results and distinguish automated checks from remaining manual checks.

## Rollback

Before a release, record the prior known-good revision names. List revisions and traffic if needed:

```bash
gcloud run revisions list --service agentic-bi-backend \
  --project "$BI_PROJECT_ID" --region "$BI_REGION"

gcloud run services describe agentic-bi-backend \
  --project "$BI_PROJECT_ID" --region "$BI_REGION" --format='yaml(status.traffic)'
```

Replace the placeholder below with the revision verified for the affected service:

```bash
export BI_ROLLBACK_REVISION='REPLACE_WITH_KNOWN_GOOD_BACKEND_REVISION'
gcloud run services update-traffic agentic-bi-backend \
  --project "$BI_PROJECT_ID" --region "$BI_REGION" \
  --to-revisions "$BI_ROLLBACK_REVISION=100"
```

For a frontend rollback, use `agentic-bi-frontend` and its own known-good revision. Recheck health and the relevant user flow. Record the rollback and remaining incident in the deployment/validation notes. Google documents [revision traffic and rollbacks](https://docs.cloud.google.com/run/docs/rollouts-rollbacks-traffic-migration).

A traffic rollback does not undo schema/data changes, IAM, seeding, or secret rotation. Check API/schema/secret compatibility first. Existing WebSockets/in-flight requests can remain on their original revision; let bounded work finish or handle reconnection. The deploy helper does not explicitly reset traffic assignments after a rollback: inspect traffic after the next successful release and intentionally route to the verified candidate revision if necessary.

## Maintenance and data operations

For an authorized shared-history reset only:

```bash
cd Backend
uv run python -m app.admin reset-history --confirm-demo-reset
cd ..
```

This deletes demo conversations, results, runs, ADK sessions, resumptions, and usage counters while preserving source tables and embeddings. There is no public reset endpoint. Coordinate with active users and retain any required evidence first. The separate `seed` command resets source tables.

Reindex only after relevant schema/model/dimension changes; changing dimensions requires matching embeddings, index, configuration, and tests. Preserve source-side read permissions, SQL AST validation, BigQuery dry-run/max-billed-byte controls, PostgreSQL read-only transactions/timeouts, and fusion limits.

Cloud SQL, storage, model calls, query scans, and Cloud Run allocation remain billable. Minimum instances zero does not stop the SQL instance or erase storage charges. Current instance/query/usage limits reduce exposure but are not a monetary spending cap. Configure billing alert thresholds/recipients with the billing administrator. Review backups and recovery before any destructive resource deletion; this guide intentionally supplies no bulk project teardown command.

Private on-premises databases require VPC egress plus routing, DNS, firewall/TLS, and VPN/Interconnect or another approved private path. A database connector alone does not establish that connectivity.

## Troubleshooting

Read targeted service logs and build status:

```bash
gcloud logging read \
  'resource.type="cloud_run_revision" AND resource.labels.service_name="agentic-bi-backend"' \
  --project "$BI_PROJECT_ID" --freshness 1h --limit 50 --format json

gcloud builds list --project "$BI_PROJECT_ID" --region "$BI_REGION" --limit 5

gcloud storage buckets get-iam-policy \
  "gs://$BI_PROJECT_ID-agentic-bi-build" --project "$BI_PROJECT_ID"
```

Use `agentic-bi-frontend` in the log filter for frontend failures. Follow the build log location printed by the helper; this project uses GCS build logs. Read logs locally and redact sensitive material before sharing them.

| Symptom | Checks and recovery |
| --- | --- |
| Build says staging bucket is inaccessible | Verify the builder identity, bucket-scoped object role, metadata-read role, and IAM propagation. Do not grant project-wide Storage Admin as a shortcut. |
| Build/push/deploy permission denied | Distinguish the operator, build account, runtime account, and Google-managed service agents. Check the permission/resource in the error; preserve the scoped design. |
| Container fails to start | Inspect the startup traceback, injected port/address, Linux dependencies, entrypoint, and production settings. A successful image build does not prove startup. |
| Ready returns 503 | Inspect Firestore database identity, reader secret reference, SQL connection name/instance state, connector IAM, reader privileges, and demo dataset access. The public response intentionally hides detailed credentials/configuration. |
| Browser reports `Failed to fetch`, but server health works | Check `BACKEND_URL`, exact browser origin, backend CORS allowlist, HTTPS, and the configuration revision. Reload after fixing the origin. WebSocket origin checks are separate from HTTP CORS. |
| Voice connects but fails to analyze | Check live model/location access, text-model access for tools, source readiness, guest/workspace quotas, and the socket's first-frame authentication. Test real hardware separately. |
| Answer works but retrieval reports fallback | Inspect embedding model/dimensions, the named database's vector index readiness, and SDK call compatibility. A passing numeric answer may have used the recorded fallback. |
| Raw Firestore transaction abort | Preserve the bounded fresh-transaction retries in `FirestoreStore.atomic`. The pinned SDK retries aborted commits but can expose aborts during callback reads. Exhausted contention returns `409 transaction_busy`; do not grant additional IAM or retry model/SQL work. |
| Stream closes before its final event | Replay from the last event ID without starting another turn. Keep the terminal sequence-drain check: completion can commit between polling events and reading run status. |
| `conversation_busy` or interrupted analysis | Wait, fork, or start a new explicit turn after worker loss. Reconnect replays persisted events; it must not rerun SQL. Keep per-object ADK revisions and atomic run/lease status reads intact. |
| SQL seed fails while altering a reader role | Use the implemented Cloud SQL-compatible role setup; the managed administrator cannot change superuser-only attributes. Do not elevate the reader. |
| Model unavailable or access denied | Recheck the configured identifier, location, API enablement, and prediction permission. Record the failure; do not silently switch models. |
| Usage limit reached | Respect the shared limit, wait for the relevant window, or make an authorized explicit configuration change. Billing alerts do not control this limit. |

## Another environment or project

Use this runbook's ordering and checks as the template, but adapt the implementation before executing commands against another target. The current scripts are application-specific, not a generic environment manager.

Review at least:

- `infra/provision.py`: project/region constants, account/resource names, conditional resource identifiers, and custom role.
- `infra/deploy.py` and `infra/cloudbuild.yaml`: image repository, bucket, service identities, environment values, secret references, capacity, and URLs.
- `Backend/app/admin.py`, `Backend/app/config.py`, and environment examples: project, SQL instance/database, dataset, models, and named Firestore database.
- `infra/runtime_check.py` and `infra/verify_runtime.py`: expected allowed/denied resources, secret/job names, and reader schema. Negative checks must target real existing resources; a 404 is not proof of a permission boundary.
- The independent seed/evaluation assumptions, documentation URLs, and release record.

Preserve environment isolation. Verify region/model availability and the target account before creating resources. A location change can require new data resources and an explicit migration rather than an in-place setting edit. For another application, replace the retail schemas, SQL allowlists, fixtures, and product-specific acceptance checks as well.

## Release handoff

A useful release record includes project/region, source revision or change identifier, build/image references, serving revisions and traffic, runtime identities, non-secret configuration/secret version references, verification results, and a known-good rollback target. Update [deployment.json](deployment.json), [validation.md](validation.md), and applicable reports after actual authorized deployments. Historical reports are evidence for their recorded release, not a substitute for verifying a later one.

Use [setup.md](setup.md) for local development, [architecture.md](architecture.md) for system boundaries, and [demo.md](demo.md) for the competition walkthrough.
