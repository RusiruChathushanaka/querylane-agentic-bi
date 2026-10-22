# Startup loading — local verification, 21 October 2026

**Outcome:** implemented and locally verified; ready for a separately authorized release. No Cloud Run deployment, warm-instance activation or GitHub publication occurred. [Machine-readable evidence](startup-loading-local-20261021.json) records the checks and limits.

## Behavior verified

History appears while sources remain pending. Source availability can enable a typed question despite a history/configuration failure. Retrying configuration preserves the draft; a background refresh failure preserves visible history. Deep-linked conversation text appears before delayed history/source checks. Report narrative appears before chart evidence; a deliberately unavailable card does not hide the narrative or another successful card. Enter on Retry restored the missing card in the final standalone build.

The checked 1280px desktop, 390px reader and 320px loading layouts had no horizontal document overflow. Dark/reduced-motion preferences and local appearance controls worked while model choices loaded. Pending resources did not claim empty libraries or zero history. Status text and skeleton markup exist in raw HTML before hydration. The optimized landing page made no backend/config requests. See [desktop loading](startup-loading-local-20261021-desktop.png) and [320px slow loading](startup-loading-local-20261021-mobile-320.png).

## Automated checks

- Backend: **450 passed, one existing skip**; Ruff passed. Existing Starlette/httpx deprecation warning retained.
- Frontend: **76 passed**; lint, TypeScript and optimized production build passed. The final artifact was served with its standalone server and packaged static/public assets.
- Focused coverage includes transient/timeout classification, one automatic GET retry, rate limits/Retry-After, invalid configuration, ambiguous guest-session POST protection, cancellation, stale results, pending poll deduplication, initial-failure stop, background retention and SSR feedback.
- A barrier-based backend test proves both source checks start concurrently while preserving BigQuery/PostgreSQL ordering and individual failure results. Pure release tests cover API service minimum one, preserved higher minima/current ceilings, unchanged frontend policy and preserved larger-data/TimesFM values.

Graph/document validation checked all 300 source hashes, both synchronized Mermaid diagrams and 272 local documentation links. Graphify indexes 2,492 nodes and 6,495 edges with cached semantics plus one host extraction of five changed documents; partial AST/external-reference limitations remain recorded.

## Timings and interpretation

Five repeated local warm HTTP completion samples (milliseconds; isolated fixture proxy, not real source latency):

| Resource | Median ms |
| --- | ---: |
| Frontend HTML | 2.816 |
| Runtime configuration | 2.776 |
| History | 1.759 |
| Source availability | 2.998 |
| Report configuration | 2.989 |

The browser separately demonstrated first usable history/text before full source/card readiness under controlled delays. Exact browser first-content/full-readiness percentiles were not instrumented; these HTTP completion medians must not be presented as those timings. No hosted before/after speedup or cold-start reduction is claimed before deployment. Production cold starts were not forced. Frontend scale-to-zero may still delay the first HTML response.

## Preservation and limitations

All failure injection and UI reads used isolated local fixtures, including copied immutable report evidence. No live analytical queries/uploads, model/voice calls, quota changes, IAM changes, seeding or shared-history resets were performed. The prepared release policy preserves `DATA_PROFILE=timeseries`, `SOURCE_ROW_LIMIT=30000` and both enabled/verified TimesFM gates; no live configuration was changed or newly recounted here. Both Submission spellings and pre-existing final-test artifacts remain outside this change.

A development preview initially emitted stale-attribute hydration warnings during hot edits; separate optimized previews showed no current-origin console errors. The first sandboxed build stalled and was stopped; a later default-output build hit an OS port-binding restriction. The final permitted isolated-output production build passed. Physical-device and screen-reader speech testing, full contrast/SVG review and the complete browser matrix remain unverified. The earlier [report highlights accessibility finding](final-reports-dropdowns-20261021.md) is retained and not claimed fixed by startup feedback. Saved exports and numerical workflows were not redesigned or reinvoked.

[Startup contract](../startup-loading.md) · [Warm-API release guidance](../deployment-guide.md#startup-latency-and-warm-api-policy). The warm API introduces ongoing instance-based idle CPU/memory charges when separately deployed; it is not active as a result of this implementation task.
