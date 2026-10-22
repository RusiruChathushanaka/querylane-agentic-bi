# Querylane knowledge graph

Refreshed **23 October 2026** using the [Graphify skill](../.agents/skills/graphify/SKILL.md), Graphify 0.9.51. This is the deployed loading-speed implementation over `7db9c58fa7641b48094480f6c0fd4c3d46072828`; actual Cloud Run release evidence is recorded separately and GitHub publication follows verification. [VALIDATION.json](VALIDATION.json) records exact working-tree source hashes.

- [graph.html](graph.html): interactive viewer, with a pinned CDN dependency.
- [graph.json](graph.json): 2,462 nodes, 6,614 edges and 160 named communities.
- [GRAPH_REPORT.md](GRAPH_REPORT.md): relationships, extraction scope and limitations.
- [cost.json](cost.json): separate model-API accounting; host semantic-token usage is unavailable, not zero.

Scope: 248 code files and 69 documents, approximately 230,890 words. One host-session semantic agent refreshed 6 changed documents; 63 unchanged document extractions were reused. [`.graphifyignore`](../.graphifyignore) excludes both Submission spellings, credentials, dependencies, generated data/media, historical assessments and graph output.

## Current deployed implementation

The map includes application-only runtime HTML configuration, bounded conditional public reads, non-overlapping idle/focus refreshes, gzip/timing for eligible JSON, short successful source-status snapshots and saved-chart reuse with live artifact checks. Nearby report charts load independently from narrative and immutable downloads. Initial bootstrap retry, cancellation, stale-response and retained-content behavior remain intact. Fresh execution/readiness checks, analytical limits and TimesFM gates are preserved. See [startup lifecycle](../docs/startup-loading.md), [architecture](../docs/architecture.md) and [local verification](../docs/evaluation/loading-speed-local-20261023.md).

The [23 October local-date loading-speed release](../docs/evaluation/loading-speed-release-20261023.md) records frontend `00026-g5t`, API `00027-cgw` and worker `00016-477`, with unchanged minima 1/1/0. Its 23 hosted HTTP checks, 24 preservation checks, desktop/mobile checks and six identical downloads are separate from graph extraction. Ten-sample median/request counts improved; a retained browser p95 outlier prevents a universal latency claim. No fresh forecasting or planning-worker acceptance is implied. The [prior release](../docs/evaluation/workspace-loading-release-20261022.md) remains historical.

## Refresh and limits

Use the Graphify skill for AST extraction plus changed-document semantics. The [curated Mermaid diagrams](../docs/graphify/README.md) remain derived from authoritative architecture blocks. Compare source hashes as well as the base commit for freshness.

The AST parser reports potentially partial extraction of `Frontend/src/components/workspace.tsx` at line 1112 (14 symbols). The undirected projection reports 1079 unresolved endpoint references and 589 collapsed relationships. External imports are not fabricated as project entities; graph navigation does not prove runtime behavior.
