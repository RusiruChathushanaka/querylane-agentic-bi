# Graph Report - 6. Google AI Builder Cup - Agentic BI  (2026-10-17)

## Corpus Check
- 242 files · ~179,380 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2037 nodes · 5397 edges · 113 communities (86 shown, 27 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 290 edges (avg confidence: 0.91)
- Token cost: 0 separate model-API tokens; host-session semantic input/output usage is unavailable (not measured as zero).

## Graph Freshness
- Built from commit: `ec84f540`
- This is a working-tree snapshot; VALIDATION.json records per-file SHA-256 hashes. Compare those hashes as well as the base commit to check freshness.
- Run `graphify update .` after code changes; use the Graphify skill for changed document semantics.

## Community Hubs (Navigation)
- Report Coordination and Contracts
- TimesFM Numerical and Recovery Tests
- Workspace Preferences and Motion
- Skill Catalog and Seeding
- Retail Bundle Publication
- Saved Chart Presentation
- Skill Author Concurrency Tests
- Dashboard Configuration and Tests
- Product Overview and Release Evidence
- Responsive Sidebar Primitives
- Application Service Architecture
- Guarded Database Queries
- Validation and Saved Result Boundaries
- Dashboard Configuration and Tests
- Dashboard Results and Actions
- TypeScript Compiler Configuration
- Reviewed Author and Preview Tabs
- Managed Forecast Comparison and Recovery
- Report Reliability Tests
- Shared Library Navigation
- ADK Session Fencing
- Frontend API and Live Transport
- Interactive Chart Formatting
- Shared Library Navigation
- Landing Tour and Workspace Routing
- Skill Draft Publication
- Workspace Preferences and Motion
- Fenced Administrative Maintenance
- Scoped Cloud Foundation
- Contributor and Presentation Guidance
- ADK Session Fencing
- Report Repository Leases
- Advanced Report Workflow Contract
- Static Landing Preview Contract
- Shared Analytical Domain Model
- Shadcn Component Configuration
- Settings and Skill Forms
- Frontend Development Dependencies
- Private Report Dispatch Architecture
- Browser Voice Client Interfaces
- Controlled Analysis Lifecycle
- Report Progress and Assumptions
- Frontend Runtime Dependencies
- Public Report API and State
- Voice Author and Model Errors
- Dashboard Detail Page
- Model and Voice Failure Tests
- Skills Library Editor
- Public API Regression Tests
- Local Setup and Verification
- Chart Tooltip Primitives
- Conversation Fencing and Recovery
- Advanced Feature Contracts
- Reference-Aware History Maintenance
- ADK Report Graph and Policy
- Frontend Package Scripts
- Immutable Report Export Storage
- Durable Report Dispatch
- Customer Cohorts and Returns
- Data Quality and Fusion
- Seasonality and Forecast Validation
- Firestore Transaction Failure Tests
- Retail Source Publication and Schema
- Competition Demonstration Workflow
- Conditional Driver Scenario Playbook
- Revenue Forecast Playbook
- Named Firestore ADK Persistence
- Original Retail Source Schema
- Expanded Retail Table Dictionary
- Skill Revision Snapshots
- Reports Library Page
- Immutable Chart Data Services
- Published Dashboard Views and Recovery
- Saved Chart View Tests
- Report Contract Validation
- Sales Change Contribution Playbook
- Comparable Store Performance Playbook
- Weighted Retail KPI Definitions
- Marketing Associations and Scenarios
- Merchandise Margin and Refunds
- Transactional Storage Interface
- Public Skill Versioning Decision
- Dashboard Mutation and Retention Plan
- Browser PCM Audio Worklet
- Chart Formatting Regression Tests
- Landing Route and Preview Tests
- Public Anonymous Workspace Decision
- Runtime Backend Configuration Route
- Frontend Health Route
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
- BeUI License Attribution
- Backend Dependency Manifest

## God Nodes (most connected - your core abstractions)
1. `AppError` - 197 edges
2. `Settings` - 118 edges
3. `MemoryStore` - 84 edges
4. `Querylane product, setup and hosted release overview` - 71 edges
5. `Connectors` - 66 edges
6. `Repository` - 63 edges
7. `Implemented Querylane architecture and source-code map` - 63 edges
8. `Dated validation and remaining verification boundaries` - 56 edges
9. `create_app()` - 54 edges
10. `FirestoreSessionService` - 53 edges

## Surprising Connections (you probably didn't know these)
- `Join-key compatibility, coverage and fan-out` --semantically_similar_to--> `Explicit fan-out and incomplete-input rejection`  [INFERRED] [semantically similar]
  Backend/app/skill_library/analytics-data-quality.md → docs/adr/0003-bounded-cross-source-fusion.md
- `Shared-method baseline and alternative scenario artifacts` --conceptually_related_to--> `Separate immutable scenario with same-method baseline and alternative`  [INFERRED]
  Backend/app/skill_library/prediction-driver-scenarios.md → docs/timesfm.md
- `Common chronological scores choose statistical or managed candidate` --conceptually_related_to--> `Common three-fold full-horizon measured method selection`  [INFERRED]
  Backend/app/skill_library/prediction-sales-forecast.md → docs/timesfm.md
- `main()` --uses--> `FirestoreSessionService`  [INFERRED]
  infra/runtime_check.py → Backend/app/adk_sessions.py
- `foundation()` --calls--> `operator_credentials()`  [INFERRED]
  infra/provision_reports.py → Backend/app/admin.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Saved-series candidate comparison and conditional-scenario validation** — docs_architecture_saved_comparison, docs_architecture_managed_timesfm, docs_architecture_forecast_selection, docs_architecture_conditional_scenarios [EXTRACTED 1.00]
- **Static saved-evidence previews retain analytical and publication boundaries** — docs_landing_page_guided_preview, docs_landing_page_forecast_fixture, docs_landing_page_scenario_fixture, docs_landing_page_captured_version_links [EXTRACTED 1.00]
- **Fenced admission, stable jobs, persistent cancellation and conservative billing** — docs_timesfm_atomic_admission, docs_timesfm_stable_jobs, docs_timesfm_persistent_cancellation, docs_timesfm_conservative_billing [EXTRACTED 1.00]
- **Frozen saved input, deterministic selection, separate scenarios and immutable exports** — docs_timesfm_frozen_saved_input, docs_timesfm_candidate_selection, docs_timesfm_separate_scenario, docs_timesfm_saved_export_evidence [EXTRACTED 1.00]

## Communities (113 total, 27 thin omitted)

### Community 0 - "Report Coordination and Contracts"
Cohesion: 0.05
Nodes (69): fixture_answer(), fixture_plan(), Explicit local-only sample planner. Never used as a Gemini fallback., change(), date_value(), metadata(), next_date(), normalized_spec() (+61 more)

### Community 1 - "TimesFM Numerical and Recovery Tests"
Cohesion: 0.09
Nodes (65): choose(), compare(), eligible(), intervals(), Application-owned candidate selection over a frozen saved series., reserve_candidates(), score_remote(), ForecastSpec (+57 more)

### Community 2 - "Workspace Preferences and Motion"
Cohesion: 0.05
Nodes (50): body, heading, metadata, mono, metadata, AppearanceSync(), AppProviders(), AnimatedNumber() (+42 more)

### Community 3 - "Skill Catalog and Seeding"
Cohesion: 0.07
Nodes (42): analytics_examples(), Stable seed IDs let operators add examples without replacing public edits., Import the reviewable, source-controlled pack before any cloud writes., seed_analytics(), seed_examples(), compatible(), export_skill(), FrontmatterLoader (+34 more)

### Community 4 - "Retail Bundle Publication"
Cohesion: 0.07
Nodes (49): demand(), generate(), GeneratorConfig, money(), promotion_window(), Path, Deterministic, bounded-memory synthetic retail history; never contacts a…, read_manifest() (+41 more)

### Community 5 - "Saved Chart Presentation"
Cohesion: 0.09
Nodes (52): csv_cell(), csv_line(), number(), present(), Shared indices preserve extrema for all series, endpoints, and null boundaries., sampled_rows(), card_image(), card_notes() (+44 more)

### Community 6 - "Skill Author Concurrency Tests"
Cohesion: 0.07
Nodes (40): asyncio, cases(), matches(), AuthorDraft, main(), Evaluate the public, hosted API against independent seed reference values., main(), Opt-in API check using existing immutable artifacts; never runs an analysis or… (+32 more)

### Community 7 - "Dashboard Configuration and Tests"
Cohesion: 0.12
Nodes (39): ChartViewState, DashboardAction, DashboardCreate, DashboardItemPatch, DashboardLayout, DashboardPatch, DashboardPin, DashboardRequest (+31 more)

### Community 8 - "Product Overview and Release Evidence"
Cohesion: 0.04
Nodes (50): Private-worker Advanced Analysis with immutable report versions, Live PCM voice with replace-aware transcripts and distinct query identities, Component and data-flow architecture guide, Public FastAPI API, controlled analytics and private report-worker entrypoint, Model/cloud budgets and billing alerts are not hard spending caps, Browser-local model, appearance, chart and voice settings, Interactive saved-result charts, full-data CSV and presentation controls, Local-only real Gemini preview using in-memory operator credentials (+42 more)

### Community 9 - "Responsive Sidebar Primitives"
Cohesion: 0.06
Nodes (22): Sheet(), SheetClose(), SheetContent(), SheetDescription(), SheetHeader(), SheetTitle(), SheetTrigger(), Sidebar() (+14 more)

### Community 10 - "Application Service Architecture"
Cohesion: 0.04
Nodes (47): ADK App / Runner / Workflow, Independent durable report execution, ADR 0006: durable versioned reports (accepted 2026-10-17), ADR 0007: public report evidence (accepted 2026-10-17), Requester-only in-memory Search panel, Verified numerical claims, Distinct writer and semantic reviewer, ADK planner and controlled analysis service (+39 more)

### Community 11 - "Guarded Database Queries"
Cohesion: 0.09
Nodes (34): Connectors, retail_data(), linked_predicate(), AST validation complements restricted database roles; it is not a SQL sandbox., Every admitted OR branch must constrain the new relation to a prior one., validate_joins(), validate_sql(), test_cancel_then_forget_during_bigquery_dry_run_prevents_late_submission() (+26 more)

### Community 12 - "Validation and Saved Result Boundaries"
Cohesion: 0.05
Nodes (45): Versioned chart view, ADR 0005: saved-result dashboards (accepted 2026-10-16), Immutable paginated results, Retained artifact references, Shared dashboard implementation plan (implemented/deployed 2026-10-16), Public shared dashboards and saved-view downloads, Chromium disclosure, mobile, Preview, dashboard and concurrent-chat checks, Historical full-result chart numerical and browser verification (+37 more)

### Community 13 - "Dashboard Configuration and Tests"
Cohesion: 0.09
Nodes (32): saved_rows(), Settings, create_app(), author_router(), MemoryStore, main(), Local-only report smoke; --gemini opts into billable model calls, never cloud…, run() (+24 more)

### Community 14 - "Dashboard Results and Actions"
Cohesion: 0.17
Nodes (25): formats, DashboardHeader(), ResearchResult, SkillEvidence(), Alert(), AlertDescription(), AlertTitle(), alertVariants (+17 more)

### Community 15 - "TypeScript Compiler Configuration"
Cohesion: 0.05
Nodes (40): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+32 more)

