# Graph Report - 6. Google AI Builder Cup - Agentic BI  (2026-10-17)

## Corpus Check
- 224 files · ~158,550 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1777 nodes · 4671 edges · 126 communities (97 shown, 29 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 247 edges (avg confidence: 0.92)
- Token cost: 0 separate model-API tokens; host-session semantic input/output token usage is unavailable (not measured as zero).

## Graph Freshness
- Built from commit: `8493ee6b`
- This is a working-tree snapshot; VALIDATION.json records per-file SHA-256 hashes. Compare those hashes as well as the base commit to check freshness.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Saved Chart Presentation
- Retail Bundle Publication
- Versioned Skill Selection
- Workspace Motion and Themes
- Guarded Database Queries
- Settings and Skill Forms
- Dashboard Results and Actions
- Frontend API and Saved Results
- Report Analysis Contracts
- TypeScript Compiler Configuration
- API Compatibility Smoke Tests
- Shared Library Navigation
- Fenced Report Orchestration
- Shared Analytical Domain Model
- Browser Preference Synchronization
- ADK Sessions and Storage
- Dashboard Configuration and Tests
- Interactive Chart Formatting
- Result Cards and Pinning
- Typed Fusion and Visualization
- Skill Author Concurrency Tests
- Responsive Sidebar Primitives
- Analytical API Boundaries
- Application Service Architecture
- Fenced Administrative Maintenance
- Conversation Persistence and Recovery
- Report Reliability Tests
- Scoped Cloud Foundation
- Shadcn Component Configuration
- Frontend Development Dependencies
- Skill Draft Publication
- Voice Skill Author Interface
- Dashboard HTTP Contracts
- Frontend Runtime Dependencies
- Advanced Feature Contracts
- Report Reader and Progress
- Typed Cross Source Fusion
- Atomic Storage Transactions
- Local Setup and Verification
- Controlled Analysis Execution
- Public API Regression Tests
- Public Retail Product Overview
- Skills Library Editor
- Chart Tooltip Primitives
- Durable Report Engine
- Landing Release and Compatibility
- Scoped Routine Release Workflow
- Landing Product Illustrations
- Mobile Navigation and Sheets
- Report Export and Recovery
- Landing Routing and Boundaries
- Dashboard Detail Page
- Forecast and Scenario Tools
- Frontend Package Scripts
- Report Dispatch and Recovery
- Customer Cohorts and Returns
- Data Quality and Fusion
- Marketing Associations and Scenarios
- Seasonality and Forecast Validation
- Firestore Contention Tests
- Saved Charts and Preferences
- Guided Product Preview Tabs
- Time Series Data Publication
- Competition Demonstration Workflow
- Repository Contributor Guidance
- Named Firestore ADK Persistence
- Saved Dashboard Retention Design
- Original Retail Source Schema
- Expanded Retail Table Dictionary
- Skill Revision Snapshots
- Reports Library Page
- Dashboard Saved Metadata Reads
- Revenue Forecast Playbook
- Backend Runtime Responsibilities
- Immutable Chart Data Services
- Published Dashboard Views and Recovery
- Frontend Contribution Guidance
- Tooltip Context Primitives
- Saved Chart View Tests
- Report Clarification Workflow
- Sales Change Contribution Playbook
- Comparable Store Performance Playbook
- Weighted Retail KPI Definitions
- Merchandise Margin and Refunds
- Saved Dashboard Smoke Probes
- Hosted Report Smoke Probes
- Public Skill Versioning Decision
- Validated Public Evidence
- Read Only Analytical Sources
- Dashboard Mutation and Retention Plan
- Immutable Report Evidence Contract
- Browser PCM Audio Worklet
- Responsive Sidebar Primitives
- Chart Formatting Regression Tests
- Landing Routing Regression Tests
- Public Anonymous Workspace Decision
- Durable Report Execution Decision
- Runtime Backend Configuration Route
- Frontend Health Route
- Markdown Rendering Regression Tests
- Scoped Routine Release Workflow
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
- Local Social Preview Asset
- Requester Only Search
- Chronological Prediction Validation
- Synthetic Retail Source Publication
- Browser Model Selection Guide
- BeUI License Attribution
- Backend Dependency Manifest

## God Nodes (most connected - your core abstractions)
1. `AppError` - 171 edges
2. `Settings` - 105 edges
3. `MemoryStore` - 74 edges
4. `Connectors` - 58 edges
5. `create_app()` - 54 edges
6. `Repository` - 54 edges
7. `FirestoreSessionService` - 48 edges
8. `StrictModel` - 43 edges
9. `AI` - 42 edges
10. `Querylane domain glossary` - 37 edges

## Surprising Connections (you probably didn't know these)
- `Join-key compatibility, coverage and fan-out` --semantically_similar_to--> `Explicit fan-out and incomplete-input rejection`  [INFERRED] [semantically similar]
  Backend/app/skill_library/analytics-data-quality.md → docs/adr/0003-bounded-cross-source-fusion.md
- `main()` --uses--> `FirestoreSessionService`  [INFERRED]
  infra/runtime_check.py → Backend/app/adk_sessions.py
- `foundation()` --calls--> `operator_credentials()`  [INFERRED]
  infra/provision_reports.py → Backend/app/admin.py
- `main()` --uses--> `Settings`  [INFERRED]
  infra/report_recovery_check.py → Backend/app/config.py
- `main()` --uses--> `Settings`  [INFERRED]
  infra/runtime_check.py → Backend/app/config.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Controlled analytical execution pipeline** — docs_architecture_analysis_service, docs_architecture_sql_guard, docs_architecture_bigquery, docs_architecture_postgresql, docs_architecture_fusion, docs_architecture_skills_selection [EXTRACTED 1.00]
- **Durable report execution and publication** — docs_architecture_cloud_tasks, docs_architecture_report_worker, docs_architecture_reconciler, docs_architecture_report_checkpoints, docs_architecture_report_harness, docs_architecture_report_revisions, docs_architecture_report_files [EXTRACTED 1.00]
- **Isolated public product introduction** — docs_landing_page_route_split, docs_landing_page_guided_preview, docs_landing_page_fixed_palette, docs_landing_page_forecast_fixture, docs_landing_page_workspace_links, docs_landing_page_legacy_redirect [EXTRACTED 1.00]

## Communities (126 total, 29 thin omitted)

### Community 0 - "Saved Chart Presentation"
Cohesion: 0.07
Nodes (66): change(), csv_cell(), csv_line(), date_value(), metadata(), next_date(), number(), present() (+58 more)

### Community 1 - "Retail Bundle Publication"
Cohesion: 0.07
Nodes (54): demand(), generate(), GeneratorConfig, money(), promotion_window(), Path, Deterministic, bounded-memory synthetic retail history; never contacts a…, read_manifest() (+46 more)

### Community 2 - "Versioned Skill Selection"
Cohesion: 0.07
Nodes (44): analytics_examples(), Stable seed IDs let operators add examples without replacing public edits., Import the reviewable, source-controlled pack before any cloud writes., seed_analytics(), seed_examples(), compatible(), export_skill(), FrontmatterLoader (+36 more)

### Community 3 - "Workspace Motion and Themes"
Cohesion: 0.06
Nodes (44): AnalysisProgress(), stages, AnimatedNumber(), AnimatedNumberProps, ColorSelector(), ColorSelectorContext, ColorSelectorContextValue, ColorSelectorItem() (+36 more)

### Community 4 - "Guarded Database Queries"
Cohesion: 0.07
Nodes (35): Connectors, cases(), evaluate(), main(), matches(), Numerical evaluation against independent Python aggregates of the retail seed., Deterministic synthetic retail data; no real customer information., retail_data() (+27 more)

### Community 5 - "Settings and Skill Forms"
Cohesion: 0.07
Nodes (29): metadata, MarkdownContent(), MessageContent(), ChoiceSetting(), preferenceLabels, sections, updatePreference(), SkillMarkdown() (+21 more)

### Community 6 - "Dashboard Results and Actions"
Cohesion: 0.15
Nodes (27): formats, DashboardEditor(), useDashboardMutation(), ResearchResult, SkillEvidence(), Alert(), AlertDescription(), AlertTitle() (+19 more)

### Community 7 - "Frontend API and Saved Results"
Cohesion: 0.07
Nodes (27): metadata, metadata, metadata, DashboardDownload(), download(), ReportEditDialog(), save(), ReportWorkspace() (+19 more)

### Community 8 - "Report Analysis Contracts"
Cohesion: 0.10
Nodes (30): check_maintenance(), Pinned text model choices; per-analysis context never mutates shared settings., resolve_text_model(), ChartMeasure, StrictModel, Report specialists use existing guarded SQL/fusion; all numerical work is…, AnalysisTask, EvidenceClaim (+22 more)

### Community 9 - "TypeScript Compiler Configuration"
Cohesion: 0.05
Nodes (40): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+32 more)

