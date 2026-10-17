# Graph Report - 6. Google AI Builder Cup - Agentic BI  (2026-10-17)

## Corpus Check
- 242 files · ~176,966 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1996 nodes · 5353 edges · 121 communities (91 shown, 30 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 296 edges (avg confidence: 0.92)
- Token cost: 0 separate model-API tokens; host-session semantic input/output token usage is unavailable (not measured as zero).

## Graph Freshness
- Built from commit: `3e9c685d`
- This is a working-tree snapshot; VALIDATION.json records per-file SHA-256 hashes. Compare those hashes as well as the base commit to check freshness.
- Run `graphify update .` after code changes; use the Graphify skill for changed document semantics.

## Community Hubs (Navigation)
- Dashboard Configuration and Tests
- Report Reliability Tests
- Saved Chart Presentation
- Workspace Preferences and Motion
- Retail Bundle Publication
- Shared Library Navigation
- Report Reliability Tests
- Skill Catalog and Seeding
- Analytical API Boundaries
- Controlled Analysis Lifecycle
- Settings and Skill Forms
- AI Retry and Managed Forecast Recovery
- ADK Session Fencing
- Fenced Administrative Maintenance
- Guarded Database Queries
- TypeScript Compiler Configuration
- Workspace Preferences and Motion
- Reviewed Author and Preview Tabs
- Skill Author Concurrency Tests
- Application Service Architecture
- Frontend API and Live Transport
- Dashboard Results and Actions
- Report Repository Leases
- Interactive Chart Formatting
- Typed Analysis Contracts
- Browser Voice Client Interfaces
- Responsive Sidebar Primitives
- Scoped Cloud Foundation
- Runtime Configuration and Sessions
- Local Setup and Verification
- Shared Analytical Domain Model
- Immutable Report Evidence Contract
- Shadcn Component Configuration
- TimesFM Verification and Release Gate
- Frontend Development Dependencies
- Private Report Dispatch Architecture
- Typed Analysis Contracts
- Advanced Feature Contracts
- Frontend Runtime Dependencies
- Skill Draft Publication
- Workspace and Report Progress
- Advanced Report Workflow Contract
- Skills Library Editor
- Public API Regression Tests
- Chart Tooltip Primitives
- Landing Product Illustrations
- Mobile Navigation and Sheets
- Dashboard Detail Page
- Frontend Package Scripts
- Customer Cohorts and Returns
- Data Quality and Fusion
- Seasonality and Forecast Validation
- Backend Runtime Responsibilities
- Saved Charts and Preferences
- AI Retry and Managed Forecast Recovery
- Time Series Data Publication
- Competition Demonstration Workflow
- Conditional Driver Scenario Playbook
- Revenue Forecast Playbook
- Named Firestore ADK Persistence
- Saved Dashboard Retention Design
- Landing Route Design
- Managed TimesFM Comparison Design
- Original Retail Source Schema
- Expanded Retail Table Dictionary
- Skill Revision Snapshots
- Reports Library Page
- Immutable Chart Data Services
- Published Dashboard Views and Recovery
- Frontend Contribution Guidance
- Tooltip Context Primitives
- Saved Chart View Tests
- Prediction Evidence Interface Tests
- Sales Change Contribution Playbook
- Comparable Store Performance Playbook
- Weighted Retail KPI Definitions
- Marketing Associations and Scenarios
- Merchandise Margin and Refunds
- Hosted Library and Voice Checks
- Hosted Library and Voice Checks
- Report Checkpoint Recovery
- Public Skill Versioning Decision
- Validated Public Evidence
- Dashboard Mutation and Retention Plan
- Browser PCM Audio Worklet
- Responsive Viewport Subscriptions
- Chart Formatting Regression Tests
- Skill Catalog and Seeding
- Live Recovery Smoke Tests
- Hosted Library and Voice Checks
- Public Anonymous Workspace Decision
- Durable Report Execution Decision
- Runtime Backend Configuration Route
- Frontend Health Route
- Markdown Rendering Regression Tests
- Table Accessibility Regression Tests
- Cloud Build Workflow
- Local Social Preview Asset
- Backend Package Description
- Classname Utility Dependency
- Report Revision Retention Decision
- Stage Feedback and Toasts
- Frontend ESLint Configuration
- Next Route Configuration
- Lucide Icon Dependency
- Motion Animation Dependency
- Next Framework Dependency
- Theme Provider Dependency
- GFM Markdown Dependency
- Tailwind Merge Dependency
- Model Preference Regression Tests
- Report Assumption Regression Tests
- Synthetic Retail Source Publication
- Browser Model Selection Guide
- BeUI License Attribution
- Backend Dependency Manifest

## God Nodes (most connected - your core abstractions)
1. `AppError` - 197 edges
2. `Settings` - 118 edges
3. `MemoryStore` - 84 edges
4. `Connectors` - 66 edges
5. `Repository` - 63 edges
6. `create_app()` - 54 edges
7. `FirestoreSessionService` - 53 edges
8. `Querylane product, setup and hosted release overview` - 48 edges
9. `AI` - 44 edges
10. `StrictModel` - 43 edges

## Surprising Connections (you probably didn't know these)
- `Join-key compatibility, coverage and fan-out` --semantically_similar_to--> `Explicit fan-out and incomplete-input rejection`  [INFERRED] [semantically similar]
  Backend/app/skill_library/analytics-data-quality.md → docs/adr/0003-bounded-cross-source-fusion.md
- `Shared-method baseline and alternative scenario artifacts` --conceptually_related_to--> `Separate immutable scenario with same-method baseline and alternative`  [INFERRED]
  Backend/app/skill_library/prediction-driver-scenarios.md → docs/timesfm.md
- `Common chronological scores choose statistical or managed candidate` --conceptually_related_to--> `Common three-fold full-horizon measured method selection`  [INFERRED]
  Backend/app/skill_library/prediction-sales-forecast.md → docs/timesfm.md
- `foundation()` --calls--> `operator_credentials()`  [INFERRED]
  infra/provision_reports.py → Backend/app/admin.py
- `main()` --uses--> `Settings`  [INFERRED]
  infra/report_recovery_check.py → Backend/app/config.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Isolated public product introduction** — docs_landing_page_route_split, docs_landing_page_guided_preview, docs_landing_page_fixed_palette, docs_landing_page_forecast_fixture, docs_landing_page_workspace_links, docs_landing_page_legacy_redirect [EXTRACTED 1.00]
- **Fenced admission, stable jobs, persistent cancellation and conservative billing** — docs_timesfm_atomic_admission, docs_timesfm_stable_jobs, docs_timesfm_persistent_cancellation, docs_timesfm_conservative_billing [EXTRACTED 1.00]
- **Frozen saved input, deterministic selection, separate scenarios and immutable exports** — docs_timesfm_frozen_saved_input, docs_timesfm_candidate_selection, docs_timesfm_separate_scenario, docs_timesfm_saved_export_evidence [EXTRACTED 1.00]
- **Actual worker ADC, enabled flags, hosted numerical acceptance and preserved sources** — docs_validation_worker_adc_success, docs_validation_enabled_flags, docs_validation_hosted_acceptance, docs_validation_source_preservation [EXTRACTED 1.00]
- **Saved monthly forecasts, conditional scenarios and dashboard reuse share immutable prediction evidence** — readme_monthly_forecast, readme_conditional_scenario, readme_prediction_dashboard, readme_immutable_reuse [EXTRACTED 1.00]
- **Worker compatibility, numerical acceptance and preserved sources establish this dated hosted release** — readme_worker_verification, readme_hosted_acceptance, readme_source_preservation, readme_hosted_timesfm_release [EXTRACTED 1.00]

## Communities (121 total, 30 thin omitted)

### Community 0 - "Dashboard Configuration and Tests"
Cohesion: 0.06
Nodes (80): saved_rows(), get_settings(), Settings, ChartViewState, DashboardAction, DashboardCreate, DashboardItemPatch, DashboardLayout (+72 more)

### Community 1 - "Report Reliability Tests"
Cohesion: 0.08
Nodes (66): choose(), compare(), eligible(), intervals(), Application-owned candidate selection over a frozen saved series., reserve_candidates(), score_remote(), ForecastSpec (+58 more)

### Community 2 - "Saved Chart Presentation"
Cohesion: 0.06
Nodes (71): change(), csv_cell(), csv_line(), date_value(), metadata(), next_date(), number(), present() (+63 more)

### Community 3 - "Workspace Preferences and Motion"
Cohesion: 0.05
Nodes (50): AnalysisProgress(), stages, AnimatedNumber(), AnimatedNumberProps, ColorSelector(), ColorSelectorContext, ColorSelectorContextValue, ColorSelectorItem() (+42 more)

### Community 4 - "Retail Bundle Publication"
Cohesion: 0.07
Nodes (54): demand(), generate(), GeneratorConfig, money(), promotion_window(), Path, Deterministic, bounded-memory synthetic retail history; never contacts a…, read_manifest() (+46 more)

### Community 5 - "Shared Library Navigation"
Cohesion: 0.06
Nodes (47): metadata, DashboardShare(), show(), DashboardEditor(), useDashboardMutation(), DashboardWidget(), ResultCard, DashboardsLibrary() (+39 more)

### Community 6 - "Report Reliability Tests"
Cohesion: 0.06
Nodes (36): ReportDispatcher, NeedsInput, Exception, ReportEngine, ExportStorage, ADK graph orchestration with global policy and explicit application checkpoints., Graph nodes carry only a run identifier. Bodies live in fenced checkpoints., ReportPolicy (+28 more)

### Community 7 - "Skill Catalog and Seeding"
Cohesion: 0.08
Nodes (42): analytics_examples(), Stable seed IDs let operators add examples without replacing public edits., Import the reviewable, source-controlled pack before any cloud writes., seed_analytics(), seed_examples(), compatible(), export_skill(), import_skill() (+34 more)

### Community 8 - "Analytical API Boundaries"
Cohesion: 0.10
Nodes (37): Durable ADK session adapter with ordered events and fenced state writes., AppError, Exception, check_maintenance(), clear_maintenance(), enter_maintenance(), purge_dashboards(), purge_reports() (+29 more)

### Community 9 - "Controlled Analysis Lifecycle"
Cohesion: 0.09
Nodes (30): AI, fixture_answer(), fixture_plan(), Explicit local-only sample planner. Never used as a Gemini fallback., AnalysisService, normalized_spec(), Called once when saving a new artifact; historical documents remain immutable., json_rows() (+22 more)

### Community 10 - "Settings and Skill Forms"
Cohesion: 0.06
Nodes (33): metadata, Catalog, ModelSettings(), ChoiceSetting(), preferenceLabels, sections, updatePreference(), DialogClose() (+25 more)

### Community 11 - "AI Retry and Managed Forecast Recovery"
Cohesion: 0.07
Nodes (47): Private-worker Advanced Analysis with immutable report versions, Live PCM voice with replace-aware transcripts and distinct query identities, Component and data-flow architecture guide, Public FastAPI API, controlled analytics and private report-worker entrypoint, Model/cloud budgets and billing alerts are not hard spending caps, Browser-local model, appearance, chart and voice settings, Interactive saved-result charts, full-data CSV and presentation controls, Local-only real Gemini preview using in-memory operator credentials (+39 more)

### Community 12 - "ADK Session Fencing"
Cohesion: 0.09
Nodes (22): FirestoreSessionService, StaleLease, Repository, test_cancellation_failure_still_releases_conversation(), test_raw_audio_is_not_persisted(), test_recent_session_context_uses_newest_events(), test_result_survives_interpreter_outage_and_reconnect(), test_transient_model_failure_retried_once_only() (+14 more)

### Community 13 - "Fenced Administrative Maintenance"
Cohesion: 0.08
Nodes (29): check_models(), cleanup_skill_authors(), cli(), dashboard_maintenance(), index_schema(), main(), operator_credentials(), Credentialed CLI only. No administrative endpoint is exposed by FastAPI. (+21 more)

### Community 14 - "Guarded Database Queries"
Cohesion: 0.09
Nodes (36): cases(), matches(), Deterministic synthetic retail data; no real customer information., retail_data(), reconcile(), linked_predicate(), AST validation complements restricted database roles; it is not a SQL sandbox., Every admitted OR branch must constrain the new relation to a prior one. (+28 more)

### Community 15 - "TypeScript Compiler Configuration"
Cohesion: 0.05
Nodes (40): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+32 more)