### Community 16 - "Reviewed Author and Preview Tabs"
Cohesion: 0.10
Nodes (26): MarkdownContent(), MessageContent(), SkillMarkdown(), Phase, requirements, template, Badge(), badgeVariants (+18 more)

### Community 17 - "Managed Forecast Comparison and Recovery"
Cohesion: 0.08
Nodes (37): Disabled until managed and actual-worker access verification, ADR 0009: Managed TimesFM comparison, Fenced immutable input/configuration and operation checkpoints, Fixed parameterized managed TimesFM 3.0 Preview adapter, Agent relevance and priority, deterministic numerical selection, Same-method scenarios in separate artifacts, Retry and recovery policy, Disabled TimesFM same-job recovery and statistical fallback (+29 more)

### Community 18 - "Report Reliability Tests"
Cohesion: 0.12
Nodes (34): NeedsInput, Exception, ReportClarification, body(), fixture, parametrize, sample_artifact(), setup() (+26 more)

### Community 19 - "Shared Library Navigation"
Cohesion: 0.09
Nodes (29): ResultCard, PinToDashboard(), create(), pin(), requestFor(), forecastMethodLabel(), PredictionEvidence(), ResultCard (+21 more)

### Community 20 - "ADK Session Fencing"
Cohesion: 0.14
Nodes (22): Durable ADK session adapter with ordered events and fenced state writes., get_settings(), StaleLease, ConversationCreate, field_validator, TurnCreate, check_lease(), Small document interface with atomic, retry-safe read/modify/write operations. (+14 more)

