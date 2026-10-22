# Workspace layout and loading — local verification, 22 October 2026

**Implemented and locally verified; not deployed or published to GitHub.** This extends the [prepared startup lifecycle](startup-loading-local-20261021.md). Existing hosted release/TimesFM evidence and both Submission folders remain outside publication scope.

## Changes and preservation

The `/app` shell reserves header/composer rows and independent conversation/history scrolling. Positioned chart figures contain hidden accessibility instructions rather than extending the document. Auto-follow targets the conversation only, pauses when reading older messages and resumes through Jump to latest. Narrow layouts use Visual Viewport sizing with zoom escape, safe-area padding and bounded textarea height. Nearby cards use the existing shared two-request loader; unchanged poll JSON retains React state identity.

The release helper prepares frontend **and** API service minima one, preserves higher minima/ceilings/billing modes and leaves worker scaling alone. This task applies no cloud settings, IAM, deployment, model call, dataset write, history reset or quota change. Preservation tests retain `timeseries`, source row limit 30,000 and both verified TimesFM gates. Dataset preservation is by absence of cloud writes, not a new count/fingerprint verification. See [warm-capacity costs](../deployment-guide.md#warm-service-operating-cost-illustration-22-october-2026).

## Verification

Backend: **450 passed**, one existing skip; Ruff passed. Frontend: **81 passed**, ESLint, TypeScript and optimized production build passed. The backend emits the existing Starlette/httpx deprecation warning. Build checks used an isolated output directory; the sandbox-stalled build was stopped and retried with compilation permissions. Generated temporary TypeScript include entries were removed without restoring unrelated configuration.

The isolated fixture uses 20 distinct saved-chart copies of recorded synthetic monthly evidence; it does not query BigQuery/PostgreSQL or run Gemini/TimesFM. Desktop, 320px/390px mobile, 844x390 landscape and 640x450 compact reflow pass document containment. At 844x390 the six sidebar links end by y=382. Header/sidebar/composer bounds stay fixed as conversation scrollTop changes. The earlier baseline grew beyond 22,000px in the same long conversation; the corrected document stays at viewport height. Pending chart instructions remain accessible within positioned figures.

Upward scrolling retains the older-message anchor and typed draft across polling. Jump to latest works with Enter; skip link focuses the conversation and PageUp scrolls it without moving the document. A chart's Line→Bar keyboard choice persists across polling. Mobile navigation restores trigger focus. Dark/light and reduced motion were checked. Visual Viewport unit tests cover height/offset, zoom preservation and cleanup; physical keyboard behavior and actual 200% browser zoom remain manual checks.

A local saved three-card dashboard renders positioned figures with retained instructions. A copied report shell/title reflows on desktop/390px without horizontal overflow; this is not a repeat of full report-worker/download acceptance. CSV export returned HTTP 200 and all **45 original rows**, January 2023 through September 2026. The browser download watcher timed out; file-save completion is unconfirmed, despite independent response-content validation. The initial watcher also preceded the required export dialog; its timeout is retained as a test observation, not treated as an application failure.

## Performance comparison

Ten warm production-build observations per version used the same 1280x900 tab, unthrottled local fixture and long conversation. Browser values include automation round trips and are observed milestones, not FCP/LCP metrics. p95 uses nearest rank (the maximum with ten samples). Cold starts were not forced.

| Observed milestone | Before median / p95 | After median / p95 |
|---|---:|---:|
| Shell available | 248.0 / 301 ms | 175.0 / 335 ms |
| Readable conversation | 564.5 / 696 ms | 510.0 / 574 ms |
| Source-dependent action usable | 612.5 / 715 ms | 526.0 / 640 ms |
| Final visible chart SVG rendered | 1413.5 / 1603 ms | 857.5 / 1379 ms |

The initial nearby chart set drops from 20 eager cards to two, leaving 18 deferred until approached. Median chart readiness improves from 1,413.5ms to 857.5ms in this fixture. Shell p95 rises by 34ms while its median falls; local noise prevents claiming every percentile improved. Preliminary control-only observations are retained in JSON but were replaced as the decision basis by actual SVG readiness.

HTTP samples separately cover HTML, runtime configuration, history, sources and conversation bodies. Initial JavaScript remains 18 assets: 373,380 → 374,653 gzip bytes (about 1.3KB added), so no bundle-size reduction is claimed. Full samples, formulas, source hashes and limitations are in [machine-readable evidence](workspace-layout-local-20261022.json). Production speed and warm capacity require a separately authorized deployment and hosted remeasurement.

## Evidence and remaining checks

- [Desktop while reading older messages](workspace-layout-local-20261022-desktop.png)
- [320px mobile](workspace-layout-local-20261022-mobile320.png)
- [390px mobile](workspace-layout-local-20261022-mobile390.png)

Physical mobile keyboard, actual 200% browser zoom, assistive-technology announcements and full contrast review remain manual. Whole-conversation printing is not introduced; chart/report/dashboard exports continue to resolve their saved evidence independently. No fresh analytical/voice/report/planning-worker suite was repeated. Graphify's parser still reports a partial workspace parse (line 1101, 14 symbols); successful TypeScript/build checks and source hashes are separate evidence.
