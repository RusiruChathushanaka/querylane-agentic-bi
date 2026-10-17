# AI Dashboard Builder

Deployed in the [18 October release](evaluation/planning-release-20261018.md). Fresh hosted proposal generation remains unverified because the shared advanced-analysis quota is exhausted. Choose **Build with AI** in Dashboards or **Improve with AI** in dashboard Edit mode. `/dashboards/build` accepts an existing `dashboard` or saved `build` query parameter.

## Workflow

Enter an objective, audience, source/date scope and model. The durable ADK workflow prepares a blueprint, searches saved evidence, gathers missing results, validates a proposal and stops for review. It defaults to four cards, proposes at most eight questions and permits at most four new analysis tasks. AI edits can propose existing-card title/note/width changes, ordering and explicit removals. The review marks added, modified, retained and removed cards. Existing dashboards retain their current cards unless a reviewed change removes them; their total remains bounded at twenty cards.

Suitable saved artifacts must match compiled scope, calculation versions, schema, source profile and coverage. Matching titles are insufficient. A matching signature can reuse chat/report/builder artifacts created with this contract; older artifacts without sufficient evidence are conservatively analyzed again. Source timestamps and coverage remain visible, without implying one distributed snapshot.

Requested predictions can select compatible saved prediction artifacts from a bounded metadata catalog. A dashboard build never starts forecasting. Missing prediction evidence produces a Forecast Plans handoff/limitation. Additional non-prediction questions exceeding the analysis budget are explicitly omitted.

Review titles, notes, chart choices, ordering, widths, reused/new evidence, omitted questions and retained/removed cards. **Use this explored view** captures a chart's explored presentation into the proposal; saving the draft does not publish it. Publication is a separate visitor action outside model tools.

## Publication and recovery

All cards, dashboard metadata, retention references and mutation counters commit transactionally. An existing dashboard must still match its captured revision. A 409 preserves generated evidence and the proposal; rebase retains newly present dashboard cards and requires another review. Rebase and publication do not rerun analysis.

Undo restores the prior dashboard state only while its revision still matches the AI publication. Intervening edits produce a conflict rather than an overwrite. Unpinned cards retain existing 30-day recovery behavior. An unpublished proposal expires after seven days; its initiating guest controls reads/edits/cancellation. Published dashboards remain public.

## Execution and API

`POST /api/v1/dashboard-builds` admits a job; list/detail are guest-scoped. PATCH updates a proposal, and `/publish` and `/undo` apply reviewed changes. Existing `/report-runs/{id}` progress, ordered events, controls, clarification and cancellation surfaces serve the shared worker envelope. UI progress currently polls persisted state; reconnection never reruns a completed stage.

Jobs reuse report outbox, Cloud Tasks, private worker, fenced leases, heartbeats, checkpoints and the shared two-job concurrency ceiling. Reports/builds/plans share the existing daily expensive-job allowance. Limits remain 10 minutes, 24 model calls, 32,000 output tokens, twelve source executions and 8 GiB cumulative BigQuery accounting, with the original per-query and fusion controls.

Build envelopes use `report_runs`/`reports` internally with an explicit kind; they never appear in the public Reports library or create fake public conversations. Proposals live in `dashboard_builds`. Expiring planning retention references preserve reused artifacts through history reset. Public viewing, sharing and downloads continue using saved evidence only.

## Explicit retention maintenance

The operator-only `uv run python -m app.admin purge-planning --confirm-demo-reset` command expires unpublished proposals after seven days and deleted forecast-plan families after their 30-day recovery period. It drains/fences workers and preserves plan families referenced by saved reports or dashboard pins. It is never run by startup, routine deployment or history reset. Inspect the deployment runbook before using operator credentials.
