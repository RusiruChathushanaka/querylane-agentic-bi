# Querylane knowledge graph

Generated using the official project-local [Graphify skill](../.agents/skills/graphify/SKILL.md) and installed Graphify 0.9.51 package on 17 October 2026.

- [graph.html](graph.html): interactive code/documentation graph. Open locally; search for `ReportEngine`, `Dashboards` or `Skills` and click a result to inspect source/neighbor details. The viewer loads its pinned vis-network library from a CDN.
- [graph.json](graph.json): native Graphify graph, with **1,650 nodes**, **4,426 edges** and **119 named communities**.
- [GRAPH_REPORT.md](GRAPH_REPORT.md): central concepts, communities/cohesion, cross-community links, questions and integrity notes.
- [VALIDATION.json](VALIDATION.json): source hashes, generation scope, diagnostics, verification and limitations.
- [cost.json](cost.json): separate model-API token accounting; host-session semantic usage is explicitly unknown.

The corpus contains **170 code files and 44 documents**. Code extraction is local AST analysis; two host-session agents extracted document concepts. No separate model API, cloud database, provisioning or deployment was invoked. Generated/secret inputs are excluded by [`.graphifyignore`](../.graphifyignore).

## Use

From the repository root:

```bash
graphify query "dashboard downloads saved artifact revision" --budget 1500
graphify explain "ReportEngine"
graphify path "ReportEngine" "ExportStorage" --undirected
```

For a full code/document refresh, invoke **`$graphify .`** in Codex. Code-only maintenance uses `graphify update .`; documentation changes still need semantic re-extraction. Keep the installed project skill aligned with the CLI when upgrading. Some CLI invocations may warn about an older global skill; this generation used the repository-local 0.9.51 skill, without modifying global installations.

## Interpretation

`AppError`, `Settings` and `MemoryStore` are the highest-degree abstractions. Centrality reflects this indexed source/test corpus, not production traffic or architectural quality. An undirected path through shared error handling is not proof that its endpoints call each other.

The default graph projection combines some same-endpoint relationships. Raw diagnostics record **704 dangling-endpoint references**, **432 collapsed same-endpoint relationships**, zero missing endpoint fields and zero self-loops. Many dangling references are external imports such as standard-library or Google SDK modules. Graphify also reports a potentially partial parse of `Frontend/src/components/workspace.tsx` at line 1064. Consult the report and validation record before treating the graph as complete.

This is a working-tree source snapshot. Dated release plans/evidence can coexist in its documents; use [the deployment record](../docs/deployment.json) and inspect live state for deployment decisions. The curated Mermaid architecture views remain under [docs/graphify/](../docs/graphify/README.md).
