# Forecast Plans skills layout — 19 October 2026

Local implementation and verification only; no Cloud Run deployment or GitHub publication occurred. [Machine-readable checks](forecast-plan-ui-20261019.json).

## Finding and correction

The public `/forecast-plans` page reproduced the supplied screenshots: skill labels were inline elements with card padding but no row layout. Their painted borders/text overlapped adjacent lines and the submit action. The same shared component is used by `/dashboards/build`.

The picker now uses a responsive grid with wrapping checkbox labels, at least 44px click targets, explicit gaps and a keyboard-focusable scroll region capped at 20rem. Skill-name search keeps attachments selected when filtered out, with a clear no-match message. Enter in search cannot implicitly submit a computation. Native checkbox labels, the three-skill limit and source eligibility remain intact. Loading, failure and an empty library have distinct messages; aborted responses cannot update the picker.

## Verification

- 58 frontend tests pass, including five picker regressions covering selection/removal, search, source eligibility, Enter submission prevention and loading/error/empty states. ESLint and TypeScript pass.
- Next.js 16.4.1 Turbopack production build passes using fresh generated output `.next-ui-check`. An initial sandboxed build failed on font networking/subprocess port permissions; retrying its cached output retained the compiler failure. Fresh output built successfully outside the sandbox. Generated configuration additions were removed from the working-tree diff.
- Both forms, using the public library's 29 skill metadata entries as local intercepted fixtures, pass geometry assertions at 320, 390, 768, 1280 and 1600px and simulated 200% CSS zoom. No card overlap, label overflow, page/grid horizontal overflow or submit-button collision; minimum observed label height is 47px.
- Browser keyboard Space selects/removes a skill with a visible 2px focus outline. Three selected skills disable the remaining 26. Searching retains hidden selections, and unmatched searches show an explicit message. Enter in search produces zero form submissions.
- Focused axe-core 4.12.1 scans of `.bi-skills` report 18 passing rules, zero violations and zero incomplete checks in light mode and dark/teal/reduced-motion mode. Next.js compilation and runtime diagnostics are clear; React inspection confirms the shared picker under Forecast Plans.
- The production-built Forecast Plans page was also loaded locally at 390px and 1280px: all 29 skills use the compiled grid, with no horizontal overflow or submit collision. An initial preview used the dev origin in its intercepted config, causing cross-origin fixture requests to fail; replacing that stale interception with the production preview's own origin resolved the test setup.

## Boundaries

Tests used isolated Chromium sessions and local read fixtures for skills, metrics, plans and model metadata. No forecast/dashboard jobs, guest mutations, analytical SQL, inference, data uploads, quota resets or service-setting changes were performed. The larger dataset and TimesFM configuration were untouched. This UI check does not close the separate fresh hierarchical forecasting worker acceptance gate.

Physical mobile devices, full screen-reader behavior and browser-menu zoom were not tested; CSS zoom is explicitly a simulation. The accessibility scan covers the changed picker, not an application-wide accessibility certification. Architecture and execution boundaries are unchanged, so no architecture/Graphify regeneration is needed for this layout correction.