### Community 16 - "Workspace Preferences and Motion"
Cohesion: 0.08
Nodes (32): body, heading, metadata, mono, AppearanceSync(), AppProviders(), PinToDashboard(), create() (+24 more)

### Community 17 - "Reviewed Author and Preview Tabs"
Cohesion: 0.12
Nodes (22): metadata, views, MarkdownContent(), MessageContent(), SkillMarkdown(), SkillRevision(), loadSavedInterview(), Phase (+14 more)

### Community 18 - "Skill Author Concurrency Tests"
Cohesion: 0.15
Nodes (23): asyncio, json_value(), Any, AuthorDraft, Small document interface with atomic, retry-safe read/modify/write operations., voice_session(), main(), Opt-in real Gemini Live/tool integration check; no microphone is recorded. Run… (+15 more)

### Community 19 - "Application Service Architecture"
Cohesion: 0.11
Nodes (30): ADK planner and controlled analysis service, Invocation-scoped analysis, query and BigQuery identities, Demo BigQuery source, Stable job IDs, fenced checkpoints and at-least-once task recovery, Revision-checked saved dashboard exports, Independent report leases and checkpoints with redelivery, Backend-only named Firestore persistence, Hosted TimesFM enabled after actual worker verification (+22 more)

### Community 20 - "Frontend API and Live Transport"
Cohesion: 0.11
Nodes (19): metadata, metadata, ReportEditDialog(), save(), ReportWorkspace(), download(), SkillAttachments(), load() (+11 more)

