---
name: prediction-hierarchical-planning
description: Interpret monthly revenue plans with one company total, transparent aggregate
  reconciliation and clearly labeled store/product allocations.
metadata:
  querylane:
    display_name: Coherent geographic and product forecast planning
    when_to_use: Company-to-region/store forecasts, category/product revenue plans,
      reconciling forecast totals, or explaining modeled versus allocated hierarchy
      nodes.
    source: all
    tags:
    - hierarchy
    - forecast-plans
    - reconciliation
---

## Workflow
Use the dedicated Forecast Plans workflow for new hierarchy computation; Advanced Analysis can reference an explicitly selected saved plan version. The supported metric is published order-date merchandise revenue in USD, monthly horizon three by default and at most six. Both geography and products share one company forecast, cutoff, metric version and horizon.

Require complete calendar/source/mapping coverage and reconciled order-versus-line revenue. Source capture, fitting and reconciliation are controlled application stages. Important aggregates may be modeled; store/product leaves use frozen trailing-twelve-complete-month parent shares and are labeled allocated. Fold-specific shares use training data only. A zero-history branch cannot acquire an invented positive allocation.

## Validation and reading
Compare complete coherent recipes against the coherent baseline across company, regions, stores, categories and products. Current policy requires at least 5% improvement, wins in two of three folds and no level worsening over 10%; retain the supported baseline otherwise. TimesFM supplies eligible aggregate candidates, not reconciliation or independent forecasts for every leaf.

Verify every parent equals its children to the cent and both views equal company. Do not sum repeated hierarchy levels or add the two views together. Point forecasts have no claimed joint interval. Show node status, horizon, cutoff, validation and limitations. Missing inputs or unsupported metric requests require clarification or a limitation, not fabricated coverage.

## Example
Create a three-month merchandise revenue plan for geography and products, then explain which nodes were modeled, reconciled or allocated and how their totals agree.
