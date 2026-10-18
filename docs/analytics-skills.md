# Analytics and prediction playbooks

The shared Skills library includes a curated pack of **24** analysis/prediction playbooks alongside the existing retail skills. They use the active discovered schema and work with the larger `timeseries` profile. They contain guidance, definitions and examples, with no scripts or additional tools.

| Skill | Use it for |
| --- | --- |
| Data quality and analysis readiness | Missing dates, genuine zeros, nulls, duplicate keys, join coverage and reconciliation |
| Retail KPI definitions and weighted ratios | Revenue definitions, overall AOV, denominators and weighted margin rates |
| Sales change and segment contributions | Comparable-period deltas, category/channel contributions, and exact volume/AOV bridges |
| Customer cohorts and repeat purchasing | Eligible cohorts, maturity, repeat purchasing and observed customer value |
| Merchandise margin and returns-adjusted performance | Historical line costs, refunds, margin and distinction from business profit |
| Campaign and promotion performance | Attributed outcomes/spend, correct join grain and causal limitations |
| Comparable-store and target performance | Like-for-like eligibility, store openings, target gaps and weighted attainment |
| Calendar trends and retail seasonality | Dense daily calendars, weekday denominators, complete periods and observed peaks |
| Revenue and demand forecasting | Revenue/orders/units forecasts with complete history and validated baselines |
| Forecast validation and uncertainty | Rolling backtests, leakage, MAE/RMSE, model promotion and interval evidence |
| Conditional driver and promotion scenarios | Explicit visitor-supplied future paths and supported conditional predictions |
| Returns and rate prediction readiness | Mature cohorts, weighted denominators, bounded rate domains and withholding unsupported predictions |

## Advanced feature pack

Twelve additional playbooks support the application's newer workflows and complementary retail questions:

| Skill | Use it for |
| --- | --- |
| Published metrics and definition consistency | Exact metric versions, dependencies, ad hoc definitions and definition conflicts |
| Executive retail performance review | Decision-focused Business/Technical reports and evidence-backed recommendations |
| AI dashboard objectives and card design | Audience/objective briefs, distinct cards, suitable evidence reuse and reviewed proposals |
| Dashboard evidence and comparability audit | Mismatched cutoffs, filters, completeness and definitions across saved cards |
| Basket composition and product affinity | Distinct-order support, directional confidence and lift with bounded pair analysis |
| Customer revenue concentration and dependency | Top-customer shares, complete purchasing populations and concentration caveats |
| Cross-source grain and join reconciliation | Explicit keys, target grain, unmatched rows and duplicate expansion |
| Conversational business decision briefing | Concise spoken findings, visual evidence and contextual follow-ups |
| TimesFM candidate comparison and evidence | Preview status, numerical candidate selection, fallback and saved evidence |
| Coherent geographic and product forecast planning | Shared company totals, hierarchical validation and transparent allocations |
| Forecast plan adjustments and assumption disclosure | Separate management versions, propagation and cross-view reallocation |
| Forecast versus actual outturn review | Realized-period errors, saved baselines and honest source-cutoff limitations |

Dashboard and forecast-planning skills guide the existing workflows; they do not add publication or computation tools to ordinary chat/voice. New hierarchy computation uses **Forecast Plans**. Reuse of a saved plan in **Advanced Analysis** keeps its explicit version. Planning adjustments remain assumptions rather than statistical predictions or learned scenarios.

Try these requests:

- “Using published metric definitions, prepare a quarterly executive retail review with reconciled category contributions and limitations.”
- “Propose a four-card leadership dashboard, reusing compatible saved evidence and identifying gaps before publication.”
- “Which categories are bought together in the last complete quarter? Show support, directional confidence and lift with at least 100 shared orders.”
- “Explain this Forecast Plan's shared company total and which store/product values are allocated.”
- “Review a proposed 5% regional plan increase, explaining cross-view reallocation separately from the statistical forecast.”
- “Compare this saved forecast with actuals only if its complete forecast periods exist; otherwise show saved backtest evidence.”