### Community 21 - "Dashboard Results and Actions"
Cohesion: 0.24
Nodes (17): formats, DashboardHeader(), ResearchResult, Button(), buttonVariants, Dialog(), DialogContent(), DialogDescription() (+9 more)

### Community 22 - "Report Repository Leases"
Cohesion: 0.12
Nodes (4): Operation and conservative budget reservation commit in one fenced transaction., ReportRepository, Opt-in hosted forecast/scenario acceptance. Public reports; read-only retail…, run()

### Community 23 - "Interactive Chart Formatting"
Cohesion: 0.16
Nodes (22): categoryColor(), InsightfulChart(), content(), download(), label(), palette, Plot(), Values() (+14 more)

### Community 24 - "Typed Analysis Contracts"
Cohesion: 0.12
Nodes (20): ChartMeasure, ConversationCreate, field_validator, StrictModel, TurnCreate, Report specialists use existing guarded SQL/fusion; all numerical work is…, AnalysisTask, EvidenceClaim (+12 more)

### Community 25 - "Browser Voice Client Interfaces"
Cohesion: 0.11
Nodes (12): path(), SkillVoiceAuthor(), connect(), publish(), saveReview(), ask(), ensureConversation(), startVoice() (+4 more)

### Community 26 - "Responsive Sidebar Primitives"
Cohesion: 0.09
Nodes (8): Sidebar(), SidebarContext, SidebarContextProps, SidebarMenuButton(), sidebarMenuButtonVariants, SidebarRail(), SidebarTrigger(), useSidebar()

