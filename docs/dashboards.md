# Shared dashboards

Dashboards collect saved analytical results. Every visitor can create, view, rename, arrange, delete, and restore them without signing in. The interface states **Public — anyone can view and edit**. Guest tokens enforce edit limits and attribute changes internally; no identity or ownership is claimed. Do not enter confidential information.

## Create and pin

Open **Dashboards** from the workspace, Skills, or Settings. Create a named dashboard with an optional description. Names are trimmed, required, and limited to 80 characters; descriptions allow 500. Duplicate names are supported.

Ask the analyst a question through text or voice. On a saved chart, KPI, or table choose **Pin to dashboard**, select a destination, review its scope and completeness, and confirm. The picker can create a dashboard inline. Creation and pinning are distinct requests: if the second fails, the empty dashboard remains available for Retry.

A result can belong to several dashboards, with one card per artifact within each dashboard. Retrying does not duplicate it. An already-pinned result links to the dashboard, where Edit layout & cards → Save card view explicitly changes its presentation. A new deliberate pin after removal restores the card; replaying the old pin request does not resurrect it.

## Saved views and exploration

Pinning records chart family, date range, primary/visible measures, category order/Top N, scatter axes, highlights, and number precision. Source evidence and data stay in the original immutable artifact. Creating/pinning/viewing/arranging/unpinning runs **no source SQL or Gemini request**.

The card uses saved analytical defaults even when a visitor's browser prefers a different chart type or comparison visibility. Theme, accent, density and reduced motion stay local. Compact cards expose exact values, series controls, exports and Expand; expanded charts expose the complete range/axis controls. Temporary exploration changes only the local view. Save card view in edit mode publishes a new default; editing card details can change its title, note, width, highlight default and precision.

Card widths are Standard or Wide, with a single column on mobile. Use Earlier/Later for keyboard-accessible arrangement; order changes save immediately and announce position. Each card retains original query timestamps, source profile, completeness and join assumptions. A dashboard is not a synchronized database snapshot and does not combine unrelated card totals.

Each saved-result section has a theme-aware outline, rounded corners and responsive internal padding. The outline groups its context, notes, chart or table, skills and source evidence together; a separate top rule distinguishes the source footer. Consistent grid gaps separate neighboring sections, and the nested chat-result frame is flattened to avoid doubled borders and padding. These dashboard-only styles preserve the existing Standard/Wide layout, chart controls and saved evidence. Downloads continue using their existing saved-view renderer.

PNG exports describe the current chart view; CSV exports the full saved result regardless of the displayed range or sampling. Existing limits, numerical rules and formula protection apply. Tables retain semantic headers and keyboard-scrollable overflow. A failed card has its own Retry state.

## Shared edits and recovery

Rename, layout, card edits, deletion and restoration check the current dashboard revision. A stale save returns `409 dashboard_conflict` and preserves the draft. Reload latest explicitly; another visitor's edit never silently replaces an open draft. Exact mutation retries reuse request IDs and do not charge quota twice. Unchanged saves do not increment the revision or consume mutation quota.

Unpin removes the card only. Undo and Recently removed cards restore it within the recovery window, subject to available capacity. The source answer and copies on other boards remain intact. Dashboard deletion is soft; Recently deleted can restore its cards. Recovery defaults to 30 days. The configured limits default to 100 active dashboards, 20 cards per dashboard, 50 changes per guest/hour and 300 workspace changes/day (`DASHBOARD_*` in the backend environment example).

All reads use FastAPI; there is no browser Firestore access. The bounded library reads metadata, not result pages. Visible cards load through a shared two-request queue with deduplication and subscriber-aware cancellation. Metadata refreshes on focus/navigation and through Reload latest; it never refreshes source data. A newer shared revision is announced without overwriting the current view.

## Retention and operator maintenance

`dashboard_artifact_refs` counts active and recoverable card references. Soft deletion keeps the count until an explicitly authorized purge. History reset preserves dashboards, retained artifact metadata/pages, Skills/revisions and capacity records while deleting unreferenced chat history. The card's original conversation may disappear, but data/SQL/assumptions/skill evidence and any recorded question remain available.

Follow [the deployment guide](deployment-guide.md) before operator actions. `reset-history`, `purge-dashboards` and `clear-maintenance` have no HTTP endpoint. Reset/purge acquire a shared maintenance fence and drain in-flight analytics/author leases. New analysis and dashboard writes receive a maintenance response until completion. A failed command deliberately leaves the fence active; stop/inspect the old operator process, fix the issue, then use the explicit recovery command before retrying. Never clear it while a previous maintenance process could still be deleting documents.

Firestore scans use separate cursor-paginated RPCs, so deletion of a cursor document does not skip the next page or keep a stream open across slow deletions. Recently deleted/removed queries filter and order on `recover_until`, using its standard single-field index; active dashboard discovery uses the single `deleted` equality filter and metadata projection. There is no new composite-index requirement for these queries under normal Standard-edition indexing.

