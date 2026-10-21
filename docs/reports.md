# Advanced analysis reports

The Advanced Analysis feature is deployed to the demo. See the dated [release record](deployment.json) and [validation evidence](validation.md) for serving revisions and verification scope. See [deployment-guide.md](deployment-guide.md#advanced-reports-release) before releasing it. Existing cloud source data is unchanged.

## Using reports

Enable **Advanced Analysis** in the question composer, choose Business or Technical, and select **Create report**. The toggle defaults off; submitting a report returns the composer to ordinary chat. Reports are public, including questions, assumptions and downloads. Anonymous guest credentials attribute requests and control cancellation/clarification; they are not private accounts.

The analyst captures the current source, model, completed conversation context, schema and up to three exact skill versions. It asks only essential clarification questions, then runs automatically. A dedicated report card shows real stages, not invented completion percentages. Ordinary chat uses its own lease and remains available. Open `/reports` to return after navigation. Only the requesting guest can clarify or cancel a run. Waiting/queued requests expire after six hours so abandoned visitors do not reserve a conversation forever.

Completed versions contain a summary, findings, interactive charts/tables, recommendations, definitions, limitations, SQL/provenance, model methods and skill evidence. Technical style provides additional methodology. Forecasts and scenarios have different labels from observations. Their charts can be pinned to dashboards through the existing pin control; pins retain the report-version link and prediction caveats.

When bounded writing/review cannot produce a valid narrative, the report explicitly uses deterministic evidence summaries instead of unsupported prose. Check its limitations for this fallback; a completed report does not imply that a model-written narrative passed review. Claim policy v2 excludes unweighted averages of grouped ratios such as monthly AOV from overall-metric claims. Overall ratios require source-calculated numerators and denominators. Presentation revisions revalidate claims from saved evidence while preserving earlier versions.

Everyone can rename, delete and restore completed reports. Deletion offers Undo and remains recoverable for 30 days. Renaming changes the library label; it never changes an old downloaded document. Active reports cannot be deleted. Conflicting edits return 409 and preserve the browser draft. The default library capacity is 100 active reports, with at most 20 completed versions per family.

**Revise report** creates a new version. Presentation revisions use saved evidence without SQL; reanalysis explicitly reads sources again. Prior versions/downloads remain unchanged. Reports can be revised even after their original chat was reset, using their saved scope and evidence. New analyses use the current source profile; presentation revisions retain the original evidence/profile.

## What the analyst can do

The ADK `App`/`Runner` graph coordinates planning, guarded evidence collection, deterministic analysis, writing/review and rendering. Separate planner, query-planner, writer and reviewer agents have narrowly defined outputs. Independent analytical questions run with at most two branches. Models receive no shell, arbitrary Python, unrestricted tools, credentials, or arbitrary fusion SQL.

Numerical claims are computed with deterministic tools over complete saved selections. They include Decimal totals, minima/maxima, leading labels, row coverage and valid adjacent-period comparisons. Grouped rates/averages do not produce unweighted average claims: monthly AOVs cannot establish overall AOV without the original denominators. Request an overall ratio as an approved source SQL aggregation. Presentation revisions recalculate eligible claims from the saved rows under the current policy and freeze them in the new version; historical versions are unchanged. Rates are not summed; zero denominators do not produce percentage changes. A writer references verified claim IDs; the renderer inserts their values. Unsupported digits, links, HTML and evidence references are rejected. After at most two narrative repairs, an unapproved narrative falls back explicitly to verified evidence summaries rather than publishing unsupported prose.

Schema strings, source cells and shared skills are untrusted input. Existing read-only permissions, SQL AST checks, source allowlists and typed fusion/cardinality checks remain authoritative. SQLGlot typed aliases for already-approved DATE/FORMAT_DATE/TO_CHAR are recognized; arbitrary anonymous functions remain blocked. Syntax/binder/schema errors enter the existing bounded SQL-repair path, while permission errors cannot authorize broader access.

## Forecasts and learned scenarios

Workflow version 2 supports [managed TimesFM 3.0 Preview comparison](timesfm.md). Local defaults are disabled; the [TimesFM release](evaluation/timesfm-deployed.md) enables the verified worker/API configuration. The agent proposes relevant forecasts; common chronological scoring selects the method, with statistical fallback. Driver scenarios can have a separate artifact so their baseline always shares the scenario method. Existing version 1 runs and completed evidence retain their original path. The capabilities endpoint reports availability; no public forecasting endpoint or Gemini model-setting change is added.


The numerical child process supports seasonal-naive baselines, ETS, bounded SARIMAX, and regularized driver/lag regression. Large seasonal periods avoid the costly SARIMAX candidate. Preprocessing is fitted inside training folds; future target lags are recursive predictions, never held-out actuals. Each evaluation covers the full requested horizon.

| Grain | Default horizon | Maximum |
| --- | ---: | ---: |
| Daily | 28 days | 90 days |
| Weekly | 12 weeks | 26 weeks |
| Monthly | 3 months | 12 months |

Require three chronological origins with at least two seasonal cycles in training. Candidates must improve aggregate baseline MAE by at least 5% and win a majority of folds. Excessive held-out MAE (over half the mean absolute target scale) withholds predictions. A valid baseline is sent to the parent before expensive fitting; candidate timeout retains it, with a warning and conservative budget charging. Irregular dates, nulls, duplicated periods, incomplete inputs and domain violations do not silently become forecasts. Negative margin may be valid; negative counts and out-of-range rates are rejected rather than clipped.

Point forecasts start after the latest complete saved observation, rather than assuming the dataset reaches today. Historical fold dates, MAE/RMSE, method, parameters, package versions and data hash are retained. Residual bands require sufficient earlier-fold calibration and later-fold coverage; otherwise intervals are omitted explicitly. Nominal and observed coverage are separate, and neither guarantees future coverage. The synthetic dataset validates implementation, not real-world predictive reliability.

Driver scenarios require historical variation, evidence against the baseline, and explicitly supplied future paths. They reject suspicious target/future features, near-identical targets, unsupported ranges and unsupported joint combinations. They are **predictions under assumptions**, not estimated causal promotion lift or guaranteed ROI.

When future paths are required, the report card shows labeled baseline and optional alternative fields for each driver. Enter a single explicit value to hold it constant, or comma-separated values for every future period. Blank values never become zero. The form uses source-data units, preserves drafts on validation/conflict errors, and requires every driver for the full horizon. Model-produced future paths are discarded. A scenario that fails validation is withheld while supported descriptive findings remain available. API clients may supply bounded `forecast_inputs` with `baseline` and `scenario` rows; legacy JSON clarification answers remain readable.

## Downloads

The same immutable report document drives web, PDF (ReportLab), Word (python-docx) and data ZIP exports. Each chart/table also has its existing individual CSV download. ZIP contains full saved CSVs and a manifest with hashes, completeness, source evidence and prediction methods. PDF/Word preview tables show up to 20 rows and 8 columns; they do not claim to contain every source row. Static charts separate mixed units and withhold invalid composition displays. No download runs SQL or invokes a model.

Files use immutable names, checksums and exclusive creation. Production uses a dedicated private bucket; backend download endpoints mediate reads. Local exports go to ignored `.reports/` (or `REPORT_LOCAL_DIRECTORY`). Rendering/fitting run in terminable child processes. PDF text is selectable and Word uses real headings/tables; PDF/UA certification is not claimed.

## Report presentation

The library groups public reports into bordered cards with ready/in-progress counts, status labels and local name/date sorting. Search and filters read saved metadata only. The reader uses the immutable document title; the editable library name and source conversation remain available in a disclosure. Renaming the library entry does not rewrite a saved document.

Each narrative section and chart has its own theme-aware border and padding. Verified-highlight cards show up to three saved numerical claims, excluding row-count and dimension-label diagnostics; values and calculations are never regenerated for display. Unicode bullet lines are displayed as semantic lists without changing stored Markdown. Desktop navigation highlights the current section; the mobile section selector moves keyboard focus to its destination. Source timestamps remain independent, not a synchronized-snapshot claim.

Forecast overviews retain cutoff, horizon, method, Preview status and interval limitations. Candidate tables show saved MAE/RMSE and selection outcomes, not accuracy percentages. Scenario panels distinguish baseline and alternative paths and show the full saved future-driver assumptions. Allocated estimates and planning adjustments remain explicitly labeled. Technical provenance is available in a disclosure; the shared result card keeps its existing evidence panel by default outside the report reader.

Newly rendered PDF/Word files use an A4 briefing layout, an executive opening, formatted tables, chart captions, headers/footers, numbered sections and a technical appendix. Reports with four or more sections include contents: clickable page references/bookmarks in PDF, internal links and normal heading navigation in Word. PDF embeds fonts packaged with Matplotlib; Word uses editable Arial styles. Tables repeat headers and preview at most 20 rows/eight columns; long text cells are abbreviated. Saved future point estimates receive a separate complete horizon table, so a historical preview cannot hide the forecast. Full-precision data is retained separately. ReportLab and Word paginate independently, so page counts may differ. These are selectable-text documents, not a PDF/UA or screen-reader certification.

Forecast diagnostics use structured method, score, fold and assumption tables instead of raw JSON in human-readable documents. Units and currency are taken only from saved metadata. Static chart colors and cutoff annotations match the report identity; mixed units remain separate. Uncertainty and synthetic-data caveats stay visible.

The data ZIP preserves existing artifact-ID CSV filenames, row values, provenance, predictions and checksums. Additive `README.md`, `data_dictionary.csv`, `report.json` and dataset titles make the bundle easier to navigate. `manifest.json` records `presentation_version: 2`; consumers should continue using its dataset entries rather than treating every CSV in the archive as an analytical dataset. Individual result CSV downloads retain their existing full-row contract.

**Compatibility:** existing persisted files are never overwritten or restyled during reads/downloads. The new renderer applies when a new version is published. A presentation revision can reuse saved analysis to create a newly styled version through the existing reviewed workflow; it may still use the report writer, but executes no new source SQL or forecast inference. Rendering and downloads themselves execute no model calls. Large-file deadlines, immutable storage checks and recovery checkpoints are unchanged.

See [local design verification](evaluation/report-design-local-20261021.md). This documents local implementation, not a Cloud Run release.

## Optional external research

Set `REPORT_RESEARCH_ENABLED=true` only after verifying the selected Vertex model and required display behavior. The opt-in Research panel uses a separate Search-only ADK agent with in-memory sessions and curated public retail topics. No database rows, schema, conversation, or free-form private question enter Search. The original response, grounding links and supplied Search Suggestions stay in the requesting browser component and disappear on navigation/clear; none feed report writing, shared history or exports. Search invocations are limited to three per guest/day and twelve workspace/day; one invocation can issue multiple billable searches.

This separation follows the conservative design discussed against [Google Cloud service terms](https://cloud.google.com/terms/service-terms). It is not a mechanism for archiving Search-grounded text in public reports.

## Execution and storage

Production uses a private Cloud Run worker, Cloud Tasks OIDC dispatch and a scheduled private reconciler. HTTP execution remains open until work is committed. Firestore outbox creation is atomic with admission; deterministic task names and application checkpoints handle delivery replay. A 45-second fenced lease and five-second heartbeat protect writes. Completed query/artifact/model/narrative stages are reused; BigQuery job IDs are stable. Uncheckpointed PostgreSQL reads may repeat, with the saved query's timestamp identifying the evidence used. Exactly-once external calls are not promised.

The workflow version is checked on recovery; incompatible releases must drain or restore matching workers. Experimental ADK invocation resumption is off. Report ADK events use their own fenced `report_adk_sessions` collection, so chat reset cannot erase report recovery evidence.

Collections: `reports/{id}/revisions`, `report_runs/{id}/{events,checkpoints}`, `report_outbox`, `report_conversations`, `report_artifact_refs`, `report_quotas`, `report_adk_sessions`, and report capacity/worker records under `system`. All access remains backend-only in `agentic-bi-demo`; single-field indexes suffice. Reports, artifacts, quotas and exports survive shared-history reset. Operator `purge-reports` releases expired report references/files, preserving dashboard-owned artifacts. Failed maintenance stays fenced for explicit recovery.

Default ceilings are ten minutes active computation, two active workspace reports, one per conversation, 24 model calls, 32,000 output tokens, twelve source executions including repairs, two repairs/query, 8 GiB cumulative BigQuery reservation, six forecast targets, 64 fits and 120 fitting seconds. Existing per-query scan/time/row/byte/fusion limits remain unchanged. Admission is three reports per guest/day and twelve workspace/day. Cancellation/failure after admission does not refund quotas; exact request retries do not charge twice.

Local mode has an application-lifetime outbox pump. **Memory storage and local container files are ephemeral**; they are not a production durability demonstration. Production rejects local dispatch. Settings and all defaults are in [Backend/.env.example](../Backend/.env.example).

## Interfaces and verification

Report admission: `POST /api/v1/conversations/{id}/reports`; public library CRUD under `/api/v1/reports`; immutable versions under `/reports/{id}/revisions/{version}`; downloads under `/downloads/{pdf,docx,data}`. Run status/events/clarifications/cancel are under `/api/v1/report-runs/{id}`. Mutations use anonymous bearer credentials. Clarifications and metadata changes carry `expected_revision`; admission/revisions carry an idempotency key. `/reports/config` exposes feature availability only. Worker handlers exist only in the separate private ASGI app.

Run the complete backend and frontend verification from the deployment guide. `test_reports.py` includes 30 fixed numerical retail assertions and runs against both memory and isolated local Firestore namespaces when `FIRESTORE_EMULATOR_HOST` is set. Real Gemini and Search checks are separate from deterministic correctness tests; see [validation.md](validation.md#advanced-analysis-reports--2026-10-17) for actual evidence and remaining cloud-release checks.

Reproduce the local compatibility check from `Backend/`:

```bash
PYTHONPATH=. uv run python scripts/smoke_reports.py
# Optional: bounded billable model calls; history, source reads and files stay local.
PYTHONPATH=. uv run python scripts/smoke_reports.py --gemini --output ../docs/evaluation/reports-gemini-local.json
```

The helper explicitly uses memory storage and the existing generated Parquet bundle. It cannot deploy, upload data, invoke production report dispatch, or persist Search responses. Use `--model gemini-3.5-flash-lite` to check the second configured text model.

The [21 October hosted release](evaluation/report-dropdown-release-20261021.md) verifies forecast version 3 and scenario version 2 through private-worker presentation revisions. Their PDF, Word and ZIP files use the new design; previous versions retain their original bytes. All 45 future point values match the saved evidence. Report version/style/mode/model filters, mobile section navigation and chart controls now share bounded, keyboard-operable Radix dropdowns with the rest of the application.