### Community 27 - "Scoped Cloud Foundation"
Cohesion: 0.15
Nodes (21): main(), Build with a resource-scoped builder, then deploy as the current operator., configuration(), main(), Prepare or deploy ONLY the private report worker. Foundation/IAM are separate…, ensure_secret(), ensure_service_account(), gcloud() (+13 more)

### Community 28 - "Runtime Configuration and Sessions"
Cohesion: 0.11
Nodes (13): Connectors, ai_service(), parametrize, Fault injection at the real structured-call and Live transport seams., test_analysis_finish_storage_failure_still_clears_local_task_registry(), test_cancel_then_forget_during_bigquery_dry_run_prevents_late_submission(), test_expected_voice_tool_failure_is_recoverable_without_reexecuting_query(), test_long_retry_after_does_not_retry_earlier_than_provider_requests() (+5 more)

### Community 29 - "Local Setup and Verification"
Cohesion: 0.10
Nodes (25): Landing frontend release 00012-mv5, Fixed landing palette and saved appearance isolation, Verified saved forecast fixture, Local guided preview boundary, Public landing page guide, Fixed same-origin legacy 307 redirect, Evidence-backed BI product story, Verified synthetic retail totals (+17 more)

### Community 30 - "Shared Analytical Domain Model"
Cohesion: 0.13
Nodes (23): Frozen report question, scope, sources, context and skills, Evaluation using only origin-available information, Bounded presentation over full saved result, Public collection of saved analytical cards, Dashboard item with retained artifact and saved view, Operator-selected legacy or timeseries source contract, Domain glossary, Factual claim linked to saved analytical evidence (+15 more)

### Community 31 - "Immutable Report Evidence Contract"
Cohesion: 0.17
Nodes (22): Single fenced reservation of backtest/final jobs, tokens, bytes and fits, Common three-fold full-horizon measured method selection, Conservative reserved seconds, token estimates and failed-work accounting, Fold-compatible shared context in multiples of 32, minimum 64, Both enablement flags and actual-worker attestation required, timesfm.py fixed queries, job identity and cancellation, report_forecasting.py admission, comparison checkpoints and selection, Complete immutable pages and exact validated-series hash (+14 more)

### Community 32 - "Shadcn Component Configuration"
Cohesion: 0.09
Nodes (22): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+14 more)

### Community 33 - "TimesFM Verification and Release Gate"
Cohesion: 0.13
Nodes (21): Workflow 2 frozen policy and retained workflow 1 behavior, Local ENABLED=false and VERIFIED=false defaults, Chromium disclosure, mobile, Preview, dashboard and concurrent-chat verification, Historical AOV error retained with claim policy v2 correction, 17 October private-worker Advanced Analysis release evidence, Both TimesFM flags enabled on hosted API and private worker, Historical skills/animation verification baseline, 17 October TimesFM enabled release: frontend 00015-6ff, API 00021-6rd, worker 00010-wnw (+13 more)