The insert-only command below checks all 24 packaged skills. It preserves the previously published pack, even where local templates have since improved; existing visitor definitions and old revisions are not overwritten.

## Try them

Open [Skills](https://agentic-bi-frontend-wekihucn7q-as.a.run.app/skills) to inspect or edit the playbooks. Automatic discovery chooses relevant metadata; **Attach skills** gives manual priority. The combined budget remains **three skills per analysis**. Choose both sources for cross-source store, campaign or customer questions. Existing answers retain their captured versions after subsequent edits.

Examples for ordinary analytics:

- “Calculate overall AOV from total merchandise revenue and completed orders. Compare it with the monthly AOVs and explain the denominator.”
- “Which categories and channels contributed most to the latest complete month's revenue change?”
- “Compare like-for-like store revenue across the last two complete quarters, separately identifying new stores.”
- “Compare three-month repeat purchasing by signup quarter, using only mature cohorts.”
- “Compare campaign attributed revenue per spend and explain the causal limitations.”

Enable **Advanced Analysis** for actual prediction fitting:

- “Forecast monthly merchandise revenue for the next three months. Compare against seasonal-naive forecasts using rolling backtests and show uncertainty.” Attach **Revenue and demand forecasting**, **Forecast validation and uncertainty**, and optionally **Calendar trends and retail seasonality**.
- “Create a conditional next-quarter revenue scenario using promotion drivers. Ask me for every required future baseline and alternative value.” Attach **Conditional driver and promotion scenarios** and **Forecast validation and uncertainty**.
- “Assess whether mature purchase cohorts support a three-month return-rate forecast. Explain limitations before predicting.” Attach **Returns and rate prediction readiness** and **Forecast validation and uncertainty**.

A playbook does not add statistical tools to ordinary chat or override SQL/fusion permissions. Advanced Analysis uses the existing controlled fitting tools and evidence gates. Short histories, immature cohorts, missing future drivers, failed validation or invalid metric domains can produce a defensible baseline or an explanation of why a prediction is withheld. The synthetic dataset is for testing; fitted accuracy does not establish real-world predictive performance.

## Reproduce the library additions

Review the individual importable Markdown files in [Backend/app/skill_library](../Backend/app/skill_library). The pack has stable IDs starting with `analytics-` or `prediction-`. From the current repository checkout, an authorized operator can add it to the existing named demo database:

```bash
cd Backend
uv run python -m app.admin seed-analysis-skills
```

The command validates all files before writing and uses the normal transactional versioned skill service. It creates missing IDs only. Repeated runs preserve edited, disabled and soft-deleted entries and their revision history. A partial failure can be retried safely; library capacity still applies. Seeding is an explicit data operation, separate from application deployment, analytical data generation, skill publication quotas and history reset. It does not invoke models or query/upload analytical data. The existing `seed-skills` command still seeds only its original two examples.

Published entries become available immediately through the running backend and private report worker; no image rebuild or vector index is required. See [Skills behavior](skills.md), [Reports](reports.md), [the deployment guide](deployment-guide.md), and [verification evidence](evaluation/analytics-skills.json).

Packaged revenue/scenario playbooks now recognize optional [TimesFM comparison](timesfm.md). Updating templates does not update published skills or overwrite visitor changes. Actual availability, fixed tools, budgets and numerical promotion gates remain application policy; a skill cannot enable managed inference.

The twelve advanced-feature additions were published on **18 October 2026**, bringing the hosted library to **29 active skills**. [Publication evidence](evaluation/advanced-feature-skills-20261018.json) records unchanged prior documents, safe seed replay, immutable revision/export checks and four real Gemini discovery cases. Those selector probes used copied published content with in-memory sessions, not new source queries or forecast/report executions. No Cloud Run rebuild was needed. The existing library header has a mobile navigation overflow at 390px; the skill cards themselves wrap correctly. This content operation does not change that layout.
