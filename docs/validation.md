# Validation and remaining deployment gates

Latest release validation: 2026-10-16. Earlier sections retain dated baseline evidence. Results distinguish local integration from deployed acceptance.

## Automated checks

The current suite includes the deployed skills library/animation release and the new locally implemented conversational voice author. The voice-author feature has not been deployed. Original evaluation files below remain dated baseline records; the latest hosted-source results are linked in the release section.

| Check | Result | Scope |
| --- | --- | --- |
| Backend pytest | 138 passed | Existing controls plus skill CRUD/revisions, edit conflicts/quotas, import validation, selection/snapshots, repair reuse, forks, and repeated voice analysis |
| Ruff | Passed | Backend application, tests, smoke scripts |
| Frontend ESLint / TypeScript | Passed | Application and generated components |
| Next.js production build | Passed | Standalone configuration, application routes, runtime configuration |
| Deterministic evaluation | 31/31 passed | Synthetic retail sources, independently calculated Python references |
| Real Gemini evaluation | 31/31 passed | `gemini-3.8-flash` generates SQL against the same synthetic sources; numeric assertions use independent references |
| Hosted numerical evaluation | 31/31 passed | Public deployed API over real BigQuery/PostgreSQL; all cases used vector retrieval |
| Deployed acceptance | 16/16 passed | Health, CORS, source evidence, follow-ups, forks, idempotency, voice handshake, live tool/audio/transcript |
| Runtime identity / persistence | 16/16 passed | Existing-resource denial, SELECT-only role, independent Firestore clients, atomic status, stale object rejection |
| Model compatibility | Passed | Text generation, 768-dimensional `gemini-embedding-001`, live model connection |
| Real live integration | Passed | Live transport → ADK tool → analysis → artifact + audio + transcript + completed turn |
| Frontend/backend HTTP | Passed locally | Production frontend `/api/health` reaches backend, runtime API configuration |
| Automated accessibility | Zero reported axe violations | Welcome and populated workspace; manual screen reader coverage remains separate |
| Responsive layout | Passed locally | 390×844 mobile viewport has no horizontal page overflow; desktop workspace inspected |
| Production dependency audit | Zero reported vulnerabilities | `npm audit --omit=dev` |

The final real-model evaluation includes one bounded retry for transient model transport failures. The first run's 29/31 outcome and targeted recheck remain in `evaluation/gemini-initial.json` and `evaluation/gemini-recheck.json`; they are not substituted for the final full run. The application retains the requested model identifiers rather than silently selecting another model.

The full npm audit also reports unresolved high-severity `braces` advisories through development tooling. `braces@3.0.3` was the available registry release at verification. The shadcn CLI is a development dependency; these packages are excluded from the final standalone runtime. Recheck tooling advisories before competition delivery. Pytest reports one upstream Starlette/httpx deprecation warning.

## Reproducible evidence

- `evaluation/fixture.json`: 31 deterministic cases.
- `evaluation/gemini.json`: full passing 31-case real-model run over fixtures.
- `evaluation/deployed-31.json`: full passing 31-case hosted-source run, with vector retrieval in every case.
- `evaluation/deployed.json`: deployed public API and live voice acceptance.
- `evaluation/cloud-runtime.json`: attached runtime identity and real Firestore checks.
- `deployment.json`: service URLs, images, identities, and serving revisions.
- `evaluation/vector-retrieval.json`: browser-submitted hosted question using the ready vector index.
- `evaluation/live-smoke.json`: live integration observations and explicit hardware limitation.
- `evaluation/accessibility.json`: populated-workspace axe report, with zero violations and an incomplete contrast check.
- Browser review also confirmed a real Gemini cross-source question, a September follow-up ($13,410 actual versus $17,600 target), and table switching over the same artifact.
- Backend tests: `pytest -q` from `Backend/`.
- UI checks: `npm run lint`, `npx tsc --noEmit`, `npm run build` from `Frontend/`.
- Real voice smoke: `uv run python -m scripts.smoke_voice` from `Backend/` (opt-in billed model access).

The original fixture and Gemini reports use local synthetic sources. Separate deployed reports exercise the seeded hosted sources and real named Firestore; see the cloud verification section below.

## Cloud deployment and identity checks