### Community 10 - "API Compatibility Smoke Tests"
Cohesion: 0.08
Nodes (31): saved_rows(), Local-only Gemini preview on synthetic fixtures, using the operator's gcloud…, get_settings(), create_app(), ConversationCreate, field_validator, TurnCreate, Cloud Tasks outbox, reconciliation and an explicitly local-only development… (+23 more)

### Community 11 - "Shared Library Navigation"
Cohesion: 0.11
Nodes (23): metadata, DashboardShare(), show(), DashboardHeader(), DashboardsLibrary(), template, Badge(), badgeVariants (+15 more)

### Community 12 - "Fenced Report Orchestration"
Cohesion: 0.10
Nodes (10): AppError, Exception, ADK graph orchestration with global policy and explicit application checkpoints., Graph nodes carry only a run identifier. Bodies live in fenced checkpoints., ReportPolicy, run_report_graph(), digest(), ReportRepository (+2 more)

### Community 13 - "Shared Analytical Domain Model"
Cohesion: 0.09
Nodes (37): Analysis Brief, Analysis Run, Backtest, Chart Presentation, Connection, Conversation, Dashboard, Dashboard Item (+29 more)

### Community 14 - "Browser Preference Synchronization"
Cohesion: 0.08
Nodes (28): body, heading, metadata, mono, AppearanceSync(), AppProviders(), Catalog, ModelSettings() (+20 more)

