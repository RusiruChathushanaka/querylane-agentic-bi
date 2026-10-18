---
name: analytics-basket-affinity
description: Analyze products purchased together using distinct-order baskets, directional
  confidence, support and lift without claiming causal cross-sell impact.
metadata:
  querylane:
    display_name: Basket composition and product affinity
    when_to_use: Frequently bought together, category basket combinations, product
      affinity, multi-category baskets, or evidence for cross-sell hypotheses.
    source: bigquery
    tags:
    - baskets
    - product-affinity
    - cross-sell
---

## Workflow
Choose a bounded period and product/category level using discovered schema. Define the eligible population as distinct completed orders under identical filters. Deduplicate each (order, item/category) presence before counting pairs; repeated lines and quantities do not create extra baskets. Count unordered pairs once using stable keys and exclude self-pairs.

Calculate support(A,B) = baskets containing both / eligible baskets. Directional confidence(A→B) = baskets containing both / baskets containing A. Lift(A→B) = confidence(A→B) / support(B). Show pair counts and denominators, including zero handling. Apply a disclosed minimum supporting basket count; request a threshold if material to the business decision.

## Interpretation
Aggregate and bound pairs at the source within existing execution limits rather than retrieving an unbounded item self-join. Pair rows represent overlapping baskets: their counts or attributed revenues cannot be summed as disjoint totals. Different category prevalence, assortments and seasonality can explain apparent affinity. Associations suggest tests, not guaranteed incremental sales or recommendations proven by an experiment.

## Example
For the last complete quarter, show the strongest category basket affinities with at least 100 shared orders. Include support, directional confidence, lift and raw basket counts.
