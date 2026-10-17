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
| [application.mmd](application.mmd) | Public landing, `/app` workspace/API, text/live analysis, guarded sources, saved charts/dashboards and report dispatch | [Application boundaries](../architecture.md#application-boundaries) |
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
