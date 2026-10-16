# Querylane shared dashboards — implementation plan

Status: implementation present; local verification is recorded in docs/validation.md and docs/evaluation/dashboards*.json. Cloud Run deployment and GitHub publication remain separate requested actions.

## 1. Product decisions

Visitors can create named dashboards, pin saved analytics results into a chosen dashboard, open dashboards created by others, and remove cards from dashboards. Add **Dashboards** beside Skills and Settings on desktop and mobile.

**Confirmed:** pinned charts use saved results. Creating, pinning, viewing, arranging, and exploring a dashboard do not call Gemini or run source SQL. Data refresh is outside this release.

Use the existing public workspace model: all visitors can view and manage dashboards, including renaming, editing layout, unpinning, deleting, and restoring. Guest tokens attribute changes internally and enforce quotas; they are not verified identities or private ownership. Display “Public — anyone can view and edit” in the library, editor, and pin dialog.

Recommended first-release scope:

- Create, rename, describe, search, share, soft-delete, and restore dashboards.
- Pin a chart, KPI, or table from an existing text or voice answer.
- Choose an existing dashboard or create one inside the pin dialog.
- Capture the current chart presentation, including its selected scope.
- Arrange cards, choose standard/wide width, and give cards an optional display title/note.
- Unpin with Undo; preserve the underlying answer and other dashboards.
- Reuse chart exploration, full-screen view, exports, and query evidence.

Five dashboards are an example, not a fixed application limit. Proposed configurable demo defaults are 100 active dashboards, 20 active cards per dashboard, 50 mutations per guest/hour, and 300 workspace mutations/day. Soft-deleted dashboards/cards have a 30-day recovery window. Purging expired records is an explicit administrator maintenance action, not an application-start or deployment side effect.

Automatic refresh, scheduled queries, dashboard-wide filters, new calculations across cards, private dashboards, AI-generated layouts, freeform pixel layouts, and dashboard PDF/image export are deferred. Existing per-card PNG and full-result CSV exports remain available.

## 2. Visitor experience

### Dashboard library: `/dashboards`

Show cards containing dashboard name, description, chart count, last change time, source badges, and public visibility. Search names/descriptions and sort by recently updated or name. Use metadata-only previews; do not render every chart while browsing the library.

Provide **Create dashboard**, **Open**, **Rename/edit details**, **Copy link**, **Delete**, and a **Recently deleted** view with Restore. Empty state explains how to ask a question and pin the resulting chart. Handle loading, unavailable service, no search results, capacity limits, and concurrent edits explicitly.

Names are required, trimmed, and at most 80 characters. Descriptions are optional plain text up to 500 characters. Duplicate names are allowed; IDs and updated timestamps distinguish them. Do not use a name as a document identifier.

### Pin from a result

1. A saved result has a clearly labeled **Pin to dashboard** action beside the visualization selector. Distinguish this from selecting/pinning an individual observation inside the chart.
2. Clicking opens a searchable dashboard picker showing names and card counts.
3. The dialog summarizes the exact chart type, measure, selected date range/Top N, hidden series, and complete/partial status being saved.
4. Choose one dashboard, optionally change the card title, and confirm. Keep the picker open while creating a new dashboard inline, then pin to it.
5. Show a Sonner success message with **Open dashboard**. Failed requests preserve the choice and draft; offer Retry.

Inline creation and pinning are two explicit operations. If creation succeeds but pinning fails, retain the new empty dashboard and offer to retry the pin; do not create another dashboard or automatically delete one that another visitor may already be using.

One artifact may appear in several dashboards. Initially allow one card for the same artifact in a particular dashboard. A retry returns the existing pin; a different view of an already pinned artifact offers **Open card** or an explicit **Update saved view** action. Never silently overwrite the existing view or create duplicate cards after a lost response.

Only published saved artifacts are pinnable: their parent metadata exists and their declared result pages are readable. Source completeness is a separate property: partial source results can be pinned with a persistent Partial result warning. Unsaved/provisional results and clarification messages without an artifact cannot be pinned. Empty saved tables remain readable and can be pinned with an explicit empty-data state. A completed voice analysis can be pinned while the voice connection remains open; dashboard mutations do not acquire the conversation's analysis lease.

### Dashboard detail: `/dashboards/[id]`

Header: name, description, “Saved results — no automatic refresh,” public-editability notice, Share, Edit layout, and dashboard actions.

Use a responsive ordered grid: one column on narrow screens, two on wide screens, with a Wide card spanning both desktop columns. Chart labels and controls respond to each card's width. Provide **Move earlier/later** and a width selector in Edit layout; drag-and-drop is not required for release one. Preserve keyboard focus after movement and announce the new position.

