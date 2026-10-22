# Querylane Graphify and architecture graphs

The official Graphify skill is registered locally at `.agents/skills/graphify/SKILL.md`. It builds a queryable code-and-documentation graph in the repository's standard **[`graphify-out/`](../../graphify-out/)** folder. This directory also retains the standalone, curated Mermaid architecture views introduced on 17 October 2026.

## Generated Graphify output

| File | Purpose |
| --- | --- |
| [`graphify-out/graph.html`](../../graphify-out/graph.html) | Interactive graph with search, community filters and node/relationship inspection |
| [`graphify-out/graph.json`](../../graphify-out/graph.json) | Graphify-native machine-readable graph with source evidence, confidence and version metadata |
| [`graphify-out/GRAPH_REPORT.md`](../../graphify-out/GRAPH_REPORT.md) | Community/cohesion analysis, central concepts, cross-community connections and suggested questions |
| [`graphify-out/VALIDATION.json`](../../graphify-out/VALIDATION.json) | Generation scope, source hashes, integrity diagnostics and extraction limitations |

Generation uses the installed Graphify **0.9.51** package: local deterministic AST extraction for code, plus cached semantics and a host-session agent for changed document extraction. No separate model API or cloud database is invoked. Host-agent token usage is unavailable from the collaboration tool and is explicitly recorded as unknown. `.graphifyignore` excludes dependencies, environments, generated data/media, third-party skills, historical evaluation files and graph outputs. Local caches and machine-specific paths are Git-ignored; graph artifacts are excluded from Cloud Build.

Graphify's audit records unresolved external-reference endpoints, relationships collapsed by its default undirected graph, and a potentially partial tree-sitter parse of `Frontend/src/components/workspace.tsx`. These graphs help navigation; source files and feature contracts remain authoritative. Consult `VALIDATION.json` and the report for actual counts rather than assuming exhaustive extraction.

## Query and rebuild

From the repository root:

```bash
graphify query "dashboard downloads saved artifact revision" --budget 1500
graphify explain "ReportEngine"
graphify god-nodes --top 10
```

To regenerate code **and document semantics**, invoke the installed skill in Codex with **`$graphify .`**. The project-scoped skill can be re-registered with `graphify install --project --platform agents` when needed. The package is `graphifyy` (double y); the command is `graphify`. Runtime application dependencies do not include it.

`graphify update .` refreshes code extraction locally; it does not substitute for the skill's semantic pass over changed documents. Preserve existing source exclusions and check the resulting report/diagnostics. The generated report and JSON are dated working-tree snapshots, not proof of current deployment or runtime correctness.

## Graphs

