---
name: analytics-seasonality
description: Inspect daily, weekly, and monthly retail patterns with dense calendars,
  complete periods, and cautious interpretation of peaks.
metadata:
  querylane:
    display_name: Calendar trends and retail seasonality
    when_to_use: Weekly seasonality, annual retail patterns, moving summaries, trend-versus-seasonality
      exploration, or unusual observed dates.
    source: bigquery
    tags:
    - time-series
    - seasonality
    - calendar
---

## Purpose
Describe recurring calendar patterns and trend from complete observed sales.

## Workflow
1. Discover coverage and business-date conventions. Aggregate at a consistent day/week/month grain; use calendar for a dense spine, with Monday week_start and matching ISO year/week where applicable.
2. Preserve observed zero sales. Fill missing aggregates with zero only when the source/calendar coverage establishes a complete observation. Surface unknown gaps and incomplete final periods.
3. Compare weekday patterns with denominators such as observed occurrences of each weekday. Compare complete months and matching prior-year periods; normalize only with an explicit denominator.
4. Request supported rolling calculations in approved source SQL. For forecasting features, shift target-derived rolling values before constructing predictors to avoid future leakage.
5. Describe the largest peaks as observed peaks. Synthetic promotion-day flags are not real public holidays, and a peak alone is not a statistical anomaly or causal campaign effect. Use decomposition only when an approved analytical tool supports it.

## Deliverable
Show the full selected chronology, units, complete-period cutoff, seasonal evidence and data gaps. Distinguish smoothed summaries from observations.

## Example
Show weekday sales patterns and month-by-month seasonality, retaining the known zero-sales day.
