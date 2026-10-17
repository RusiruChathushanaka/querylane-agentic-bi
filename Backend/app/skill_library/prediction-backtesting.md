---
name: prediction-backtesting
description: Audit time-series leakage, baseline selection, rolling backtests, uncertainty
  intervals, and forecast reliability.
metadata:
  querylane:
    display_name: Forecast validation and uncertainty
    when_to_use: Validate a forecast, compare prediction models, explain MAE/RMSE
      or interval coverage, or assess whether a forecast is reliable enough to publish.
    source: all
    tags:
    - predictions
    - backtesting
    - uncertainty
---

## Purpose
Gate prediction claims on out-of-sample evidence rather than in-sample fit.

## Workflow
1. Use Advanced Analysis's approved fitting/validation tools. Review completeness, date grain, latest complete cutoff, forecast horizon, metric domain and train/test separation.
2. Use at least three chronological rolling-origin backtests covering the full prediction horizon. Fit preprocessing on each training window only; shift before creating target-derived lags/rolling summaries. Future business drivers must be independently supplied or genuinely known at the origin.
3. Compare candidates with an appropriate naive/seasonal-naive baseline using MAE and RMSE on identical folds. At least 5% aggregate MAE improvement plus improvement in a majority of folds is required for promotion. A low training error alone is insufficient; zero-heavy targets make MAPE unsuitable.
4. Inspect impossible values, unstable folds and history adequacy. A rate needs its correct bounded domain; negative merchandise margin can be legitimate. Keep validation failures and baseline retention visible.
5. Display intervals only when the retained method and validation support them. Report nominal interval level and observed coverage where measured; a prediction interval is not a guarantee or a confidence interval for a causal effect.

## Deliverable
Return fold dates, candidate/baseline errors, selection rule, interval limitations and publish/retain-baseline/withhold outcome. Never invent diagnostics absent from saved tool evidence.

## Example
Validate a quarterly revenue forecast and explain whether it beats a seasonal-naive baseline across rolling backtests.
