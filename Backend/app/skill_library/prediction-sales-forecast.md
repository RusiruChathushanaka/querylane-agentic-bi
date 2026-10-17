---
name: prediction-sales-forecast
description: Forecast retail revenue, order counts, or unit demand through Advanced
  Analysis using complete series, naive baselines, and chronological validation.
metadata:
  querylane:
    display_name: Revenue and demand forecasting
    when_to_use: Predict future sales or demand, forecast next month or quarter, estimate
      future order counts, or compare a sales forecast with historical seasonality.
    source: bigquery
    tags:
    - predictions
    - forecasting
    - demand
---

## Purpose
Produce a defensible forecast using the application's controlled Advanced Analysis fitting tools.

## Workflow
1. Resolve target, source filters, daily/weekly/monthly grain, desired horizon and business decision. Ordinary chat can prepare history; actual fitting requires Advanced Analysis. A skill adds instructions, not tools or permissions.
2. Retrieve a complete aggregated series with explicit units and latest complete observation. Distinguish zeros, gaps, partial periods and distance from the cutoff to today. Forecasts begin after the actual cutoff, not an invented current date.
3. Use last-value/seasonal-naive baselines and only available approved candidates: ETS, SARIMAX, regularized regression and optional managed TimesFM 3.0 Preview. The agent proposes candidate policy and priority; common backtest scores choose the winner. TimesFM may be disabled or fail compatibility/budget checks; retain a supported statistical method with disclosure. Use chronological rolling-origin evaluation across the entire requested horizon and at least three usable origins; seasonal candidates need two seasonal cycles in each training window.
4. Defaults: daily 28 days (max 90), weekly 12 weeks (max 26), monthly 3 months (max 12), further bounded by history and validation. Request fewer series/horizon when the existing fit/time budgets require it.
5. Promote a candidate only when aggregate MAE improves at least 5% over its baseline and improvement occurs in a majority of folds. Retain a defensible baseline or withhold an unsupported forecast. Preserve genuine negative values for signed metrics; counts/revenue require a nonnegative domain. Invalid predictions require diagnosis, not silent clipping.

## Deliverable
Separate observed and forecast values. Include cutoff, horizon, retained method, fold evidence, MAE/RMSE, supported intervals and limitations. Synthetic retail fit quality is not proof of real-world predictive accuracy.

## Example
Create an Advanced Analysis report forecasting the next three complete months of merchandise revenue, with backtested baselines and uncertainty.