### Community 34 - "Frontend Development Dependencies"
Cohesion: 0.10
Nodes (21): babel-plugin-react-compiler, eslint, eslint-config-next, devDependencies, babel-plugin-react-compiler, eslint, eslint-config-next, shadcn (+13 more)

### Community 35 - "Private Report Dispatch Architecture"
Cohesion: 0.14
Nodes (20): Record actual readiness, traffic, identities and image digests, Usage controls reduce exposure without guaranteed monetary cap, API and compatible private worker before frontend with old runs drained, Separate operator, local ADC and attached runtime credentials, Separate first-time missing-resource foundation, Opt-in public forecast/scenario acceptance over saved evidence, Verified image-only rollout preserves runtime configuration, Separate authorized fenced reset and expiry purge (+12 more)

### Community 36 - "Typed Analysis Contracts"
Cohesion: 0.25
Nodes (18): _arrow_bytes(), fuse(), _identifier(), Any, A typed plan compiler; no model-supplied SQL or Python reaches DuckDB., _worker(), Calculation, FusionPlan (+10 more)

### Community 37 - "Advanced Feature Contracts"
Cohesion: 0.11
Nodes (19): Authoritative architecture Mermaid and derived graph exports, Separate authorized deployment and data operations, Repository contributor constraints, Disabled managed forecasting and immutable bounded inference, Three-skill budget and controlled query pipeline, Independent report leases and immutable retained evidence, Explicit-key joins and invocation-scoped voice evidence, Advanced Analysis tools and evidence gates (+11 more)

### Community 38 - "Frontend Runtime Dependencies"
Cohesion: 0.11
Nodes (19): class-variance-authority, clsx, dependencies, class-variance-authority, clsx, radix-ui, react, react-dom (+11 more)

### Community 40 - "Workspace and Report Progress"
Cohesion: 0.12
Nodes (15): forecastMethodLabel(), PredictionEvidence(), SkillEvidence(), AuthorBrief, AuthorSession, ChartChange, ChartRow, Connection (+7 more)

### Community 41 - "Advanced Report Workflow Contract"
Cohesion: 0.19
Nodes (15): Three-origin full-horizon backtests and baseline/domain gates, Deterministic verified claims and grouped-ratio policy v2, Transactional outbox, private OIDC worker and checkpoint reuse, Workflow 2 with enabled verified hosted TimesFM and disabled local defaults, Captured report source, model, completed context, schema and skill revisions, Visitor-supplied complete baseline and alternative driver paths, Same saved document drives web, PDF, Word and full CSV ZIP, Public immutable report versions and prediction caveats (+7 more)

### Community 42 - "Skills Library Editor"
Cohesion: 0.18
Nodes (8): metadata, contentOf(), SkillsWorkspace(), editSkill(), exportFile(), importFile(), openEditor(), sourceLabel()

### Community 43 - "Public API Regression Tests"
Cohesion: 0.28
Nodes (12): guest(), parametrize, A worker may finish after the event query but before the status read., test_analysis_replay_fork_and_provenance(), test_guest_scope_and_no_administrative_routes(), test_origin_and_payload_validation(), test_stream_drains_events_committed_between_poll_and_terminal_read(), test_voice_does_not_fake_model_in_fixture_mode() (+4 more)

### Community 44 - "Chart Tooltip Primitives"
Cohesion: 0.21
Nodes (11): ChartConfig, ChartContainer(), ChartContext, ChartContextProps, ChartLegendContent(), ChartTooltipContent(), getPayloadConfigFromPayload(), INITIAL_DIMENSION (+3 more)

### Community 45 - "Landing Product Illustrations"
Cohesion: 0.20
Nodes (9): capabilities, faqs, metadata, OpenQuerylane(), LandingMobileNavigation(), HeroProduct(), money(), RevenueIllustration() (+1 more)

### Community 46 - "Mobile Navigation and Sheets"
Cohesion: 0.27
Nodes (7): Sheet(), SheetClose(), SheetContent(), SheetDescription(), SheetHeader(), SheetTitle(), SheetTrigger()

### Community 47 - "Dashboard Detail Page"
Cohesion: 0.24
Nodes (6): metadata, DashboardWorkspace(), refreshRemoved(), restoreItem(), setMode(), unpin()

### Community 48 - "Frontend Package Scripts"
Cohesion: 0.20
Nodes (9): name, private, scripts, build, dev, lint, start, test (+1 more)

### Community 49 - "Customer Cohorts and Returns"
Cohesion: 0.36
Nodes (8): Signup cohorts and first observed purchase cohorts, Customer cohorts and repeat purchasing, Equally mature customer observation windows, Repeat purchase and activity retention denominators, Validated bounded-rate or monetary forecast domain, Explicit return-rate target and denominator, Returns and rate prediction readiness, Refund latency and cohort maturity

