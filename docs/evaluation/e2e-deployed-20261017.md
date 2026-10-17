# Deployed end-to-end assessment — 2026-10-17

**Overall outcome: not passing.** Two functional blockers were found: an incorrect generated daily-revenue query and a BigQuery job collision during repeated voice analysis. Duplicate persisted voice transcripts and one report accessibility finding also need correction. No application fix or release was performed during this assessment.

## Environment and data

Tests ran against the public Cloud Run application on 17 October 2026, approximately 06:39–06:52 UTC. [Observed configuration](e2e-runtime-20261017.json): frontend `agentic-bi-frontend-00012-mv5`, backend `agentic-bi-backend-00017-cnf`, private worker `agentic-bi-report-worker-00006-sk6`, each serving 100% of traffic. Both analytical services retain cloud sources, named Firestore storage, `DATA_PROFILE=timeseries`, and `SOURCE_ROW_LIMIT=30000`.

Fresh hosted queries reconciled **573,348 completed orders**, **45 monthly observations**, and **USD 354,425,112.20** merchandise revenue against the independent local generated-data ledger/Parquet files. History covers January 2023–September 2026. Cross-source customer-segment totals also reconciled. The daily result had all **1,369 dates**, including the genuine zero-sales date, but its values failed reconciliation as described below.

Only labeled public verification chats, reports and dashboards were created/edited. The two API-only verification dashboards were soft-deleted by their test. The new report, its two versions, conversations, and the report-evidence dashboard remain inspectable. No analytical upload, seed, source mutation, shared-history/usage reset, IAM change, deployment or GitHub publication occurred. No new unit-suite/build result is claimed; this was a hosted acceptance run.

## Results

| Area | Result | Evidence |
| --- | --- | --- |
| Hosted analytics and Live protocol | **39/40 checks passed**; daily revenue failed | [Time-series checks](e2e-timeseries-20261017.json) |
| Durable reports | **26/26 passed** | [Report checks](e2e-reports-20261017.json) |
| Saved-result dashboard lifecycle | **10/10 passed** | [Dashboard checks](e2e-dashboards-20261017.json) |
| Independent forecast gates and five dashboard exports | **19/19 passed** | [Saved-evidence checks](e2e-saved-evidence-20261017.json) |
| PDF/Word content and hashes, including the browser-downloaded Technical PDF | **13/13 passed** | [Document checks](e2e-document-content-20261017.json) |
| Browser flows and accessibility | Functional voice failure and one moderate report finding | [Browser checks](e2e-browser-20261017.json) |

The landing page's Reports/Predictions/Voice BI previews and mobile menu were exercised. Its recorded pre-entry network requests contained no backend, guest-session or model requests. The mobile CTA opened `/app` without sign-in. Legacy root conversation links preserved their query parameters and loaded saved results under `/app`; New exploration returned to `/app`. A browser-submitted KPI question returned the independently verified revenue and order count. Advanced Analysis exposed report style and Create report controls; the billable report submission itself used the API harness.

The private Cloud Tasks worker produced a fresh Business report in approximately two minutes while ordinary chat remained usable. Its narrative passed review. A Technical presentation revision reused identical immutable artifacts, and the original revision/download manifest remained unchanged. Idempotent admission, persisted event replay, stale metadata rejection, deletion/restoration, owner-only cancellation and confirmed cancellation passed.

The forecast used **ETS**, three full three-month chronological origins, seven fits, and a **2026-09-30** observation cutoff. Independent seasonal-naive MAE was **790,444.8233**; selected ETS MAE was **273,664.8924**, with improvement in all three folds. Training data matched all 45 independent monthly totals. Point predictions were **9,821,574.3852**, **13,396,864.1120**, and **13,004,166.8882** for October, November and December 2026. Intervals were explicitly withheld; these synthetic-data checks do not establish real-world predictive accuracy. The browser showed observed solid lines, a dashed forecast, cutoff and uncertainty caveats.

Report PDF, editable Word and full CSV ZIP passed hashes, row counts, report/version identity, key numerical values and prediction references. Dashboard PNG/JPEG/PDF/CSV ZIP/JSON downloads passed; its CSV retained all 45 observed and 48 observed/predicted saved rows, with matching hashes and revenue reconciliation. Downloads left the dashboard unchanged. Browser checks covered card editing, View/Edit navigation, canonical share output, actual PNG/PDF download controls, report version selection and pinning the new forecast from the report reader.

Landing, KPI workspace and dashboard axe scans each had zero reported violations. The report scan found the duplicate region names below. SVG contrast retained automated manual-review items. Landing/report layouts had no horizontal page overflow at 390px. No uncaught browser JavaScript error was recorded.

## Findings

### P1 — Daily revenue silently multiplied by 200

[Test conversation](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/app?chat=a58e244ea66e4228913e21222fe801ab), artifact `8523f9fa68e447af8d7204f4c476dc36`, model `gemini-3.5-flash-lite`.