### Community 21 - "Frontend API and Live Transport"
Cohesion: 0.10
Nodes (22): metadata, metadata, SavedCsvDownload(), download(), DashboardDownload(), download(), ReportEditDialog(), save() (+14 more)

### Community 22 - "Interactive Chart Formatting"
Cohesion: 0.13
Nodes (28): categoryColor(), InsightfulChart(), content(), download(), label(), palette, Plot(), Values() (+20 more)

### Community 23 - "Shared Library Navigation"
Cohesion: 0.10
Nodes (21): metadata, DashboardShare(), show(), DashboardEditor(), useDashboardMutation(), DashboardsLibrary(), Card(), CardContent() (+13 more)

### Community 24 - "Landing Tour and Workspace Routing"
Cohesion: 0.09
Nodes (20): metadata, capabilities, faqs, metadata, OpenQuerylane(), DashboardWidget(), LandingMobileNavigation(), HeroProduct() (+12 more)

### Community 25 - "Skill Draft Publication"
Cohesion: 0.13
Nodes (4): AppError, Exception, owned(), SkillAuthor

### Community 26 - "Workspace Preferences and Motion"
Cohesion: 0.11
Nodes (19): AnalysisProgress(), stages, Reveal(), InputGroup(), InputGroupAddon(), inputGroupAddonVariants, InputGroupButton(), inputGroupButtonVariants (+11 more)

