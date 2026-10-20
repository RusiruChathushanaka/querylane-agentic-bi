# Sample-question frontend release — 20 October 2026

**Outcome: deployed and verified. All four fresh deployed sample-card analyses passed with the default Gemini 3.8 Flash model.** Full saved CSV values match independent aggregates from the larger generated retail bundle. Earlier provider-timeout observations remain in the [preparation assessment](sample-questions-20261020.md); this fresh release test closes its all-four default-model verification gap without changing model settings or fallback behavior.

## Release and scope

- Frontend: `agentic-bi-frontend-00045-gej`, 100% traffic. Previous revision `agentic-bi-frontend-00042-van` remains available for rollback.
- Image: `frontend@sha256:ff932f12eb824ba6808cb78a1fc0a071c2204c47fc54e7bd2d776e450b8209f6` in the existing dedicated Artifact Registry repository.
- Cloud Build: `7040ce92-ead0-4041-b3dc-a91f8c4dc0de`, `SUCCESS`, built from working-tree source based on `c645023eae92fdc9e6482b71a8f3b4771e67e9e4`.
- API `agentic-bi-backend-00024-rnd` and private worker `agentic-bi-report-worker-00013-sm4` are unchanged.

The four cards now create conversations with their advertised BigQuery or cross-source scope, even when the visitor saved PostgreSQL as the default. The saved preference remains unchanged, and ordinary typed questions retain their selected/default source. Prompts specify completed orders, after-discount merchandise revenue before refunds/tax/shipping, USD and complete historical periods. Category analysis uses line revenue to prevent order-level duplication. The customer-segment example explicitly requests ad hoc analysis because the shared revenue definition does not support that dimension. Catalog compilation, SQL validation and backend execution are unchanged.

The runbook's image-only path built with the dedicated builder, deployed a no-traffic candidate, verified readiness/configuration and four candidate routes, then promoted the exact revision. Its temporary tag was removed. No environment, secret, identity, IAM, quota, data or backend deployment changes were made. Submission materials in the actual `Submision/` folder remain local, excluded from Git and Cloud Build. The inspected upload also contained no `Submission/` path or root `.env`.

## Fresh deployed sample acceptance

Each card was activated once through the real deployed UI in an isolated Chromium session, with PostgreSQL saved and the text model left at **default**. At most two analyses ran concurrently. There were no mocked API responses, replacement runs or model substitutions. The mobile customer-segment card was activated with keyboard focus and Enter. Each run reached terminal completion, rendered its saved chart and retained expected source provenance.

| Card | Saved conversation | Result / independent comparison |
| --- | --- | --- |
| See the bigger picture | [Monthly revenue](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/app?chat=5af777da9fe84118b1134feb46330400) | 45 complete months; artifact `fdd5de319c6841619ce3e318c955c046`; every month matches |
| Actuals meet ambition | [Regional actuals and targets](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/app?chat=5f17782ba6354051832202f2d00357f0) | Four regions; artifact `13a570b995f34cd1be0f56e2f0fb1c36`; actuals and full-month targets match |
| Know your customers | [Customer segments](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/app?chat=d3b66a62b6c94844bc2dce5d6ec7c96d) | Two source-defined segments; artifact `349de15dfb07456790081be8238410af`; explicit ad hoc calculation matches |
| Find what sells | [Product categories](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/app?chat=0bb8e7474a354b59b393115a582adee2) | Eight categories; artifact `76c4f582ee834d46ad57c43dc063bcdd`; every category matches |

All four revenue breakdowns reconcile to **USD 354,425,112.20** across the complete synthetic retail history. Verification uses full CSV exports and independent DuckDB aggregates over the existing generated Parquet bundle, rather than model prose or the 30-row preview. Cross-source results retain both BigQuery and PostgreSQL evidence; monthly/category results retain BigQuery evidence. All **26 analytical checks** and **16 card-routing/preference/layout assertions** pass. The four browser sessions recorded no JavaScript errors.

