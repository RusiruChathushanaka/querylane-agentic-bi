# Querylane knowledge graph

Generated with the project-local [Graphify skill](../.agents/skills/graphify/SKILL.md) and Graphify 0.9.51 on 17 October 2026, after the verified TimesFM Cloud Run release.

- [graph.html](graph.html): interactive code/documentation graph. Search for `TimesFM`, `compare`, `prepare_series`, `ReportEngine`, `ReportRepository` or `PredictionEvidence`, then inspect the source/neighbor details. The viewer loads its pinned vis-network library from a CDN.
- [graph.json](graph.json): native graph with **1,996 nodes**, **5,353 edges** and **121 named communities**.
- [GRAPH_REPORT.md](GRAPH_REPORT.md): central concepts, community cohesion, cross-community links, questions and integrity notes.
- [VALIDATION.json](VALIDATION.json): source hashes, generation scope, diagnostics, verification and limitations.
- [cost.json](cost.json): separate model-API accounting; host-session semantic usage is unknown.

The corpus contains **193 code files and 49 documents** (~176,966 words). Local AST extraction covers code; 42 document extractions were reused and one host-session agent refreshed 7 changed documents in two passes (including the README correction). No separate model API, cloud database, provisioning or deployment was invoked. [`.graphifyignore`](../.graphifyignore) excludes credentials/environments, generated data, historical evaluation files and graph outputs. Machine-specific paths and extraction caches remain ignored.

## Latest forecasting coverage

The graph maps agent-prioritized candidate reservations, common chronological validation, fixed managed TimesFM queries, stable job recovery, immutable forecast/scenario artifacts, shared diagnostics and the worker-identity probe. [Hosted acceptance](../docs/evaluation/timesfm-deployed.md) passed 31 checks: actual worker ADC compatibility and report/scenario inference, immutable exports, presentation reuse, dashboard pinning and larger-data preservation. The API/worker gates are enabled in the recorded release; local defaults remain disabled. [TimesFM guidance](../docs/timesfm.md) describes the bounded controls. Graph extraction itself makes no cloud/model call and is not runtime verification.


## Use

From the repository root:

```bash
graphify query "TimesFM comparison job identity cancellation" --budget 1500
graphify explain "TimesFM"
graphify path "ReportEngine" "ExportStorage" --undirected
```

Invoke **`$graphify .`** in Codex for a full code/document refresh. `graphify update .` covers code-only maintenance; document changes still need semantic extraction. Keep the local skill aligned with the installed CLI. This refresh used the repository-local 0.9.51 skill without modifying older global skill installations.

## Interpretation and limits

Centrality reflects indexed code, tests and documentation, not production traffic or architectural quality. An undirected path through shared error handling does not establish a call between its endpoints. The graph retains the default undirected projection for compatibility; diagnostics record **826 unresolved endpoint references** and **491 collapsed same-endpoint relationships**, with zero missing endpoint fields and zero self-loops. Many unresolved references are external imports. Graphify reports a potentially partial parse of `Frontend/src/components/workspace.tsx` at line 1080 (13 extracted symbols).

This is a working-tree snapshot over base commit `3e9c685d`; per-file SHA-256 hashes establish the indexed content. Host-agent token counts are unavailable, not zero. Read the report/validation before assuming exhaustive coverage. The curated Mermaid views remain in [docs/graphify/](../docs/graphify/README.md); [deployment.json](../docs/deployment.json) records the last verified release. The larger `timeseries` dataset and serving application were unchanged by this refresh.