### Community 27 - "Fenced Administrative Maintenance"
Cohesion: 0.15
Nodes (16): check_models(), cleanup_skill_authors(), cli(), dashboard_maintenance(), index_schema(), main(), operator_credentials(), Credentialed CLI only. No administrative endpoint is exposed by FastAPI. (+8 more)

### Community 28 - "Scoped Cloud Foundation"
Cohesion: 0.15
Nodes (21): main(), Build with a resource-scoped builder, then deploy as the current operator., configuration(), main(), Prepare or deploy ONLY the private report worker. Foundation/IAM are separate…, ensure_secret(), ensure_service_account(), gcloud() (+13 more)

### Community 29 - "Contributor and Presentation Guidance"
Cohesion: 0.08
Nodes (26): Playbooks cannot extend tools or forecasting permissions, Authoritative architecture Mermaid and derived graph exports, Current library/service documentation via Context7 CLI, Separate authorized deployment and data operations, Repository contributor constraints, Static four-tab landing preview with captured version evidence, Verified hosted TimesFM with disabled unverified defaults, Three-skill budget and controlled query pipeline (+18 more)

### Community 30 - "ADK Session Fencing"
Cohesion: 0.14
Nodes (12): FirestoreSessionService, AI, test_cancellation_failure_still_releases_conversation(), test_raw_audio_is_not_persisted(), test_recent_session_context_uses_newest_events(), test_result_survives_interpreter_outage_and_reconnect(), test_transient_model_failure_retried_once_only(), test_checkpointed_queries_are_not_reexecuted_after_worker_recovery() (+4 more)

### Community 32 - "Advanced Report Workflow Contract"
Cohesion: 0.11
Nodes (22): Default local plan and opt-in bounded billable probe, Named Firestore and private report bucket, TimesFM 3.0 Preview comparison over saved evidence, Private report worker app.report_worker:app, Public API for chat, voice and shared libraries, Separate routine releases, skill seeding and analytical upload, Saved-artifact-only dashboard download contract, Three-origin full-horizon backtests and baseline/domain gates (+14 more)

### Community 33 - "Static Landing Preview Contract"
Cohesion: 0.09
Nodes (24): ADR 0008 landing and workspace split, Query-aware 307 compatibility redirect, Landing palette and workspace preference isolation, Local evidence-only guided preview, Server-rendered public introduction, Direct unauthenticated workspace entry, Canonical saved report version-1 links without prefetch, Historical initial landing frontend release 00012-mv5 (+16 more)

### Community 34 - "Shared Analytical Domain Model"
Cohesion: 0.13
Nodes (23): Frozen report question, scope, sources, context and skills, Evaluation using only origin-available information, Bounded presentation over full saved result, Public collection of saved analytical cards, Dashboard item with retained artifact and saved view, Operator-selected legacy or timeseries source contract, Domain glossary, Factual claim linked to saved analytical evidence (+15 more)

