# Fresh forecast and scenario acceptance — 18 October 2026

**Outcome: passed, 31/31 hosted checks.** One fresh invocation completed both new analytical reports through Cloud Tasks and the private report worker after the normal UTC quota reset. The conditional scenario was actually published; this is not a saved-report replay or provider-only compatibility probe. No fresh analytical report was retried to obtain a passing result.

This closes the original fresh-generation gap in [the earlier final assessment](final-e2e-20261018.md). Its 119 successful checks, quota-denied attempt, recovered health 503 and manual verification limits remain historical evidence. The two dated suite totals now contain **150 passing checks**; they are not one simultaneous test of every subsequently added feature.

## New public evidence

| Output | Link and outcome |
| --- | --- |
| Monthly forecast | [Technical version 1](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/reports/9ef66a621f51ebe08d597f8380fecb18?version=1): complete 45-month history, three-month horizon, cutoff 2026-09-30, TimesFM selected by measured comparison |
| Conditional scenario | [Technical version 1](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/reports/e4112a63cba9d6886594cb89988ac4c5?version=1): complete 1,369-day history, fourteen-day horizon, explicit all-zero baseline/all-one alternative promotion paths, separate same-method scenario artifact |
| Presentation revision | [Business version 2](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/reports/9ef66a621f51ebe08d597f8380fecb18?version=2): reused every saved prediction/artifact; no new BigQuery job |
| Dashboard | [Saved prediction dashboard](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/dashboards/9b38ec4cc6a94fafa5db61de80549631): one immutable version-1 prediction pin, saved view, source link and PNG export |

TimesFM's monthly backtest MAE/RMSE were **251,955.17 / 307,092.06 USD**, versus seasonal-naive MAE **790,444.82 USD**. The daily conditional comparison recorded MAE/RMSE **19,946.65 / 23,659.32 USD**. The suite independently recalculated the saved remote scores; candidate selection remained numerical rather than forcing a preferred model. Monthly source revenue reconciled to **USD 354,425,112.20**.

The scenario asked for clarification twice and accepted the already authorized explicit promotion paths. It reached evidence gathering, comparison, writing and downloads. These paths are hypothetical assumptions; conditional accuracy assumes driver paths are known and does not establish promotion causality or guaranteed lift.

Both reports explicitly withhold unsupported prediction intervals. Predictions start after **30 September 2026**, not the request date: the monthly prediction covers October–December and the daily scenario covers the first fourteen days after the saved cutoff. No post-cutoff actuals are implied. Synthetic data validates implementation, not real-world predictive reliability.

## End-to-end and browser checks

- Idempotent admission returned the same run; both analytical reports and the presentation revision completed.
- PDF, Word and data ZIP downloads matched their immutable manifest checksums and file signatures; data manifests retained the same prediction metadata.
- Event replay includes real comparison progress and completion. Presentation reuse and dashboard reads do not rerun inference.
- Four managed BigQuery jobs completed under `agentic-bi-report-worker@project-e8b1593d-009a-4822-abf.iam.gserviceaccount.com`. Durable run/checkpoint evidence and successful Google-Cloud-Tasks worker requests were inspected.
- Fresh readers show cutoff, TimesFM Preview/method comparison, unavailable intervals, conditional labels and same-method/causal caveats. Keyboard activation opens forecast-validation details and the dashboard download dialog; Escape dismisses it.
- At the tested desktop and 390px mobile sizes, loaded readers/dashboard have no horizontal page overflow or uncaught browser errors. The saved dashboard PNG returned HTTP 200 and displayed **Dashboard download ready**.
- Scoped axe scans found zero violations and one incomplete contrast rule in each settled reader/dashboard. Manual contrast review, full screen-reader, Safari/Firefox, physical microphone/speaker, interruption fidelity and outage/crash testing were not repeated.

## Preservation

The preflight at 00:06 UTC confirmed the normal reset had passed and no daily quota document existed, equivalent to **0/12**. After the two reports and presentation revision, usage was **3/12**. No quota was manually reset, raised or bypassed.

All five BigQuery tables retain identical before/after full-row JSON content fingerprints and counts: **573,348 orders**, **1,317,941 line items**, **97,122 returns**, **200 products** and **1,369 calendar days**. These new paired fingerprints hash `TO_JSON_STRING(row)`; the original final suite hashed `record_hash`, so the hash integers across those different algorithms are not directly comparable. Counts agree with the original suite. Its independent 25,000-profile PostgreSQL verification remains dated evidence and was not redundantly rerun.

Live frontend/API/worker revisions were **00018-kd4 / 00024-rnd / 00013-sm4**, newer than the original final assessment. Every service spec, revision and traffic allocation matched the new before/after snapshots. API and worker preserve `DATA_PROFILE=timeseries`, `SOURCE_ROW_LIMIT=30000`, `REPORT_TIMESFM_ENABLED=true` and `REPORT_TIMESFM_VERIFIED=true`. All final health/readiness requests returned HTTP 200.

This follow-up performs no deployment, IAM/secret/settings change, analytical upload/seed, shared-history reset or Graphify regeneration. Labeled public test conversations/reports and the dashboard remain as evidence. No guest token, credential or raw audio is committed. New AI-dashboard generation and 237-node Forecast Plans execution remain separate acceptance gates from the original forecast/scenario scope.

## Machine-readable records

- [31 hosted checks, reports, predictions and assumptions](final-e2e-20261018-fresh-timesfm.json)
- [Source/quota before](final-e2e-20261018-fresh-sources-before.json), [source/quota after](final-e2e-20261018-fresh-sources-after.json)
- [Service configuration preservation](final-e2e-20261018-fresh-configuration.json)
- [Managed job identity/checkpoint audit](final-e2e-20261018-fresh-job-audit.json), [private dispatch requests](final-e2e-20261018-fresh-worker-dispatch.json)
- [Final HTTP health](final-e2e-20261018-fresh-http.json), [browser/accessibility checks](final-e2e-20261018-fresh-browser.json)