Each card shows its title, selected scope, saved/query execution timestamps, recorded data profile, sources, completeness, and any inferred-join warning. Query timestamps are per source; do not imply that independently queried charts form a synchronized database snapshot. Never display a fabricated dashboard-wide total across unrelated cards.

Use a compact card toolbar, with full exploration controls in the expanded view. Inspecting, zooming, toggling series, or changing a chart type temporarily affects that visitor's view. Saving a changed default requires an explicit **Save card view** action in edit mode. Theme/accent, reduced motion, and density remain browser-local. The saved chart's analytical scope, visible measures, highlights, and number precision take precedence over browser chart defaults.

**Unpin** removes only that card. Offer Undo and a recently removed-card list within the dashboard. It does not delete the artifact, source answer, another dashboard's card, or source data. Dashboard deletion is recoverable and preserves its cards until an authorized purge after the recovery window.

Open original conversation when it still exists. If history was reset, explain that the original chat is unavailable while keeping the saved result, SQL, assumptions, and skill references inspectable. Do not display a nonfunctional Explore action or automatically start a new analysis.

## 3. Save data and presentation separately

The existing application already writes immutable artifacts and paginated result rows. Dashboard cards should reference those artifacts rather than copying rows, saving screenshots, or rerunning SQL. A chart remains interactive, and several dashboards can share one result.

Introduce a versioned `ChartViewState` with validated fields:

| Field | Meaning |
| --- | --- |
| `version` | Presentation contract version, initially 1 |
| `view` | Existing chart family, KPI, or table |
| `start`, `end` | Optional selected ISO date bounds |
| `primary` | Primary measure from the saved result |
| `visible_measures` | Explicit resolved series selection; at most the supported four measures |
| `order`, `top` | Existing category order and Top 5/10/20 choice |
| `scatter_x`, `scatter_y` | Valid numeric fields for scatter only |
| `highlights` | Captured highlight preference |
| `decimals` | Existing supported precision: 0, 1, or 2 |

Resolve comparison visibility into the visible-measure list. Validate all references against actual columns and normalized visualization metadata, including units, composition eligibility, and supported chart types. Do not accept SQL, expressions, HTML, styles, or arbitrary chart configuration. Normalize values before persistence and discard transient pointer/hover/selected-observation state.

Lift the currently split view state in `ResultCard` and `InsightfulChart` into a shared presentation module with an explicit initial state and change callback. Conversation results initialize from existing preferences; dashboard cards initialize from persisted state. Before pinning, flush a pending brush update and wait for the requested presentation to finish loading, so the saved view matches the dialog preview. If it cannot render faithfully, explain the limitation and offer a valid table view explicitly.

The existing chart-data and CSV interfaces remain the source of presentation data and downloads. They keep all current completeness, full-result calculation, sampling, row/byte, composition, and CSV protections. Pinning never converts a partial result into a complete one. Loading a dashboard never substitutes a fixture, refreshes an artifact, or rewrites historical visualization metadata.

## 4. Storage and mutation contracts

Keep all application storage backend-only in the existing named Firestore database `agentic-bi-demo`.

| Document path | Responsibility |
| --- | --- |
| `dashboards/{id}` | Name, description, revision, ordered active item IDs, active card count, public visibility, timestamps, deletion state, internal guest attribution |
| `dashboards/{id}/items/{item_id}` | Immutable artifact reference, source conversation/message links when known, validated saved view, display title/note, standard/wide width, timestamps and removal state |
| `dashboard_artifact_refs/{artifact_id}` | Retained card-reference count protecting this artifact and its pages |
| `dashboard_requests/{request_id_hash}` | Payload hash and idempotent operation result; bounded expiry/maintenance retention |
| Existing `quotas` / `system` | Transactional dashboard mutation quotas and workspace capacity |

Use deterministic item identity from dashboard + artifact for the initial one-artifact-per-dashboard rule. Keep layout order only in the parent; reorder requests must contain each active item exactly once. No result rows or full SQL payload belong in dashboard metadata documents.

Every mutation atomically checks `expected_revision`, validates state/capacity, changes the parent/card/ref records as necessary, and charges successful non-no-op edits once. All operations use stable client request IDs. Exact replay returns its original outcome; reuse with a different payload is a conflict. Do not replay an earlier successful pin by creating another item after the user subsequently unpins it.

A new, deliberate pin request may restore a previously removed item and apply its reviewed view. Restoring a retained tombstone does not increment its artifact-reference count twice. Distinguish this new intent from replaying the original request. Keep idempotency records for at least the guest-session lifetime and document the retry window; purging them is an explicit bounded maintenance policy.