### Community 35 - "Shadcn Component Configuration"
Cohesion: 0.09
Nodes (22): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+14 more)

### Community 36 - "Settings and Skill Forms"
Cohesion: 0.13
Nodes (15): Catalog, ModelSettings(), Field(), FieldContent(), FieldLegend(), FieldSet(), FieldTitle(), fieldVariants (+7 more)

### Community 37 - "Frontend Development Dependencies"
Cohesion: 0.10
Nodes (21): babel-plugin-react-compiler, eslint, eslint-config-next, devDependencies, babel-plugin-react-compiler, eslint, eslint-config-next, shadcn (+13 more)

### Community 38 - "Private Report Dispatch Architecture"
Cohesion: 0.14
Nodes (20): Record actual readiness, traffic, identities and image digests, Usage controls reduce exposure without guaranteed monetary cap, API and compatible private worker before frontend with old runs drained, Separate operator, local ADC and attached runtime credentials, Separate first-time missing-resource foundation, Opt-in public forecast/scenario acceptance over saved evidence, Verified image-only rollout preserves runtime configuration, Separate authorized fenced reset and expiry purge (+12 more)

### Community 39 - "Browser Voice Client Interfaces"
Cohesion: 0.16
Nodes (7): loadSavedInterview(), path(), SkillVoiceAuthor(), connect(), publish(), saveReview(), LiveVoice

### Community 40 - "Controlled Analysis Lifecycle"
Cohesion: 0.16
Nodes (11): AnalysisService, json_rows(), json_value(), Any, evaluate(), main(), Numerical evaluation against independent Python aggregates of the retail seed., Deterministic synthetic retail data; no real customer information. (+3 more)

### Community 41 - "Report Progress and Assumptions"
Cohesion: 0.16
Nodes (16): active(), ConversationReports(), ReportRunCard(), cancel(), clarify(), poll(), assumptionHorizon(), assumptionRows() (+8 more)

### Community 42 - "Frontend Runtime Dependencies"
Cohesion: 0.11
Nodes (19): class-variance-authority, clsx, dependencies, class-variance-authority, clsx, radix-ui, react, react-dom (+11 more)

### Community 43 - "Public Report API and State"
Cohesion: 0.20
Nodes (12): check_maintenance(), Pinned text model choices; per-analysis context never mutates shared settings., resolve_text_model(), ReportRevisionCreate, digest(), public(), Transactional report lifecycle, budgets, leases, event replay, and immutable…, Transient requester-only Google Search. Never uses the public Firestore ADK… (+4 more)

### Community 44 - "Voice Author and Model Errors"
Cohesion: 0.16
Nodes (11): model_failure(), model_retry_delay(), Public model failures and one bounded retry policy, never a tool replay policy., Respect a short Retry-After; don't retry earlier than a long provider delay., AuthorBrief, AuthorCreate, AuthorPublish, Durable, guest-scoped interviews. Drafts become shared skills only on… (+3 more)

### Community 45 - "Dashboard Detail Page"
Cohesion: 0.14
Nodes (10): metadata, DashboardWorkspace(), refreshRemoved(), restoreItem(), setMode(), unpin(), base, compiledModule (+2 more)

### Community 46 - "Model and Voice Failure Tests"
Cohesion: 0.22
Nodes (14): live(), ai_service(), live_harness(), parametrize, Fault injection at the real structured-call and Live transport seams., test_analysis_finish_storage_failure_still_clears_local_task_registry(), test_expected_voice_tool_failure_is_recoverable_without_reexecuting_query(), test_long_retry_after_does_not_retry_earlier_than_provider_requests() (+6 more)

### Community 47 - "Skills Library Editor"
Cohesion: 0.18
Nodes (8): metadata, contentOf(), SkillsWorkspace(), editSkill(), exportFile(), importFile(), openEditor(), sourceLabel()

### Community 48 - "Public API Regression Tests"
Cohesion: 0.28
Nodes (12): guest(), parametrize, A worker may finish after the event query but before the status read., test_analysis_replay_fork_and_provenance(), test_guest_scope_and_no_administrative_routes(), test_origin_and_payload_validation(), test_stream_drains_events_committed_between_poll_and_terminal_read(), test_voice_does_not_fake_model_in_fixture_mode() (+4 more)

