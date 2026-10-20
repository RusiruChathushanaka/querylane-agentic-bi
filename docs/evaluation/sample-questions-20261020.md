# Workspace sample-question fixes — 20 October 2026

**Outcome: local UI fixes pass. All four corrected prompts have independent numerical verification against the deployed backend, with a model-availability limitation.** Monthly/category prompts passed with Gemini 3.8 Flash. Regional-target/customer-segment prompts first returned provider timeouts with Flash, then passed one explicitly selected Gemini 3.5 Flash-Lite verification each. The default model and fallback behavior were not changed. The frontend changes are not deployed or published to GitHub by this task.

The subsequent authorized [Cloud Run release](sample-questions-release-20261020.md) deployed these fixes and verified all four fresh card activations with the default model. The local/preparation observations below remain unchanged as historical evidence.

## Reproduced findings

1. The cards displayed BigQuery or Cross-source labels but submitted whatever source the visitor had saved in Settings. A local browser regression with a PostgreSQL default recorded `postgres` for all four cards; all four source assertions failed. The corrected handlers pass an explicit required source into conversation creation. Ordinary questions retain their normal source behavior, and the saved preference is not overwritten. Existing conversations are not retargeted to another database.
2. The customer-segment card asked a generic revenue question that matched the shared revenue definition. That published definition supports region/store/category/product/channel, not customer segment. The deployed browser reproduced the resulting clarification with no artifact in conversation `eae6e04ca60246e0942cbdfbf8d448b3`; previous public attempts had the same response. The revised sample explicitly asks for an ad hoc segment breakdown through the existing guarded pipeline, without changing or bypassing an explicitly requested catalog definition.

The revised examples also state completed orders, after-discount merchandise revenue before refunds/tax/shipping, USD, and available-history/full-month scope. Category analysis requests line revenue to avoid order-level fan-out. No catalog entries, compiler, SQL validation, numerical service or backend code changed.

## Local verification

- **20 browser checks pass**: four samples plus ordinary typed questions under all three saved source preferences; four responsive widths (320/390/768/1280px); one focused sample-grid accessibility scan. All API responses in this browser matrix are intercepted, including synthetic guest credentials and completion events. No model or source calls occur in these tests.
- The settled focused axe scan reports zero violations. An initial production scan during the welcome reveal flagged one contrast rule; a 700ms transition wait resolved it, and both observations are retained. Viewports are emulated; no physical mobile device or full screen-reader test was performed.
- **58 frontend tests**, ESLint, TypeScript and an isolated production build pass.
- **Nine existing metric-policy tests** preserve explicit/negated ad hoc intent, competing definitions and catalog forecast/target behavior. **65 SQL/analytics tests** pass. No new backend implementation was required.
- Reproduce the source regression with a local frontend: `python3 Frontend/tests/browser/workspace_samples.py --frontend http://localhost:3013`. It refuses non-local frontend origins and intercepts API traffic.

## Hosted numerical evidence

Each corrected prompt was submitted once initially, with at most two concurrent analyses. Complete CSV exports were reconciled independently against the existing generated Parquet bundle, rather than against model summaries or the 30-row preview. Tests created labeled public conversations/artifacts and made billable read-only model/source calls. No report/forecast-plan job, quota reset, data upload, IAM change or deployment was performed.

| Example | Verified model | Saved result | Reconciliation |
| --- | --- | --- | --- |
| Monthly revenue | Gemini 3.8 Flash | `657572d22da840b785801bf51b3298ea` | 45 months; every monthly amount matches |
| Regional revenue and targets | Explicit Gemini 3.5 Flash-Lite probe | `bbd840c700854288aa159bb22369befd` | Four regions; actuals and full-month targets match |
| Customer-segment revenue | Explicit Gemini 3.5 Flash-Lite probe | `9f3459e5301f4e3fb93618f6292536f6` | Both source-defined segments match; ad hoc evidence |
| Category revenue | Gemini 3.8 Flash | `dc204645be314212af96e38b678b8d1a` | Eight categories; every category amount matches |

Each revenue breakdown reconciles to **USD 354,425,112.20** over the larger synthetic history. Monthly and category outputs use BigQuery; regional and segment outputs record both BigQuery and PostgreSQL provenance with complete source results. This verifies the existing backend can answer the corrected prompts; it is not a deployed-button acceptance test for the pending frontend source.

### Provider limitation retained

The initial regional and segment runs returned `model_transient`. Targeted backend logs show upstream Google `504 DEADLINE_EXCEEDED`, including the existing bounded model-call retries. These are preserved in the initial record and are not claimed fixed by prompt wording. One explicit Flash-Lite probe per affected example then succeeded sequentially. No silent model substitution, default-model change or new automatic fallback was introduced. Fresh all-four success under the default Flash model remains unverified.

## Evidence and preservation

- [Before/after browser cases, exact questions and local gates](sample-questions-20261020-browser.json)
- [Initial four Flash analyses, including the two failed provider calls](sample-questions-20261020-live.json)
- [Explicit Flash-Lite cross-source verification](sample-questions-20261020-flash-lite.json)

The larger dataset was queried read-only and matched its independent reference; no analytical source or TimesFM setting was modified. Existing history and failed attempts remain intact. Guest tokens, credentials, raw audio and submission materials are not included. Historical deployment/Graphify snapshots remain dated records; this correction adds no new architecture or execution service.
