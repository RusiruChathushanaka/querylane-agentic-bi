---
name: analytics-customer-concentration
description: Measure customer concentration and purchasing-customer contributions
  using observed period revenue, with clear population and acquisition-profile caveats.
metadata:
  querylane:
    display_name: Customer revenue concentration and dependency
    when_to_use: Top-customer dependency, Pareto revenue distribution, customer concentration
      by region or channel, or the revenue share of high-value purchasing customers.
    source: all
    tags:
    - customers
    - concentration
    - pareto
---

## Workflow
Specify period, revenue definition and purchasing-customer population. Aggregate orders to customer before ranking. Distinguish registered profiles from customers who purchased in the selected period. Join profile attributes only on validated customer keys and disclose unmatched rows; profile region is not transaction/store region.

Rank customers by period merchandise revenue with a disclosed tie rule. Report top-N or top-percent revenue share only from complete, nonnegative, additive revenue evidence. Use the full eligible population for the denominator, not the returned top-N preview. If evidence is incomplete, show observed contributions and withhold population-wide shares.

## Interpretation
Present cumulative revenue versus cumulative purchasing-customer share and supporting counts. Describe concentration as exposure or dependence under the chosen definition, not as proof of churn risk or future lifetime value. Synthetic fixed loyalty/segment attributes are not historical as-of snapshots. Use customer IDs or aggregate groups; avoid unnecessarily printing names in shared reports.

## Example
How much of last quarter's merchandise revenue came from the top 10% of purchasing customers? Compare channels and explain population coverage and tie handling.