The explicitly approved IAM grants were applied on 2026-10-15. Both public Cloud Run services are deployed in `asia-southeast1`, using the dedicated frontend and backend identities. Firestore `agentic-bi-demo`, BigQuery `agentic_bi_demo`, Cloud SQL `agentic-bi-demo-pg`, demo secrets, and the source/image build resources are configured. Both hosted sources contain the deterministic seed. The 768-dimensional vector index is ready, and a hosted browser question was verified to use `gemini-embedding + full-schema` retrieval.

`evaluation/deployed.json` records passing health, runtime configuration, CORS, hosted numerical answers, follow-ups, fork context, query evidence, denied voice origins/tokens, and live audio/transcript/tool results. `evaluation/cloud-runtime.json` records real named-Firestore concurrency and ADK persistence checks, a rejected stale object write, restricted PostgreSQL reader privileges, and denied access to all pre-existing Firestore databases and enterprise BigQuery datasets. Existing-resource checks requested only metadata/read-only transaction setup, never business documents or table rows. The temporary private check job is removed after verification.

Cloud verification found and corrected two concurrency issues: revisions must belong to individual loaded session objects, and run/lease completion status must be read atomically. Regression tests cover both. The initial hosted 31-case evaluation retained correct numbers in the affected case but reported a false interruption; it is preserved separately in `evaluation/deployed-31-initial.json`. The final stable-revision run passes all 31 cases and uses vector retrieval throughout. A contention probe returned an unexpected loser response once; a diagnostic rerun and four targeted repetitions all produced exactly one winner and one `conversation_busy` response. No probe produced two committed turns or corrupted conversation state.

The scoped resources are active and billable. Request/scan/instance limits are configured. Billing alerts require a billing administrator and do not constitute a spending cap.

## Remaining manual competition checks

1. Exercise a real microphone and speaker across at least ten representative scenarios, including interruption, mute, reconnect, microphone denial, and source failure recovery. Automated live checks inject text into the live transport and do not prove microphone hardware operation.
2. Complete the manual keyboard/screen reader review. Automated axe checks cover the populated deployed workspace with zero reported violations, but include an incomplete contrast check.
3. Rehearse the five-minute script and prepare the backup recording using the deployed application.
4. Configure the desired billing alert recipients and thresholds with the billing administrator.

## Local review modes

The standard local command uses deterministic planning and in-memory synthetic sources. `app.cloud_preview` uses real Gemini with the same synthetic sources and memory history, and is labeled accordingly in the interface. Its operator token remains in memory and expires; restart the preview to refresh it. This local-only entry point must not be used for Cloud Run deployment.

## Browser settings verification

The settings implementation was verified locally and deployed on 2026-10-15. Frontend revision `agentic-bi-frontend-00002-zhq` serves 100% of traffic; backend revision `agentic-bi-backend-00005-rqk` and its configuration are unchanged. See [settings reference](settings.md), [local results](evaluation/settings.json), and [deployed release checks](evaluation/settings-deployed.json).

Frontend lint, TypeScript, production build, and three voice preference regression tests pass. Browser checks cover reload persistence, cross-tab updates, system theme changes, explicit theme overrides, new versus existing conversation sources, composer shortcuts, numeric formatting, manual chart switching, unsupported-view fallback, reset preservation, malformed storage, and blocked-storage recovery. Mobile checks at 320px and 390px found no horizontal document overflow.

Stable light and dark settings screens and populated table/chart views report zero axe violations. The settings scans have no incomplete rules; SVG chart contrast remains an automated-review limitation. Axis and legend text use semantic foreground colors, and primary text/background contrast exceeds 5.3:1 in every accent and mode combination. Voice preference tests use mocked microphone and audio APIs; they do not replace the real-hardware voice acceptance checks above.

The deployed release passes seven HTTP checks covering both services, runtime API configuration, connected analytical sources, the settings page, and the workspace. Real-browser checks confirm theme/density/chart/composer/voice preference persistence, mobile layout, an existing cross-source conversation, manual chart switching, and reset controls. Both deployed settings color modes report zero axe violations; the inspected new-revision logs contain no errors. This frontend-only verification required no new model calls or public conversations. The build uses source commit `2fade7a`; the previous frontend revision `agentic-bi-frontend-00001-6tf` remains recorded for rollback.

## Motion and notification verification