### Community 49 - "Local Setup and Verification"
Cohesion: 0.15
Nodes (13): Operator-token Gemini fixture preview, ADC local cloud-service development, In-memory deterministic fixture mode, Loopback Firestore emulator tests, Independent Next.js output directories, Local landing and workspace entry, Local development setup, Isolated voice-author preview (+5 more)

### Community 50 - "Chart Tooltip Primitives"
Cohesion: 0.21
Nodes (11): ChartConfig, ChartContainer(), ChartContext, ChartContextProps, ChartLegendContent(), ChartTooltipContent(), getPayloadConfigFromPayload(), INITIAL_DIMENSION (+3 more)

### Community 51 - "Conversation Fencing and Recovery"
Cohesion: 0.21
Nodes (4): Repository, test_recovery_uses_saved_sql_repair_and_its_attempt_identity(), test_shared_limit_applies_across_repository_instances(), test_simultaneous_turns_have_one_winner()

### Community 52 - "Advanced Feature Contracts"
Cohesion: 0.17
Nodes (12): Advanced Analysis tools and evidence gates, Analytics and prediction playbook catalog, Separate insert-only transactional playbook seeding, Twelve curated analytics and prediction playbooks, Packaged TimesFM templates do not overwrite published skills, Combined automatic/manual selection budget of three, Public versioned Skills library, Guest-scoped skill_author_sessions (+4 more)

### Community 53 - "Reference-Aware History Maintenance"
Cohesion: 0.36
Nodes (9): clear_maintenance(), enter_maintenance(), purge_dashboards(), purge_reports(), Operator-only, reference-aware cleanup. Failed operations stay fenced for…, Explicit operator purge after recovery expires; preserve dashboard references., reset_history(), wait_for_idle() (+1 more)

### Community 54 - "ADK Report Graph and Policy"
Cohesion: 0.22
Nodes (5): ADK graph orchestration with global policy and explicit application checkpoints., Graph nodes carry only a run identifier. Bodies live in fenced checkpoints., ReportPolicy, run_report_graph(), BasePlugin

### Community 55 - "Frontend Package Scripts"
Cohesion: 0.20
Nodes (9): name, private, scripts, build, dev, lint, start, test (+1 more)

### Community 58 - "Customer Cohorts and Returns"
Cohesion: 0.36
Nodes (8): Signup cohorts and first observed purchase cohorts, Customer cohorts and repeat purchasing, Equally mature customer observation windows, Repeat purchase and activity retention denominators, Validated bounded-rate or monetary forecast domain, Explicit return-rate target and denominator, Returns and rate prediction readiness, Refund latency and cohort maturity

### Community 59 - "Data Quality and Fusion"
Cohesion: 0.32
Nodes (8): Data quality and analysis readiness, Calendar spine, unknown gaps and observed zeros, Join-key compatibility, coverage and fan-out, Independent totals reconciliation, Explicit fan-out and incomplete-input rejection, ADR: Typed bounded cross-source fusion, Gemini relationship-key and business-assumption hypotheses, Trusted compiler for typed relational fusion

### Community 60 - "Seasonality and Forecast Validation"
Cohesion: 0.32
Nodes (8): Dense retail calendar at consistent time grain, Shifted target-derived rolling predictors, Observed peaks with causal limitations, Calendar trends and retail seasonality, Baseline comparison and candidate promotion, Forecast validation and uncertainty, Chronological rolling-origin backtests, Supported prediction intervals and publication outcome

### Community 61 - "Firestore Transaction Failure Tests"
Cohesion: 0.43
Nodes (7): firestore_store(), Exercise real SDK transaction decoration with a read-phase contention fault., test_business_validation_errors_are_not_retried_or_disguised(), test_exhausted_sdk_commit_budget_is_not_multiplied(), test_read_abort_retries_then_reports_conversation_busy(), test_read_retries_are_bounded_and_exhaustion_is_a_busy_response(), test_read_retry_commits_mutation_only_once()

### Community 62 - "Retail Source Publication and Schema"
Cohesion: 0.29
Nodes (7): Original demo retail schema (seed evidence 2026-10-16), Fenced insert-only cloud publication, Independent bundle reconciliation, Expanded retail column dictionary (retail-timeseries-v1), Stable full-window extend workflow, Deterministic streaming Parquet bundle, Additional timeseries source profile

### Community 63 - "Competition Demonstration Workflow"
Cohesion: 0.29
Nodes (7): Cross-source actual-versus-target exploration, Five-minute competition demonstration, Landing previews and direct workspace entry, Production rehearsal and backup recording, Public conversation sharing and forks, Spoken analysis and interruption, Warehouse question with SQL evidence

