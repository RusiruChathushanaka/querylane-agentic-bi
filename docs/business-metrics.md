# Business Metrics Catalog

Deployed in the [18 October release](evaluation/planning-release-20261018.md); consult its verification boundaries. `/metrics` is the public catalog, with individual draft/detail pages and immutable `/metrics/{id}/revisions/{version}` evidence pages.

## Shared definitions

Anyone can create, edit, structurally validate, publish, duplicate, archive and restore metrics. Publishing creates an immutable revision and advances the current pointer; editing a published metric changes its draft. Revision checks prevent silent overwrites. Guest attribution is internal and does not identify a verified person. “Published shared definition” is not an organizational certification.

Definitions contain business meaning, aliases, units, explicit order/refund time basis, supported dimensions, limitations, examples and a typed formula. Operations are approved measure sums/counts/distinct counts, differences and ratios over exact published dependency revisions. No visitor SQL, arbitrary functions, tools or expressions are accepted. Dependency depth is bounded, cycles and incompatible dimensions/units/time bases are rejected, and dependency snapshots have a size budget.

The compiler owns the fact grains and joins. Order revenue maps to line revenue for product/category breakdowns; order-level revenue is never summed after an item join. Ratios retain components and aggregate before division. Refund-date net revenue combines sales occurring in the reporting period with refunds processed in that period; it is not order-cohort net revenue. AOV does not support product/category breakdowns in this release. Merchandise margin excludes operating expenses and is not accounting profit.

## Agent use and evidence

Text and analyst-voice questions share the same planner. Explicit names/aliases resolve published versions; relevant definitions are captured before execution. Broader Gemini discovery uses bounded metadata. The scope agent selects dates, grain and allowed filters; application code generates the calculation. Its filter map uses JSON output with strict local validation because ADK/GenAI response-schema conversion does not accept this dictionary shape. Unapproved filter keys remain rejected before SQL execution. Explicit ad hoc requests retain the existing guarded analysis path and receive no catalog certification. Negated wording such as “not an ad hoc calculation” retains catalog resolution; positive and negated opt-outs have regression coverage.

Reports persist metric context and query plans in their fenced checkpoints. Simple forecast series bind the compiler's date/value aliases to the forecast contract. Driver-based feature queries are additionally checked against independently saved canonical metric values at identical dates/grain. Those checks consume the original report query budget; they cannot expand it. Compiled metric SQL is not rewritten by a model repair. Guarded feature queries retain bounded repair and must still pass numerical reconciliation.

Artifact snapshots include definitions and transitive dependencies. Result cards link to saved revisions. Updates and archival do not change existing answers. Archiving excludes direct discovery; published derived definitions retain their exact historical dependency references.

## APIs and controls

`/api/v1/metrics` provides list/create, detail/draft edit, `validate`, `test`, `publish`, `archive`, `restore`, and revision list/detail operations. Mutations use guest credentials, request IDs and expected revisions. Stale changes return 409 while the UI retains its draft.

The catalog has 100 entries, definitions are at most 16 KiB, and mutations are transactionally limited to 20 per guest/hour and 100 workspace-wide/day. Metric counters survive history reset. Numerical previews consume ordinary analysis allowance, use approved read-only connectors, and label structural validation separately from numerical testing.

The operator command `cd Backend && uv run python -m scripts.seed_metrics --cloud` inserts sixteen packaged definitions, preserving all existing IDs and visitor changes. It is never called during startup, deployment or history reset. Omitting `--cloud` uses isolated ephemeral memory. Source data and IAM are unaffected.

Implementation: the metric contracts/compiler/service, approved target-comparison adapter and forecast-value binding guard live in the backend. Frontend editors use structured fields, native validation, explicit publication, conflict recovery and unsaved-navigation warnings. SQL/metadata are rendered as escaped text.
