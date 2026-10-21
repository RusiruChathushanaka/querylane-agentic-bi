# Querylane knowledge graph

Refreshed **21 October 2026** with the [project Graphify skill](../.agents/skills/graphify/SKILL.md), Graphify 0.9.51, as a documentation follow-up to published implementation commit [`82e9f7a`](https://github.com/RusiruChathushanaka/querylane-agentic-bi/commit/82e9f7a538a684acf2bf061661e45de5d2aa553b). Per-file SHA-256 hashes in [VALIDATION.json](VALIDATION.json) identify the indexed working tree over `82e9f7a5`.

- [graph.html](graph.html): interactive graph; its pinned vis-network viewer loads from a CDN.
- [graph.json](graph.json): 2,369 nodes, 6,395 edges and 148 named communities.
- [GRAPH_REPORT.md](GRAPH_REPORT.md): hubs, cohesion, relationships and scope limitations.
- [cost.json](cost.json): separate model-API accounting; host semantic-token usage is unknown.

Scope: 226 code files and 68 documents, approximately 223,073 words. One host-session agent refreshed 3 changed documents; 65 unchanged document extractions were reused. Both Submission spellings, credentials, dependencies, generated data/media, historical evaluation files and graph output stay excluded through [`.graphifyignore`](../.graphifyignore).

## Report design and shared dropdowns

The map covers bordered report sections, saved-document titles, responsive navigation, complete future-point tables, explicit scenario paths and structured forecast diagnostics. PDF/Word/data ZIP rendering occurs at new-version publication, with original exported bytes and full-precision CSV/prediction provenance retained. Shared `AppSelect`/Radix dropdowns unify 36 controls across reports, dashboards, metrics, planning and charts, preserving empty/numeric values, portaled scrolling, themes and keyboard focus. Action menus and multi-select checkboxes keep their distinct behavior.

The [recorded release](../docs/evaluation/report-dropdown-release-20261021.md) served frontend `00023-hsg`, API `00025-8ml` and private worker `00014-kgl`, preserving the larger dataset and verified enabled TimesFM gates. Two presentation-only worker runs and six exports passed; this is saved-evidence reuse, not fresh numerical forecasting. [README](../README.md), [AGENTS](../AGENTS.md) and [architecture](../docs/architecture.md) distinguish that latest release from earlier dashboard/navigation history. No application code, deployment record, cloud service, dataset or model was changed by this documentation follow-up.

## Refresh and limits

Use `$graphify .` for code plus changed-document semantics. The [curated Mermaid views](../docs/graphify/README.md) remain synchronized with the authoritative architecture. Compare hashes as well as the base commit for freshness; graph relationships are navigation evidence, not runtime proof.

The AST parser reports a potentially partial parse of `Frontend/src/components/workspace.tsx` at line 1141 (13 symbols). The undirected projection reports 993 unresolved endpoint references and 594 collapsed same-endpoint relationships. External imports are not fabricated as project entities. Host semantic-token counts remain unavailable, not zero.
