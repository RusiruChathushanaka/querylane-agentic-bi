# Navigation icon release — 18 October 2026

**Outcome: deployed and verified.** Business metrics now has a target icon and Forecast plans a trend-line icon in the shared desktop/mobile workspace navigation. Both reuse existing Lucide imports, match the other links' 16px sizing, and use `aria-hidden="true"` so their visible text remains the accessible name.

## Release

- Frontend: `agentic-bi-frontend-00019-gvr`, 100% traffic.
- Previous revision / rollback target: `agentic-bi-frontend-00018-kd4`.
- Cloud Build: `2f560c13-5d84-4336-8ed3-08c3b64de878`, successful.
- Image digest: `sha256:03adba9fb62c77c858e6d9b49cc0aa8a77302e53268cb169d4b603ef175a65a5`.
- API `00024-rnd` and private worker `00013-sm4` are unchanged.
- Image-only deployment created a no-traffic candidate. Readiness, immutable image, unchanged frontend runtime spec/annotations, and four candidate HTTP routes passed before promotion. The temporary `release-check` tag was removed afterward.

The [source manifest](navigation-icons-release-20261018-source.json) hashes 131 runtime/build files over base commit `22625a68d64aebcaa7e8e3dcdb2c604475132652`, including the uncommitted icon change used in this build. The manifest distinguishes the exact built source from the later GitHub publication commit.

## Verification

The preceding implementation checks passed on the same unchanged source: **53 frontend tests**, lint, TypeScript and an isolated production build. That local build stalled inside the restricted sandbox, then passed outside it. Cloud Build independently completed the Docker production build. No backend code changed, so backend/model suites were not repeated.

Hosted verification passed **13 browser checks**, **17 preservation checks**, **11 health/configuration checks**, eight HTTP routes and four candidate HTTP routes. These are scoped release checks, not another full analytics acceptance suite.

- Desktop at 1280×960 and mobile at 557×904 show both icons at 16px, aligned with the other four library/settings icons. All six icons remain visible at 390×844; no horizontal page overflow was observed.
- Keyboard Tab exposes visible focus on Business metrics and Forecast plans; Enter opens `/metrics` and `/forecast-plans`. Escape closes mobile navigation and restores the menu-trigger focus after its transition.
- Settled mobile-sheet and navigation-footer axe scans found zero violations and zero incomplete checks. An initial scan during the opening fade flagged contrast; the browser record preserves that observation alongside the settled rechecks. An immediate post-Escape inspection also preceded unmount; settled dismissal/focus verification passed.
- Landing entry reaches `/app`. Application/library routes return HTTP 200. Backend live/readiness, frontend health, runtime backend URL, both connected sources and TimesFM report configuration pass.
- Browser errors and inspected new-frontend-revision error logs are empty. The browser made no new analysis or expensive-job requests.

This uses an isolated Chrome test session. Physical mobile devices, full screen-reader use, Safari/Firefox, live voice and fresh report/forecast generation were not rerun for this icon-only release. The separately documented [fresh TimesFM acceptance](final-e2e-20261018-fresh.md) and [planning workflow limitations](planning-release-20261018.md) retain their original scope.

## Dataset and settings preservation

API and worker service specs, serving revisions and traffic match their captured baselines. Both retain:

```text
DATA_PROFILE=timeseries
SOURCE_ROW_LIMIT=30000
REPORT_TIMESFM_ENABLED=true
REPORT_TIMESFM_VERIFIED=true
```

Before/after BigQuery metadata matches for all five larger-source tables: **573,348 orders**, **1,317,941 line items**, **97,122 returns**, **200 products** and **1,369 calendar days**. Row counts, byte counts, schema and modification timestamps were compared through metadata reads, without analytical SQL or a new content scan. PostgreSQL was not recounted; its connected status and unchanged API/worker configuration were verified.

This release performs no analytical upload/seed, schema migration, source write, IAM/secret change, quota/history reset or model inference. Frontend runtime overrides and both analytical services' TimesFM/planning configuration are preserved. [deployment.json](../deployment.json) records the actual serving release.

## Evidence

- [Built source and local gates](navigation-icons-release-20261018-source.json)
- [No-traffic candidate checks](navigation-icons-release-20261018-candidate.json)
- [Service and source metadata preservation](navigation-icons-release-20261018-preservation.json)
- [Health and report configuration](navigation-icons-release-20261018-http.json)
- [Application/library HTTP routes](navigation-icons-release-20261018-routes.json)
- [Desktop/mobile, keyboard and accessibility checks](navigation-icons-release-20261018-browser.json)
