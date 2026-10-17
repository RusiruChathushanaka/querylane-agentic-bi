---
name: prediction-rates-returns
description: Assess whether return rates or other bounded retail rates can be forecast
  using mature cohorts, valid denominators, and supported domains.
metadata:
  querylane:
    display_name: Returns and rate prediction readiness
    when_to_use: Forecast return rates, predict refund trends, model bounded retail
      percentages, or check whether recent cohorts are mature enough for prediction.
    source: bigquery
    tags:
    - predictions
    - returns
    - rates
---

## Purpose
Forecast a clearly defined rate only when its underlying cohort and denominator support the analysis.

## Workflow
1. Define the target: returned units / eligible sold units, orders with a return / eligible orders, or refund amount / compatible merchandise revenue. These answer different questions. Refund-date net measures differ from order-cohort return behavior.
2. Aggregate multiple returns per original line/order before joining. Use consistent cohort eligibility and disclose refund latency. Recent purchases have incomplete return follow-up; use an explicit supported maturity rule or ask for the policy rather than inventing a universal return window.
3. Retrieve the full numerator and denominator series and calculate weighted rates in source SQL. Preserve undefined zero-denominator periods, low-volume instability and missing observations. An amount/revenue ratio is not automatically bounded by one under every refund-date definition.
4. For an eligible bounded target, use Advanced Analysis's supported forecast tools with the actual fraction (0–1) or percentage (0–100) domain, chronological baselines and backtests. For a monetary refund target, select its supported monetary domain separately. Withhold results that fail completeness, maturity, domain or validation gates; do not silently clip.
5. Treat expected refunds as a forecast with uncertainty. A return-rate model is not an individual-customer risk score or a guarantee of future refunds.

## Deliverable
Provide definition, denominator, maturity cutoff, supported forecast or precise reason to withhold, and evidence/uncertainty.

## Example
Assess whether mature order cohorts support a three-month return-rate forecast, and explain any limitations before predicting.