### Community 50 - "Data Quality and Fusion"
Cohesion: 0.32
Nodes (8): Data quality and analysis readiness, Calendar spine, unknown gaps and observed zeros, Join-key compatibility, coverage and fan-out, Independent totals reconciliation, Explicit fan-out and incomplete-input rejection, ADR: Typed bounded cross-source fusion, Gemini relationship-key and business-assumption hypotheses, Trusted compiler for typed relational fusion

### Community 51 - "Seasonality and Forecast Validation"
Cohesion: 0.32
Nodes (8): Dense retail calendar at consistent time grain, Shifted target-derived rolling predictors, Observed peaks with causal limitations, Calendar trends and retail seasonality, Baseline comparison and candidate promotion, Forecast validation and uncertainty, Chronological rolling-origin backtests, Supported prediction intervals and publication outcome

### Community 52 - "Backend Runtime Responsibilities"
Cohesion: 0.25
Nodes (7): Default local plan and opt-in bounded billable probe, Named Firestore and private report bucket, TimesFM 3.0 Preview comparison over saved evidence, Private report worker app.report_worker:app, Public API for chat, voice and shared libraries, Separate routine releases, skill seeding and analytical upload, Saved-artifact-only dashboard download contract

### Community 53 - "Saved Charts and Preferences"
Cohesion: 0.25
Nodes (8): Immutable saved-result chart presentation, Motion and feedback (deployed 2026-10-16), Reader-aware answer following, Unified device/application reduced motion, Versioned browser-local preferences, Local chart exploration defaults, Pinned analysis model catalog, Task-local captured analysis model

### Community 54 - "AI Retry and Managed Forecast Recovery"
Cohesion: 0.25
Nodes (8): Retry and recovery policy, Disabled TimesFM same-job recovery and statistical fallback, Permanent access/request failures fail fast without substitution, Fenced report redelivery with shared budgets and three-delivery cap, Bounded persisted-cursor SSE replay without query restart, Thread-held cancellation survives delayed query responses, At-most-two structured model attempts with bounded jitter, Expected analyst tool errors remain nonfatal

### Community 55 - "Time Series Data Publication"
Cohesion: 0.29
Nodes (7): Original demo retail schema (seed evidence 2026-10-16), Fenced insert-only cloud publication, Independent bundle reconciliation, Expanded retail column dictionary (retail-timeseries-v1), Stable full-window extend workflow, Deterministic streaming Parquet bundle, Additional timeseries source profile

### Community 56 - "Competition Demonstration Workflow"
Cohesion: 0.29
Nodes (7): Cross-source actual-versus-target exploration, Five-minute competition demonstration, Landing previews and direct workspace entry, Production rehearsal and backup recording, Public conversation sharing and forks, Spoken analysis and interruption, Warehouse question with SQL evidence

### Community 57 - "Conditional Driver Scenario Playbook"
Cohesion: 0.33
Nodes (6): Conditional predictions with historical driver support, Conditional driver and promotion scenarios playbook, Visitor-supplied complete future driver paths, Optional available TimesFM with complete covariate context, Shared-method baseline and alternative scenario artifacts, Chronological scenario validation and extrapolation rejection

### Community 58 - "Revenue Forecast Playbook"
Cohesion: 0.33
Nodes (6): Advanced Analysis controlled forecast fitting, Common chronological scores choose statistical or managed candidate, Complete series and actual latest-observation cutoff, Revenue and demand forecasting playbook, Observed-versus-predicted values and retained method evidence, Five-percent MAE improvement and majority-fold promotion

### Community 59 - "Named Firestore ADK Persistence"
Cohesion: 0.47
Nodes (6): Separate skill author session lease collection, Bounded fresh-transaction retries for read aborts, Custom Firestore ADK session adapter, ADR: ADK persistence in named Firestore, Loaded-session revision and conversation lease fencing, Terminal event stream sequence draining

### Community 60 - "Saved Dashboard Retention Design"
Cohesion: 0.33
Nodes (6): Versioned chart view, ADR 0005: saved-result dashboards (accepted 2026-10-16), Immutable paginated results, Retained artifact references, Shared dashboard implementation plan (implemented/deployed 2026-10-16), Public shared dashboards and saved-view downloads

### Community 61 - "Landing Route Design"
Cohesion: 0.33
Nodes (6): ADR 0008 landing and workspace split, Query-aware 307 compatibility redirect, Landing palette and workspace preference isolation, Local evidence-only guided preview, Server-rendered public introduction, Direct unauthenticated workspace entry

