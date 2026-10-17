# Analytics and voice fixes: deployed acceptance — 2026-10-17

**The four findings from the [original assessment](e2e-deployed-20261017.md) are fixed and their hosted rechecks pass.** The original failed artifacts and assessment remain unchanged as historical evidence.

## Released changes

- Source SQL now rejects Cartesian/implicit joins, constant predicates, self-only conditions and OR branches that do not connect the new relation to an existing one through explicit equality keys. Nested CTEs/subqueries are inspected. Approved keyed joins and the bounded two-attempt SQL repair path remain available. This is a conservative supported-join contract, not a proof of every metric's business grain.
- Every text/voice analytical invocation namespaces query records and BigQuery job legs by its own captured analysis ID. Several tools in one voice run retain distinct evidence/jobs; deterministic repair identities, parent-run cancellation and different-SQL recovery checks remain intact.
- ADK partial transcripts accumulate; final full text replaces that buffer. Already-flushed user text is not saved again if the same final arrives during the turn. The browser honors replacement and role/turn boundaries. Deliberate repeated questions in separate turns remain valid.
- Report result tables expose title-specific, keyboard-scrollable named regions. Redundant outer regions and generic unnamed table landmarks were removed; native captions and column semantics remain.

## Serving release

| Service | Serving revision | Traffic |
| --- | --- | --- |
| Public backend | `agentic-bi-backend-00018-ctv` | 100% |
| Private report worker | `agentic-bi-report-worker-00007-pfq` | 100% |
| Frontend | `agentic-bi-frontend-00013-hrz` | 100% |

Both Cloud Build images succeeded and revision image digests were checked before explicit promotion. The API and worker share backend digest `sha256:f8379a30ad7622e8487121d6905d61a16eefdc36aef25bd73e53a41576ac9ca7`. See [deployment.json](../deployment.json), [configuration](e2e-fixes-configuration.json), [pre-release snapshot](deployment-before-e2e-fixes.json), and [application source hashes](e2e-fixes-release-source.json). The images were built from the pre-publication working tree; the source manifest identifies the deployed files. Publishing this source does not change the serving revisions.

The existing identities, environment and secret references, resources, concurrency and timeouts were preserved. Worker anonymous invocation still returns **403**. No analytical upload/seed, IAM change, history/usage reset or temporary diagnostic Cloud Run job was performed.

## Verification

| Check | Result | Record |
| --- | --- | --- |
| Backend suite | **317 passed, 1 existing skip** | [Local checks](e2e-fixes-local.json) |
| Targeted SQL/voice regressions | Reproduced the old failures, then **93 passed**; transcript test also rerun after the final audio-config adjustment | [Local checks](e2e-fixes-local.json) |
| Frontend | **35 tests**, lint, TypeScript and production build passed | [Local checks](e2e-fixes-local.json) |
| Hosted time-series analytics | **40/40 passed** | [Analytics](e2e-fixes-timeseries.json) |
| Repeated Live analysis in one connection | **4/4 passed** | [Live protocol](e2e-fixes-voice-turns.json) |
| Browser synthetic spoken input and persistence | **9/9 passed** | [Spoken browser test](e2e-fixes-browser-speech.json) |
| Durable report workflow | **26/26 passed** | [Reports](e2e-fixes-reports.json) |
| Dashboard lifecycle | **10/10 passed** | [Dashboards](e2e-fixes-dashboards.json) |
| Saved forecast/export reconciliation | **19/19 passed** | [Saved evidence](e2e-fixes-saved-evidence.json) |
| PDF/Word content and hashes | **12/12 passed** | [Documents](e2e-fixes-document-content.json) |
| Browser navigation/downloads and four axe scans | All recorded checks passed; **zero axe violations** | [Browser](e2e-fixes-browser.json) |

The skipped backend case is the existing memory-store independent-client durability variant; a new emulator-backed run was not performed. Ruff passes when run from `Backend/` as required by the runbook. Running Ruff from the repository root changes first-party import classification and is not the configured release command. One pre-existing social-image-generator lambda lint issue was corrected without regenerating the image. The existing Starlette/httpx deprecation warning remains; deprecated `save_live_audio` usage in the analyst was replaced by `save_live_blob=False`.

