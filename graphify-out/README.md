# Querylane knowledge graph

Refreshed **22 October 2026 UTC** with the [project Graphify skill](../.agents/skills/graphify/SKILL.md), Graphify 0.9.51, for the deployed workspace/loading implementation; hosted verification is recorded separately. Per-file SHA-256 hashes in [VALIDATION.json](VALIDATION.json) identify the indexed working tree over `221b8253`.

- [graph.html](graph.html): interactive graph; its pinned vis-network viewer loads from a CDN.
- [graph.json](graph.json): 2,395 nodes, 6,488 edges and 158 named communities.
- [GRAPH_REPORT.md](GRAPH_REPORT.md): hubs, cohesion, relationships and scope limitations.
- [cost.json](cost.json): separate model-API accounting; host semantic-token usage is unknown.

Scope: 234 code files and 69 documents, approximately 227,332 words. One host-session agent refreshed 7 changed documents; 62 unchanged document extractions were reused. Both Submission spellings, credentials, dependencies, generated data/media, historical evaluation files and graph output stay excluded through [`.graphifyignore`](../.graphifyignore).

## Independent startup loading and warm services

The map includes viewport-owned conversation/history scrolling, nearby saved charts, unchanged-read identity and independent workspace history/source/report configuration reads, immediate deep-linked conversation text, saved report/card placeholders, shared slow/error/retry feedback and backend source-check concurrency. Initial GETs have one transient retry; initial failure stops polling until manual retry, background failures retain content and Retry-After bounds recovery. Mutations, guest-session POSTs and inference remain outside this policy. The release helper enforces service-level frontend and API minima one without resetting worker scaling or existing ceilings. The [hosted workspace/loading assessment](../docs/evaluation/workspace-loading-release-20261022.md) verifies service minima one on frontend and API. See [startup behavior](../docs/startup-loading.md) and [local verification](../docs/evaluation/startup-loading-local-20261021.md).

## Existing report design and shared dropdowns

The map covers bordered report sections, saved-document titles, responsive navigation, complete future-point tables, explicit scenario paths and structured forecast diagnostics. PDF/Word/data ZIP rendering occurs at new-version publication, with original exported bytes and full-precision CSV/prediction provenance retained. Shared `AppSelect`/Radix dropdowns unify 36 controls across reports, dashboards, metrics, planning and charts, preserving empty/numeric values, portaled scrolling, themes and keyboard focus. Action menus and multi-select checkboxes keep their distinct behavior.

The [recorded release](../docs/evaluation/report-dropdown-release-20261021.md) served frontend `00023-hsg`, API `00025-8ml` and private worker `00014-kgl`, preserving the larger dataset and verified enabled TimesFM gates. Two presentation-only worker runs and six exports passed; this is saved-evidence reuse, not fresh numerical forecasting. [README](../README.md), [AGENTS](../AGENTS.md) and [architecture](../docs/architecture.md) distinguish that historical release from the later workspace/loading release. The startup implementation changes browser loading and availability-check concurrency; graph generation itself changes no cloud service, analytical dataset or model. The later hosted workspace/loading release is recorded separately.

## Refresh and limits

Use `$graphify .` for code plus changed-document semantics. The [curated Mermaid views](../docs/graphify/README.md) remain synchronized with the authoritative architecture. Compare hashes as well as the base commit for freshness; graph relationships are navigation evidence, not runtime proof.

The AST parser reports a potentially partial parse of `Frontend/src/components/workspace.tsx` at line 1101 (14 symbols). The undirected projection reports 1016 unresolved endpoint references and 585 collapsed same-endpoint relationships. External imports are not fabricated as project entities. Host semantic-token counts remain unavailable, not zero.