On concurrent edits return `409 dashboard_conflict`. Preserve the visitor's local draft and show Reload latest; do not retry an overwrite silently. A capacity change, removed dashboard, or missing artifact has its own actionable error. Undo restores one item with current validation, not an entire obsolete dashboard snapshot; a full dashboard cannot evict another visitor's chart to restore it.

Use bounded retry behavior from the existing storage abstraction. Anonymous attribution is omitted from public responses. Metadata lists omit chart rows, raw guest tokens, and credentials. Start with bounded metadata search matching the Skills pattern; determine any query/index requirements from the final queries during implementation rather than promising an index-free design.

## 5. Artifact retention and administrative reset

This is a required part of implementation. Today `app.admin.reset()` recursively deletes **all** artifacts. Adding dashboard references without changing it would break every pinned chart on the next reset.

- A successful pin establishes a retained reference in the same transaction as the card.
- Unpinning or soft-deleting a dashboard keeps retained references during recovery. Undo therefore cannot reference a newly deleted result.
- An explicit purge releases references transactionally after the recovery window. Never delete an artifact that another active/recoverable card still uses.
- Change history reset to preserve dashboard records, item records, retained artifact metadata/pages, existing Skills/revisions, and capacity records. Unreferenced history can follow the documented reset behavior.
- Fence reset/purge using a shared maintenance state checked by new analysis and dashboard mutations. Enter maintenance, drain bounded in-flight work, inspect a stable retained-reference set, perform the reset, and clear maintenance with operator recovery instructions if it fails. A pin racing a reset must not succeed with a dangling reference.
- A retained artifact is self-contained numerical/query evidence even if its source conversation/run is removed. Store optional `analysis_id`, `run_id`, and actual analysis question on newly created artifacts, for text and each voice invocation. Older artifacts remain supported; missing question/link context is labeled unavailable rather than guessed.
- Treat any future artifact garbage collector as reference-aware. Do not add an implicit cleanup job or change source data as part of this feature.

## 6. Proposed HTTP interfaces

Public reads; authenticated mutations use existing guest tokens. All paths have the existing `/api/v1` prefix. Mutations include a request ID and revision check where applicable.

| Interface | Purpose |
| --- | --- |
| `GET /dashboards` | Bounded public metadata list; active/recently deleted, search/sort |
| `POST /dashboards` | Idempotently create a dashboard |
| `GET /dashboards/{id}` | Dashboard metadata and ordered card summaries, no bulk row loading |
| `PATCH /dashboards/{id}` | Rename/edit description |
| `DELETE /dashboards/{id}` | Soft-delete with a revision check |
| `POST /dashboards/{id}/restore` | Restore a recoverable dashboard |
| `POST /dashboards/{id}/items` | Pin an artifact and validated view |
| `PATCH /dashboards/{id}/items/{item_id}` | Explicitly change display metadata, width, or saved view |
| `DELETE /dashboards/{id}/items/{item_id}` | Unpin without deleting its artifact |
| `POST /dashboards/{id}/items/{item_id}/restore` | Undo/recover an unpinned card |
| `GET /dashboards/{id}/items?removed=true` | Paginated recoverable cards |
| `PUT /dashboards/{id}/layout` | Atomically reorder the active item IDs |

Reuse `GET /artifacts/{id}`, saved pages, chart-data, and export.csv. Add a metadata-only artifact read or equivalent projection for dashboard rendering, so opening a 20-card dashboard does not download 20 previews of 1,000 rows before charts become visible.

The Dashboards module owns validation, quotas, revisions, idempotency, layout, and retention coordination behind this interface. Reuse the same MemoryStore/FirestoreStore adapters so concurrency and failure cases can be tested locally. Do not add dashboard tools to ADK or give the model write access.

## 7. Performance, freshness, and feedback

- Render library summaries without Recharts instances. Dynamically load visible dashboard charts with a bounded queue; start with two concurrent card presentations and abort obsolete requests on navigation.
- Reuse duplicate in-flight reads of the same immutable artifact/view. Preserve existing backend materialization limits: 50,000 saved rows / 64 MiB / 1,024 pages, two concurrent materializations per instance, and 2,000 plotted observations.
- A failure affects its card, with Retry and evidence access; other cards remain usable. Missing artifact/pages produce a visible unavailable state, never invented or silently truncated data.
- Refresh shared dashboard metadata on navigation/window focus and through a visible Reload action. When another visitor edits a board, show a newer-version notice; do not replace an unsaved layout or card draft. A metadata reload does not refresh source data.
- Toast useful outcomes: create, pin, already pinned, view saved, copied link, unpin with Undo, dashboard delete/restore, conflict, quota, and failure. Do not toast hover, routine card loading, or every local range change.
- Use existing theme tokens, shadcn primitives, Motion/reduced-motion behavior, chart annotations, units, and semantic table alternatives. Provide labeled controls, predictable dialog focus, keyboard move actions, and touch-friendly targets. Announce saved/moved/removed states without moving focus unexpectedly.

