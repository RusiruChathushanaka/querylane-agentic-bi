# Querylane knowledge graph

Generated with the project-local [Graphify skill](../.agents/skills/graphify/SKILL.md) and Graphify 0.9.51 on 2026-10-17, after the verified TimesFM analytical and landing-page releases.

- [graph.html](graph.html): interactive graph with search and named communities. Try `TimesFM`, `ReportEngine`, `ProductTour`, `ScenarioIllustration` or `Landing Page`. The viewer loads its pinned vis-network library from a CDN.
- [graph.json](graph.json): native graph with **2,037 nodes**, **5,397 edges** and **113 named communities**.
- [GRAPH_REPORT.md](GRAPH_REPORT.md): central concepts, cohesion, cross-community connections and suggested questions.
- [VALIDATION.json](VALIDATION.json): source hashes, extraction diagnostics, scope and verification limits.
- [cost.json](cost.json): separate model-API accounting; host-session semantic token usage is unknown.

The corpus contains **193 code files and 49 documents** (~179,380 words). Local AST extraction covers code; 44 document extractions were reused and one host-session agent refreshed 5 documents. No separate model API, cloud/database read or write, provisioning or deployment was invoked. [`.graphifyignore`](../.graphifyignore) excludes environments, generated data/media, raw historical evaluation files, deployment JSON, third-party skills and graph outputs. Machine-specific paths and caches remain ignored.

## TimesFM and landing coverage

The graph maps agent-proposed forecasts, measured chronological candidate selection, immutable captured inputs, fixed BigQuery TimesFM jobs, deterministic recovery, statistical fallback and explicit conditional driver paths. [TimesFM hosted acceptance](../docs/evaluation/timesfm-deployed.md) records 31 actual analytical/reuse checks and worker-identity verification. API/worker gates are enabled in that recorded release; local defaults and unverified environments remain disabled. The graph does not itself establish runtime access or forecast quality.

The four local previews—Reports, Forecasts, Scenarios and Voice BI—use packaged examples. `ProductTour` and `ScenarioIllustration` expose saved monthly model comparisons and fourteen-day baseline/alternative paths, with cutoff, Preview and uncertainty/association caveats. Evidence links target immutable report version 1; primary CTAs enter `/app` without sign-in. Preview browsing makes no backend or microphone calls. [Landing acceptance](../docs/evaluation/landing-timesfm-deployed.md) records frontend `00016-tw2`, backend `00021-6rd` and worker `00010-wnw`; the frontend-only release preserved analytical runtime settings and the larger dataset.

## Use

```bash
graphify query "TimesFM comparison job identity cancellation" --budget 1500
graphify query "landing preview saved scenario report evidence" --budget 1500
graphify explain "ScenarioIllustration"
```

From the repository root, invoke **`$graphify .`** for a code/document refresh. `graphify update .` covers code-only maintenance; changed documents also need the skill's semantic pass. Keep the local skill aligned with installed Graphify. Curated Mermaid copies live in [docs/graphify/](../docs/graphify/README.md), derived from authoritative architecture blocks.

## Interpretation and limits

This is a working-tree snapshot over base commit `ec84f540`. Per-file SHA-256 hashes identify indexed content. Centrality/community links are navigation heuristics, not execution traces. The undirected projection can combine relationships: diagnostics record **829 unresolved endpoints** and **521 collapsed same-endpoint relationships**, with zero missing endpoint fields and zero self-loops. External references explain many unresolved nodes. Graphify reports a potentially partial parse of `Frontend/src/components/workspace.tsx` at line 1080 (13 extracted symbols). Host-session token usage is unavailable, not zero.

See [deployment.json](../docs/deployment.json) for dated serving configuration and [validation.md](../docs/validation.md) for test evidence. This documentation refresh did not rerun application tests, inference or cloud checks and did not alter the larger `timeseries` dataset, `SOURCE_ROW_LIMIT=30000`, TimesFM gates or deployed services.

The CLI query smoke passed and found the saved scenario evidence and `ScenarioIllustration` source node. Its 1,500-token view was explicitly truncated. The CLI warns about an older global 0.9.42 skill installation; this refresh used the matching project-local 0.9.51 skill directly and did not modify global installations.
