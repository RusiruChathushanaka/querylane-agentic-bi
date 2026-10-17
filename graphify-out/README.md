# Querylane knowledge graph

Generated with the project-local [Graphify skill](../.agents/skills/graphify/SKILL.md) and Graphify 0.9.51 on 17 October 2026, after the analytics/voice fix release.

- [graph.html](graph.html): interactive code/documentation graph. Search for `validate_joins`, `linked_predicate`, `AnalysisService`, `voice_session`, `Table` or `ReportEngine`, then inspect the source/neighbor details. The viewer loads its pinned vis-network library from a CDN.
- [graph.json](graph.json): native graph with **1,797 nodes**, **4,772 edges** and **129 named communities**.
- [GRAPH_REPORT.md](GRAPH_REPORT.md): central concepts, community cohesion, cross-community links, questions and integrity notes.
- [VALIDATION.json](VALIDATION.json): source hashes, generation scope, diagnostics, verification and limitations.
- [cost.json](cost.json): separate model-API accounting; host-session semantic usage is unknown.

The corpus contains **181 code files and 46 documents** (~161,087 words). Local AST extraction covers code; 41 document extractions were reused and one host-session agent refreshed 5 changed documents. No separate model API, cloud database, provisioning or deployment was invoked. [`.graphifyignore`](../.graphifyignore) excludes credentials/environments, generated data, historical evaluation files and graph outputs. Machine-specific paths and extraction caches remain ignored.

## Latest fix coverage

The graph now maps nested explicit-key SQL join validation, invocation-scoped query/job identities, partial/final transcript replacement with turn-scoped deduplication, and shared table accessibility. It also includes the new deterministic SQL/voice/table regressions and repeated-tool Live smoke harness. The [deployed assessment](../docs/evaluation/e2e-fixes-deployed.md) remains the source for hosted results and test boundaries; the graph itself does not verify runtime behavior.

## Use

From the repository root:

```bash
graphify query "voice analysis query identity cancellation" --budget 1500
graphify explain "validate_joins"
graphify path "ReportEngine" "ExportStorage" --undirected
```

Invoke **`$graphify .`** in Codex for a full code/document refresh. `graphify update .` covers code-only maintenance; document changes still need semantic extraction. Keep the local skill aligned with the installed CLI. This refresh used the repository-local 0.9.51 skill without modifying older global skill installations.

## Interpretation and limits

Centrality reflects indexed code, tests and documentation, not production traffic or architectural quality. An undirected path through shared error handling does not establish a call between its endpoints. The graph retains the default undirected projection for compatibility; diagnostics record **750 unresolved endpoint references** and **438 collapsed same-endpoint relationships**, with zero missing endpoint fields and zero self-loops. Many unresolved references are external imports. Graphify reports a potentially partial parse of `Frontend/src/components/workspace.tsx` at line 1075 (13 extracted symbols). The AST extractor automatically completed sequentially after its initial multiprocessing attempt from stdin failed.

This is a working-tree snapshot over base commit `97315c59`; per-file SHA-256 hashes establish the indexed content. Host-agent token counts are unavailable, not zero. Read the report/validation before assuming exhaustive coverage. The curated Mermaid views remain in [docs/graphify/](../docs/graphify/README.md); [deployment.json](../docs/deployment.json) records the last verified release. The larger `timeseries` dataset and serving application were unchanged by this refresh.
