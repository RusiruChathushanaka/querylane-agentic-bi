---
name: prediction-forecast-outturn-review
description: Compare saved predictions with subsequently observed complete periods,
  distinguishing real outturn monitoring from historical backtests and revisions.
metadata:
  querylane:
    display_name: Forecast versus actual outturn review
    when_to_use: Forecast accuracy after actuals arrive, predicted-versus-realized
      revenue, directional forecast bias, or deciding whether a saved forecast should
      be recomputed.
    source: all
    tags:
    - forecast-monitoring
    - accuracy
    - outturn
---

## Workflow
Identify the immutable forecast/report/plan version, original cutoff, horizon, metric revision, units and source filters. Preserve the saved predictions as the baseline. Use newly requested guarded evidence for actual observations only when they exist in source coverage. Advanced Analysis handles detailed evaluation or explicit refitting; reopening a saved artifact never refreshes it.

Align forecast dates/grain with complete realized periods. Do not score future or partial observations as zero actuals. The current synthetic source cutoff may precede all predicted periods; then explain that live outturn evaluation is not yet possible and show saved rolling-backtest diagnostics instead. Requesting actuals after the source cutoff does not authorize data generation or upload.

## Measures
For aligned periods report signed error = actual minus forecast, MAE and RMSE, with sample count and evaluated dates. Describe systematic positive/negative errors only within that convention. Avoid percentage-error metrics with zero actual denominators. Keep aggregate and per-series errors distinct; allocated hierarchy leaves are not independently modeled forecasts.

Separate point predictions, learned conditional scenarios and management adjustments. Backtest error is not subsequent real-world accuracy, and synthetic performance is not a guarantee. Recommend explicit recomputation only when justified; never silently replace the original prediction evidence.

## Example
Compare this saved forecast with actual monthly revenue if those complete periods exist. Otherwise explain the cutoff limitation and summarize the saved baseline comparison.