### Community 64 - "Conditional Driver Scenario Playbook"
Cohesion: 0.33
Nodes (6): Conditional predictions with historical driver support, Conditional driver and promotion scenarios playbook, Visitor-supplied complete future driver paths, Optional available TimesFM with complete covariate context, Shared-method baseline and alternative scenario artifacts, Chronological scenario validation and extrapolation rejection

### Community 65 - "Revenue Forecast Playbook"
Cohesion: 0.33
Nodes (6): Advanced Analysis controlled forecast fitting, Common chronological scores choose statistical or managed candidate, Complete series and actual latest-observation cutoff, Revenue and demand forecasting playbook, Observed-versus-predicted values and retained method evidence, Five-percent MAE improvement and majority-fold promotion

### Community 66 - "Named Firestore ADK Persistence"
Cohesion: 0.47
Nodes (6): Separate skill author session lease collection, Bounded fresh-transaction retries for read aborts, Custom Firestore ADK session adapter, ADR: ADK persistence in named Firestore, Loaded-session revision and conversation lease fencing, Terminal event stream sequence draining

### Community 67 - "Original Retail Source Schema"
Cohesion: 0.33
Nodes (6): Original PostgreSQL retail.customer_profiles, Original BigQuery order_items, Original BigQuery orders, Original BigQuery products, Original PostgreSQL retail.regional_targets, Original BigQuery returns

### Community 68 - "Expanded Retail Table Dictionary"
Cohesion: 0.40
Nodes (6): Dense daily calendar date spine, Time-series customer_profiles, Time-series sales_order_items, Time-series sales_orders, Time-series sales_returns, Full-month store targets

### Community 69 - "Skill Revision Snapshots"
Cohesion: 0.33
Nodes (6): Per-analysis skill snapshots, Bounded metadata-only skill discovery, Public optimistic skill mutations, Immutable skill revisions and recovery, Conversational voice author (documented local implementation), Conversational voice skill author plan and contracts

### Community 70 - "Reports Library Page"
Cohesion: 0.40
Nodes (4): metadata, ReportsLibrary(), change(), restore()

### Community 71 - "Immutable Chart Data Services"
Cohesion: 0.40
Nodes (5): Deterministic bounded chart sampling, Saved-artifact chart-data endpoint, Deterministic truthful chart insights, Full saved-result CSV export, Version-2 VisualizationSpec metadata

### Community 72 - "Published Dashboard Views and Recovery"
Cohesion: 0.40
Nodes (5): Active and recoverable artifact retention, Canonical public dashboard sharing, Public revision-checked editing, Published saved chart views, Revision-checked whole-dashboard exports

### Community 73 - "Saved Chart View Tests"
Cohesion: 0.50
Nodes (3): { initialChartView, describeChartView }, load(), reader()

### Community 75 - "Sales Change Contribution Playbook"
Cohesion: 0.50
Nodes (4): Observed concentrations versus causal explanations, Sales change and segment contributions, Reconciled segment change contributions, Exact order-volume and AOV revenue bridge

### Community 76 - "Comparable Store Performance Playbook"
Cohesion: 0.67
Nodes (4): Comparable-store and target performance, Comparable-store eligibility, Store and regional target join grain, Weighted attainment and reconciled target gaps

### Community 77 - "Weighted Retail KPI Definitions"
Cohesion: 0.67
Nodes (4): Completed-order merchandise revenue, Retail KPI definitions and weighted ratios, Overall AOV from revenue and distinct orders, Weighted margin rate and additive reconciliation

### Community 78 - "Marketing Associations and Scenarios"
Cohesion: 0.67
Nodes (4): Attributed revenue per campaign spend, Compatible campaign and period aggregation, Campaign and promotion performance, Validated future promotion scenario

### Community 79 - "Merchandise Margin and Refunds"
Cohesion: 0.67
Nodes (4): Historical line merchandise revenue and cost, Merchandise margin and returns-adjusted performance, Order-cohort refund and returned-cost adjustment, Signed margin and return-cohort maturity

### Community 81 - "Public Skill Versioning Decision"
Cohesion: 0.50
Nodes (4): ADR 0004: public versioned skills (accepted 2026-10-15), Bounded metadata skill selector, Public Markdown playbooks, Analysis-scoped immutable skill snapshots

