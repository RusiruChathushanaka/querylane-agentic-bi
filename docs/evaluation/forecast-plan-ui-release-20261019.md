# Forecast Plans UI release — 19 October 2026

**Outcome: deployed and verified.** The shared skills picker in Forecast Plans and AI Dashboard Builder now uses wrapping grid cards with clear spacing, skill-name search and a bounded, keyboard-accessible scroll region. Loading, error, empty and no-match states are distinct. Selected skills remain attached when filtered; source compatibility and the three-skill limit are preserved. Enter in skill search does not submit a computation.

## Release

- Frontend **`agentic-bi-frontend-00042-van`**, 100% production traffic.
- Previous serving revision / rollback target: `agentic-bi-frontend-00019-gvr`.
- Cloud Build: `2bc1a72a-f897-4292-b762-a6af7432b907`, `SUCCESS`.
- Image: `sha256:b8a87d35e5e344f37b4ee9232a81b70f5b075f269b0aebe07850097d5a5e91e6`.
- API `agentic-bi-backend-00024-rnd` and private worker `agentic-bi-report-worker-00013-sm4` unchanged.

The image-only release created a no-traffic candidate, verified readiness, exact digest, unchanged runtime spec/annotations and four HTTP routes, then promoted the named revision. The temporary candidate tag was removed. No IAM, environment, secret, analytical runtime, quota or source-data settings changed.

The [source manifest](forecast-plan-ui-release-20261019-source.json) verifies 149 frontend/build-control hashes against the actual uploaded Cloud Build archive, based on Git commit `fa6627b`. The archive contains no submission materials or `.env` files. `Submision/` is now explicitly ignored by Git and Cloud Build. Its existing local content was preserved.

Context7's monthly documentation quota was exhausted; this was disclosed before deployment. The existing repository runbook and Cloud Run skill were used with Google's [official deployment reference](https://docs.cloud.google.com/run/docs/deploying). Restoring Context7 access requires `npx ctx7@latest login` or `CONTEXT7_API_KEY`; no application settings were changed for this tooling limitation.

## Verification

The unchanged frontend source passed **58 tests**, ESLint, TypeScript and a fresh local Turbopack production build. Cloud Build independently completed the Docker production build. See the [local assessment](forecast-plan-ui-20261019.md) for original reproduction, corrections and local build-environment observations. Backend code is unchanged, so numerical/model/voice suites were not repeated.

Hosted verification passed **24 browser checks**, **19 preservation checks**, **nine health/configuration checks**, nine application/library routes and four no-traffic candidate routes.

- All 29 live skills use a responsive grid at 320, 390, 768, 1280 and 1600px on both `/forecast-plans` and `/dashboards/build`, plus simulated 200% CSS zoom. No overlapping cards, text overflow, horizontal overflow or submit collision. Labels are at least 47px tall.
- Space selects a native checkbox with a visible 2px focus outline. Three attachments disable other choices; a selected choice remains removable. Case-insensitive search preserves attachments hidden by filtering. No-match search has explicit feedback. Enter is prevented from submitting the parent form.
- Focused axe-core 4.12.1 scans of the changed picker report 18 passing rules, zero violations and zero incomplete checks in light mode and dark/teal/reduced-motion mode.
- Frontend and backend health/readiness, source connections, runtime backend URL, report dispatch and TimesFM availability pass. Browser errors and the inspected new-revision error log window contain no entries.

The browser harness initially used an empty-string fill that cleared the DOM value without notifying React. Ordinary Backspace input restored all 29 skills and retained three selected attachments; the remaining checks continued from the settled state. That observation is retained in the browser record. The initial blanket no-POST assertion also observed one expected guest-session request: Dashboard Builder authenticates reads of the initiating guest's unpublished builds. No credential bodies/tokens are recorded, and no analytical or library mutation request was made.

This scoped release does not rerun fresh hierarchical forecasting, dashboard generation, report/TimesFM inference or voice. No physical mobile devices, full screen reader, Safari/Firefox or browser-menu zoom were tested. CSS zoom is explicitly a simulation. Focused axe scans do not establish application-wide accessibility certification. The separate fresh planning worker acceptance gate remains unchanged.

## Larger dataset and TimesFM preservation

API and private-worker specs, latest revisions and traffic match the before-release snapshots; IAM policies for all three services also match. Both analytical runtimes retain:

```text
DATA_PROFILE=timeseries
SOURCE_ROW_LIMIT=30000
REPORT_TIMESFM_ENABLED=true
REPORT_TIMESFM_VERIFIED=true
```

All five BigQuery tables retain identical row counts, byte counts, schemas and modification timestamps: **573,348 orders**, **1,317,941 line items**, **97,122 returns**, **200 products** and **1,369 calendar days**. This uses table metadata only, without analytical SQL or a fresh content scan. PostgreSQL was not recounted; its connected status and unchanged analytical runtime configuration were verified. No upload/seed, history reset, quota increase, IAM/secret change or model inference occurred.

## Evidence

- [Built source and upload exclusions](forecast-plan-ui-release-20261019-source.json)
- [No-traffic candidate](forecast-plan-ui-release-20261019-candidate.json)
- [Service, IAM and source preservation](forecast-plan-ui-release-20261019-preservation.json)
- [Health, configuration and routes](forecast-plan-ui-release-20261019-http.json)
- [Desktop/mobile, keyboard and accessibility](forecast-plan-ui-release-20261019-browser.json)
- [Desktop screenshot](forecast-plan-ui-release-20261019-desktop.png)
- [Mobile screenshot](forecast-plan-ui-release-20261019-mobile.png)
- [Current deployment record](../deployment.json)