### Community 62 - "Managed TimesFM Comparison Design"
Cohesion: 0.33
Nodes (6): Disabled until managed and actual-worker access verification, ADR 0009: Managed TimesFM comparison, Fenced immutable input/configuration and operation checkpoints, Fixed parameterized managed TimesFM 3.0 Preview adapter, Agent relevance and priority, deterministic numerical selection, Same-method scenarios in separate artifacts

### Community 63 - "Original Retail Source Schema"
Cohesion: 0.33
Nodes (6): Original PostgreSQL retail.customer_profiles, Original BigQuery order_items, Original BigQuery orders, Original BigQuery products, Original PostgreSQL retail.regional_targets, Original BigQuery returns

### Community 64 - "Expanded Retail Table Dictionary"
Cohesion: 0.40
Nodes (6): Dense daily calendar date spine, Time-series customer_profiles, Time-series sales_order_items, Time-series sales_orders, Time-series sales_returns, Full-month store targets

### Community 65 - "Skill Revision Snapshots"
Cohesion: 0.33
Nodes (6): Per-analysis skill snapshots, Bounded metadata-only skill discovery, Public optimistic skill mutations, Immutable skill revisions and recovery, Conversational voice author (documented local implementation), Conversational voice skill author plan and contracts

### Community 66 - "Reports Library Page"
Cohesion: 0.40
Nodes (4): metadata, ReportsLibrary(), change(), restore()

### Community 67 - "Immutable Chart Data Services"
Cohesion: 0.40
Nodes (5): Deterministic bounded chart sampling, Saved-artifact chart-data endpoint, Deterministic truthful chart insights, Full saved-result CSV export, Version-2 VisualizationSpec metadata

### Community 68 - "Published Dashboard Views and Recovery"
Cohesion: 0.40
Nodes (5): Active and recoverable artifact retention, Canonical public dashboard sharing, Public revision-checked editing, Published saved chart views, Revision-checked whole-dashboard exports

### Community 69 - "Frontend Contribution Guidance"
Cohesion: 0.40
Nodes (5): Frontend contributor instructions, Guest-scoped report clarification and skill draft recovery, Installed Next.js version guides, Browser preferences and reduced-motion feedback, Explicit saved chart publication and revision checks

### Community 70 - "Tooltip Context Primitives"
Cohesion: 0.40
Nodes (4): Tooltip(), TooltipContent(), TooltipProvider(), TooltipTrigger()

### Community 71 - "Saved Chart View Tests"
Cohesion: 0.50
Nodes (3): { initialChartView, describeChartView }, load(), reader()

### Community 72 - "Prediction Evidence Interface Tests"
Cohesion: 0.40
Nodes (4): base, compiledModule, render(), require

### Community 73 - "Sales Change Contribution Playbook"
Cohesion: 0.50
Nodes (4): Observed concentrations versus causal explanations, Sales change and segment contributions, Reconciled segment change contributions, Exact order-volume and AOV revenue bridge

### Community 74 - "Comparable Store Performance Playbook"
Cohesion: 0.67
Nodes (4): Comparable-store and target performance, Comparable-store eligibility, Store and regional target join grain, Weighted attainment and reconciled target gaps

### Community 75 - "Weighted Retail KPI Definitions"
Cohesion: 0.67
Nodes (4): Completed-order merchandise revenue, Retail KPI definitions and weighted ratios, Overall AOV from revenue and distinct orders, Weighted margin rate and additive reconciliation

### Community 76 - "Marketing Associations and Scenarios"
Cohesion: 0.67
Nodes (4): Attributed revenue per campaign spend, Compatible campaign and period aggregation, Campaign and promotion performance, Validated future promotion scenario

### Community 77 - "Merchandise Margin and Refunds"
Cohesion: 0.67
Nodes (4): Historical line merchandise revenue and cost, Merchandise margin and returns-adjusted performance, Order-cohort refund and returned-cost adjustment, Signed margin and return-cohort maturity

### Community 78 - "Hosted Library and Voice Checks"
Cohesion: 0.67
Nodes (3): main(), Opt-in API check using existing immutable artifacts; never runs an analysis or…, run()

### Community 79 - "Hosted Library and Voice Checks"
Cohesion: 0.67
Nodes (3): main(), Opt-in hosted report acceptance; creates public verification…, run()

### Community 81 - "Public Skill Versioning Decision"
Cohesion: 0.50
Nodes (4): ADR 0004: public versioned skills (accepted 2026-10-15), Bounded metadata skill selector, Public Markdown playbooks, Analysis-scoped immutable skill snapshots

### Community 82 - "Validated Public Evidence"
Cohesion: 0.50
Nodes (4): ADR 0007: public report evidence (accepted 2026-10-17), Requester-only in-memory Search panel, Verified numerical claims, Distinct writer and semantic reviewer

