---
name: prediction-planning-adjustments
description: Explain separate management planning versions, adjustment propagation
  and cross-view reallocations while preserving original statistical predictions.
metadata:
  querylane:
    display_name: Forecast plan adjustments and assumption disclosure
    when_to_use: Setting planned revenue, percentage adjustments to a forecast plan,
      comparing original versus adjusted versions, or explaining how a regional change
      affects the company and product view.
    source: all
    tags:
    - planning
    - adjustments
    - assumptions
---

## Workflow
Start from an explicit saved Forecast Plan version and distinguish its statistical baseline from a visitor's planned values. Advanced Analysis may explain the saved evidence; plan changes use the dedicated adjustment controls and revision checks. A skill grants no mutation tool. Obtain the node, set-value or percentage operation and business reason before proposing a change.

One adjustment operation is saved per version. A set-value means the same specified USD amount for each forecast month. Explain this meaning before applying a request that could instead mean a horizon-wide total. Original statistical values remain available.

## Propagation
A company change redistributes both views using saved proportions. A region/category change redistributes its children and updates the company; store/product changes update ancestors. The other hierarchy is proportionally reallocated to the new shared company total. Disclose that this cross-view redistribution is an accounting/planning rule, not a learned store-to-product relationship.

Reject negative planned revenue and unsupported positive allocations from zero-history branches. Validate cent-level parent/child consistency. Label changed rows as planning assumptions, with operation, reason, base version and resulting values; they are neither source-database changes nor conditional driver-model scenarios. Recompute is a separate explicit analytical action.

## Example
Review a proposed 5% increase to one region's plan. Explain effects on company, stores and the product hierarchy, preserving the statistical forecast and naming the adjustment assumption.