### Community 15 - "ADK Sessions and Storage"
Cohesion: 0.09
Nodes (18): FirestoreSessionService, MemoryStore, main(), VoiceHarness, test_maintenance_scans_more_than_one_page_without_skipping_deleted_cursors(), test_raw_audio_is_not_persisted(), test_recent_session_context_uses_newest_events(), test_transient_model_failure_retried_once_only() (+10 more)

### Community 16 - "Dashboard Configuration and Tests"
Cohesion: 0.23
Nodes (27): Settings, ChartViewState, Dashboards, action(), create(), pin(), request(), saved() (+19 more)

### Community 17 - "Interactive Chart Formatting"
Cohesion: 0.12
Nodes (29): categoryColor(), InsightfulChart(), content(), download(), label(), palette, Plot(), Values() (+21 more)

### Community 18 - "Result Cards and Pinning"
Cohesion: 0.09
Nodes (28): SavedCsvDownload(), download(), DashboardWidget(), ResultCard, PinToDashboard(), create(), pin(), requestFor() (+20 more)

### Community 19 - "Typed Fusion and Visualization"
Cohesion: 0.19
Nodes (16): AI, fixture_answer(), fixture_plan(), Explicit local-only sample planner. Never used as a Gemini fallback., AnalysisPlan, Answer, FusionPlan, JoinKey (+8 more)

### Community 20 - "Skill Author Concurrency Tests"
Cohesion: 0.18
Nodes (25): asyncio, live(), AuthorDraft, client(), create(), guest(), prepared(), fixture (+17 more)

### Community 21 - "Responsive Sidebar Primitives"
Cohesion: 0.09
Nodes (8): Sidebar(), SidebarContext, SidebarContextProps, SidebarMenuButton(), sidebarMenuButtonVariants, SidebarRail(), SidebarTrigger(), useSidebar()

### Community 22 - "Analytical API Boundaries"
Cohesion: 0.20
Nodes (11): Durable ADK session adapter with ordered events and fenced state writes., json_rows(), json_value(), Any, StaleLease, check_lease(), Small document interface with atomic, retry-safe read/modify/write operations., Opt-in real Gemini Live/tool integration check; no microphone is recorded. Run… (+3 more)

### Community 23 - "Application Service Architecture"
Cohesion: 0.11
Nodes (25): ADK planner and interpreter, Controlled analysis service, Querylane architecture, Reviewed atomic skill publication, Saved-result chart presentation, Bounded dashboard exports, Shared saved-result dashboards, Named backend-only Firestore (+17 more)

