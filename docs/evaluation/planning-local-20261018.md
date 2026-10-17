# Metrics and planning: local acceptance — 18 October 2026

This assessment concerns the new implementation in the working tree. No Cloud Run deployment, IAM mutation, source upload, hosted example seeding or GitHub publication was performed. Existing serving revisions and hosted TimesFM settings are unchanged.

## Automated verification

- Backend: **433 passed, one existing opt-in skip**; Ruff passed. The suite includes numerical metric fixtures, aliases and conflicting definitions, exact dependency versions, read-only compilation, preview idempotency, shared admission/fitting limits, durable dashboard review/publication/replay/reuse/conflict/rebase/Undo, complete forecast generation, adjustment versions, retention and exports. A Starlette/httpx deprecation warning is informational.
- Frontend: **53 passed**; ESLint, TypeScript and production build passed. A final focused forecast/adjustment/export check also passed after the planning-view preference was completed. New focused checks cover reviewed card change sets, stable retry identities, immutable metric links/escaping, and planning-versus-prediction labels.
- The adjusted-plan PDF, data ZIP and JSON checksums reconcile across separate downloads. Verification found and fixed a PDF metadata issue: the document's default `invariant=None` overrode the partial Canvas configuration. Setting invariance on the document produces stable bytes. Historical exports remain unchanged.
- Existing report/TimesFM recovery, bounded SQL/fusion, chart, voice-client and persistence regression tests remain included. These local tests do not establish fresh hosted model access.

## Existing larger dataset

The isolated development preview used the existing `retail-timeseries-20260930` Parquet bundle with `DATA_PROFILE=timeseries` and `SOURCE_ROW_LIMIT=30000`: **573,348 orders, 1,317,941 line items, 1,369 days and 45 months**. Every bundle file still matches its original manifest hash. No generation or upload was needed.

Five bounded reads reconciled store/order and product/line histories to **USD 354,425,112.20**. A plan captured **237 nodes**, a common company total, and October–December 2026 point predictions. The adaptive coherent recipe passed its three-fold selection gate: level-balanced normalized MAE was **0.05774538**, versus **0.11292275** for the coherent baseline. These are historical synthetic-data diagnostics, not future accuracy guarantees. Leaf estimates remain explicitly allocated.

A separately saved +5% company planning assumption preserved all original observations and statistical predictions. Both saved versions passed **84 exact-cent parent/view reconciliation checks**. A four-card AI dashboard was reviewed and published, the adjusted company chart was pinned as a fifth card, and a completed report was generated from that saved plan version. A local metric was created, structurally validated and explicitly published as version 1.

See [the sanitized machine-readable record](planning-local-20261018.json). IDs and browser evidence there describe ephemeral local application storage, not hosted library URLs. The latest checksum and recovery paths were tested against the current implementation by automated integration tests; earlier browser preview records retain their actual local context.

## Browser and accessibility

Chromium checks covered `/metrics`, its structured editor/compiled evidence, `/dashboards/build`, a published dashboard, `/forecast-plans` and its versioned reader, and the saved-plan report. The tested metric/editor/builder/plan/report states reported zero axe WCAG 2 A/AA and 2.1 AA violations after fixes.

Manual checks included 320px, 390px and desktop layouts, keyboard focus/skip links, semantic tables, hierarchy controls, explicit publication and reduced motion. All four supported accent styles in both light/dark modes had no plan-reader overflow or reported axe violations. Stored preferences were restored after style probes. Browser verification found and fixed grid overflow, inaccessible scrollable evidence, and duplicate React keys for multiple same-source provenance entries.

## Release preparation and limits

Follow [the deployment runbook](../deployment-guide.md). Release a workflow-3-compatible private worker before enabling public planning admission. Existing report workflows 1/2 remain supported. Reports, dashboard builds and plans share the existing expensive-job allowance and two-job workspace ceiling. Forecast Plans alone may reserve up to 128 fits; existing report limits remain unchanged.

Release helpers preserve existing TimesFM enabled/verified flags, planning limits and same-profile source-row limits. No new queue, database, bucket, GPU service or IAM role is required. Hosted metric examples are insert-only and explicitly operator-triggered. Retention cleanup is a separate fenced operator action, preserving plans referenced by reports or dashboards.

Fresh Gemini planning, actual managed TimesFM comparisons within a 237-node plan, Cloud Tasks deliveries, hosted Firestore contention, physical-device behavior and screen-reader acceptance remain release-stage checks. Local planning used fixture agent decisions and real local statistical fits. The new feature is implemented and locally verified; this assessment is not a claim of deployed end-to-end acceptance.
