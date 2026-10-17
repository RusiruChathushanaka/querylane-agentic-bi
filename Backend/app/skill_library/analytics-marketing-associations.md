---
name: analytics-marketing-associations
description: Compare attributed sales, campaign spend, and promotion-associated outcomes
  without confusing observational attribution with incremental impact.
metadata:
  querylane:
    display_name: Campaign and promotion performance
    when_to_use: Campaign efficiency, promotion performance, attributed revenue per
      spend, or discount-associated sales and margin.
    source: all
    tags:
    - campaigns
    - promotions
    - attribution
---

## Purpose
Measure recorded campaign/promotion associations while retaining causal limitations.

## Workflow
1. Discover the actual campaign and promotion coverage. Join orders to campaigns using campaign_id; join order lines to promotions using promotion_id. Profile key uniqueness and unmatched identifiers before fusion.
2. Aggregate revenue and spend separately to a compatible campaign/period grain before joining. Count each campaign's spend once. Full-month spend cannot silently be compared with partial-month revenue.
3. Label attributed revenue / campaign spend as attributed revenue per spend (or attributed ROAS with that definition), not incremental profit or guaranteed ROI. Explicit order campaign links represent synthetic last-touch association.
4. For promoted versus unpromoted comparisons, describe differences in timing, product/region mix, discount intensity and sample coverage as possible confounders. Use merchandise margin separately when historical costs are present.
5. A future promotion scenario requires Advanced Analysis, a validated driver model and visitor-supplied future paths. An observed correlation alone cannot establish promotion lift.

## Deliverable
Show attributed outcomes, spend, ratio denominators, coverage, unmatched rows and limitations.

## Example
Compare campaigns by attributed revenue per spend and explain why this does not estimate incremental ROI.
