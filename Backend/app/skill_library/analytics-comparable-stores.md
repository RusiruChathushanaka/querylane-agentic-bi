---
name: analytics-comparable-stores
description: Compare stores and regions fairly using opening dates, equivalent reporting
  periods, target grain, and transaction-region definitions.
metadata:
  querylane:
    display_name: Comparable-store and target performance
    when_to_use: Like-for-like store growth, store ranking, new-store effects, store
      target gaps, or regional performance normalized for coverage.
    source: all
    tags:
    - stores
    - like-for-like
    - targets
---

## Purpose
Separate comparable-store performance from differences in footprint and observation time.

## Workflow
1. Join stores by store_id, retaining transaction/store region separately from customer home region. Define eligibility before ranking: stores open for both full comparison periods with complete source coverage.
2. Compare the same eligible stores in both periods; separately report new/ineligible stores. Store opening dates support eligibility but are not proof of operating hours or stock availability.
3. Aggregate actuals at month and store_id before joining store_targets. Regional targets require month and region; state partial-month coverage against full-month targets.
4. Compute weighted aggregate attainment and growth from their total numerators/denominators. Report zero targets explicitly and preserve negative gaps.
5. Reconcile store totals to regional actuals/targets and report unmatched keys. Sales per trading day is available only when genuine trading-day observations exist; calendar days are not a substitute.

## Deliverable
Provide eligibility criteria, comparable-store totals, new-store contribution, target variance and evidence.

## Example
Compare like-for-like store revenue growth across the latest two complete quarters and identify stores below target.
