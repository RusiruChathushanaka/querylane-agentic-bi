---
name: analytics-merchandise-margin
description: Evaluate product margin, discount intensity, and return-adjusted merchandise
  performance using historical line costs and correct refund grain.
metadata:
  querylane:
    display_name: Merchandise margin and returns-adjusted performance
    when_to_use: Margin pressure, profitable categories, discount-versus-margin analysis,
      or returns-adjusted revenue and merchandise margin.
    source: bigquery
    tags:
    - margin
    - discounts
    - returns
---

## Purpose
Explain merchandise economics with source-supported costs and refund timing.

## Workflow
1. Use sales_order_items.line_revenue and cost_amount for historical product/category margin. Current catalogue unit prices/costs do not replace historical line values.
2. Merchandise margin before returns = SUM(line_revenue-cost_amount). Margin rate = total margin / total line_revenue. This excludes operating expense and is not full business profit.
3. Aggregate sales_returns per order_item_id before joining items, because one line can have multiple refunds. For a coherent order-cohort return adjustment, net merchandise revenue subtracts refund_amount; net merchandise cost subtracts returned_cost. Explain if refund-date reporting is requested instead.
4. Preserve signed margin; zero or negative margin must remain visible. Discount intensity uses compatible gross amounts as denominator. Report mature versus immature return cohorts and partial data.
5. Reconcile item/category totals to their independent aggregate; a full-order revenue joined to multiple items must not be summed repeatedly.

## Deliverable
Show revenue, costs, margin, weighted margin rate, refunds and coverage with separate units. Interpret discount/margin associations cautiously.

## Example
Which categories have the weakest merchandise margin after observed returns, and how mature are those return cohorts?