### Community 83 - "Dashboard Mutation and Retention Plan"
Cohesion: 0.50
Nodes (4): Validated ChartViewState, Fenced reference-aware history maintenance, Revision-checked idempotent dashboard mutations, Immutable saved-artifact dashboard cards

### Community 85 - "Responsive Viewport Subscriptions"
Cohesion: 0.67
Nodes (3): SidebarProvider(), subscribe(), useIsMobile()

### Community 90 - "Public Anonymous Workspace Decision"
Cohesion: 1.00
Nodes (3): Anonymous guest token attribution, quotas and cancellation, Public shared conversations, ADR: Public workspace without accounts

### Community 91 - "Durable Report Execution Decision"
Cohesion: 0.67
Nodes (3): ADK App / Runner / Workflow, Independent durable report execution, ADR 0006: durable versioned reports (accepted 2026-10-17)

### Community 97 - "Cloud Build Workflow"
Cohesion: 0.67
Nodes (3): Cloud Build Docker build step, Cloud Build Docker push step, Dedicated GCS-only build logs

## Knowledge Gaps
- **249 isolated node(s):** `agentic-bi-backend`, `$schema`, `style`, `rsc`, `tsx` (+244 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **30 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AppError` connect `Analytical API Boundaries` to `Dashboard Configuration and Tests`, `Report Reliability Tests`, `Saved Chart Presentation`, `Typed Analysis Contracts`, `Retail Bundle Publication`, `Report Reliability Tests`, `Skill Draft Publication`, `Skill Catalog and Seeding`, `Controlled Analysis Lifecycle`, `ADK Session Fencing`, `Fenced Administrative Maintenance`, `Guarded Database Queries`, `Skill Author Concurrency Tests`, `Report Repository Leases`, `Typed Analysis Contracts`, `Runtime Configuration and Sessions`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Why does `Settings` connect `Dashboard Configuration and Tests` to `Report Reliability Tests`, `Saved Chart Presentation`, `Retail Bundle Publication`, `Report Reliability Tests`, `Skill Catalog and Seeding`, `Analytical API Boundaries`, `Controlled Analysis Lifecycle`, `Public API Regression Tests`, `ADK Session Fencing`, `Fenced Administrative Maintenance`, `Guarded Database Queries`, `Skill Author Concurrency Tests`, `Runtime Configuration and Sessions`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Why does `Connectors` connect `Runtime Configuration and Sessions` to `Dashboard Configuration and Tests`, `Report Reliability Tests`, `Retail Bundle Publication`, `Typed Analysis Contracts`, `Report Reliability Tests`, `Skill Catalog and Seeding`, `Analytical API Boundaries`, `Controlled Analysis Lifecycle`, `ADK Session Fencing`, `Fenced Administrative Maintenance`, `Guarded Database Queries`, `Skill Author Concurrency Tests`?**
  _High betweenness centrality (0.012) - this node is a cross-community bridge._
- **Are the 77 inferred relationships involving `AppError` (e.g. with `AI` and `AnalysisService`) actually correct?**
  _`AppError` has 77 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `Settings` (e.g. with `Connectors` and `create_app()`) actually correct?**
  _`Settings` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `MemoryStore` (e.g. with `test_every_chart_family_and_mixed_units_can_render()` and `test_complex_plan_uses_json_mode_and_still_validates_locally()`) actually correct?**
  _`MemoryStore` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `Connectors` (e.g. with `Settings` and `AppError`) actually correct?**
  _`Connectors` has 11 INFERRED edges - model-reasoned connections that need verification._
## Extraction Integrity and Scope

Generated with Graphify 0.9.51. All 49 detected documents have semantic nodes: 42 cached and 7 re-extracted in one host-session agent. Code extraction is local AST analysis. No separate model API, analytical database or cloud deployment was invoked.

- Graphify tree-sitter reported potentially partial extraction of Frontend/src/components/workspace.tsx at line 1080; 13 symbols extracted.
- Raw external import references can have no matching project node; unresolved endpoints are reported, not fabricated.
- The default undirected simple graph can combine multiple relationships between an endpoint pair; diagnostic counts retain this limitation.
- Host semantic-token usage is unavailable, not zero.

Raw extraction contains **826 unresolved endpoint references**, **0 missing endpoint fields**, **0 self-loops** and **491 same-endpoint relationships collapsed** by the default undirected graph. Many unresolved references are external SDK/module imports; absent entities are not invented. These are extraction limits, not runtime defects.

Community names, centrality and cross-document links are navigation heuristics. Dated deployment/plan statements retain their scope. [VALIDATION.json](VALIDATION.json) records source hashes; [the graph guide](../docs/graphify/README.md) explains maintenance.