The earlier two Flash `504 DEADLINE_EXCEEDED` failures and explicitly selected Flash-Lite probes remain unchanged in the preparation evidence. This successful rerun demonstrates current default-model completion; it does not guarantee future provider availability or claim a new automatic fallback.

## Interface and engineering checks

- **58 frontend tests**, ESLint and TypeScript pass again. Cloud Build independently completed the production build.
- **20 isolated local browser checks** pass again: four cards plus ordinary questions under all three saved source preferences, four responsive widths and a settled focused accessibility scan. All local API traffic is intercepted.
- Deployed layouts at **320, 390, 768 and 1280px** show four readable cards without document horizontal overflow. Native keyboard tab order passes. Explicit light and dark/teal/reduced-motion sample-grid axe scans report **zero violations and zero incomplete checks**.
- The initial system-theme scan rendered dark, so its light label was not accepted. The final recheck explicitly forces and confirms light, then checks dark; the initial observation is retained in the layout record.
- Nine public application routes return HTTP 200. Nine health/configuration checks pass, including connected analytical sources, the active `timeseries` profile, unchanged default text model, report Cloud Tasks mode and enabled TimesFM. No frontend severity-ERROR entries were found in the inspected new-revision verification window.
- The preparation also passed nine metric intent/policy tests and 65 SQL/analytics tests. Backend code did not change and these suites were not unnecessarily repeated during this frontend release.

Visual evidence: [desktop cards](sample-questions-release-20261020-desktop.png), [mobile cards](sample-questions-release-20261020-mobile.png), [regional result](sample-questions-release-20261020-regional-result.png), [mobile segment result](sample-questions-release-20261020-segment-result-mobile.png).

## Dataset and configuration preservation

All **19 preservation checks** pass. API and worker specifications, serving/created revisions, traffic and IAM policies are unchanged; frontend runtime specification and annotations are unchanged except its image. Both API and worker retain:

```text
DATA_PROFILE=timeseries
SOURCE_ROW_LIMIT=30000
REPORT_TIMESFM_ENABLED=true
REPORT_TIMESFM_VERIFIED=true
```

Before/after BigQuery metadata matches for **573,348 orders, 1,317,941 line items, 97,122 returns, 200 products and 1,369 calendar days**, including bytes, schemas and modification timestamps. Metadata checks do not claim a new full-table content fingerprint. PostgreSQL was not independently recounted during this release; its connection and unchanged configuration were verified, and fresh segment/target calculations matched the independent larger-bundle reference. No analytical source writes, uploads or seeding occurred.

These were ordinary analytical questions and public test artifacts; no new report, TimesFM inference or Forecast Plan job was started. Existing forecast/report acceptance remains separately dated. Physical mobile devices, full screen-reader behavior, other browsers, voice/audio and infrastructure outage/crash scenarios were not retested. No architecture/execution-service boundary changed; Graphify remains its separately dated snapshot.

## Machine-readable evidence

- [Actual Cloud Build source hashes and upload exclusions](sample-questions-release-20261020-source.json)
- [No-traffic candidate readiness/configuration checks](sample-questions-release-20261020-candidate.json)
- [Local regression rerun](sample-questions-release-20261020-local.json)
- [Fresh deployed card activations and rendered results](sample-questions-release-20261020-browser.json)
- [Independent numerical comparisons and CSV values](sample-questions-release-20261020-analytics.json)
- [Responsive layout, keyboard and accessibility checks](sample-questions-release-20261020-layout.json)
- [Health, connections, model configuration and routes](sample-questions-release-20261020-http.json)
- [Before/after preservation checks](sample-questions-release-20261020-preservation.json)

The source manifest compares 147 frontend/build-control files against the actual uploaded archive. The generated TypeScript incremental cache changed during local type-checking and is recorded separately as a build cache, not application source. Release files contain no guest credentials, secret values, raw audio or submission materials.
