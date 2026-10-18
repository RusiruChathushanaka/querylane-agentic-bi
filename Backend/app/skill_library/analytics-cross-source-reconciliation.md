---
name: analytics-cross-source-reconciliation
description: Reconcile retail measures across BigQuery and PostgreSQL using explicit
  business keys, compatible grains and visible unmatched or duplicate evidence.
metadata:
  querylane:
    display_name: Cross-source grain and join reconciliation
    when_to_use: BigQuery/PostgreSQL total mismatches, regional target joins, customer/store
      mapping checks, or analysis relying on inferred cross-source relationships.
    source: all
    tags:
    - cross-source
    - joins
    - reconciliation
---

## Workflow
Identify each source's row grain, metric basis, filter window and keys. Aggregate facts to the smallest compatible reporting grain before combining them. Prefer declared validated relationships; inferred ones require supporting uniqueness, type, overlap and business-meaning evidence.

For targets, use compatible month+region or month+store keys when time is retained. Aggregate customer purchases before joining customer profiles where appropriate. A region label is not a unique store/customer key. Inspect null keys, duplicates, normalization assumptions, expected/observed cardinality, unmatched rows and total reconciliation.

## Completion
Publish independent source timestamps, relationship assumptions and completeness. Reject unsupported many-to-many expansion or incomplete fusion inputs; do not hide missing entities by presenting inner-join totals as the full population. An apparent discrepancy may be a legitimate definition or timing difference; explain it before recommending a corrected query. Apply the application's existing controlled connector/fusion tools and limits.

## Example
Reconcile regional monthly sales and targets, including unmatched regions, duplicate keys, source timestamps and any inferred join assumptions.
