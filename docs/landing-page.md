# Public landing page and workspace entry

The homepage `/` introduces Querylane; `/app` opens the public conversation workspace without sign-in. Reports, Dashboards, Skills and Settings retain their existing paths. Deployed and verified on 17 October 2026 as frontend `agentic-bi-frontend-00012-mv5`. The [deployment record](deployment.json) and [hosted acceptance](evaluation/landing-deployed-api.json) describe the release; backend `00017-cnf` and report worker `00006-sk6` remain unchanged. It changes no backend contract, analytical data, IAM or Firestore schema.

## Product story

The page introduces advanced evidence-backed reports, validated predictions and conversational voice BI, followed by ordinary questions/follow-ups, cross-source analysis, interactive results, shared dashboards, versioned skills and downloads. All copy identifies the public synthetic retail demo. No customer adoption, testimonials, accuracy guarantees or unsupported connectors are claimed.

The six capability groups are supported by the current [architecture](architecture.md), [reports](reports.md), [charts](charts.md), [dashboards](dashboards.md), [skills](skills.md), [voice author](voice-skill-author-plan.md) and [settings](settings.md) contracts. Voice analytics does not directly launch Advanced Analysis; its preview directs visitors to the composer for reports. Optional requester-only Search is not advertised as a shared report feature.

The fixed light palette is scoped to `.landing-page` and `.landing-sheet`. Workspace light/dark, accent, density and reduced-motion preferences remain stored and are restored on application entry. Existing fonts, shadcn Tabs/Sheet and Motion are reused. Native anchors, FAQs and server-rendered copy work independently of client animation; the default Reports preview is rendered on the server. Interactive tabs and the mobile navigation sheet require JavaScript; the hero/footer application links remain native links.

## Guided preview boundary and evidence

The page renders small local SVG product illustrations and a local scripted transcript. It never mounts Workspace, report-reader, query-backed chart or live voice clients. Its controls make no source queries, model calls, guest-session requests or microphone requests. Preview downloads are format labels rather than nonfunctional download buttons. Every application/library entry disables prefetching.

`Frontend/src/lib/landing-preview-data.json` captures a checked saved synthetic report: report `b900baa4adb461dec439d869b7c8e20a`, revision 4, generated 2026-10-16. Forecast artifact `0401fa3ce367eaa4bafccde082b00e6e` supplies January–September 2026 observations and October–December point predictions. [The deployed report evaluation](evaluation/reports-deployed.json) records its ETS model, three rolling-origin backtests, September 30 cutoff and unavailable intervals. The illustrative composition is not the full original report layout.

The full-period totals reconcile to [overall AOV evidence](evaluation/reports-overall-aov.json): 573,348 completed orders, $354,425,112.20 merchandise revenue and $618.17 overall AOV, January 2023–September 2026. The rounded 1.3 million line items and 45 months describe generated-data scope, not business adoption. Revenue is after item discounts and before refunds, tax and shipping. September revenue is $9,447,724.90 versus August $9,576,580.10, a 1.35% decrease. No fabricated prediction intervals or accuracy percentages are shown.

The preview fixture is versioned with the page; the browser does not fetch its source artifacts. Update it only against independently verified saved evidence. Formatting and chart tables preserve observed/forecast distinctions. Forecasts use dashed teal lines, observed values solid cobalt, with cutoff and uncertainty notes.

`Frontend/public/querylane-social.png` is a local 1200×630 social preview. Regenerate from packaged fonts and the same fixture with `Backend/.venv/bin/python infra/generate_landing_social.py`; no remote images/fonts are downloaded by the generator. Homepage metadata has the deployed origin as its canonical URL; update it if the canonical frontend host changes.

## Route compatibility

`Frontend/src/lib/workspace-links.ts` owns canonical new-chat and conversation paths. Workspace history selection, New exploration, forks, shared links and source-conversation links use `/app`. Brand links return to `/`.

The Next.js `redirects()` configuration matches only `/` with a `chat` query key, returns a temporary 307 to the fixed `/app` destination, and forwards query parameters. No query-controlled host or path is accepted. Bare `/` stays the landing page; `/app` never redirects back. Legacy `/?chat=ID&other=value` links continue to work in one hop. [ADR 0008](adr/0008-landing-workspace-routes.md) records the choice.

## Verification and release

Run frontend tests, lint, TypeScript and a production build, then the loaded browser flow. Focused regression tests cover encoded paths, redirect configuration, verified preview values and live-client import boundaries. Browser coverage includes tour tabs/arrow keys, manual follow-up, chart tables, FAQ, mobile sheet/Escape, route/query preservation, workspace navigation/share/New exploration and saved preferences. Check narrow reflow, desktop, reduced motion and no-JavaScript content. Inspect network and the production route bundle to ensure no backend clients or app prefetch are pulled into the landing page.

See the dated local and hosted acceptance in [validation.md](validation.md#landing-page-cloud-release--2026-10-17). Deployment follows the [primary runbook](deployment-guide.md), including existing `timeseries` profile preservation; homepage publication is a frontend release, not a data operation. Do not overwrite the last actual deployment record with local build results.
