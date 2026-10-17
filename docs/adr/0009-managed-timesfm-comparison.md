# ADR 0009: Managed TimesFM comparison over saved report evidence

Status: Accepted; implemented locally, disabled pending managed compatibility and worker-access verification.

Use BigQuery `AI.FORECAST` with explicit TimesFM 3.0 Preview in the existing private report workflow. A fixed parameterized adapter receives saved, validated observations. Do not expose arbitrary forecasting SQL or download model weights. This avoids a new serving stack and retains the managed licensing path.

The agent chooses analytical relevance and candidate priority; deterministic chronological evidence chooses the published method. Preserve existing baseline/promotion/domain gates. Scenario baselines and alternatives share one method; publish a separate scenario artifact when needed. Provider intervals are diagnostic until application validation supports publication.

Freeze policy, inputs, configuration and operation identity in fenced application checkpoints. Reserve remote work transactionally, reuse deterministic jobs after ambiguous responses, retain conservative failed-work budgets and archive outcomes. Managed identifiers do not guarantee immutable underlying weights; saved outputs establish historical evidence. New runs use workflow version 2; old runs and completed documents retain their original behavior.

Inference stays disabled until compatibility and actual worker identity are verified. No automatic IAM expansion, source migration or model-version substitution is permitted. See [TimesFM behavior and limits](../timesfm.md) and [the release runbook](../deployment-guide.md).
