# Querylane knowledge graph

Refreshed **21 October 2026** with the [project Graphify skill](../.agents/skills/graphify/SKILL.md), Graphify 0.9.51, from the working tree over `4a355ba2`. Per-file SHA-256 hashes in [VALIDATION.json](VALIDATION.json) identify indexed content.

- [graph.html](graph.html): interactive graph; pinned vis-network viewer library loads from a CDN.
- [graph.json](graph.json): 2,359 nodes, 6,326 edges, 157 named communities.
- [GRAPH_REPORT.md](GRAPH_REPORT.md): hubs, cohesion, connections and extraction diagnostics.
- [cost.json](cost.json): separate API accounting; host semantic-token usage is unknown.

Scope: 226 code files and 68 documents, approximately 222,794 words. Local AST extraction and one semantic agent refreshed eight documents; 60 cached document extractions were reused. Both Submission spellings, credentials, dependencies, generated data/media, historical evaluation files and graph output are excluded through [`.graphifyignore`](../.graphifyignore).

## Current coverage

The map includes report briefings and PDF/Word/full-row data bundles, immutable prior-version exports, shared `AppSelect`/Radix dropdown presentation, dashboard borders, the history-focused sidebar and 24 packaged playbooks. Empty/numeric choice adaptation and report section focus are browser presentation boundaries; they add no analytical execution. The [architecture](../docs/architecture.md) remains authoritative and its [curated Mermaid copies](../docs/graphify/README.md) are synchronized.

The [report/dropdown release](../docs/evaluation/report-dropdown-release-20261021.md) records actual worker/API/frontend deployment and presentation-only forecast/scenario versions. Graph generation performs no deployment or inference. Fresh numerical, AI Dashboard Builder and Forecast Plans acceptance remain separately scoped. Consult the dated assessment rather than treating graph edges as proof of runtime behavior.

## Refresh and interpretation

Use `$graphify .` for code plus changed-document semantics. `graphify update .` alone covers structural maintenance. The AST parser reports a potentially partial parse of `Frontend/src/components/workspace.tsx` at line 1141 (13 symbols). The undirected projection has 993 unresolved endpoint references and 592 collapsed same-endpoint relationships. Host token counts are unavailable, not zero. Community labels and centrality are navigation heuristics, not runtime traces.