## 8. Delivery sequence

| Phase | Work | Completion gate |
| --- | --- | --- |
| 1. Domain/storage | Typed dashboard/item/view contracts, transactional CRUD, quotas, idempotency, conflict handling, retained references | Duplicate retries and simultaneous edits are safe in both storage adapters |
| 2. Library | Navigation, `/dashboards`, create/edit/share, metadata search, delete/restore and public notices | A second browser can find and manage the same dashboards |
| 3. Pinning | Extract shared chart state, result-card pin dialog, inline dashboard creation, saved-view capture, text/voice artifact support | A selected chart appears in the chosen dashboard with identical data/scope and no query/model call |
| 4. Dashboard experience | Lazy card grid, standard/wide layout, keyboard reorder, view-save, unpin/recovery, per-card exports/evidence | Changes persist on reload; removing a card leaves source/other dashboards intact |
| 5. Lifecycle and verification | Fenced reset/purge, backwards compatibility, numerical/accessibility/browser verification, documentation | Pinned evidence survives a history reset; all release checks pass |

Implement lifecycle contracts in phase 1 even though their operator workflow is completed in phase 5. Do not expose a partially implemented pin feature that can lose artifacts during reset. Plan roughly 7–10 working days for a verified demo release, revising the estimate after the shared-renderer/retention spike.

Likely files:

- `Backend/app/dashboards.py`: module and router; dashboard model declarations may be colocated or in a focused contracts file.
- `Backend/app/main.py`, `analysis.py`, `admin.py`, `config.py`, and a narrowly scoped maintenance/retention module.
- `Frontend/src/app/dashboards/page.tsx`, `dashboards/[id]/page.tsx`, dashboard library/detail/card and pin-dialog components.
- Shared chart presentation state/types, `result-card.tsx`, `charts/insightful-chart.tsx`, API helpers, and navigation in workspace, Skills, and Settings.
- Backend dashboard/retention/concurrency tests and frontend view-state/pin/reorder tests.

## 9. Acceptance and release preparation

Verify the complete visitor journey with five named dashboards and several results. Pin a monthly trend, daily series, cross-source segment bar, KPI, and table; pin one artifact to two boards; unpin it from one and verify the other and original chat are unchanged.

Required checks:

- All 45 months / 1,369 days and saved-source totals match independent fixtures; zero values, sampling, partial results, mixed units, and historical metadata remain correctly labeled.
- Chart type, selected scope, Top N/order, visible measures, scatter axes, highlights, and precision survive pin/reload. Browser defaults do not override a saved dashboard view.
- Pin/open/reorder/unpin perform zero source connector query calls and zero Gemini calls, in text and voice-result paths.
- Expired guest tokens, invalid IDs/configuration, unavailable artifacts/pages, capacity/quotas, and stale edits fail clearly.
- Repeated/lost-response requests do not duplicate dashboards/cards, charge quotas twice, or resurrect an intentionally removed item.
- Concurrent pin/unpin/reorder/delete/restore and reset/purge races preserve order, capacities, reference counts, and evidence. Test Undo when the board is full or another visitor changed it.
- Soft-delete/recovery and an actual isolated history reset preserve pinned pages/SQL/skill evidence. Unpinned unreferenced data follows the documented cleanup behavior.
- Restarting/scaling preserves dashboards; a second anonymous browser sees the same saved content.
- Desktop/narrow mobile, every accent, light/dark, reduced motion, keyboard-only controls, focus restoration, and axe checks pass. Screen-reader review is a separate explicit check.
- A full dashboard loads only visible chart data within the concurrency limits; one failed card cannot fail the whole board.
- Existing backend tests plus frontend tests, lint, types, production build, and browser verification pass.

Document use and decisions in README, `docs/dashboards.md`, architecture, CONTEXT.md (Dashboard, Dashboard Item, Saved Chart View, Retained Artifact), validation reports, and the deployment guide. Record the saved-result and shared-editability tradeoffs in a short ADR.

No new analytical database tables, source uploads, Gemini models, browser Firestore access, or runtime IAM grants are expected. Verify final Firestore query/index needs before release. For a separately requested deployment, follow the primary deployment guide, deploy backward-compatible backend changes before frontend, and preserve `--data-profile timeseries`. New additive dashboard documents and retained artifacts remain intact during rollback; use a compatible reference-aware history-reset command after rollback.