### Community 24 - "Fenced Administrative Maintenance"
Cohesion: 0.21
Nodes (22): check_models(), cleanup_skill_authors(), cli(), dashboard_maintenance(), index_schema(), main(), operator_credentials(), Credentialed CLI only. No administrative endpoint is exposed by FastAPI. (+14 more)

### Community 25 - "Conversation Persistence and Recovery"
Cohesion: 0.13
Nodes (13): Repository, test_cancellation_failure_still_releases_conversation(), test_result_survives_interpreter_outage_and_reconnect(), test_default_retry_reuses_original_model_after_operator_default_changes(), setup_run(), test_completion_between_status_reads_is_not_reported_as_interrupted(), test_expired_worker_cannot_append_or_release_successor(), test_fork_keeps_immutable_artifact_references() (+5 more)

### Community 26 - "Report Reliability Tests"
Cohesion: 0.18
Nodes (23): body(), parametrize, sample_artifact(), setup(), started(), test_approved_date_formatting_typed_sqlglot_alias(), test_artifact_checkpoint_never_rewrites_saved_pages(), test_budgets_survive_worker_recovery_and_prevent_overspend() (+15 more)

### Community 27 - "Scoped Cloud Foundation"
Cohesion: 0.18
Nodes (19): main(), Build with a resource-scoped builder, then deploy as the current operator., configuration(), main(), Prepare or deploy ONLY the private report worker. Foundation/IAM are separate…, ensure_secret(), ensure_service_account(), gcloud() (+11 more)

### Community 28 - "Shadcn Component Configuration"
Cohesion: 0.09
Nodes (22): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+14 more)

### Community 29 - "Frontend Development Dependencies"
Cohesion: 0.10
Nodes (21): babel-plugin-react-compiler, eslint, eslint-config-next, devDependencies, babel-plugin-react-compiler, eslint, eslint-config-next, shadcn (+13 more)

### Community 31 - "Voice Skill Author Interface"
Cohesion: 0.17
Nodes (6): path(), SkillVoiceAuthor(), connect(), publish(), saveReview(), LiveVoice

### Community 32 - "Dashboard HTTP Contracts"
Cohesion: 0.22
Nodes (12): DashboardAction, DashboardCreate, DashboardItemPatch, DashboardLayout, DashboardPatch, DashboardPin, DashboardRequest, field_validator (+4 more)

### Community 33 - "Frontend Runtime Dependencies"
Cohesion: 0.11
Nodes (19): class-variance-authority, clsx, dependencies, class-variance-authority, clsx, radix-ui, react, react-dom (+11 more)

### Community 34 - "Advanced Feature Contracts"
Cohesion: 0.11
Nodes (19): Advanced Analysis prediction gates, Analytics and prediction playbook catalog, Insert-only seed-analysis-skills operation, Twelve analytics and prediction playbooks, Three-skill analysis budget, Cloud Tasks report dispatch, Private scheduled report reconciler, Fenced application checkpoints (+11 more)

### Community 35 - "Report Reader and Progress"
Cohesion: 0.18
Nodes (15): active(), ConversationReports(), ReportRunCard(), cancel(), clarify(), poll(), assumptionHorizon(), assumptionRows() (+7 more)

### Community 36 - "Typed Cross Source Fusion"
Cohesion: 0.27
Nodes (16): _arrow_bytes(), fuse(), _identifier(), Any, A typed plan compiler; no model-supplied SQL or Python reaches DuckDB., _worker(), Calculation, QueryResult (+8 more)

### Community 37 - "Atomic Storage Transactions"
Cohesion: 0.12
Nodes (7): FirestoreStore, fixture, storage_adapter(), fixture, storage_adapter(), Key, Mutation

### Community 38 - "Local Setup and Verification"
Cohesion: 0.12
Nodes (18): Operator-token Gemini fixture preview, ADC local cloud-service development, In-memory deterministic fixture mode, Loopback Firestore emulator tests, Independent Next.js output directories, Local landing and workspace entry, Local development setup, Isolated voice-author preview (+10 more)

### Community 39 - "Controlled Analysis Execution"
Cohesion: 0.18
Nodes (7): AnalysisService, normalized_spec(), Called once when saving a new artifact; historical documents remain immutable., model_evidence(), ResultArtifact, skill_reference(), BaseModel