| File | Scope | Source |
| --- | --- | --- |
| [application.mmd](application.mmd) | Public landing, history-focused `/app` workspace, Sources sheet, versioned playbooks, text/live analysis, guarded sources and saved evidence | [Application boundaries](../architecture.md#application-boundaries) |
| [reports.mmd](reports.mmd) | Report outbox, task dispatch, private worker, checkpoints, evidence, exports and isolated research | [Advanced analysis reports](../architecture.md#advanced-analysis-reports) |

The fenced Mermaid blocks in [architecture.md](../architecture.md) are authoritative for these two curated views. They are distinct from the generated Graphify graph. The architecture's source-code map identifies implementation owners. [Root agent instructions](../../AGENTS.md) describe when to update them.

The public API contains the voice bridge and author handlers. The report worker is a separate private service. Dashboard exports read immutable saved results; report execution can perform new guarded analytical work. Optional Search is disabled in the dated deployment record and stays outside public report evidence.

## Refresh

Run from the repository root after editing the architecture diagrams:

```bash
python3 - <<'PY'
import re
from pathlib import Path

source = Path("docs/architecture.md").read_text()
blocks = re.findall(r"^```mermaid\n(.*?)^```", source, re.M | re.S)
names = ("application", "reports")
if len(blocks) != len(names):
    raise SystemExit("Update the graph name mapping for added/removed diagrams.")
for name, block in zip(names, blocks, strict=True):
    Path(f"docs/graphify/{name}.mmd").write_text(block.rstrip() + "\n")
PY
```

Review each graph diff against its source modules and feature contracts. Verify both files match the corresponding fenced blocks byte-for-byte (after trailing-newline normalization), and check relative documentation links. Mermaid-capable Markdown viewers can render the source document; Mermaid tooling can consume the standalone files. Refreshing these files does not inspect cloud state or rerun application acceptance tests.

## Latest fix coverage

The refreshed graph includes nested SQL equality-key validation, per-invocation query/job identities, partial/final voice transcript handling, and shared table accessibility. Start at `validate_joins`, `linked_predicate`, `AnalysisService`, `voice_session` or `Table` in the viewer, then inspect the referenced source. The curated application diagram identifies the distinct analysis-ID boundary on the Live tool path.

The [deployed fix assessment](../evaluation/e2e-fixes-deployed.md) records the numerical, voice, report, dashboard and accessibility rechecks and their physical-device limitations. Its excluded historical evidence files are linked from documentation rather than ingested as raw result rows. The larger `timeseries` dataset is unchanged; this graph refresh performs no cloud reads, source writes or application deployment.

## Evidence and maintenance

- Use [deployment.json](../deployment.json) for the last recorded revisions, digests and active data profile; inspect live state for a deployment task.
- Use [validation.md](../validation.md) and [evaluation/](../evaluation/) for dated test evidence and limitations.
- Use [the deployment guide](../deployment-guide.md) before cloud operations. Diagram maintenance does not authorize deployment, seeding, IAM changes or history resets.
- Keep credentials, raw database rows, visitor transcripts and generated analytical bundles outside graph references.

## Managed forecasting release coverage

The latest map includes `TimesFM`, `compare`, `reserve_candidates`, shared series preparation, deterministic inference recovery, immutable prediction/scenario artifacts and the worker-identity release probe. [TimesFM guidance](../timesfm.md) separates disabled local defaults from the verified enabled hosted release. [The deployed assessment](../evaluation/timesfm-deployed.md) records the actual worker gate, 31 analytical/reuse checks and unchanged larger data; the graph itself is navigation evidence rather than a runtime test.

## TimesFM landing preview coverage

The refreshed map includes `ProductTour`, `ScenarioIllustration`, the four preview views, fixed saved-version evidence links, packaged model-comparison/scenario values and `/app` entry boundaries. The [landing-only release](../evaluation/landing-timesfm-deployed.md) records frontend `00016-tw2` with backend `00021-6rd` and worker `00010-wnw` unchanged. The separate [TimesFM assessment](../evaluation/timesfm-deployed.md) records numerical forecasts and scenarios; graph generation does not repeat inference. Both analytical runtimes preserve the larger `timeseries` profile, 30,000-row limit and verified enabled TimesFM gates. Local/unverified environments still require the compatibility gate.

The application diagram distinguishes static preview content from an explicit evidence-link navigation to a saved report. Historical evaluation JSON and `deployment.json` remain excluded from raw graph ingestion; the graph indexes their documented references without treating old observations as live discovery.

## Metrics and planning release coverage

The source map includes the public metric compiler/revisions, reviewed AI dashboard jobs and adaptive hierarchical planning. See [Metrics](../business-metrics.md), [Dashboard Builder](../ai-dashboard-builder.md) and [Forecast Plans](../forecast-plans.md). They are included in the dated 18 October deployment; consult its release record for actual serving revisions and verification boundaries. Preserve shared worker quotas/fencing, old report workflows, exact-version evidence and modeled/allocated/adjusted distinctions in graph updates.

The [18 October planning release](../evaluation/planning-release-20261018.md) records deployed Metrics, reviewed AI dashboards and Forecast Plans, 129 hosted checks, and both final metric-intent/SDK corrections. Its quota-limited hosted acceptance is distinct from the local 237-node numerical evidence; graph relationships are not proof of successful fresh worker execution.

The final metric-agent map includes `requests_ad_hoc` and `AI._structured_once`: affirmative ad hoc requests, negated opt-outs, JSON metric scope, strict filter validation, frozen definitions and controlled compilation. That planning release recorded frontend `00017-dxz`, API `00024-rnd` and worker `00013-sm4`; the later sidebar release advances only the frontend. Regenerating this graph runs no model-backed analytics or live deployment checks.

## Sidebar and expanded skills coverage

The application diagram now places source/schema inspection in the header **Sources** sheet, leaving the sidebar for history and navigation with one **New exploration** action. Query source selection stays in the composer. Inspect `Workspace` and [the architecture contract](../architecture.md#workspace-navigation-and-source-inspection) for schema loading, stale-response protection and focus behavior. [Sidebar release evidence](../evaluation/sidebar-release-20261018.md) records frontend `00018-kd4` and the unchanged API/worker.

The semantic graph includes all 24 packaged [analytics/prediction playbooks](../analytics-skills.md), including metric definitions, dashboard design/evidence, TimesFM comparison, hierarchy planning, management adjustments and outturn review. [Publication evidence](../evaluation/advanced-feature-skills-20261018.json) records 12 insert-only additions and 29 active hosted entries; these dated counts are not a live catalog query. Metadata discovery, manual priority and immutable three-skill snapshots remain the execution boundary. Playbooks add no tools or permissions.

The [post-reset TimesFM assessment](../evaluation/final-e2e-20261018-fresh.md) closes the earlier ordinary-report quota gap with 31 fresh checks; it leaves separate AI Dashboard Builder/Forecast Plans worker acceptance outstanding. Historical evidence remains excluded from graph ingestion, while its documented references retain these distinctions. Existing mobile-library overflow, physical-device and contrast-review limits are not resolved by graph regeneration.

## Navigation icon release coverage

The current map includes the shared desktop/mobile Business metrics and Forecast plans links, their decorative `Target`/`TrendingUp` icons, and the [18 October icon release](../evaluation/navigation-icons-release-20261018.md). That dated release records frontend `00019-gvr`, API `00024-rnd` and worker `00013-sm4`, candidate testing before promotion, settled keyboard/accessibility checks and unchanged larger-data/TimesFM configuration. The initial transition-time observations remain distinguishable from settled results. BigQuery preservation used metadata, not a new content scan; PostgreSQL was not recounted.

The two curated Mermaid diagrams remain unchanged because icons introduce no service or dataflow boundary. Generated code/document semantics, source hashes, community analysis and HTML are refreshed together. This documentation refresh neither repeats the release nor reruns its application tests, cloud inspection or inference.

## Report briefing and shared dropdown coverage

The [21 October report/dropdown release](../evaluation/report-dropdown-release-20261021.md) adds consistent report sections and a shared Radix choice adapter across libraries, authoring and chart controls. The application diagram now identifies this browser-only component boundary. The generated map refreshes code and changed-document semantics, including report export presentation and immutable saved-evidence reuse. Its graph generation invokes no analytical work; actual worker/download/browser checks remain in the dated assessment. Both Submission spellings are excluded from graph/build/Git scope.

### Documentation synchronization after publication

The documentation follow-up indexes the published report/dropdown implementation in commit [`82e9f7a`](https://github.com/RusiruChathushanaka/querylane-agentic-bi/commit/82e9f7a538a684acf2bf061661e45de5d2aa553b). README now identifies frontend `00023-hsg`, API `00025-8ml` and private worker `00014-kgl` as the latest recorded release, retaining earlier releases as history. AGENTS and architecture describe immutable new-version exports, complete future-point/scenario evidence, the 36-control shared dropdown adapter and focused regression checks. This follow-up refreshes document semantics and graph hashes only; it performs no deployment, source/model operation or new runtime verification. The two architecture Mermaid flows remain unchanged and synchronized.


## Startup resource lifecycle (local preparation)

The application diagram adds the browser-only independent read/loading/retry boundary. Code/document semantics include `useReadResource`, `ResourceFeedback`, initial GET retry limits, parallel source checks and the warm-API release policy. See [startup loading](../startup-loading.md) and its [local assessment](../evaluation/startup-loading-local-20261021.md). Graph generation and local tests neither deploy a warm instance nor establish production latency improvement. Landing-page isolation, mutation/inference boundaries, data/TimesFM settings and historical release evidence remain authoritative.

## Viewport workspace and nearby saved charts

The local workspace update contains header/sidebar/composer within the viewport and directs automatic scrolling only to the conversation. Positioned chart figures contain hidden accessibility instructions. Nearby saved conversation cards use IntersectionObserver and the bounded shared saved-result loader; unchanged JSON reads preserve React identity. The warm-service policy is prepared for frontend and API, with worker scaling preserved. See [startup behavior](../startup-loading.md) and [local verification](../evaluation/workspace-layout-local-20261022.md). Graph refresh does not deploy these changes or rerun analytics.

The [22 October UTC workspace/loading release](../evaluation/workspace-loading-release-20261022.md) verifies frontend/API service minima one, viewport scroll ownership, nearby saved-chart reads and a narrow Skills header correction. Source-hashed knowledge-graph generation is separate from hosted runtime acceptance.

The [23 October local loading optimization](../evaluation/loading-speed-local-20261023.md) adds application runtime bootstrap, conditional transport/timing, short UI status snapshots, bounded immutable views and nearby report evidence. The graph describes implemented local behavior; it does not establish a new deployment or change warm-service settings.

The [23 October local-date hosted loading-speed release](../evaluation/loading-speed-release-20261023.md) records runtime bootstrap, conditional/gzip reads, nearby report charts and saved-view reuse. Warm settings/data/TimesFM and immutable exports are preserved. Browser median/request reductions and the p95 outlier are distinct from graph extraction evidence.
