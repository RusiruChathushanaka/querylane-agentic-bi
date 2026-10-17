# Querylane knowledge graph

Generated with the project-local [Graphify skill](../.agents/skills/graphify/SKILL.md) and Graphify **0.9.51** on **18 October 2026**, from the current implementation working tree.

- [graph.html](graph.html): interactive search, named communities and source/relationship inspection. The viewer loads its pinned vis-network library from a CDN.
- [graph.json](graph.json): **2,314 nodes, 6,251 edges and 131 named communities**.
- [GRAPH_REPORT.md](GRAPH_REPORT.md): hubs, cohesion, cross-community links and suggested questions.
- [VALIDATION.json](VALIDATION.json): source hashes, extraction diagnostics, generation scope and verification limits.
- [cost.json](cost.json): separate model-API accounting; host-session semantic token usage is unknown.

The corpus contains **220 code files and 56 documents**, approximately **209,431 words**. Deterministic local AST extraction covers code; 52 document extractions were reused and one host-session semantic agent refreshed four documents. Graph generation made no separate model API or cloud calls. [`.graphifyignore`](../.graphifyignore) excludes dependencies, credentials, third-party skills, generated data/media, historical evaluation JSON, deployment JSON and graph outputs.

## New implementation coverage

Start with `requests_ad_hoc`, `AI._structured_once`, `Metrics`, `compile_metric`, `PlanningEngine`, `DashboardBuilder`, `ForecastPlans`, `reconcile`, `adjust_plan`, `preserve_analysis_settings` or `purge_planning`. The graph maps shared published metric revisions and canonical calculations, bounded durable dashboard proposals, explicit atomic publication/rebase/Undo, and coherent company/geography/product planning with separate adjustment versions and saved-only exports.

The [local implementation assessment](../docs/evaluation/planning-local-20261018.md) records 433 backend tests, 53 frontend tests, build/lint/type checks, a 237-node larger-bundle plan, adjustments, saved-plan report/dashboard integration and browser checks. The [18 October release](../docs/evaluation/planning-release-20261018.md) deploys the worker, API and frontend. The final release record contains 129 hosted checks (121 core plus eight final metric-guided text/Live checks), 442 backend tests and 53 frontend tests after metric-intent and SDK-schema corrections. This documentation refresh did not rerun them. Fresh hosted builder/plan execution was quota-denied during the recorded tests and still requires its own acceptance run. Fixture planning and local statistical validation do not establish fresh hosted Gemini, TimesFM, Firestore contention or Cloud Tasks acceptance.

## Existing TimesFM and landing coverage

The map retains managed candidate comparison, deterministic inference recovery, explicit conditional scenarios, preview boundaries and immutable report links. [TimesFM acceptance](../docs/evaluation/timesfm-deployed.md) and [landing acceptance](../docs/evaluation/landing-timesfm-deployed.md) remain dated deployed evidence. Their historical serving records remain unchanged; the later planning release preserves the larger source profile and verified TimesFM gates.

## Use and refresh

```bash
graphify query "metric compiler dashboard proposal forecast reconciliation" --budget 1500
graphify explain "PlanningEngine"
graphify path "Metrics" "ForecastPlans"
```

Use **`$graphify .`** to refresh both code and changed-document semantics. `graphify update .` covers structural code maintenance. The matching local skill is used directly; CLI tools also warn about an older global 0.9.42 skill, which this implementation did not change. Curated Mermaid copies in [docs/graphify/](../docs/graphify/README.md) match the authoritative architecture blocks.

## Interpretation and limitations

This is a working-tree snapshot over base commit `2ec5d397`; per-file SHA-256 hashes identify the actual indexed content. Source files and feature contracts remain authoritative. The undirected projection reports **923 unresolved endpoint references and 583 collapsed same-endpoint relationships**, with zero missing endpoint fields and zero self-loops. External imports explain many unresolved references. Tree-sitter reports a potentially partial parse of `Frontend/src/components/workspace.tsx` at line 1082 (13 extracted symbols). Host semantic-token usage is unavailable, not zero.

The corpus-aware navigation benchmark estimates 11.9× fewer tokens than reading the entire corpus; it is a traversal heuristic rather than a measured application/model performance claim. Consult [deployment.json](../docs/deployment.json) for dated serving configuration and [validation.md](../docs/validation.md) for actual application evidence.