### Community 40 - "Public API Regression Tests"
Cohesion: 0.22
Nodes (14): client(), guest(), fixture, parametrize, A worker may finish after the event query but before the status read., test_analysis_replay_fork_and_provenance(), test_guest_scope_and_no_administrative_routes(), test_origin_and_payload_validation() (+6 more)

### Community 41 - "Public Retail Product Overview"
Cohesion: 0.16
Nodes (15): Dashboard actions cloud release 2026-10-17, Advanced Analysis reports, Analytics and prediction playbooks, Browser-local settings, Real Gemini local fixture preview, Recorded cloud status 2026-10-17, Shared dashboard library, Landing page local release preparation (+7 more)

### Community 42 - "Skills Library Editor"
Cohesion: 0.18
Nodes (8): metadata, contentOf(), SkillsWorkspace(), editSkill(), exportFile(), importFile(), openEditor(), sourceLabel()

### Community 43 - "Chart Tooltip Primitives"
Cohesion: 0.21
Nodes (11): ChartConfig, ChartContainer(), ChartContext, ChartContextProps, ChartLegendContent(), ChartTooltipContent(), getPayloadConfigFromPayload(), INITIAL_DIMENSION (+3 more)

### Community 45 - "Landing Release and Compatibility"
Cohesion: 0.17
Nodes (12): ADR 0008 landing and workspace split, Query-aware 307 compatibility redirect, Landing palette and workspace preference isolation, Local evidence-only guided preview, Server-rendered public introduction, Direct unauthenticated workspace entry, Local landing acceptance and release preparation, Landing production bundle separation (+4 more)

### Community 46 - "Scoped Routine Release Workflow"
Cohesion: 0.26
Nodes (12): Dedicated Cloud Build identity, Separately authorized data operations, Explicit first-time foundation, Fenced history reset and purge, Actual serving revision release record, Dedicated demo resource boundaries, Verified revision traffic rollback, Routine application release (+4 more)

### Community 47 - "Landing Product Illustrations"
Cohesion: 0.20
Nodes (9): capabilities, faqs, metadata, OpenQuerylane(), LandingMobileNavigation(), HeroProduct(), money(), RevenueIllustration() (+1 more)

### Community 48 - "Mobile Navigation and Sheets"
Cohesion: 0.27
Nodes (7): Sheet(), SheetClose(), SheetContent(), SheetDescription(), SheetHeader(), SheetTitle(), SheetTrigger()

### Community 49 - "Report Export and Recovery"
Cohesion: 0.18
Nodes (5): ExportStorage, test_checkpointed_queries_are_not_reexecuted_after_worker_recovery(), test_export_storage_immutable_integrity_and_path_traversal(), test_recovery_uses_saved_sql_repair_and_its_attempt_identity(), test_source_profile_mismatch_fails_before_model_or_queries()

### Community 50 - "Landing Routing and Boundaries"
Cohesion: 0.25
Nodes (11): Landing and workspace release acceptance, Fixed landing palette and saved appearance isolation, Verified saved forecast fixture, Local guided preview boundary, Public landing page guide, Fixed same-origin legacy 307 redirect, Evidence-backed BI product story, Verified synthetic retail totals (+3 more)

### Community 51 - "Dashboard Detail Page"
Cohesion: 0.24
Nodes (6): metadata, DashboardWorkspace(), refreshRemoved(), restoreItem(), setMode(), unpin()

### Community 52 - "Forecast and Scenario Tools"
Cohesion: 0.38
Nodes (10): ForecastSpec, _entry(), _forecast(), _valid_domain(), series(), test_driver_scenarios_require_supported_nonleaking_explicit_paths(), test_forecast_full_horizon_independent_seasonal_fixture(), test_forecast_rejects_invalid_inputs() (+2 more)

### Community 53 - "Frontend Package Scripts"
Cohesion: 0.20
Nodes (9): name, private, scripts, build, dev, lint, start, test (+1 more)

### Community 54 - "Report Dispatch and Recovery"
Cohesion: 0.31
Nodes (3): ReportDispatcher, test_expired_waiting_report_releases_conversation_slot(), test_outbox_recovers_abandoned_workers_and_queued_cancellation()

