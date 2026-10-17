# TimesFM Cloud Run release — 17 October 2026

**Passed:** worker-identity compatibility, enabled private-worker reporting, ordinary forecasts, explicit conditional scenarios, saved downloads/dashboard reuse and larger-data preservation. [Deployment record](../deployment.json) identifies the serving revisions. Local configuration still defaults both TimesFM gates to false.

## Serving application

| Service | Revision |
| --- | --- |
| Frontend | `agentic-bi-frontend-00015-6ff` |
| API | `agentic-bi-backend-00021-6rd` |
| Private worker | `agentic-bi-report-worker-00010-wnw` |

API and worker have `REPORT_TIMESFM_ENABLED=true` and `REPORT_TIMESFM_VERIFIED=true`. The worker remains private (anonymous health request: 403), uses its original service account and shares the verified backend digest. Existing identities, secrets, resource limits, dispatch settings, source controls and unrelated resources were preserved. No IAM grant, analytical upload/seed, schema migration, skill seed or history/quota reset was performed. New records are labeled public verification chats/reports and a saved-result dashboard.

## Managed compatibility and analytical acceptance

The [worker runtime probe](timesfm-worker-runtime.json) passed four real parameterized inference jobs under the actual attached worker identity using workload ADC, without impersonation. A uniquely named temporary check job was removed afterward. Monthly/daily driver inputs were synthetic interface checks, not the retail accuracy benchmark. The earlier [impersonation failure](timesfm-worker-compatibility.json) is retained as historical operator evidence and is superseded by this actual runtime check.

[Hosted acceptance](timesfm-deployed.json) passed **31 checks** across two real Gemini-planned, Cloud-Tasks-dispatched report runs and one presentation revision. Both analytical runs used complete saved evidence from the larger retail sources, froze workflow-2 policy and captured TimesFM comparisons.

| Analysis | Baseline MAE | TimesFM MAE | Published selection |
| --- | ---: | ---: | --- |
| Three monthly revenue periods; 45-month history | 790,444.82 USD | 251,955.17 USD | TimesFM 3.0 Preview |
| Fourteen daily revenue periods with explicit promotion paths; 1,369-day history | 39,751.05 USD | 19,946.65 USD | TimesFM 3.0 Preview |

These are held-out absolute errors for the tested metric/horizon, not guaranteed future accuracy. The monthly comparison also evaluated ETS and SARIMAX; the daily comparison evaluated ETS and driver regression. The tests independently recomputed TimesFM MAE/RMSE from saved predictions and held-out observations. Baseline promotion and fold-win gates selected the winner; the test did not force TimesFM to win. Both observation cutoffs are 30 September 2026. Unsupported uncertainty bands were omitted and disclosed.

The scenario flow requested clarification. The test supplied hypothetical `promotion_day=0` baseline and `promotion_day=1` alternative paths for all fourteen future dates. The separate scenario artifact uses the same method, history and configuration for both paths; it does not claim causal promotion lift. Chronological conditional scores assume the historical driver paths were known.

Monthly saved revenue reconciled to the independent ledger: **354,425,112.20 USD**. The daily source had **1,369 complete calendar observations**, including the genuine zero-sales day. PDF/Word/data ZIP downloads matched immutable checksums; ZIP prediction metadata matched the reader's saved artifacts. The presentation revision reused identical artifact IDs. The [job audit](timesfm-job-audit.json) confirms exactly two inference jobs per analytical run under the worker identity and **zero** for the presentation run; replays, downloads and dashboard reads introduced no additional report inference jobs.

The first [acceptance attempt](timesfm-deployed-initial.json) correctly received 422 when the operator's pin payload omitted visible measures. The harness was corrected to provide observed/forecast measures and resumed the completed reports and existing dashboard. No report, model fit or inference was repeated to fix that operator payload.

## Interface and regression checks

[Browser evidence](timesfm-browser.json) verifies the landing CTA to `/app`, ordinary chat in the same conversation while a report ran (573,348 completed orders), the real TimesFM Preview label/comparison table, keyboard disclosure, a separate conditional-scenario label, and the pinned prediction in dashboard View mode. Desktop and 390px layouts had no page overflow or uncaught browser errors. The actual report was visually inspected in dark mode. Axe found **zero violations**, with one incomplete contrast rule affecting SVG chart labels; automated results do not establish full screen-reader or cross-browser conformance.

[Runtime regression](timesfm-backend-runtime.json) passed named-Firestore access/persistence, out-of-scope denials, restricted PostgreSQL reader checks, 25,000 customers, larger source counts and both Gemini text models. [Live regression](timesfm-voice-regression.json) passed two real spoken analytical responses in one connection with distinct query jobs and independently known counts. This socket test uses text turn input and real model/audio output; physical microphone capture was not retested. [Release health](timesfm-release-health.json) records final readiness, flags and private-worker access. New serving revisions produced no ERROR-level log entries during the recorded inspection window.

Local verification remains [385 backend tests, one existing skip; 47 frontend tests](timesfm-local.md), with Ruff, lint, type checks and production build passing. Additional release helpers passed Ruff/compilation; both real Cloud Builds succeeded. Production crash injection, future-accuracy guarantees and exhaustive device/accessibility coverage are not claimed.

## Data preservation and examples

[Before](timesfm-sources-before.json) and [after](timesfm-sources-after.json) read-only counts/content fingerprints match for all five demo BigQuery tables. [Preservation comparison](timesfm-data-preservation.json) records 573,348 orders, 1,317,941 items, 97,122 returns, 200 products and 1,369 calendar days. PostgreSQL reader verification retained 25,000 customers. Both API and worker retained `DATA_PROFILE=timeseries` / `SOURCE_ROW_LIMIT=30000`.

- [Monthly forecast report](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/reports/2ed05089e9a86e1ef3046fa6c6728680?version=1)
- [Conditional promotion scenario report](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/reports/f0853cca9462ee293ddaf45e6627e843?version=1)
- [Saved prediction dashboard](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/dashboards/7d213e6c777244fb99c9bc363ff42f22)

These examples are public and recoverably editable, consistent with the application's shared-demo model. Saved numerical outputs remain immutable evidence for their revisions.
