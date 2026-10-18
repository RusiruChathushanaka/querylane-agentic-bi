---
name: prediction-timesfm-comparison
description: Interpret managed TimesFM 3.0 Preview against validated statistical baselines,
  recording candidate outcomes and supported uncertainty.
metadata:
  querylane:
    display_name: TimesFM candidate comparison and evidence
    when_to_use: A request to compare TimesFM with statistical forecasts, explain
      a selected forecasting method, investigate a skipped TimesFM candidate, or review
      managed-model forecast evidence.
    source: all
    tags:
    - timesfm
    - model-comparison
    - predictions
---

## Workflow
Use Advanced Analysis for new controlled forecast fitting. Resolve target, grain, horizon, complete cutoff and purpose; let the planner propose relevant candidates within available capabilities. Include TimesFM only when the application's verified gate, history and remaining budgets permit it. Shared instructions cannot enable providers, grant permissions or increase limits.

Compare candidates on identical saved observations, full-horizon chronological folds and domain checks. The current promotion policy needs at least 5% lower aggregate MAE than baseline and improvement in at least two of three folds; the lowest MAE among passing candidates wins, with an exact tie favoring the existing statistical method. Application policy remains authoritative. A requested brand is not evidence that its predictions are best.

## Deliverable
Show selected method, candidate MAE/RMSE, fold dates, selection rationale, cutoff, horizon and limitations. Label managed output TimesFM 3.0 Preview. When it loses, fails or is skipped, retain supported statistical findings and state the reason. Native intervals are diagnostic unless calibration, later-fold coverage and domain checks support publication; omit unsupported bands explicitly.

Reopening evidence, creating presentation-only revisions, downloads and dashboard views reuse saved predictions. They do not invoke TimesFM again. Preview model weights are not guaranteed permanently identical; captured outputs, configuration, input hashes and job references preserve evidence.

## Example
Create a three-month revenue forecast with eligible TimesFM comparison and explain the numerical method selection, even if TimesFM does not win.