Prompt: “Show daily after-discount merchandise revenue for ALL available history. Include zero-sales dates using the calendar spine. Return exactly order_date (ISO business date) and revenue. One row per date, as a line chart.”

The generated query introduced the unrelated 200-row products table:

```sql
FROM sales_products AS p
RIGHT JOIN calendar AS c ON 1 = 1
LEFT JOIN sales_orders AS o
  ON c.calendar_date = o.order_date AND o.status = 'completed'
```

It returned all 1,369 dates and was marked complete, but the total was **USD 70,885,022,440.00**, exactly **200×** the independently verified **USD 354,425,112.20**. This is an analytical correctness failure, not chart downsampling or source truncation. Do not use this artifact as a valid daily baseline. Historical successful daily artifacts were not modified.

The current [SQL guard](../../Backend/app/sql_guard.py) validates permitted operations/resources/functions but does not reject this Cartesian join. Add fail-closed checks for unsupported Cartesian relationships, semantic/cardinality validation and a regression for this exact query. Merely adding a prompt instruction or rerunning until a correct answer appears would not resolve the gap.

### P1 — Multiple voice analyses collide on the same BigQuery job ID

[Test conversation](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/app?chat=aa77ecaabcca4230bf7ea9863ecdf31b).

Synthetic spoken input went through a simulated browser microphone, the actual capture AudioWorklet/WebSocket, hosted ADK/Gemini Live and controlled source queries. The first question returned **573,348** orders, transcripts and spoken PCM output. Permission-denial feedback, mute/unmute controls and three connection-ready events were exercised. After reconnect, a spoken 2024 follow-up produced the correct **152,694** orders, reconciled independently with Parquet. A subsequent tool invocation in that connection failed before another spoken answer.

At **06:45:45 UTC**, backend `00017-cnf` logged BigQuery `409 Already Exists` for `abi_1d2afde8fb41be2f5ded687057132c24_0`, followed by **“A recovered query job belongs to different SQL.”** The UI displayed the generic Live-unavailable/reconnect error. The saved chart survived, but the multi-question voice experience did not pass.

[Analysis execution](../../Backend/app/analysis.py) creates a distinct `analysis_id`, but its query records/job IDs use only the parent run and reset query/repair index. [Voice](../../Backend/app/voice.py) invokes it repeatedly under one voice run. [Connector recovery](../../Backend/app/connectors.py) correctly refuses to reuse different SQL, exposing the collision. Allocate persisted, distinct analytical-invocation namespaces for query records and job IDs, retaining deterministic retry/replay behavior and parent-run cancellation. Add a real repeated-voice-tool regression; do not weaken the different-SQL recovery check.

### P2 — Voice transcripts are saved twice

The same conversation persists the initial full question twice in one user message and the spoken assistant sentence twice in one assistant message. The 2024 follow-up fragments are duplicated too. Browser event capture received identical final transcription text after earlier text; [the voice handler](../../Backend/app/voice.py) appends each event unconditionally. Handle partial/final transcription semantics and deduplicate cumulative/final text without discarding legitimate repeated utterances. Test persisted messages as well as the transient voice panel.

### P2 — Repeated report table regions have identical accessible names

Axe `landmark-unique`, moderate impact: multiple wrappers are named **“Data table scroll area.”** [The shared Table component](../../Frontend/src/components/ui/table.tsx) derives this from a default when the table receives no unique label. Pass each artifact/table title into its label so report landmarks are distinguishable. Retest reports containing multiple tables; the single-table dashboard scan does not expose this issue.

## Inspectable test output

- [New report, Business version](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/reports/972a2453eb11478182bf855af5d65d94?version=1)
- [Technical version](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/reports/972a2453eb11478182bf855af5d65d94?version=2)
- [Dashboard with reconciled monthly evidence and forecast](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/dashboards/77e0df7c96ff41f2bf3a61e90d683298)
- [Verified browser KPI conversation](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/app?chat=77e6d1a0764148f8827ebce5f16dc1c3)

## Boundaries and next acceptance gate

No physical microphone/speaker, native OS sharing, real touch device, Safari/Firefox or full screen-reader certification was performed. Clipboard output was inspected through an intercepted writer. Representative report/dashboard PDF pages were visually inspected, not every page or PDF/UA conformance. The voice smoke's text-over-Live pass is distinct from the richer synthetic-spoken browser test that found the collision. Barge-in and sustained reconnection remain uncertified. Conditional driver scenarios, optional disabled Search and production worker crash/fault injection were not exercised.

Correct the four findings and run targeted regressions before another authorized release. After release, repeat both the daily numerical reconciliation and multiple spoken analyses within one connection, then the multi-table accessibility scan. Keep the larger profile and the current immutable evidence; do not overwrite this failed acceptance record with a later passing run.
