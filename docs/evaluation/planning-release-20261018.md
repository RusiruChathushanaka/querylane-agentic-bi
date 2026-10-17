# Metrics and planning release — 18 October 2026

**Deployed; partial end-to-end acceptance.** The Metrics Catalog, reviewed AI Dashboard Builder and hierarchical Forecast Plans are available on [Querylane](https://agentic-bi-frontend-wekihucn7q-as.a.run.app). The core hosted suites passed **121 checks**, and final metric-guided text/Live retests passed **eight more**. Fresh dashboard-builder and forecast-plan computation was correctly refused at the pre-existing **12/12 workspace daily allowance**; those private-worker workflows remain unverified on this release. No limit was reset, raised or bypassed.

[Machine-readable assessment](planning-release-20261018.json) records the boundaries. Earlier [local implementation evidence](planning-local-20261018.md) independently covers the complete 237-node plan, exact-cent reconciliation, adjustments, reviewed publication and matching plan exports; it does not replace hosted execution.

## Release and preservation

| Service | Serving revision | Previous revision for rollback |
| --- | --- | --- |
| Private report/planning worker | `agentic-bi-report-worker-00013-sm4` | `agentic-bi-report-worker-00010-wnw` |
| API | `agentic-bi-backend-00024-rnd` | `agentic-bi-backend-00021-6rd` |
| Frontend | `agentic-bi-frontend-00017-dxz` | `agentic-bi-frontend-00016-tw2` |

Both Cloud Builds succeeded. The worker and API share backend digest `73e239ec3a76e390f271d71fbdad9d0c3e6fa167331990786871e9eae9dd9d94`; frontend digest is `0d545a6b9a04758b481bf0d87041658982e40e61a6c60edf05b8a57bc3603f46`. Candidates were deployed without traffic, checked through temporary tagged URLs, then promoted explicitly in worker → API → frontend order. The private worker's candidate health request was authenticated. Temporary tags were removed.

[deployment.json](../deployment.json) contains build references, serving traffic, runtime settings and rollback targets. The [source manifest](planning-release-20261018-source.json) captures 187 runtime-file hashes over base commit `e4af083a`; images were built from that working tree, before the documentation/publication commit.

Runtime identity, secret references, source limits, capacity and dispatch were preserved. The only runtime-setting addition was `PLANNING_ENABLED=true` on API and worker. Both retain `DATA_PROFILE=timeseries`, `SOURCE_ROW_LIMIT=30000`, `REPORT_TIMESFM_ENABLED=true` and `REPORT_TIMESFM_VERIFIED=true`. Private-worker IAM is unchanged; anonymous health requests receive 403. No IAM grant, analytical migration/upload/seed, packaged-metric seeding, history reset or quota change was performed.

[Before](planning-release-20261018-sources-before.json) and [after](planning-release-20261018-sources-after.json) read-only fingerprints match for every row of all five BigQuery tables: **573,348 orders**, **1,317,941 items**, **97,122 returns**, **200 products** and **1,369 calendar days**. Fingerprints use the same `BIT_XOR(FARM_FINGERPRINT(TO_JSON_STRING(row)))` calculation in both snapshots; differently calculated historical fingerprints are not compared. PostgreSQL retains **25,000 profiles**. Revenue reconciles to **USD 354,425,112.20** across **45 months**.

## Verification

| Suite | Result |
| --- | --- |
| Local regression | **442 backend tests passed**, one existing opt-in emulator skip; Ruff passed. **53 frontend tests**, ESLint, TypeScript and an isolated production build passed. The first sandboxed local build stalled; the isolated build and both Cloud Builds succeeded. |
| [Actual runtime identity](planning-release-20261018-runtime.json) | **21 checks**: allowed/denied resource access, restricted PostgreSQL, larger-source coverage, Gemini Flash/Flash-Lite, embeddings, named Firestore persistence, transactional single-winner chat admission and ADK event fencing. The temporary job was deleted. |
| [Fresh analytics](planning-release-20261018-analytics.json) | **39 checks**: real Flash/Flash-Lite, complete monthly/daily results, zero-sales date, charts/CSV, follow-ups, forks, idempotency, replay, cross-source segment totals and voice origin/token rejection. |
| [Live assistant](planning-release-20261018-voice.json) | **4 checks**: two analyses in one real Live connection, separate query jobs, correct 573,348 / 152,694 order counts, transcripts and generated audio. Input was text through Live transport; physical microphone/speaker hardware was not tested. |
| [Metrics and saved evidence](planning-release-20261018-api.json) | **45 checks**: create/replay, validate/publish, immutable revision, stale edit 409, unsafe measure rejection, full 45-month numerical preview and replay, archive/restore; fresh expensive-job quota rejection; saved TimesFM forecast/scenario PDF/Word/data downloads; all five dashboard formats; libraries, health, legacy redirect and private-worker denial. |
| [Browser](planning-release-20261018-browser.json) | **12 checks**: landing makes no backend requests before entry; four application CTAs and keyboard preview switching; desktop/320px reflow on six application pages; immutable metric reader; builder quota error preserves its objective and leaves submission usable. Seven tested page states reported zero axe violations. One workspace SVG contrast rule remains incomplete for manual review. No uncaught browser errors were recorded. |

The metrics test retained one clearly labeled [published revenue definition](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/metrics/1a533e8152c847688126f80587fc66a5/revisions/1) for the next planning acceptance run. It has no aliases and does not claim organizational certification. Its saved version remains unchanged after draft edits and archival/restoration.

An initial operator dashboard-download request omitted the required `expected_revision` and correctly received 422. Corrected requests passed for PDF, CSV ZIP, PNG, JPEG and JSON. This was a test-harness correction, not an application failure. The initial core-suite window contained no unexpected application ERROR entries. Subsequent reproduced schema errors and their correction are documented below; final serving revisions are checked separately.

## Remaining acceptance after the normal quota reset

The allowance resets at **00:00 UTC / 05:30 Sri Lanka time on 18 October 2026**. Respect the existing combined report/builder/plan allowance and two-job concurrency ceiling.

1. Use **Dashboards → Build with AI** to request a new dashboard, inspect reused/new evidence, review and publish it. Exercise an existing-board improvement and a concurrent-edit conflict without repeating source work.
2. Use **Forecast Plans** with the published test revenue version and the full January 2023–September 2026 history. Complete a three-month plan through Cloud Tasks and the private worker. Inspect actual TimesFM outcomes, common company totals, all 237 nodes, allocated labels and backtests.
3. Save a separate adjustment, verify parent/view totals to the cent, compare unchanged statistical predictions, download PDF/data ZIP/JSON, and pin the exact version to a dashboard. Confirm reopening/exporting performs no inference.
4. Record new dated evidence. Saved TimesFM reports and earlier provider-identity checks do not certify a fresh hierarchical run. Keep the same dataset, TimesFM gates and original quotas.

Full screen-reader use, Safari/Firefox, physical audio quality and production crash/outage injection were outside this release check. Deployment is complete; fresh expensive-job acceptance remains explicitly partial.

## Additional metric-intent correction

A fresh question requesting the published metric and saying “not an ad hoc calculation” exposed an intent-routing defect after the first rollout. [The initial failed check](planning-release-20261018-catalog-agent-initial.json) is retained. The correction distinguishes negated mentions from affirmative opt-outs; seven integration cases and the full 440-test backend suite passed at that stage. The corrected shared backend image was released worker-first; the frontend image did not change. Core runtime/analytics/CRUD suites above ran on the initial rollout; final live metric-guided checks are recorded separately below.

The first intent correction exposed an independent ADK/GenAI dictionary-schema incompatibility in `MetricScope.filters`. [The diagnosis](planning-release-20261018-metric-scope-initial.json) and [failed Live probe](planning-release-20261018-voice-catalog-initial.json) are retained. Metric scope now uses JSON output with strict local validation. Two additional SDK-seam tests and the full **442-test** suite passed. A [real Gemini compatibility call](planning-release-20261018-metric-scope-compat.json) passed before rebuilding; it used operator credentials, not the worker identity.

Final serving API `00024-rnd` passed [three real metric-guided text checks](planning-release-20261018-catalog-agent.json): the exact previously failing question now captures published version 1, returns all 45 complete monthly observations and reconciles to **USD 354,425,112.20**. [Five final Live checks](planning-release-20261018-voice-catalog.json) verify the same immutable version for two separate spoken analyses, distinct query jobs, full-history revenue and independently calculated **USD 93,401,855.62** for 2024. Input was text over Live; generated speech/transcripts were received. The final chart's browser reader displays the exact saved metric-version link.

This brings the hosted suite count to **129 passing checks**, with **442 backend tests** and **53 frontend tests** locally. Final API/worker/frontend revision logs contained no ERROR entries from 21:45:40 UTC through inspection. Earlier reproduced failures are retained above. All five source fingerprints and private-worker IAM still match the pre-release snapshots. Fresh builder/plan worker execution remains unverified at the normal daily quota; successful text/voice tests do not substitute for it.

Rollback must use a compatible service set after checking active jobs. The table retains the pre-feature worker/API/frontend rollback targets; intermediate revisions `00011/00022` and `00012/00023` were superseded during acceptance and are not the final sign-off. No source data should be reset during rollback.