## Interfaces and evidence

See [the implementation plan](dashboard-plan.md) for the full route table and [ADR 0005](adr/0005-saved-result-dashboards.md) for the main decisions. Mutation bodies include `request_id` and, except creation, `expected_revision`. DELETE supplies them as query parameters. Exact request IDs are retained for 24 hours; cleanup of expired records is explicit.

New artifacts record the actual question, run and analysis IDs. Historical artifacts remain readable without these fields. No public connection/credential management, automatic refresh, arbitrary chart expressions, agent write tools, or source-data mutation is added.

This feature is deployed to Cloud Run; see [hosted validation](validation.md#dashboard-library-cloud-release--2026-10-16) and [the release record](deployment.json). Preserve the larger `timeseries` profile on future releases. Local emulator tests use a demo project and `(default)` because the emulator does not support multiple named databases; hosted verification also exercises the existing named `agentic-bi-demo` database under its restricted backend identity. Deployment does not seed dashboards, reset history, or upload analytical data.

## View, edit, share and whole-dashboard downloads

Each active library card has **View**, **Edit**, **Share**, and **Download** actions. View opens an exploration-focused dashboard; Edit opens `?mode=edit`, exposing dashboard details, card titles/notes, saved views, ordering, widths, unpinning and recovery. **View dashboard** returns to view mode. Mode is a local interface choice, not an access restriction: dashboards remain public and everyone can enter edit mode. Existing transactional revision checks continue to protect shared edits.

Share opens a dialog with the canonical public dashboard link, Copy link, and native device sharing where supported. A denied/unavailable clipboard selects the visible link for manual copying. Links omit edit mode, open the latest published dashboard, and do not freeze a revision or create private access.

Download is available in both the library and the open dashboard:

| Format | Contents |
| --- | --- |
| PNG / JPEG | Print-friendly light overview of all saved cards, in published order and widths, with scope/completeness notes |
| PDF | Paginated saved cards, chart legends/units, table previews, source timestamps and caveats |
| CSV data ZIP | All original saved rows/columns per artifact, plus a dashboard/provenance/checksum manifest |
| JSON snapshot | Dashboard layout, saved views, revision and evidence metadata; no data rows or import/restore operation |

Exports use **published saved views**, including cards not yet scrolled into view. Unsaved edits and temporary chart exploration are excluded. The dialog captures the current dashboard revision and rejects a stale download rather than combining revisions. Source artifacts are immutable; no SQL or model calls run. CSVs include the complete saved result regardless of image date filters, Top N or downsampling. Partial source results remain labeled partial. Spreadsheet formulas in textual cells are escaped.

Static charts use the existing headless Matplotlib/report export stack and conservative light styling, rather than a screen capture. Mixed units are separated, comparator/prediction lines use dashes, date scopes and visible series are retained, and prediction caveats include cutoffs and available interval coverage. PDF/image tables preview up to 20 rows and 8 columns; long cells may be shortened. CSV ZIP retains all saved data. PNG/JPEG is an image; PDF titles, notes, KPI values and table previews are selectable; charts are rasterized. PDF/UA conformance is not claimed.

`GET /api/v1/dashboards/{id}/downloads/{png,jpeg,pdf,data,json}?expected_revision=N` reads only saved backend evidence. It requires no new storage, IAM or dependencies. Each backend instance prepares one dashboard export at a time, rejecting competing preparations with a retryable busy error. Input is bounded to 200,000 distinct saved rows / 32 MiB combined, with a 60-second evidence-load deadline and an isolated renderer capped at 45 seconds. PNG/JPEG is bounded to 24 megapixels; overly large images should use PDF or individual card downloads. Missing pages, deleted dashboards and concurrent snapshot edits fail explicitly; the service never returns a successful truncated export. No export files or dashboard revisions are persisted by downloading.

This addition is deployed to Cloud Run. See [hosted validation](validation.md#dashboard-actions-cloud-release--2026-10-17), [API evidence](evaluation/dashboard-actions-deployed-api.json), and [the release record](deployment.json). Future releases must follow the deployment guide, deploy the backend before the frontend download controls, and preserve the larger `timeseries` data profile.

## Nearby dashboard card code — local correction

[The loading investigation](evaluation/loading-contention-local-20261023.md) adds parallel code/saved-metadata loading after viewport admission and synchronous use of the ready result-card component, with the existing dynamic fallback retained. App/evidence links use the shared click-only AppLink policy. Saved parameters, full-row evidence, exported bytes and revision controls are unchanged. Off-screen evidence is not fetched merely to warm code. The [hosted release](evaluation/loading-contention-release-20261023.md) verifies desktop/mobile scheduling and unchanged exports/settings; the historical 4.52s cause remains unproven.