### Community 82 - "Dashboard Mutation and Retention Plan"
Cohesion: 0.50
Nodes (4): Validated ChartViewState, Fenced reference-aware history maintenance, Revision-checked idempotent dashboard mutations, Immutable saved-artifact dashboard cards

### Community 85 - "Landing Route and Preview Tests"
Cohesion: 0.67
Nodes (3): load(), source(), { workspacePath }

### Community 86 - "Public Anonymous Workspace Decision"
Cohesion: 1.00
Nodes (3): Anonymous guest token attribution, quotas and cancellation, Public shared conversations, ADR: Public workspace without accounts

### Community 91 - "Cloud Build Workflow"
Cohesion: 0.67
Nodes (3): Cloud Build Docker build step, Cloud Build Docker push step, Dedicated GCS-only build logs

## Knowledge Gaps
- **360 isolated node(s):** `agentic-bi-backend`, `$schema`, `style`, `rsc`, `tsx` (+355 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Implemented Querylane architecture and source-code map` connect `Application Service Architecture` to `Advanced Report Workflow Contract`, `Static Landing Preview Contract`, `Skill Revision Snapshots`, `Private Report Dispatch Architecture`, `Product Overview and Release Evidence`, `Validation and Saved Result Boundaries`, `Managed Forecast Comparison and Recovery`, `Local Setup and Verification`, `Advanced Feature Contracts`, `Data Quality and Fusion`, `Contributor and Presentation Guidance`, `Retail Source Publication and Schema`?**
  _High betweenness centrality (0.404) - this node is a cross-community bridge._
- **Why does `Public landing page guide` connect `Static Landing Preview Contract` to `Advanced Report Workflow Contract`, `Skill Revision Snapshots`, `Private Report Dispatch Architecture`, `Product Overview and Release Evidence`, `Application Service Architecture`, `Validation and Saved Result Boundaries`, `Local Setup and Verification`, `Advanced Feature Contracts`, `Contributor and Presentation Guidance`?**
  _High betweenness centrality (0.325) - this node is a cross-community bridge._
- **Why does `Canonical workspace link construction` connect `Static Landing Preview Contract` to `Landing Tour and Workspace Routing`?**
  _High betweenness centrality (0.313) - this node is a cross-community bridge._
- **Are the 77 inferred relationships involving `AppError` (e.g. with `AI` and `AnalysisService`) actually correct?**
  _`AppError` has 77 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `Settings` (e.g. with `Connectors` and `create_app()`) actually correct?**
  _`Settings` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `MemoryStore` (e.g. with `test_every_chart_family_and_mixed_units_can_render()` and `test_complex_plan_uses_json_mode_and_still_validates_locally()`) actually correct?**
  _`MemoryStore` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `Connectors` (e.g. with `Settings` and `AppError`) actually correct?**
  _`Connectors` has 11 INFERRED edges - model-reasoned connections that need verification._
## Extraction Integrity and Scope

Generated with Graphify 0.9.51. All 49 detected documents have semantic nodes: 44 cached and 5 refreshed by one host-session agent. Code extraction is local AST analysis. No separate model API, analytical database or deployment was invoked.

- Graphify tree-sitter reported potentially partial extraction of Frontend/src/components/workspace.tsx at line 1080; 13 symbols extracted.
- Raw external import references can have no matching project node; unresolved endpoints are reported, not fabricated.
- The default undirected simple graph can combine multiple relationships between an endpoint pair; diagnostic counts retain this limitation.
- Host semantic-token usage is unavailable, not zero.

Raw extraction contains **829 unresolved endpoint references**, **0 missing endpoint fields**, **0 self-loops** and **521 same-endpoint relationships collapsed** by the default undirected graph. Many unresolved references are external imports; absent entities are not invented. These are extraction limitations rather than runtime defects.

The graph includes managed TimesFM candidate selection, scenario evidence and static landing previews. Dated release records remain separate from implementation contracts. [VALIDATION.json](VALIDATION.json) records source hashes; [the graph guide](../docs/graphify/README.md) explains maintenance.

The CLI query smoke passed and found the saved scenario evidence and `ScenarioIllustration` source node. Its 1,500-token view was explicitly truncated. The CLI warns about an older global 0.9.42 skill installation; this refresh used the matching project-local 0.9.51 skill directly and did not modify global installations.
