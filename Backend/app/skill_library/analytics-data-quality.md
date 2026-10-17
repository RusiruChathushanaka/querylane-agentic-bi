---
name: analytics-data-quality
description: Audit missing dates, nulls, duplicate keys, join coverage, and incomplete
  periods before trusting retail findings.
metadata:
  querylane:
    display_name: Data quality and analysis readiness
    when_to_use: Data-quality checks, reconciliation discrepancies, suspicious gaps,
      duplicate totals, or readiness for detailed analysis and forecasting.
    source: all
    tags:
    - data-quality
    - completeness
    - reconciliation
---

## Purpose
Establish whether the requested analysis has trustworthy, complete inputs.

## Workflow
1. Discover the active schema and actual date coverage. Report source timestamps, grain, row completeness, nulls, duplicate logical keys, and invalid domains for the requested metrics.
2. For daily series, compare the calendar spine with source aggregates. Treat a missing observation as unknown until coverage establishes a genuine zero; retain actual zero-sales dates.
3. Profile proposed join keys and aggregate to a compatible grain before joining. Report unmatched keys, expected cardinality and observed fan-out. Stay within approved source/fusion limits; request narrower aggregates when complete inputs cannot fit.
4. Reconcile independent totals at the same filters and grain. Explain discrepancies before using the result for population claims or forecasts.

## Deliverable
Return a concise quality table with check, evidence, severity, affected period, and analytical consequence. Partial evidence must stay labeled partial.

## Example
Audit the daily sales series for gaps and zero-sales days before forecasting next month's revenue.