### Numerical and voice regression results

The fresh daily Flash-Lite result contains **1,369 dates**, including zero sales on **2024-02-29**, and reconciles to **USD 354,425,112.20**. It uses only the calendar and completed orders with an equality date join; the 200-row products fan-out is absent. All 45 monthly amounts, the 2024 follow-up and cross-source segment totals reconcile independently too.

Two synthetic spoken questions ran through the browser capture AudioWorklet, hosted WebSocket/ADK/Gemini, actual source queries, saved artifacts and returned audio in **one connection**. They returned **573,348** all-history orders and **152,694** orders for 2024. Both query records remain in Firestore with different analysis IDs and BigQuery job IDs under the same parent run. Each finalized question and spoken answer appears exactly once in shared messages. Mute/unmute disabled/enabled the simulated audio track; graceful stop/reconnect produced another ready event without error.

The additional text-over-Live harness also returned two spoken analytical answers in one connection with distinct jobs. Its first run mistakenly expected preview rows in metadata-only Live notifications; that harness error is retained in [the initial record](e2e-fixes-voice-harness-initial.json). The corrected harness reads the immutable artifact endpoint. This was not a deployed API error or a model retry hidden from the results.

### Reports, predictions and dashboards

A fresh Business report completed through the private worker with a **reviewed narrative**, complete source evidence and an ETS prediction. Independent checks reconcile all 45 training months, recompute the three seasonal-naive backtest folds, and verify candidate promotion, cutoff and explicit omission of unsupported intervals. A Technical presentation revision reused immutable evidence. PDF, editable Word and data ZIP matched their saved checksums, claims and full-row manifests. The browser-downloaded PDF matched that exact version. The report describes monthly order-count ranges; tests verify its stated figures rather than requiring it to claim an overall order total.

Normal chat remained available during reporting. Idempotent admission/replay, metadata conflicts, version immutability, deletion/restoration and owner-only cancellation passed. Three worker error-level SDK log entries at **07:10:59 UTC** were the intentionally requested cancellation; all terminated with `Report cancellation requested`. No new query-identity conflict or unrelated error appeared in the inspected new-revision entries.

The new forecast was pinned through the report reader. Dashboard View/Edit, public sharing, real PNG download, lifecycle/recovery and all five server export formats passed. CSV ZIP rows/checksums reconcile independently; exports execute no source queries or models. The previously failing report and a new report containing multiple tables both have **zero axe violations**. Landing previews, mobile application entry, legacy links, New exploration, version switching and 390px report layout passed. No uncaught browser JavaScript errors were recorded.

## Larger dataset preserved

[Source metadata before/after](e2e-fixes-source-preservation.json) is identical: **573,348 orders**, **1,317,941 line items**, **1,369 calendar days**, unchanged modification timestamps. Both runtimes retain **`DATA_PROFILE=timeseries`** and **`SOURCE_ROW_LIMIT=30000`**. The period remains January 2023–September 2026; hosted numerical checks, not just metadata labels, confirm this profile.

## Inspectable output and boundaries

- [New Business report](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/reports/8a9a241d23d4c83384af22896ace71fd?version=1)
- [Technical revision](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/reports/8a9a241d23d4c83384af22896ace71fd?version=2)
- [New dashboard and forecast](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/dashboards/f068828374df446fb968264e9c4288d8)
- [Correct daily analysis](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/app?chat=3cec5989c73d4cbab583d52d09e7e452)
- [Two-question spoken conversation](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/app?chat=28662d1ef3f5459d98e6f663a32db587)

Physical microphone/speaker quality, native OS sharing, full screen-reader use, real touch hardware, Safari/Firefox and PDF/UA certification remain untested. Browser speech used local synthetic audio, with no raw recording retained. Clipboard output used an intercepted writer. SVG contrast and other automated manual-review items remain documented in the browser record. Representative PDF pages were visually reviewed. Conditional driver scenarios, disabled Search and production worker crash injection were not added to this fix verification. Historical failed artifacts remain immutable; the new daily result is the corrected comparison.