### Community 55 - "Customer Cohorts and Returns"
Cohesion: 0.36
Nodes (8): Signup cohorts and first observed purchase cohorts, Customer cohorts and repeat purchasing, Equally mature customer observation windows, Repeat purchase and activity retention denominators, Validated bounded-rate or monetary forecast domain, Explicit return-rate target and denominator, Returns and rate prediction readiness, Refund latency and cohort maturity

### Community 56 - "Data Quality and Fusion"
Cohesion: 0.32
Nodes (8): Data quality and analysis readiness, Calendar spine, unknown gaps and observed zeros, Join-key compatibility, coverage and fan-out, Independent totals reconciliation, Explicit fan-out and incomplete-input rejection, ADR: Typed bounded cross-source fusion, Gemini relationship-key and business-assumption hypotheses, Trusted compiler for typed relational fusion

### Community 57 - "Marketing Associations and Scenarios"
Cohesion: 0.36
Nodes (8): Attributed revenue per campaign spend, Compatible campaign and period aggregation, Campaign and promotion performance, Validated future promotion scenario, Bounded regression/SARIMAX scenario predictions, Conditional driver and promotion scenarios, Visitor-supplied future driver paths, Historically supported driver model

### Community 58 - "Seasonality and Forecast Validation"
Cohesion: 0.32
Nodes (8): Dense retail calendar at consistent time grain, Shifted target-derived rolling predictors, Observed peaks with causal limitations, Calendar trends and retail seasonality, Baseline comparison and candidate promotion, Forecast validation and uncertainty, Chronological rolling-origin backtests, Supported prediction intervals and publication outcome

### Community 59 - "Firestore Contention Tests"
Cohesion: 0.43
Nodes (7): firestore_store(), Exercise real SDK transaction decoration with a read-phase contention fault., test_business_validation_errors_are_not_retried_or_disguised(), test_exhausted_sdk_commit_budget_is_not_multiplied(), test_read_abort_retries_then_reports_conversation_busy(), test_read_retries_are_bounded_and_exhaustion_is_a_busy_response(), test_read_retry_commits_mutation_only_once()

### Community 60 - "Saved Charts and Preferences"
Cohesion: 0.25
Nodes (8): Immutable saved-result chart presentation, Motion and feedback (deployed 2026-10-16), Reader-aware answer following, Unified device/application reduced motion, Versioned browser-local preferences, Local chart exploration defaults, Pinned analysis model catalog, Task-local captured analysis model

### Community 61 - "Guided Product Preview Tabs"
Cohesion: 0.43
Nodes (6): views, Tabs(), TabsContent(), TabsList(), tabsListVariants, TabsTrigger()

### Community 62 - "Time Series Data Publication"
Cohesion: 0.29
Nodes (7): Original demo retail schema (seed evidence 2026-10-16), Fenced insert-only cloud publication, Independent bundle reconciliation, Expanded retail column dictionary (retail-timeseries-v1), Stable full-window extend workflow, Deterministic streaming Parquet bundle, Additional timeseries source profile

### Community 63 - "Competition Demonstration Workflow"
Cohesion: 0.29
Nodes (7): Cross-source actual-versus-target exploration, Five-minute competition demonstration, Landing previews and direct workspace entry, Production rehearsal and backup recording, Public conversation sharing and forks, Spoken analysis and interruption, Warehouse question with SQL evidence

### Community 64 - "Repository Contributor Guidance"
Cohesion: 0.33
Nodes (6): Controlled analytics and prediction playbooks, Authoritative architecture and derived graph references, Deployment guide and dated release evidence, Immutable saved evidence and revision-checked public edits, Repository instructions, Insert-only fenced retail data operations

### Community 65 - "Named Firestore ADK Persistence"
Cohesion: 0.47
Nodes (6): Separate skill author session lease collection, Bounded fresh-transaction retries for read aborts, Custom Firestore ADK session adapter, ADR: ADK persistence in named Firestore, Loaded-session revision and conversation lease fencing, Terminal event stream sequence draining

### Community 66 - "Saved Dashboard Retention Design"
Cohesion: 0.33
Nodes (6): Versioned chart view, ADR 0005: saved-result dashboards (accepted 2026-10-16), Immutable paginated results, Retained artifact references, Shared dashboard implementation plan (implemented/deployed 2026-10-16), Public shared dashboards and saved-view downloads

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

