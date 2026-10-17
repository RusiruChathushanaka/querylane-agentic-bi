---
name: analytics-customer-cohorts
description: Analyze acquisition cohorts, repeat purchasing, observed customer value,
  and retention using mature comparable observation windows.
metadata:
  querylane:
    display_name: Customer cohorts and repeat purchasing
    when_to_use: Customer retention, repeat-purchase rate, signup cohorts, observed
      RFM summaries, or value by acquisition channel.
    source: all
    tags:
    - customers
    - cohorts
    - retention
---

## Purpose
Measure observed customer behavior with explicit eligibility and observation windows.

## Workflow
1. Distinguish signup_date cohorts from first observed purchase cohorts. The earliest order in the available dataset need not be a lifetime first purchase. Profile attributes such as segment/loyalty tier are current fixed synthetic attributes, not historical snapshots.
2. Aggregate orders per customer and period before joining customer_profiles on customer_id. Verify uniqueness, unmatched IDs and full fusion coverage. Narrow the scope or push aggregation upstream when limits prevent complete evidence.
3. Define an eligible cohort and denominator. Repeat-purchase rate uses customers with at least two eligible orders / eligible purchasing customers. Activity retention at month k uses active eligible cohort customers / the original eligible cohort size; disclose whether reactivation counts.
4. Compare equally mature observation windows and exclude not-yet-observable cohort cells. Distinguish zero activity from an unobserved future period.
5. Label recency/frequency/monetary summaries as observed-window measures. Lifetime-value predictions require a validated supported model; offer observed value when those tools/data are unavailable.

## Deliverable
Return a cohort/segment table, denominators, maturity cutoff, and a chart supported by the application. Keep customer-level personal details out of public summaries.

## Example
Compare three-month repeat purchasing by signup quarter using only cohorts with three complete months of follow-up.