The [motion and feedback update](motion-and-feedback.md) was verified locally and released to Cloud Run on 2026-10-16. [Its evaluation record](evaluation/motion-and-feedback.json) separates real local retail results from isolated analysis-event and synthetic voice-transport fixtures. Frontend lint, TypeScript, production build, and the existing three voice tests pass; the production dependency audit reports zero vulnerabilities.

Browser checks cover beUI keyboard interaction, toast deduplication and dismissal, success/error/confirmed-cancellation lifecycles, voice permission recovery, microphone/session feedback, application/device reduced motion, reader-aware scrolling, and mobile layout. The real local total remains $118,951, and the monthly follow-up retains nine result rows. All recorded accessibility scans have zero reported violations; SVG/animated color-contrast checks include incomplete rules. Synthetic audio verifies static reduced-motion voice meters while connected; real microphone hardware remains a separate acceptance check.

## Skills library verification

The skills library was verified locally, pushed to GitHub, and deployed to Cloud Run on 2026-10-16. The following paragraphs describe the original local checks; hosted evidence is recorded in the release section. See the [skills reference](skills.md), [local verification](evaluation/skills-library.json), and [real Gemini evidence](evaluation/skills-gemini.json).

The original skills implementation passed **112 backend tests** (the release suite now passes 120), including CRUD/revisions, concurrent edits, transactional quotas/capacity, import validation, metadata-only selection, failure/no-match behavior, manual priority, unavailable attachments, forks, immutable repair/replay snapshots, numerical fixtures, and repeated voice-tool analysis. Ruff passes for application, tests, and scripts. The existing Starlette/httpx deprecation warning remains.

Frontend lint, TypeScript, all three voice-preference tests, and production build pass. Production dependency audit reports zero vulnerabilities. Next.js compilation/runtime checks pass after correcting a reduced-motion hydration mismatch in the shared hook. Browser verification covers publication, editing, preview/export/import, stale-edit recovery without draft loss, discard/keep-editing, deletion with Undo offered, Recently deleted restoration, enabling/disabling, manual chat attachment, answer-version links, and unavailable-attachment removal.

One real Gemini analysis using `gemini-3.8-flash` against synthetic fixture sources selected the relevant revenue skill automatically, excluded a PostgreSQL-only skill, generated a guarded query, and returned **$118,951.00**, matching the independent expected total. Its answer retained the selected revision and reporting assumptions. This uses memory storage; it does not replace deployed persistence verification or the earlier 31-case evaluation.

Six axe scans (desktop library, dark editor, populated workspace, immutable version, mobile light library, mobile light editor) report **zero violations**. Modal scans retain an incomplete Radix focus-guard check; the chart has an incomplete contrast check. Keyboard focus remained in the editor. At 390px the library has no horizontal overflow, and OS reduced motion produces static entrance transforms. A Markdown preview test rendered zero unsafe nodes, executed no injected script, and made zero remote-image requests. Import/cancel did not publish the file.