### Community 72 - "Revenue Forecast Playbook"
Cohesion: 0.60
Nodes (5): Approved naive, ETS, SARIMAX and regression candidates, Complete observed series and actual forecast cutoff, Forecast horizons and fit budgets, Candidate promotion, baseline retention or withholding, Revenue and demand forecasting

### Community 73 - "Backend Runtime Responsibilities"
Cohesion: 0.50
Nodes (5): Querylane backend, Named Firestore and private report bucket, Private report worker with Cloud Tasks checkpoints, Public chat, voice and analytical libraries API, Saved-artifact dashboard download contract

### Community 74 - "Immutable Chart Data Services"
Cohesion: 0.40
Nodes (5): Deterministic bounded chart sampling, Saved-artifact chart-data endpoint, Deterministic truthful chart insights, Full saved-result CSV export, Version-2 VisualizationSpec metadata

### Community 75 - "Published Dashboard Views and Recovery"
Cohesion: 0.40
Nodes (5): Active and recoverable artifact retention, Canonical public dashboard sharing, Public revision-checked editing, Published saved chart views, Revision-checked whole-dashboard exports

### Community 76 - "Frontend Contribution Guidance"
Cohesion: 0.40
Nodes (5): Frontend contributor instructions, Guest-scoped report clarification and skill draft recovery, Installed Next.js version guides, Browser preferences and reduced-motion feedback, Explicit saved chart publication and revision checks

### Community 77 - "Tooltip Context Primitives"
Cohesion: 0.40
Nodes (4): Tooltip(), TooltipContent(), TooltipProvider(), TooltipTrigger()

### Community 78 - "Saved Chart View Tests"
Cohesion: 0.50
Nodes (3): { initialChartView, describeChartView }, load(), reader()

### Community 79 - "Report Clarification Workflow"
Cohesion: 0.50
Nodes (3): NeedsInput, Exception, test_graph_preserves_clarification_without_running_downstream_stages()

### Community 80 - "Sales Change Contribution Playbook"
Cohesion: 0.50
Nodes (4): Observed concentrations versus causal explanations, Sales change and segment contributions, Reconciled segment change contributions, Exact order-volume and AOV revenue bridge

### Community 81 - "Comparable Store Performance Playbook"
Cohesion: 0.67
Nodes (4): Comparable-store and target performance, Comparable-store eligibility, Store and regional target join grain, Weighted attainment and reconciled target gaps

### Community 82 - "Weighted Retail KPI Definitions"
Cohesion: 0.67
Nodes (4): Completed-order merchandise revenue, Retail KPI definitions and weighted ratios, Overall AOV from revenue and distinct orders, Weighted margin rate and additive reconciliation

### Community 83 - "Merchandise Margin and Refunds"
Cohesion: 0.67
Nodes (4): Historical line merchandise revenue and cost, Merchandise margin and returns-adjusted performance, Order-cohort refund and returned-cost adjustment, Signed margin and return-cohort maturity

### Community 84 - "Saved Dashboard Smoke Probes"
Cohesion: 0.67
Nodes (3): main(), Opt-in API check using existing immutable artifacts; never runs an analysis or…, run()

### Community 85 - "Hosted Report Smoke Probes"
Cohesion: 0.67
Nodes (3): main(), Opt-in hosted report acceptance; creates public verification…, run()

### Community 86 - "Public Skill Versioning Decision"
Cohesion: 0.50
Nodes (4): ADR 0004: public versioned skills (accepted 2026-10-15), Bounded metadata skill selector, Public Markdown playbooks, Analysis-scoped immutable skill snapshots

### Community 87 - "Validated Public Evidence"
Cohesion: 0.50
Nodes (4): ADR 0007: public report evidence (accepted 2026-10-17), Requester-only in-memory Search panel, Verified numerical claims, Distinct writer and semantic reviewer

### Community 88 - "Read Only Analytical Sources"
Cohesion: 0.67
Nodes (4): Demo BigQuery dataset, Demo read-only PostgreSQL, SQL AST validation and budgets, Timeseries source profile

### Community 89 - "Dashboard Mutation and Retention Plan"
Cohesion: 0.50
Nodes (4): Validated ChartViewState, Fenced reference-aware history maintenance, Revision-checked idempotent dashboard mutations, Immutable saved-artifact dashboard cards

### Community 90 - "Immutable Report Evidence Contract"
Cohesion: 0.50
Nodes (4): Verified-claim policy v2, Fenced transactional outbox and application checkpoints, Immutable PDF / DOCX / CSV ZIP exports, Immutable report families and revisions

