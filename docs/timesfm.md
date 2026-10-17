# TimesFM comparison in Advanced Analysis

The hosted feature is **enabled following the 17 October 2026 worker-identity compatibility check and release**. Local configuration still defaults both gates to false. [deployment.json](deployment.json) records the serving revisions; [the deployed assessment](evaluation/timesfm-deployed.md) records actual forecasts, scenarios and data-preservation checks. Historical local/operator failures remain dated evidence, not the current worker-access status.

## Behavior

Gemini/ADK proposes relevant forecasts, their priority and a bounded candidate policy. Numerical backtests select the published method. TimesFM is the managed **TimesFM 3.0 Preview** model invoked through BigQuery `AI.FORECAST`; no downloaded weights, GPU service or custom trained model is used. Gemini text-model settings remain separate.

A forecast compares seasonal-naive, ETS, eligible SARIMAX/driver regression and eligible TimesFM on three chronological full-horizon folds. A candidate must improve baseline MAE by at least 5%, win at least two folds, satisfy the metric domain and pass the existing excessive-error gate. Lowest passing MAE wins; exact ties favor statistics. Provider failure or a lost comparison preserves supported statistical evidence and explains the limitation.

A conditional scenario requires explicit baseline/alternative future driver paths. Historical support, variation and leakage checks remain authoritative. Forecast and scenario winners can differ: the scenario is a separate immutable artifact, with baseline and alternative from the same driver-capable method, history and configuration. Native multivariate inference supports one target and up to four future-known drivers here; joint targets and past-only covariates are deferred. Conditional backtest errors assume those historical driver paths were known; they are not unconditional forecast accuracy or causal lift.

## Saved input and context

Candidate comparison reads the complete immutable artifact pages, excludes recorded partial periods and hashes the exact validated series. It never rereads source SQL. The fixed SQL maps values into application-owned aliases and receives one bounded JSON query parameter. Ordinary generated SQL still cannot invoke `AI.FORECAST`.

Univariate history supports the current 45-month and 1,369-day series. Inputs over 2,048 observations require an explicit narrower analysis. Missing dates are not imputed; known zeros remain zero. Covariate inference requires complete context plus explicit future rows with NULL targets. Its context is the largest complete multiple of 32 supported by the earliest fold, with a minimum of 64 observations, shared across folds and final prediction. The exact context and historical prefix lengths are recorded and shown. This can use a shorter recent context than the source artifact; full saved source history remains available. A 45-month driver series is too short at its early folds and falls back to supported statistical scenarios. No artificial padding or hidden grain change is permitted.

Native model intervals remain diagnostic. Published bands use the existing earlier-fold residual calibration/later-fold coverage and domain gates. A monthly point forecast can have no validated interval despite provider interval fields. Forecasts begin after the latest complete observation, not the request date.

## Execution and limits

New runs use workflow version 2 and freeze the TimesFM policy in their brief. Version 1 runs retain the old numerical path. Presentation revisions, exports and dashboards reuse saved artifacts and invoke no inference.

| Setting | Default |
| --- | ---: |
| `REPORT_TIMESFM_ENABLED` | `false` |
| `REPORT_TIMESFM_VERIFIED` | `false` |
| `REPORT_TIMESFM_TARGETS` | 2 |
| `REPORT_TIMESFM_JOBS` | 4 |
| `REPORT_TIMESFM_JOB_SECONDS` | 45 |
| `REPORT_TIMESFM_SECONDS` | 120 |
| `REPORT_TIMESFM_INPUT_TOKENS` | 100,000 |
| `REPORT_TIMESFM_OUTPUT_TOKENS` | 10,000 |

Both enablement flags are required. `VERIFIED` is an operator attestation after the managed compatibility/runtime-identity gate; an operator-only success does not establish worker access. The capabilities endpoint `/api/v1/reports/config` exposes availability/model/Preview status only. No public inference endpoint is added.

Priority-ordered admission reserves a backtest/final job pair, conservative token estimates, maximum byte reservations and fit units in a single fenced transaction before evidence gathering. Each job shares the existing 12-job/8-GiB report ceilings and 1-GiB individual query cap. One batched job evaluates three isolated folds; a second runs only when TimesFM is needed for a selected forecast/scenario. Local candidate evaluation is checkpointed before remote work. Fit reservations remain conservative after crashes; retries cannot obtain free unlimited computation.

Stable job IDs capture input/configuration identity. Ambiguous submission reconciles the same job once. Recovery verifies SQL/parameters and reuses completed output; terminal failures are saved rather than submitted under a fresh ID. A bounded five-second read-only reconciliation window can retrieve an already-completed job after its inference deadline; it cannot restart expired inference. Per-operation and parent cancellation flags survive registry cleanup, including a delayed submission response. Fenced writes prevent stale publication. Cancellation remains a request until the job is confirmed terminal.

Job seconds are reserved before submission and settled once after successful capture. Failed/interrupted work retains conservative reservations. The ten-minute overall report limit still applies. Bytes, model input/output estimates, series counts and horizons are separately bounded; these controls are not a guaranteed monetary spending cap. Pricing assumptions were reviewed on 17 October 2026; Google documents a separate token billing transition on 1 December 2026. Recheck the [current pricing](https://docs.cloud.google.com/bigquery/docs/reference/standard-sql/bigqueryml-syntax-ai-forecast#pricing) before release.

## Compatibility probe

From `Backend/`, the default prints a local plan:

```bash
uv run python -m scripts.smoke_timesfm
# Opt-in: up to four billed inference jobs, synthetic inline parameters only.
uv run python -m scripts.smoke_timesfm --live --gcloud-credentials \
  --impersonate agentic-bi-report-worker@project-e8b1593d-009a-4822-abf.iam.gserviceaccount.com \
  --output ../docs/evaluation/TIMESFM_WORKER_RECORD.json
```

For actual workload verification without an impersonation grant, use the runbook's `infra/verify_timesfm.py --image VERIFIED_BACKEND_DIGEST --output RECORD.json --apply`. It runs the same four bounded queries in a temporary job with the existing worker identity, then removes the job. No additional IAM or model service is created.

Without `--gcloud-credentials`, the local command uses ADC. The CLI option holds a short-lived token only in memory and creates no credential file. Impersonation requires an existing grant; the command does not add one. An existing runtime can also execute the probe under its workload identity. The probe's Firestore-style state is local memory, and it changes no hosted feature flag, analytical table, IAM or infrastructure. Its monthly and daily-driver examples establish interface compatibility, not retail predictive accuracy.

Release requires successful parameterized inputs, output shapes, same-job recovery/cancellation tests, billing metadata and actual private worker access. Failure leaves both flags false; do not introduce staging tables, broaden roles or substitute another TimesFM version automatically. Follow [the deployment guide](deployment-guide.md) and preserve `DATA_PROFILE=timeseries` / `SOURCE_ROW_LIMIT=30000`.

## Implementation owners

- `Backend/app/report_statistics.py`: shared preparation, statistical candidates and legacy compatibility.
- `Backend/app/report_forecasting.py`: admission, immutable comparison checkpoints, scoring, selection and separate scenarios.
- `Backend/app/timesfm.py`: fixed managed queries, job identity, output checks and cancellation.
- Report repository/engine: fenced reservations, policy capture, recovery and immutable publication.
- `Frontend/src/components/prediction-evidence.tsx`: semantic comparison tables, native disclosure, Preview labels and diagnostic evidence.

PDF, Word and data ZIP retain the same prediction metadata, saved values and source/version references. Original skill revisions and visitor changes remain untouched; packaged example instructions describe the newly approved capabilities without seeding the public catalog.
