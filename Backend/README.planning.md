# Planning development

See [Metrics](../docs/business-metrics.md), [AI Dashboard Builder](../docs/ai-dashboard-builder.md), and [Forecast Plans](../docs/forecast-plans.md). These use the existing API/private-worker image, named Firestore database, task queue, and export storage.

Use `DATA_PROFILE=timeseries`, the existing retail bundle for local fixture execution, and `SOURCE_ROW_LIMIT=30000`. Fixture execution does not call Gemini or TimesFM. Hosted TimesFM gates remain independent.

Example publication is explicit: `uv run python -m scripts.seed_metrics --cloud` uses operator credentials and inserts only missing packaged IDs. Omitting `--cloud` demonstrates seeding in ephemeral memory; it does not populate a running backend. No startup or deploy path seeds metrics or analytical data.