### Community 92 - "Responsive Sidebar Primitives"
Cohesion: 0.67
Nodes (3): SidebarProvider(), subscribe(), useIsMobile()

### Community 94 - "Landing Routing Regression Tests"
Cohesion: 0.67
Nodes (3): load(), source(), { workspacePath }

### Community 95 - "Public Anonymous Workspace Decision"
Cohesion: 1.00
Nodes (3): Anonymous guest token attribution, quotas and cancellation, Public shared conversations, ADR: Public workspace without accounts

### Community 96 - "Durable Report Execution Decision"
Cohesion: 0.67
Nodes (3): ADK App / Runner / Workflow, Independent durable report execution, ADR 0006: durable versioned reports (accepted 2026-10-17)

### Community 101 - "Scoped Routine Release Workflow"
Cohesion: 0.67
Nodes (3): Cloud Build Docker build step, Cloud Build Docker push step, Dedicated GCS-only build logs

## Knowledge Gaps
- **237 isolated node(s):** `agentic-bi-backend`, `$schema`, `style`, `rsc`, `tsx` (+232 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AppError` connect `Fenced Report Orchestration` to `Saved Chart Presentation`, `Retail Bundle Publication`, `Versioned Skill Selection`, `Guarded Database Queries`, `Report Analysis Contracts`, `API Compatibility Smoke Tests`, `ADK Sessions and Storage`, `Dashboard Configuration and Tests`, `Typed Fusion and Visualization`, `Skill Author Concurrency Tests`, `Analytical API Boundaries`, `Fenced Administrative Maintenance`, `Conversation Persistence and Recovery`, `Report Reliability Tests`, `Skill Draft Publication`, `Dashboard HTTP Contracts`, `Typed Cross Source Fusion`, `Atomic Storage Transactions`, `Controlled Analysis Execution`, `Durable Report Engine`, `Report Export and Recovery`, `Forecast and Scenario Tools`, `Report Dispatch and Recovery`, `Firestore Contention Tests`, `Dashboard Saved Metadata Reads`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Why does `operator_credentials()` connect `Fenced Administrative Maintenance` to `Retail Bundle Publication`, `Guarded Database Queries`, `API Compatibility Smoke Tests`, `ADK Sessions and Storage`, `Analytical API Boundaries`, `Scoped Cloud Foundation`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Why does `foundation()` connect `Scoped Cloud Foundation` to `Fenced Administrative Maintenance`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Are the 62 inferred relationships involving `AppError` (e.g. with `AI` and `AnalysisService`) actually correct?**
  _`AppError` has 62 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `Settings` (e.g. with `Connectors` and `create_app()`) actually correct?**
  _`Settings` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `MemoryStore` (e.g. with `test_every_chart_family_and_mixed_units_can_render()` and `test_complex_plan_uses_json_mode_and_still_validates_locally()`) actually correct?**
  _`MemoryStore` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `Connectors` (e.g. with `Settings` and `AppError`) actually correct?**
  _`Connectors` has 11 INFERRED edges - model-reasoned connections that need verification._
## Extraction Integrity and Scope

Generated with Graphify 0.9.51. All 46 detected documents have semantic nodes: 36 cached documents and 10 re-extracted documents in one host-session agent. Code extraction uses the local AST parser. No separate model API, analytical database or cloud deployment was invoked.

- Graphify tree-sitter reported potentially partial extraction of Frontend/src/components/workspace.tsx at line 1070; 13 symbols extracted.
- Raw external import references can have no matching project node; unresolved endpoints are reported, not fabricated.
- The default undirected simple graph can combine multiple relationships between an endpoint pair; diagnostic counts retain this limitation.
- Host semantic-token usage is unavailable, not zero.

Raw extraction contains **727 unresolved endpoint references**, **0 missing endpoint fields**, **0 self-loops** and **434 same-endpoint relationships collapsed** by the default undirected graph. External SDK/module imports account for many unresolved nodes; absent entities are not invented. These are extraction limits, not runtime defects.

Community names, centrality and cross-document relationships are navigation heuristics. Dated deployment/plan statements retain their scope. [VALIDATION.json](VALIDATION.json) captures source hashes; [the guide](../docs/graphify/README.md) explains maintenance.
