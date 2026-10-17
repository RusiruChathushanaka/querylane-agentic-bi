# Public landing page and workspace entry

The homepage `/` introduces Querylane; `/app` opens the public conversation workspace without sign-in. Reports, Dashboards, Skills and Settings retain their existing paths. The initial landing release was verified on 17 October 2026 as frontend `agentic-bi-frontend-00012-mv5`, with backend `00017-cnf` and worker `00006-sk6` unchanged at that time. [Initial hosted acceptance](evaluation/landing-deployed-api.json) is historical; [deployment.json](deployment.json) records the later serving release. The TimesFM landing update is deployed as frontend `agentic-bi-frontend-00016-tw2`; [its hosted acceptance](evaluation/landing-timesfm-deployed.md) records the live checks and unchanged backend/worker settings. It changes no backend contract, analytical data, IAM or Firestore schema.

## Product story

The page introduces advanced evidence-backed reports, validated predictions and conversational voice BI, followed by ordinary questions/follow-ups, cross-source analysis, interactive results, shared dashboards, versioned skills and downloads. All copy identifies the public synthetic retail demo. No customer adoption, testimonials, accuracy guarantees or unsupported connectors are claimed.

The six capability groups are supported by the current [architecture](architecture.md), [reports](reports.md), [charts](charts.md), [dashboards](dashboards.md), [skills](skills.md), [voice author](voice-skill-author-plan.md) and [settings](settings.md) contracts. Voice analytics does not directly launch Advanced Analysis; its preview directs visitors to the composer for reports. Optional requester-only Search is not advertised as a shared report feature.

The fixed light palette is scoped to `.landing-page` and `.landing-sheet`. Workspace light/dark, accent, density and reduced-motion preferences remain stored and are restored on application entry. Existing fonts, shadcn Tabs/Sheet and Motion are reused. Native anchors, FAQs and server-rendered copy work independently of client animation; the default Reports preview is rendered on the server. Interactive tabs and the mobile navigation sheet require JavaScript; the hero/footer application links remain native links.

## Guided preview boundary and evidence

The page renders small local SVG product illustrations and a local scripted transcript. It never mounts Workspace, report-reader, query-backed chart or live voice clients. Its controls make no source queries, model calls, guest-session requests or microphone requests. Preview downloads are format labels rather than nonfunctional download buttons. Every application/library entry disables prefetching.

`Frontend/src/lib/landing-preview-data.json` captures immutable version-1 examples from the [verified TimesFM release](evaluation/timesfm-deployed.json). Monthly report `2ed05089e9a86e1ef3046fa6c6728680`, artifact `47bca8c3fbc89b5e2f50c5b4e92e484d`, supplies October–December 2026 TimesFM 3.0 Preview point predictions and MAE/RMSE scores against seasonal-naive, ETS and SARIMAX candidates. The preview shows the last nine observed months, with three future monthly predictions. Selection uses three chronological folds and the existing baseline-improvement policy, not a claim of guaranteed future accuracy.

The separate **Scenarios** tour tab uses report `f0853cca9462ee293ddaf45e6627e843`, artifact `8931efa3298ac039d18105973aad4e7f`, for October 1–14, 2026. The explicit binary promotion driver is 0 every baseline day and 1 every alternative day. Both paths use the same TimesFM configuration/history, with 1,312 observations per comparison-fold context from 1,369 saved days. Baseline and alternative are both predictions, distinguished by dashed/dotted lines, endpoint shapes and labels. Rounded fourteen-day totals, a semantic data table, cutoff and unavailable-interval note accompany the chart. Conditional scores assume known driver paths; no causal lift is claimed.

Each example links to its canonical hosted report **version 1**, with prefetch disabled. These are secondary evidence links; all primary Open Querylane actions still enter `/app` directly. Visitors can inspect the packaged chart values/method comparison without following a link, API access, microphone access or model invocation. The preview composition is an excerpt, not the entire original report layout.

The full-period totals reconcile to [overall AOV evidence](evaluation/reports-overall-aov.json): 573,348 completed orders, $354,425,112.20 merchandise revenue and $618.17 overall AOV, January 2023–September 2026. The rounded 1.3 million line items and 45 months describe generated-data scope, not business adoption. Revenue is after item discounts and before refunds, tax and shipping. September revenue is $9,447,724.90 versus August $9,576,580.10, a 1.35% decrease. No fabricated prediction intervals or accuracy percentages are shown.

The preview fixture is versioned with the page; the browser does not fetch its source artifacts. Update it only against independently verified saved evidence. Formatting and chart tables preserve observed/forecast distinctions. Forecasts use dashed teal lines, observed values solid cobalt, with cutoff and uncertainty notes.

`Frontend/public/querylane-social.png` is a local 1200×630 social preview. Regenerate from packaged fonts and the same fixture with `Backend/.venv/bin/python infra/generate_landing_social.py`; no remote images/fonts are downloaded by the generator. Homepage metadata has the deployed origin as its canonical URL; update it if the canonical frontend host changes.

## Route compatibility

`Frontend/src/lib/workspace-links.ts` owns canonical new-chat and conversation paths. Workspace history selection, New exploration, forks, shared links and source-conversation links use `/app`. Brand links return to `/`.

The Next.js `redirects()` configuration matches only `/` with a `chat` query key, returns a temporary 307 to the fixed `/app` destination, and forwards query parameters. No query-controlled host or path is accepted. Bare `/` stays the landing page; `/app` never redirects back. Legacy `/?chat=ID&other=value` links continue to work in one hop. [ADR 0008](adr/0008-landing-workspace-routes.md) records the choice.

## Verification and release

Run frontend tests, lint, TypeScript and a production build, then the loaded browser flow. Focused regression tests cover encoded paths, redirect configuration, verified preview values and live-client import boundaries. Browser coverage includes tour tabs/arrow keys, manual follow-up, chart tables, FAQ, mobile sheet/Escape, route/query preservation, workspace navigation/share/New exploration and saved preferences. Check narrow reflow, desktop, reduced motion and no-JavaScript content. Inspect network and the production route bundle to ensure no backend clients or app prefetch are pulled into the landing page.

See the dated local and hosted acceptance in [validation.md](validation.md#landing-page-cloud-release--2026-10-17). Deployment follows the [primary runbook](deployment-guide.md), including existing `timeseries` profile preservation; homepage publication is a frontend release, not a data operation. Do not overwrite the last actual deployment record with local build results.
