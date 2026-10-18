---
name: analytics-published-metrics
description: Use shared metric versions consistently, distinguish catalog-backed calculations
  from ad hoc definitions, and resolve materially conflicting business meanings.
metadata:
  querylane:
    display_name: Published metrics and definition consistency
    when_to_use: Questions using published metric names or aliases, inconsistent KPI
      definitions across charts, metric dependencies, or requests to define a new
      shared business measure.
    source: all
    tags:
    - metrics
    - definitions
    - provenance
---

## Workflow
Resolve a requested published name or alias before calculating. Keep its exact revision, transitive dependencies, units, time basis, supported dimensions and filters. If competing definitions materially change the answer, ask which definition to use. A request such as “not an ad hoc calculation” retains catalog resolution.

For a deliberately different definition, label the calculation ad hoc or guide the visitor to create and publish a separate metric through Metrics. Preparing a definition is separate from publishing it. Use the controlled compiler for catalog-backed calculations; unsupported dimensions need a supported alternative rather than rewritten catalog SQL.

## Checks
Aggregate ratio components before dividing: overall AOV is total merchandise revenue / distinct completed orders. Preserve zero-denominator behavior and distinct-count semantics. Product/category AOV is unsupported by the current catalog. Refund-date net revenue and order-cohort revenue answer different questions. Merchandise margin excludes operating costs.

## Deliverable
Identify the published shared definition and version, reporting basis, filters and limitations. Shared publication is not organizational certification. Historical results retain their captured versions.

## Example
Use the published merchandise revenue and AOV metrics for the last complete quarter; explain their definitions and why an unweighted average of monthly AOVs differs.