The named demo database was inspected read-only and confirmed as Standard edition / Native mode in `asia-southeast1`. No cloud resources, IAM grants, secrets, or indexes were created. The release followed the [skills release steps](deployment-guide.md#skills-library-release), deployed backend before frontend, and verified Firestore history across a new backend revision. Real Gemini Live skill analysis is now covered by hosted checks; microphone hardware scenarios and manual screen-reader review remain separate acceptance gates.

## Skills and animation cloud release — 2026-10-16

The shared skills library, Framer Motion/beUI animations, and Sonner feedback are released to the existing two Cloud Run services. [deployment.json](deployment.json) records the serving revisions, images, source commits, builds, and rollback predecessors. Existing identities, secret references, runtime limits, origins, and resource configuration were preserved. No analytical data or shared history was reset, and no example skills were seeded.

- **120 backend tests** and Ruff pass. Eight release regressions cover read-phase Firestore contention, bounded retry/error translation, and terminal event-stream draining for success/failure/cancellation.
- Frontend ESLint, TypeScript, all three voice-preference tests, and the production build pass. A sandbox port-binding failure was resolved by clearing generated production caches and rebuilding outside the sandbox; the final Cloud Build also compiles the release.
- [Hosted numerical evaluation](evaluation/skills-deployed-31.json): **31/31** pass against independent seed fixtures on backend `00007-z4d`. The first release run also passed and is preserved in `skills-deployed-31-initial.json`.
- [Hosted skills checks](evaluation/skills-deployed.json): **22/22** pass, including real named-Firestore CRUD, stale-edit rejection, import/export, automatic/manual selection, follow-ups, forks, historical revision links, and skill/answer persistence from backend `00006-zwn` to `00007-z4d`. Gemini Live produced audio, transcripts, and a skill-guided result of **$118,951**, independently checked by value because its generated column alias differed from the prompt. The temporary verification playbook was soft-deleted; immutable versions remain readable.
- [Runtime checks](evaluation/cloud-runtime.json): **16/16** pass on `00007-z4d`, including independent-client persistence and one conversation winner with a `conversation_busy` loser. The temporary private verification job was removed.
- [Final smoke checks](evaluation/skills-release-smoke.json): **16/16** pass on backend `00008-854`; they cover health, frontend/backend configuration, CORS, hosted numerical results, follow-ups, forks, idempotency, query/join evidence, voice origin/token rejection, and real Gemini Live tool/audio/transcript events.
- [Final HTTP/configuration checks](evaluation/skills-release-final.json): **11/11** routes pass on frontend `00004-7gh` and backend `00008-854`; both serve 100% traffic with their pre-release runtime contracts preserved.
- [Deployed browser checks](evaluation/skills-release-browser.json) cover public visibility, historical skill links, beUI themes and reload persistence, toast deduplication/header offsets, hover motion, reduced motion, mobile layout, and axe accessibility.

Cloud verification caught two timing issues. The initial runtime probe returned a raw Firestore read-phase abort for the losing writer; fresh bounded transaction retries now let it observe the winner. The subsequent smoke probe found a saved answer whose stream closed before delivering the final event; the stream now drains through the committed run sequence before closing. The failing observations remain in `cloud-runtime-initial-skills.json` and `skills-release-smoke-intermediate.json`, alongside passing rechecks and deterministic regressions. A mobile loading-state accessibility finding was corrected by giving the labeled loading container a status role; the final deployed loading DOM and both final mobile axe scans pass. All recorded stable-page axe scans in this release have zero violations.

The final backend log inspection recorded a `WebSocketDisconnect(1006)` traceback during a late close after the invalid-token client disconnected. Token rejection and valid live audio/tool/transcript checks pass. Suppressing this already-disconnected close-path noise is a maintenance follow-up, not a failed analysis.

The final event-stream change does not alter SQL generation or query controls. The 31-case and skills-specific reports retain their actual tested backend revisions; the final smoke report tests the subsequent stream fix. Live transport tests inject text and do not prove microphone hardware behavior. Manual screen-reader checks, real-microphone scenarios, and the competition rehearsal remain as listed above.

## Conversational voice skill author — 2026-10-16

Implemented locally; **not deployed to Cloud Run or pushed to GitHub as part of this feature**. The [detailed plan](voice-skill-author-plan.md), [usage guide](skills.md#conversational-voice-author), and [evaluation](evaluation/voice-skill-author.json) describe the new author flow and operational limits. The existing deployed application and five retail playbooks are unchanged.

- **138 backend tests** and Ruff pass. New coverage includes guest ownership, idempotent creation/quotas, required interview fields, draft invalidation, immutable reviewed publication, retry behavior, capacity/quota rejection, competing edit/publish, author/ADK lease fencing, expiry, UTF-8/transcript/turn/tool budgets, handshake/origin validation, a streamed draft, and scoped administrator cleanup.
- Frontend lint, TypeScript, **eight voice transport/preference tests**, and the standalone production build pass. Transport tests cover the author endpoint, typing without microphone permission, microphone denial, late permission after cancellation, graceful pause/final-state delivery, playback interruption, and existing preferences.
- [Real Gemini Live evaluation](evaluation/voice-skill-author-live.json): **9/9** checks pass. The interview asks follow-up questions, records requirements, creates a gross-revenue draft, reconnects with saved context, accepts a correction to net revenue, produces a replacement draft, saves reviewed edits, and publishes once despite a repeated HTTP request. A manually attached published skill then guides `gemini-3.8-flash` analysis to **$110,695.00** net revenue, matching independent fixture totals ($118,951 gross minus $8,256 refunds).
- Browser checks use real Gemini in a local memory/fixture preview. They cover the library entry point, typed conversation with spoken output/transcripts, requirements checklist, pause/review, explicit public publication, library visibility, validation without draft loss, keep-working confirmation, review-edit recovery, and a standalone frontend using runtime configuration. The scoped browser's temporary config override was removed before model/write requests; no fake voice/model messages were used for these real browser checks.
- Four final axe scans (welcome, keyboard-focusable review, mobile light, mobile dark) have **zero violations**. Modal focus-guard/contrast checks retain incomplete rules. At 390px the page and dialog fit the viewport; OS reduced motion is active. React inspection and Next.js compilation/runtime probes were also used.

The first real probe exposed duplicate final transcriptions and premature control/tool-only turn completion. A deterministic failing regression now verifies full-transcript replacement and completion only after a non-interrupted assistant reply. An initial downstream numeric check also caught an invented status literal (`Completed` versus actual `completed`); [the observation is retained](evaluation/voice-skill-author-live-initial.json), exact user-provided literals are now explicitly preserved, and the final real-model check supplies the actual stored value. Generated playbooks still require review. A scrollable preview accessibility finding was fixed with keyboard focus and a visible focus ring.

Firebase agent skills were refreshed. The existing named database was confirmed read-only as Standard/Native in `asia-southeast1` using the authenticated Google Cloud CLI after Firebase CLI reported no login. No Firestore resource/rule/index/IAM changes were made. The new author collection has **not** been verified across deployed Cloud Run revisions; follow the voice-author release section in the deployment guide when deployment is requested. Existing cloud acceptance reports remain dated baseline evidence.

The real-model smoke injects text through Live and receives audio; it does not prove microphone hardware, barge-in acoustics, or a manual screen-reader journey. These remain manual checks. The local preview uses memory storage and temporary operator credentials; restart the backend after credential expiry. Its data disappears on backend restart, and it does not alter the hosted library.

## Markdown rendering fix — local verification, 16 October 2026

Assistant messages previously rendered inside plain paragraphs, exposing Markdown markers. Analytics messages, saved/live skill-assistant replies, and skill previews now share a safe React Markdown renderer with GitHub-flavored table/task-list support. Visitor messages remain literal. Raw HTML and remote images remain blocked; links retain safe URL handling. Tables and code have keyboard-focusable scroll containers and theme-based styling.

- Frontend lint, TypeScript, production build, and **13/13 frontend tests** pass. Five new renderer regressions cover formatting, GFM, unsafe content, literal visitor text, and incomplete streaming content.
- The actual chat browser reproduction failed before the fix and passed afterward with synthetic API responses. Browser checks also verified saved author replies and editor previews without publishing or changing shared data.
- At 390px, long code stays within the editor dialog and scrolls with the keyboard. Final chat and preview axe scans report **zero violations**; the dialog scan retains two manual-review items concerning modal focus guards and an obscured label's contrast. Next.js reports no runtime or compilation issues; React inspection confirms the shared renderer is mounted.

This is local verification only; no cloud release or GitHub push was performed for this fix.

## Analysis model settings — local verification, 16 October 2026

Settings now offers the workspace default, pinned Gemini 3.8 Flash, and pinned Gemini 3.5 Flash-Lite. Selections persist per browser and are captured per run, including analyst voice data tools. Shared AI settings are never mutated; model context remains isolated across concurrent tasks. Live speech, skill interviews, and embeddings retain their separate configured models. Result evidence distinguishes actual Gemini execution from local fixture mode.

- **149 backend tests** and Ruff pass. Eleven model regressions cover catalog/validation, numerical fixtures, idempotency after a model/default change, concurrent model isolation, ADK model construction, unavailable-model errors, positive/negative voice handshakes, and guarded SQL repairs.
- Frontend lint, TypeScript, production build, and **15 frontend tests** pass, including model preference migration/validation and voice handshake propagation.
- Browser checks verify choice/reload persistence, an actual local turn carrying the selected identifier, keyboard activation, mobile containment at 390px, catalog failure/retry, React state, and result evidence. Desktop and mobile settings axe scans report **zero violations**. Next.js reports no compilation/runtime issues.
- [Real-model checks](evaluation/model-selection-live.json): **2/2** pass through the ADK planner, guarded local SQL, and interpreter. Both selected models return the independently calculated **$118,951** using `global`, an operator identity, ephemeral memory, and synthetic local source tables. This proves operator access and the selected analysis pipeline, not Cloud Run runtime-identity access or real microphone behavior.

The [initial live check](evaluation/model-selection-live-initial.json) completed with empty aggregates. A subsequent SQL probe identified `status = 'Completed'` against lowercase seeded values. The schema description now explicitly states `status='completed'`; the final report preserves both actual SQL statements and their correct totals. No seed rows or query permissions changed. The first checker also omitted decimal strings; the final checker accepts the application's existing JSON decimal representation.

No deployment, IAM change, index refresh, data seeding, or GitHub push was performed for this feature. Release backend before frontend using the deployment guide, and verify both model choices under the dedicated runtime identity before release acceptance.

## Expanded time-series data — 16 October 2026

The requested larger source dataset is generated and **uploaded to the existing demo BigQuery dataset and Cloud SQL database** using additional tables/schema. It covers 2023-01-01 through 2026-09-30 with 573,348 orders, 1,317,941 line items, 97,122 refunds, 25,000 customers, 200 products, 24 stores, and a 1,369-day calendar. The generated Parquet bundle is approximately 105 MB. [The workflow](retail-timeseries.md) documents generation, validation, upload, later extension, profile activation, and limitations; [the dictionary](retail-timeseries-schema.md) describes every column/type.

- [Independent reconciliation](evaluation/retail-timeseries-local.json): **26/26 checks** pass across keys, references, financial arithmetic, refund bounds/timing, monthly targets, date spine, and monthly/rolling SQL. Merchandise revenue is **$354,425,112.20** and refunds through the as-of end are **$19,558,027.70**.
- [First cloud upload](evaluation/retail-timeseries-cloud.json) and [repeat upload](evaluation/retail-timeseries-cloud-repeat.json) complete successfully. Repeating the identical bundle leaves counts unchanged and inserts **zero PostgreSQL rows**. Data publication is insert-only, hash-checked, and fenced; query execution rejects loading/failed/missing readiness state.
- [Before](evaluation/retail-timeseries-before.json) and [after](evaluation/retail-timeseries-after.json) checks preserve the original 720-order / $118,951 demo and original PostgreSQL counts. All new fact keys are unique, six operational primary keys and two foreign keys are present, and upload staging tables are cleaned up. No passwords, instance settings, or project IAM bindings changed. The existing reader received SELECT/USAGE only on the new SQL schema.
- [Hosted Gemini checks](evaluation/retail-timeseries-gemini-cloud.json): **2/2** pass against the real new sources. Gemini 3.8 Flash's 45 monthly totals and Gemini 3.5 Flash-Lite's 45-month YoY result match independent numerical references, including NULL prior-year comparisons. The PostgreSQL reader can read and cannot insert/update/delete. BigQuery/Gemini use the operator identity in this smoke test; it is not proof of a new Cloud Run revision's runtime identity.
- [Interactive preview](evaluation/retail-timeseries-browser.json): real Gemini over the generated local files combines all eligible customer-level revenue with the 25,000-customer dimension. Segment totals **$118,729,938.91** and **$235,695,173.29** reconcile to the overall total without incomplete fusion inputs. Desktop/mobile stable-page axe scans report **zero violations** with one manual chart-contrast review item. A progress-animation scan captured a transient contrast finding; it disappeared on the completed page. Mobile has no page overflow, and Next.js reports no runtime/compilation issues.
- **169 backend tests** and Ruff pass; 20 data regressions cover deterministic generation, extension stability and delayed returns, corruption, financial validation, upload boundaries/insert-only transactions, dense dates, prior-year/window boundaries, follow-up filters, profile SQL isolation, and fail-closed source readiness. Frontend lint, TypeScript, **15 tests**, and production build pass.

The original deterministic test fixture remains small and unchanged. The time-series helper explicitly sets a 30,000-row source retrieval limit for its 25,000-customer dimension; byte/scan bounds, incomplete-input rejection, 50,000-row fusion output cap, and deadlines remain active. Imports are not distributed transactions across both services; quiesce the profile while loading and retry a failed bundle to finish publication.

The serving Cloud Run application has **not** been redeployed or switched to this profile. The uploaded data is ready for a separately requested backend/frontend release with `--data-profile timeseries`. No Firestore history/reset, schema-embedding write, or GitHub push was performed. The local preview is separately configured for the new profile, uses real Gemini over local synthetic Parquet, and retains history only in memory.
