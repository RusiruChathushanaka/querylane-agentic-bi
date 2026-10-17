---
name: analytics-change-contributions
description: Explain period-over-period sales changes using reconciled product, region,
  channel, order-volume, and AOV contributions.
metadata:
  querylane:
    display_name: Sales change and segment contributions
    when_to_use: Why revenue changed, month-over-month or year-over-year comparisons,
      category contribution, or separating order volume from basket value.
    source: bigquery
    tags:
    - diagnostics
    - contributions
    - comparisons
---

## Purpose
Explain where a measured sales change is concentrated without asserting unsupported causes.

## Workflow
1. Resolve the metric and compare equal complete periods with identical filters. Label partial comparisons explicitly; compare adjacent calendar periods only when claiming consecutive growth.
2. Compute both period totals and segment deltas in approved source SQL. Contribution to total change is segment delta / overall delta, with explicit zero-denominator handling; contributions may exceed 100% when other segments offset growth.
3. Reconcile every segment delta to the overall delta, including missing categories. Distinguish additive revenue contribution from share-of-current-sales.
4. When decomposing revenue = completed orders * AOV, use an exact documented bridge: volume=(O1-O0)*A0; basket=O1*(A1-A0). Calculate period AOV from period numerators/denominators. Disclose this ordering-dependent allocation and reconcile the sum to revenue change.
5. Describe associations and observed concentrations. Support causal explanations only with a suitable design; otherwise label hypotheses for follow-up.

## Deliverable
Present prior/current values, absolute and percent changes, ranked contributions, offsetting segments, definitions, and caveats.

## Example
Which categories and channels contributed most to the latest complete month's revenue change?
