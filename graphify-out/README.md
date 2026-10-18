# Querylane knowledge graph

Generated with the project-local [Graphify skill](../.agents/skills/graphify/SKILL.md) and Graphify **0.9.51** on **18 October 2026**, from the implementation working tree over base `3dbebe41`.

- [graph.html](graph.html): interactive search, named communities and source/relationship inspection. The viewer loads its pinned vis-network library from a CDN.
- [graph.json](graph.json): **2,473 nodes, 6,578 edges and 134 named communities**.
- [GRAPH_REPORT.md](GRAPH_REPORT.md): hubs, cohesion, cross-community links and suggested questions.
- [VALIDATION.json](VALIDATION.json): source hashes, extraction diagnostics, generation scope and verification limits.
- [cost.json](cost.json): separate model-API accounting; host-session semantic token usage is unknown.

The corpus contains **220 code files and 68 documents**, approximately **215,149 words**. Local AST extraction covers code; 64 document extractions were reused and one host-session semantic agent refreshed 4 documents. No separate model API or cloud/database operation was invoked. [`.graphifyignore`](../.graphifyignore) excludes dependencies, credentials, third-party skills, generated data/media, historical evaluation files and graph outputs. Local caches and machine paths remain ignored.

## Navigation and curated skill coverage

The [workspace architecture](../docs/architecture.md#workspace-navigation-and-source-inspection) places source inspection in the header **Sources** sheet, with one **New exploration** action and more sidebar space for public history. Query source selection remains in the composer. `Workspace` owns guarded asynchronous schema loading and the responsive controls; the AST limitation below means its internal functions may not appear individually.

The graph includes all **24 packaged playbooks**: 16 analytics and eight prediction skills. Search for **AI dashboard objectives and card design**, **Published metrics and definition consistency**, **TimesFM candidate comparison and evidence**, or **Forecast plan adjustments and assumption disclosure**. [The catalog](../docs/analytics-skills.md) describes each guide. Explicit insert-only seeding preserves visitor changes and deleted entries. Automatic/manual discovery retains a three-skill budget and immutable versions; playbooks add no execution tools or permissions.

[The navigation icon release](../docs/evaluation/navigation-icons-release-20261018.md), published in commit `3dbebe4`, records frontend `00019-gvr` at full traffic, with API `00024-rnd` and worker `00013-sm4` unchanged. Business metrics uses `Target` and Forecast plans `TrendingUp`, matching the other links at 16px with decorative SVGs and native labels. Desktop/mobile, keyboard activation and settled accessibility checks passed. The evidence retains initial transition-time observations alongside settled rechecks. Source preservation used BigQuery metadata, without a new content scan or PostgreSQL recount. The earlier [sidebar release](../docs/evaluation/sidebar-release-20261018.md) remains dated history. [Skill publication evidence](../docs/evaluation/advanced-feature-skills-20261018.json) records 12 additions, 29 active hosted entries and four Gemini selection probes, without analytical execution. The recorded Skills-library header overflow at 390px remains unresolved.

## Verification boundaries

The [post-reset assessment](../docs/evaluation/final-e2e-20261018-fresh.md) records 31 fresh TimesFM forecast/scenario, download, replay and pin checks. It closes the earlier ordinary-report admission gap while preserving the larger dataset and runtime settings. The [aggregate final assessment](../docs/evaluation/final-e2e-20261018.md) preserves the original quota-denied attempt and physical-device/contrast-review limits. The separate [planning release](../docs/evaluation/planning-release-20261018.md) still requires fresh AI Dashboard Builder and Forecast Plans worker acceptance. A graph relationship establishes no runtime test outcome.

The map retains metric compilation, reviewed dashboard publication, coherent hierarchy allocations, separate management adjustments, fixed managed-inference jobs, durable recovery and static landing previews. Saved reports, dashboards and downloads reuse immutable evidence. [Deployment records](../docs/deployment.json) are dated observations; this refresh performs no deployment, seeding, source query, quota change or inference.

## Use and refresh

```bash
graphify query "Sources schema sidebar history" --budget 1500
graphify query "TimesFM hierarchical planning skills evidence" --budget 1500
graphify explain "Workspace"
```

Use **`$graphify .`** to refresh both code and changed-document semantics. `graphify update .` covers structural code maintenance. Curated Mermaid copies in [docs/graphify/](../docs/graphify/README.md) match the authoritative architecture blocks. Source hashes in the validation record establish freshness across documentation commits; base commit identity alone is insufficient.

## Interpretation and limitations

The default undirected projection reports **916 unresolved endpoint references and 587 collapsed same-endpoint relationships**, with **0 missing endpoint fields and 0 self-loops**. External imports explain many unresolved references; absent entities are not invented. Tree-sitter reports a potentially partial parse of `Frontend/src/components/workspace.tsx` at line 1127 (13 extracted symbols). Community names and centrality are navigation heuristics rather than runtime traces. Host semantic-token usage is unavailable, not zero. Consult [VALIDATION.json](VALIDATION.json) before assuming exhaustive extraction.
