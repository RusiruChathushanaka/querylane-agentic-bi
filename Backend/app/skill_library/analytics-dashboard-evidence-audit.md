---
name: analytics-dashboard-evidence-audit
description: Review a saved dashboard for mismatched periods, stale cutoffs, incompatible
  definitions, incomplete results and misleading chart interpretations.
metadata:
  querylane:
    display_name: Dashboard evidence and comparability audit
    when_to_use: Auditing a dashboard before sharing, reconciling cards with different
      totals, reviewing AI dashboard proposals, or checking whether saved results
      are comparable.
    source: all
    tags:
    - dashboards
    - evidence
    - comparability
---

## Workflow
Inspect each saved card's artifact, metric revision, units, date basis, filters, grain, completeness and source timestamps. Report unavailable evidence as a limitation; do not infer freshness from the dashboard's modification time. Distinct timestamps do not imply one distributed snapshot.

Check that headline totals agree with compatible breakdowns and weighted ratios retain their components. Separate differences caused by source scope, refund/order date, omitted categories, partial results, selected chart ranges or forecast cutoffs. Do not add observed, forecast and scenario rows together as realized revenue.

## Review outcome
Recommend explicit title, note, ordering or supported visualization changes. Show which cards can be retained, need new analysis or should be removed, with reasons. Saved chart exploration, View/Edit and exports operate on saved evidence; requesting updated figures requires a separate analytical action. Publishing changes requires visitor review and the current dashboard revision. A conflict preserves the proposal for review rather than overwriting others' edits.

## Example
Audit this revenue dashboard before sharing. Explain why its KPI, category bars and refunds table differ, including definitions, date windows and any incomplete coverage.
