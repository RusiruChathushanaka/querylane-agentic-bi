# TimesFM landing release — 17 October 2026

The updated [public landing page](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/) is deployed. Its forecast and conditional-scenario previews use immutable examples from the [verified TimesFM reports](timesfm-deployed.md). Primary actions open `/app` without sign-in.

## Release evidence

- Frontend: `agentic-bi-frontend-00016-tw2`, ready and serving 100% traffic.
- Image: `frontend@sha256:0b6f98bbd6b967fa6d8f99b73fecec7b870c088779fc9f764d4457954a1d3db5` in the dedicated `agentic-bi-demo` repository.
- Cloud Build: `45478798-8192-45c2-bedd-f44973e1366c`, `SUCCESS`. All eight tested source hashes matched the staged build archive. Generated data, environment files and Git metadata were excluded.
- The exact revision was staged with zero traffic; readiness, digest and unchanged runtime settings were verified before promotion. Prior revision `agentic-bi-frontend-00015-6ff` remains available for rollback through the deployment runbook.

[Machine-readable evidence](landing-timesfm-deployed.json) contains service observations, build source, source hashes, HTTP and browser results. [Local acceptance](landing-timesfm-local.json) records 49 passing frontend tests, lint, TypeScript and production build. The source was unchanged for deployment; Cloud Build performed another production build.

## Live checks

The landing page, runtime configuration, frontend/backend health, both saved report revisions and report pages returned HTTP 200. The served social image matched the packaged SHA-256. A legacy root conversation URL returned one 307 to `/app`, preserving both query parameters. The private worker returned 403 to anonymous access.

Chromium verified four preview tabs, the four-row method comparison, visible September 30 cutoff, keyboard tab switching, fourteen-row scenario table, distinct cobalt/teal dashed/dotted paths, and the correct version-1 report links. Scenario totals were $4,571,971 and $4,828,573, labeled as conditional predictions. Four primary CTAs target `/app`. Before application entry, recorded resource requests included no backend/API requests. Workspace entry loaded the composer, multi-year profile and two connected analytical sources.

At 320px and 390px there was no horizontal page overflow. Dark-system and reduced-motion checks passed. Axe returned zero violations, 50 passes and one incomplete SVG contrast rule requiring manual consideration. No uncaught browser errors or ERROR-level entries for the new frontend revision were observed at verification.

## Preserved configuration and boundaries

Backend `agentic-bi-backend-00021-6rd` and worker `agentic-bi-report-worker-00010-wnw` retained identical service specs, serving revisions and traffic. Both retain `DATA_PROFILE=timeseries`, `SOURCE_ROW_LIMIT=30000`, `REPORT_TIMESFM_ENABLED=true` and `REPORT_TIMESFM_VERIFIED=true`. Source connections and report configuration matched their before-release responses; Cloud Tasks mode and disabled Search remain unchanged.

This was a frontend image-only release. No analytical writes, data generation/upload, seeding, history/quota reset, IAM change or inference occurred. The larger source profile remains selected: 573,348 orders, 1,317,941 line items, 25,000 customers, 45 months and 1,369 days. The [prior source counts/fingerprints](timesfm-data-preservation.json) remain the dated numerical reconciliation; this release did not recount source rows.

New report generation, TimesFM inference/scenarios and Live voice were not rerun for this landing-only change; their actual hosted numerical/runtime results remain in the separately dated TimesFM assessment. Full screen-reader, Safari/Firefox and physical microphone/speaker checks were not repeated. These results describe the release-time observations, not continuous monitoring.
