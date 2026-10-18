# Workspace sidebar release — 18 October 2026

The deployed workspace now exposes connection/schema inspection through **Sources** in the header. The sidebar retains one **New exploration** action and removes the duplicate **Ask your data** section. This release changes only the frontend image.

## Deployment

- Serving revision: `agentic-bi-frontend-00018-kd4`, 100% traffic.
- Previous revision / rollback target: `agentic-bi-frontend-00017-dxz`.
- Build: `2196c5f3-f35f-456a-aab3-b063d361024a`, successful.
- Image digest: `sha256:cd256d3b15d406f3fe6c907ce45d4bb42866c79becc6e011838fa7c6533245bf`.
- Candidate readiness, landing page, runtime configuration and health were checked before promotion. The temporary `release-check` tag was removed afterward.
- Frontend runtime settings were preserved. Backend `00024-rnd` and private worker `00013-sm4`, including their configuration and traffic, are unchanged.

## Verification

Frontend tests (53), ESLint, TypeScript and the isolated local production build passed before release. Cloud Build also compiled the production image successfully. Hosted checks verified:

- Landing CTAs open `/app`; viewing the landing page generated no backend requests.
- One fresh-exploration button; no source cards in desktop/mobile navigation.
- At 1009×904, history has a 221px viewport and loads 100 public chats. Search and opening an existing daily-result conversation work.
- Saved charts reopen without a new analysis request. New exploration clears the selected chat URL.
- Sources shows both connected databases, five BigQuery tables and six PostgreSQL tables. Escape dismisses the panel and restores trigger focus.
- Mobile navigation at 390×844, full-width source panel at 320px, and a narrow active-chat header without overlapping actions or horizontal page overflow.
- All six library/settings routes return HTTP 200; legacy chat URLs retain their parameters through one HTTP 307.
- Backend live/readiness, frontend health/configuration and report configuration pass. Browser error output and new frontend revision error logs are empty.
- Scoped axe scan: zero violations, one incomplete contrast check. This does not certify screen-reader or complete application accessibility.

## Data and model preservation

A bounded, read-only BigQuery summary verified **573,348 orders**, **45 months**, **1 January 2023–30 September 2026**, and **$354,425,112.20** merchandise revenue. The summary ran before promotion; the subsequent configuration comparison confirmed both analytical services were untouched.

API and worker retain `DATA_PROFILE=timeseries`, `SOURCE_ROW_LIMIT=30000`, `REPORT_TIMESFM_ENABLED=true`, `REPORT_TIMESFM_VERIFIED=true` and `PLANNING_ENABLED=true`. The public report configuration also reports TimesFM enabled. No seed/upload, schema migration, analytical write, quota/history reset or IAM change occurred.

This is a frontend regression release. It starts no fresh AI analysis, voice session, report, scenario or hierarchical plan. Earlier prediction/voice evidence remains dated evidence; the fresh planning-generation quota gate recorded in [the previous feature assessment](planning-release-20261018.md) is unchanged. GitHub publication was not requested for this release.

Evidence: [source hashes](sidebar-release-20261018-source.json), [data summary](sidebar-release-20261018-data.json), [HTTP checks](sidebar-release-20261018-http.json), [routes](sidebar-release-20261018-routes.json), [configuration comparison](sidebar-release-20261018-configuration.json), [browser checks](sidebar-release-20261018-browser.json). Current runtime details are in [deployment.json](../deployment.json).
