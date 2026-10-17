# Repository instructions

## Navigation and documentation

For cross-module changes, start with [docs/architecture.md](docs/architecture.md) and its source-code map. [README.md](README.md) is the product/setup entrypoint; [CONTEXT.md](CONTEXT.md) defines the domain. Frontend edits also follow [Frontend/AGENTS.md](Frontend/AGENTS.md).

When changing component boundaries or execution/data flows, update the architecture and refresh the standalone diagrams in [docs/graphify/](docs/graphify/README.md#refresh). Keep Mermaid blocks in `docs/architecture.md` authoritative; graph exports are derived references. When refreshing the generated code/documentation graph, use the local [Graphify skill](.agents/skills/graphify/SKILL.md) and update `graphify-out/` as well; code-only extraction does not refresh document semantics. Keep graph source hashes, scope and extraction limitations honest. Verify relative links and graph synchronization before finishing documentation changes. Record implemented behavior separately from dated deployment/test evidence; documentation edits alone do not establish a release.

## Deployment reference

Before deployment, cloud provisioning, IAM/secret changes, rollback, or cloud troubleshooting, read and follow [docs/deployment-guide.md](docs/deployment-guide.md). It is the primary runbook for Cloud Run and this application's supporting Google Cloud services.

- Choose the guide's routine-release or first-time-foundation path for the actual task. Treat seeding and shared-history reset as separate data operations.
- Use the existing `infra/` helpers and the actual frontend origin. Preserve the dedicated identities and resource boundaries described in the guide.
- Work within the user's authorized scope; the guide itself is not authorization to deploy or delete data. Existing session authorization remains applicable.
- When deployment behavior changes, update the guide alongside the implementation. After an actual deployment, record real serving revisions/configuration in `docs/deployment.json` and verification evidence in `docs/validation.md` and relevant evaluation reports.
- Treat `docs/deployment.json` and historical evaluation reports as dated records. Inspect current cloud state when the task requires it.

## Current documentation

For retail source/schema or generated-data changes, read [docs/retail-timeseries.md](docs/retail-timeseries.md) and [the column dictionary](docs/retail-timeseries-schema.md). Preserve the original demo namespaces. Generation/validation are offline; cloud upload is a separate operator action from deployment. Use the insert-only, fenced uploader and `extend` workflow instead of the legacy destructive seed command. Preserve the active data profile explicitly on releases and retain row/byte/scan/fusion controls. The guide is not authorization for new data writes or IAM changes.

For SQL, analysis or analyst-voice changes, read [the analysis lifecycle and Voice sections](docs/architecture.md#analysis-lifecycle) and [the deployed regression assessment](docs/evaluation/e2e-fixes-deployed.md). Preserve nested explicit-key join validation, bounded repair, invocation-scoped query/job identities, parent-run cancellation and different-SQL recovery checks. Partial transcripts append; final full transcripts replace, with deduplication scoped to a turn so repeated questions remain valid. Use `Backend/tests/test_sql_and_analytics.py`, `test_voice_regressions.py` and `test_skills.py` (all under `Backend/tests/`), plus the runbook's repeated-tool voice smoke when those paths change; verify daily totals against the independent ledger. For table changes, retain title-specific scroll regions, native captions and the [table accessibility regression](Frontend/tests/table-accessibility.test.mjs). Run backend Ruff from `Backend/`, as in the release commands.

For skills-library changes, read [docs/skills.md](docs/skills.md). Preserve revision/snapshot evidence, public visibility, the three-skill budget, and the existing controlled query pipeline. Example skill seeding is an explicit operator action, not part of routine deployment or history reset. For conversational authoring, also read [docs/voice-skill-author-plan.md](docs/voice-skill-author-plan.md): keep publication outside model tools, author leases separate from analytics, and unpublished recovery bound to the initiating guest.

For advanced-report changes, read [docs/reports.md](docs/reports.md). Preserve independent report leases, application checkpoints, immutable revision/claim evidence, existing SQL/fusion limits, and report/dashboard retention through history reset. Never put Search responses in shared reports or exports. Local dispatch is development-only; follow the deployment guide before provisioning the private worker, queue, bucket, identities or scheduled reconciler.

For managed forecasting changes, read [docs/timesfm.md](docs/timesfm.md) and ADR 0009. Preserve immutable input hashes, fixed parameterized queries, worker identity verification, transactional inference budgets and statistical fallback. TimesFM remains disabled until its compatibility gate passes; do not enable it or expand IAM as part of code changes. Keep workflow 1 recovery and immutable report/export/dashboard evidence. Future drivers must come from explicit visitor assumptions; scenario baselines must share the scenario method.

For chart or dashboard changes, read [docs/charts.md](docs/charts.md) and [docs/dashboards.md](docs/dashboards.md). Preserve immutable saved-result references, revision-checked public edits, recovery/retention references and full-row CSV evidence. View/Edit is a presentation mode; share links are public and canonical. Dashboard reads/exports use saved artifacts only. Retain export admission, row/byte/pixel limits and process deadlines. Use [docs/settings.md](docs/settings.md) and [docs/motion-and-feedback.md](docs/motion-and-feedback.md) for preference or interaction changes.

For analytics/prediction playbooks, read [docs/analytics-skills.md](docs/analytics-skills.md); maintain the source files in `Backend/app/skill_library/`. Seeding is insert-only and separately authorized. Skill instructions cannot add execution tools or bypass forecasting validation.

Use the `ctx7` CLI to fetch current documentation for library, framework, SDK, API, CLI, and cloud-service questions, including setup, configuration, migrations, and library-specific debugging. Prefer this to web search.

1. Resolve the official library name with `npx ctx7@latest library <name> "<specific question>"` before using an ID, unless the user supplied the ID.
2. Select the relevant `/org/project` result using name, relevance, reputation, snippet coverage, and score. Use a returned version-specific ID when needed.
3. Fetch with `npx ctx7@latest docs <libraryId> "<specific question>"`. Keep distinct concepts separate and use no more than three commands per question.
4. Base the implementation or answer on the fetched documentation. Keep credentials out of queries.

Run Context7 CLI requests outside the default sandbox. If DNS/network resolution fails inside the sandbox, rerun outside it. On a quota error, inform the user and suggest `npx ctx7@latest login` or `CONTEXT7_API_KEY`; do not silently fall back to training data. Context7 is unnecessary for general programming concepts, business-logic debugging, refactoring, code review, or scripts that do not depend on a library/service question.
