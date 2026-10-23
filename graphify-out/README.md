# Querylane knowledge graph

Refreshed **23 October 2026** using the [Graphify skill](../.agents/skills/graphify/SKILL.md), Graphify 0.9.51. This is the hosted loading-contention release source over `d6727163b9e1ec27441bd0875dd7fe09ad19d05b`; immutable build source and actual serving revisions are recorded separately. [VALIDATION.json](VALIDATION.json) records exact working-tree source hashes.

- [graph.html](graph.html): interactive viewer, with a pinned CDN dependency.
- [graph.json](graph.json): 2,486 nodes, 6,713 edges and 156 named communities.
- [GRAPH_REPORT.md](GRAPH_REPORT.md): relationships, extraction scope and limitations.
- [cost.json](cost.json): separate model-API accounting; host semantic-token usage is unavailable, not zero.

Scope: 252 code files and 69 documents, approximately 232,701 words. One host-session semantic agent refreshed 9 changed documents; 60 unchanged document extractions were reused. [`.graphifyignore`](../.graphifyignore) excludes both Submission spellings, credentials, dependencies, generated data/media, historical assessments and graph output.

## Current implementation

The map includes shared click-only AppLink navigation, parallel admitted saved-card code and metadata, stable synchronous ready-component reuse, the existing split dynamic fallback, exact-origin Timing-Allow-Origin and fresh safe per-read correlation IDs. Initial read retry/cancellation, bounded evidence concurrency, off-screen deferral and immutable exports remain intact. Fresh execution/readiness checks, analytical limits and TimesFM gates are preserved. See [startup lifecycle](../docs/startup-loading.md), [architecture](../docs/architecture.md) and [local verification](../docs/evaluation/loading-contention-local-20261023.md).

The [loading-contention release](../docs/evaluation/loading-contention-release-20261023.md) is the latest deployment record: frontend `00027-26h`, API `00028-4rq`, worker `00017-ghr`. Frontend/API minima one, worker scaling, TimesFM and dataset settings were not changed. Twenty new hosted warm traces did not reproduce the historical 4.52s stall, whose exact cause remains unproven. Ten hosted warm samples improve chart-ready median 1.14s to 0.87s, with post-data wait 314ms to 8ms and speculative route requests twenty to zero. Endpoint timings vary; no universal speedup or new worker inference acceptance is claimed.

## Refresh and limits

Use the Graphify skill for AST extraction plus changed-document semantics. The [curated Mermaid diagrams](../docs/graphify/README.md) remain derived from authoritative architecture blocks. Compare source hashes as well as the base commit for freshness.

The AST parser reports potentially partial extraction of `Frontend/src/components/workspace.tsx` at line 1109 (13 symbols). The undirected projection reports 1068 unresolved endpoint references and 591 collapsed relationships. External imports are not fabricated as project entities; graph navigation does not prove runtime behavior.
