---
name: analytics-kpi-definitions
description: Calculate revenue, orders, units, AOV, and margin with explicit denominators
  and consistent retail definitions.
metadata:
  querylane:
    display_name: Retail KPI definitions and weighted ratios
    when_to_use: Overall AOV, KPI scorecards, weighted averages, gross-versus-net
      revenue, or reconciling metrics across segments and months.
    source: bigquery
    tags:
    - kpi
    - aov
    - weighted-ratios
---

## Purpose
Make retail metrics comparable and numerically defensible.

## Definitions
For the expanded schema, sales_orders.revenue is completed-order merchandise sales after discounts and before refunds, tax and shipping. gross_sales is before discounts; total_paid includes tax/shipping. Use the active discovered schema if another profile is selected. Currency and business-date conventions belong in the result.

## Workflow
1. State filters, reporting grain and coverage. Use orders for order-level metrics and item aggregates for product measures; preserve one order per order_id when counting orders.
2. Calculate overall AOV as SUM(revenue)/COUNT(DISTINCT order_id), or from independently aggregated compatible numerators and denominators. An unweighted mean of monthly/category AOVs is not overall AOV.
3. Calculate margin rate as SUM(margin)/SUM(revenue). Calculate weighted rates from the original eligible denominator; keep null/zero denominators explicit.
4. Reconcile segment numerators and denominators to the overall source aggregate. Sum only additive measures. Explain net-of-refund timing and cost coverage when requested.

## Deliverable
Show metric, definition, numerator, denominator, units, period, and evidence. Separate established findings from interpretation.

## Example
Compare overall AOV with monthly AOV and explain why averaging the monthly averages gives a different answer.
