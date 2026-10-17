---
name: prediction-driver-scenarios
description: Compare future predictions under explicit baseline and alternative driver
  assumptions, with historical support and causal caveats.
metadata:
  querylane:
    display_name: Conditional driver and promotion scenarios
    when_to_use: What-if forecasts, changed promotion schedules or discount intensity,
      alternative future driver paths, or scenario comparison for business planning.
    source: all
    tags:
    - predictions
    - scenarios
    - drivers
---

## Purpose
Estimate conditional scenarios from a supported historical model, without presenting associations as interventions.

## Workflow
1. Use Advanced Analysis. Identify the target, time grain/horizon, observed historical driver columns and business question. Retrieve compatible aggregated historical drivers through approved SQL/fusion, never arbitrary code.
2. Check missing dates, lag/leakage, limited driver variation, confounding and support for proposed combinations. Models must pass chronological backtesting against their baseline; regression coefficients alone are not proof of impact.
3. Request visitor-supplied baseline and optional alternative values for every required driver and every forecast period using the application's clarification form. Leave unknown future paths unset; genuine zero is different from missing. Do not invent campaign schedules or driver values from the question's desired outcome.
4. Use only the application's supported regression/SARIMAX scenario tools and existing bounds. Reject unsupported extrapolation/combinations. If the scenario cannot pass validation, retain the supported descriptive analysis and explain the limitation.
5. Compare baseline and scenario predictions at identical periods and scope. Label differences as conditional model predictions, not guaranteed lift, causal impact, incremental ROI or inventory feasibility.

Use optional managed TimesFM only when the application reports it available and complete covariate context/future paths exist. Compare it with validated driver regression using the same folds. Baseline and alternative must use the same method; a different ordinary forecast winner belongs in a separate artifact. Never invent future drivers or causal effects.

## Deliverable
Show explicit future assumptions, historical support, validation, predicted paths/differences and uncertainty limitations, with observed values separate.

## Example
Compare next quarter's revenue under my baseline and alternative promotion-driver schedules, asking me for each required future value.
