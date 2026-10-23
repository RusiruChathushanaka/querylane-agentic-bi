# Graph Report - 6. Google AI Builder Cup - Agentic BI  (2026-10-23)

## Corpus Check
- 321 files · ~232,701 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2486 nodes · 6713 edges · 156 communities (120 shown, 36 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 351 edges (avg confidence: 0.91)
- Token cost: 0 separate model-API tokens; host semantic input/output usage is unavailable, not zero.

## Graph Freshness
- Built from commit: `d6727163`
- Working-tree snapshot: compare VALIDATION.json source hashes as well as the base commit.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Forecast Plan Reader and Controls
- Saved Chart Data Presentation
- Accessible Motion Preferences
- Dashboard Editing and Sharing
- Report Recovery and Export Tests
- Retail Generation and Upload
- TimesFM Validation and Recovery
- Skill Selection and Snapshot Tests
- Read-Only SQL Safety Tests
- Evidence-Backed Report Workflow
- Forecast Plan Reader and Controls
- Application Error Contracts
- Voice and Text Workspace
- Evidence-Backed Report Contracts
- Managed Forecast Comparison Policy
- Dashboard Editing and Sharing
- Metric and Planning Regression Tests
- Skill Author Concurrency Tests
- TypeScript Compiler Configuration
- Typed Fusion Regression Tests
- Accessible Motion Preferences
- Skill Selection and Snapshot Tests
- Transactional Storage and Persistence
- Scoped Cloud Provisioning
- Read-Only SQL Safety Tests
- Operator Maintenance Commands
- Read-Only SQL Safety Tests
- Read-Only SQL Safety Tests
- Shared Job Admission and Leases
- Static Product Preview Contract
- Independent Startup Reads and Nearby Saved Charts
- Operator Maintenance Commands
- Local Setup and Verification
- Responsive Sidebar Primitives
- Shared Analytical Domain Model
- Analytics and Prediction Playbooks
- Shadcn Component Configuration
- Forecast Plan Reader and Controls
- Frontend Development Dependencies
- Interactive Chart Exploration
- Release Evidence and Acceptance Boundaries
- Frontend Runtime Dependencies
- Runtime Application Configuration
- Accessible Motion Preferences
- Durable Advanced Report Contract
- Public Versioned Skill Contract
- Transactional Storage and Persistence
- AI Retry and Failure Tests
- Coherent Forecast Planning Contract
- Validation Evidence and Limits
- Independent Startup Reads and Nearby Saved Charts
- Public API Regression Tests
- Coherent Forecast Planning Contract
- Independent Resource Loading and Retry Feedback
- Skills Library Interface
- Read-Only SQL Safety Tests
- Chart Tooltip and Legend Primitives
- Immutable Shared Dashboards
- Frontend HTTP and Stream Recovery
- Responsive Sidebar Primitives
- Shared Analytical Domain Model
- Local Setup and Verification
- Frontend Package Scripts
- Frontend HTTP and Stream Recovery
- Managed Forecast Comparison Policy
- Public Versioned Skill Contract
- Validation Evidence and Limits
- Dashboard Editing and Sharing
- Read-Only SQL Safety Tests
- Customer Cohorts and Returns
- Data Quality and Fusion
- Seasonality and Backtesting
- Durable Advanced Report Contract
- Dashboard Editing and Sharing
- Coherent Forecast Planning Contract
- Retail Data Publication Workflow
- Controlled Analytics Architecture
- Report Presentation Regression Tests
- Named Firestore ADK Persistence
- Original Retail Source Schema
- Expanded Retail Column Dictionary
- Dashboard Editing and Sharing
- Startup Release Policy Tests
- Reviewed Dashboard Publication Decision
- Immutable Chart Presentation Contract
- Public Versioned Skill Contract
- Repository Release Contracts
- Responsive Sidebar Primitives
- Shared Dropdown Regression Tests
- Saved Dashboard View Tests
- Planning Skill Picker Tests
- Planning Review and Retry Tests
- Prediction Evidence Rendering Tests
- Analytics and Prediction Playbooks
- Sales Change Contribution Playbook
- Comparable Store Performance Playbook
- Analytics and Prediction Playbooks
- Weighted Retail KPI Definitions
- Marketing Associations and Scenarios
- Merchandise Margin and Refunds
- Skill Author Concurrency Tests
- Skill Author Concurrency Tests
- Application Error Contracts
- Public Skill Versioning Decision
- Static Product Preview Contract
- Public Report Evidence Boundary
- Coherent Forecast Planning Contract
- Immutable Saved-Artifact Dashboard Cards
- Browser PCM Audio Worklet
- Responsive Sidebar Primitives
- Workspace Sample Question Probes
- Chart Formatting Regression Tests
- Forecast Plan Reader and Controls
- Server-rendered Resource Feedback Tests
- Skill Author Concurrency Tests
- Skill Author Concurrency Tests
- Public Anonymous Workspace Decision
- Controlled Analytics Architecture
- Repository Release Contracts
- Runtime Backend Configuration Route
- Frontend Health Route
- Accessible Table Regression Tests
- Workspace Scroll Regression Harness
- Scoped Cloud Build Workflow
- Local Social Preview Asset
- Backend Package Entrypoint
- Analytics and Prediction Playbooks
- Analytics and Prediction Playbooks
- Analytics and Prediction Playbooks
- Analytics and Prediction Playbooks
- Analytics and Prediction Playbooks
- Analytics and Prediction Playbooks
- Class Name Utility Dependency
- Immutable Durable Report Decision
- Actual-Event Analysis Stage Feedback
- Frontend ESLint Configuration
- Next Workspace Route Compatibility
- Lucide React Dependency
- Motion Dependency
- Next Dependency
- Next Themes Dependency
- Remark Gfm Dependency
- Tailwind Merge Dependency
- Model Preference Regression Tests
- Future Driver Assumption Tests
- Static Product Preview Contract
- Repository Release Contracts
- BeUI License Attribution
- Backend Dependency Manifest

## God Nodes (most connected - your core abstractions)
1. `AppError` - 239 edges
2. `Settings` - 131 edges
3. `MemoryStore` - 94 edges
4. `Connectors` - 77 edges
5. `create_app()` - 70 edges
6. `Repository` - 65 edges
7. `StrictModel` - 59 edges
8. `api()` - 57 edges
9. `FirestoreSessionService` - 55 edges
10. `AI` - 49 edges

## Surprising Connections (you probably didn't know these)
- `Atomic dashboard publication` --semantically_similar_to--> `Skill Publication`  [INFERRED] [semantically similar]
  docs/ai-dashboard-builder.md → CONTEXT.md
- `Join-key compatibility, coverage and fan-out` --semantically_similar_to--> `Explicit fan-out and incomplete-input rejection`  [INFERRED] [semantically similar]
  Backend/app/skill_library/analytics-data-quality.md → docs/adr/0003-bounded-cross-source-fusion.md
- `foundation()` --calls--> `operator_credentials()`  [INFERRED]
  infra/provision_reports.py → Backend/app/admin.py
- `main()` --uses--> `Settings`  [INFERRED]
  infra/report_recovery_check.py → Backend/app/config.py
- `main()` --uses--> `AppError`  [INFERRED]
  infra/report_recovery_check.py → Backend/app/errors.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Reviewed revision-safe dashboard publication** — docs_ai_dashboard_builder_atomic_dashboard_publication, docs_ai_dashboard_builder_revision_aware_rebase, docs_ai_dashboard_builder_conditional_undo, docs_ai_dashboard_builder_guest_owned_proposal_expiry [EXTRACTED 1.00]
- **Immutable controlled metric execution** — docs_business_metrics_closed_typed_metric_formula, docs_business_metrics_application_owned_grain_compiler, docs_business_metrics_immutable_dependency_snapshots, docs_business_metrics_canonical_forecast_value_reconciliation [EXTRACTED 1.00]
- **Validated coherent hierarchy recipe** — docs_forecast_plans_aggregate_candidate_selection, docs_forecast_plans_training_only_leaf_allocation, docs_forecast_plans_cent_exact_monetary_reconciliation, docs_forecast_plans_level_balanced_promotion_gate, docs_forecast_plans_coherent_baseline_fallback [EXTRACTED 1.00]
- **Static saved-evidence previews retain analytical and publication boundaries** — docs_landing_page_guided_preview, docs_landing_page_forecast_fixture, docs_landing_page_scenario_fixture, docs_landing_page_captured_version_links [EXTRACTED 1.00]
- **Immutable briefing outputs from saved evidence** — docs_reports_versions, docs_reports_reader, docs_reports_diagnostics, docs_reports_briefing, docs_reports_zip, docs_reports_old [EXTRACTED 1.00]
- **Independent cancellable resource lifecycle** — docs_startup_loading_shell_first, docs_startup_loading_parallel_workspace, docs_startup_loading_request_ownership, docs_startup_loading_get_policy, docs_startup_loading_rate_cooldown, docs_startup_loading_retained_content [EXTRACTED 1.00]
- **Fenced admission, stable jobs, persistent cancellation and conservative billing** — docs_timesfm_atomic_admission, docs_timesfm_stable_jobs, docs_timesfm_persistent_cancellation, docs_timesfm_conservative_billing [EXTRACTED 1.00]
- **Frozen saved input, deterministic selection, separate scenarios and immutable exports** — docs_timesfm_frozen_saved_input, docs_timesfm_candidate_selection, docs_timesfm_separate_scenario, docs_timesfm_saved_export_evidence [EXTRACTED 1.00]
- **Distinct ordinary-report and planning acceptance gates** — docs_validation_blocked, docs_validation_fresh, docs_validation_planning [EXTRACTED 1.00]

## Communities (156 total, 36 thin omitted)

### Community 0 - "Forecast Plan Reader and Controls"
Cohesion: 0.06
Nodes (49): metadata, metadata, metadata, metadata, DashboardBuilder(), JobControls(), send(), ResultCard (+41 more)

### Community 1 - "Saved Chart Data Presentation"
Cohesion: 0.07
Nodes (69): change(), csv_cell(), csv_line(), date_value(), metadata(), next_date(), normalized_spec(), number() (+61 more)

### Community 2 - "Accessible Motion Preferences"
Cohesion: 0.05
Nodes (57): body, heading, metadata, mono, metadata, AppearanceSync(), AppProviders(), DashboardWidget() (+49 more)

### Community 3 - "Dashboard Editing and Sharing"
Cohesion: 0.08
Nodes (45): SavedCsvDownload(), download(), DashboardDownload(), download(), DashboardShare(), show(), formats, DashboardEditor() (+37 more)

### Community 4 - "Report Recovery and Export Tests"
Cohesion: 0.05
Nodes (48): ReportDispatcher, ExportStorage, ReportPolicy, ForecastSpec, field_validator, model_validator, ReportClarification, _entry() (+40 more)

### Community 5 - "Retail Generation and Upload"
Cohesion: 0.07
Nodes (56): demand(), generate(), GeneratorConfig, money(), promotion_window(), Path, Deterministic, bounded-memory synthetic retail history; never contacts a…, read_manifest() (+48 more)

### Community 6 - "TimesFM Validation and Recovery"
Cohesion: 0.11
Nodes (54): choose(), compare(), eligible(), intervals(), Application-owned candidate selection over a frozen saved series., reserve_candidates(), score_remote(), ReportCreate (+46 more)

### Community 7 - "Skill Selection and Snapshot Tests"
Cohesion: 0.07
Nodes (44): fixture_answer(), analytics_examples(), Stable seed IDs let operators add examples without replacing public edits., Import the reviewable, source-controlled pack before any cloud writes., seed_analytics(), seed_examples(), compatible(), export_skill() (+36 more)

### Community 8 - "Read-Only SQL Safety Tests"
Cohesion: 0.08
Nodes (35): FirestoreSessionService, AI, AnalysisService, Settings, Connectors, main(), test_cancel_then_forget_during_bigquery_dry_run_prevents_late_submission(), test_cancellation_failure_still_releases_conversation() (+27 more)

### Community 9 - "Evidence-Backed Report Workflow"
Cohesion: 0.08
Nodes (26): json_rows(), json_value(), Any, evidence_signature(), model_evidence(), Answer, ResultArtifact, chart_state() (+18 more)

### Community 10 - "Forecast Plan Reader and Controls"
Cohesion: 0.06
Nodes (36): metadata, metadata, metadata, ForecastPlans(), create(), download(), narrative(), pickNode() (+28 more)

### Community 11 - "Application Error Contracts"
Cohesion: 0.09
Nodes (29): Durable ADK session adapter with ordered events and fenced state writes., get_settings(), StaleLease, Operator-only, reference-aware cleanup. Failed operations stay fenced for…, model_failure(), model_retry_delay(), Public model failures and one bounded retry policy, never a tool replay policy., Respect a short Retry-After; don't retry earlier than a long provider delay. (+21 more)

### Community 12 - "Voice and Text Workspace"
Cohesion: 0.07
Nodes (38): metadata, MetricEvidence(), PinToDashboard(), create(), pin(), requestFor(), forecastMethodLabel(), PredictionEvidence() (+30 more)

### Community 13 - "Evidence-Backed Report Contracts"
Cohesion: 0.08
Nodes (40): artifact_summary(), check_maintenance(), matched_metrics(), metric_router(), MetricFormula, MetricRef, MetricScope, Versioned public business definitions and a closed, application-owned SQL… (+32 more)

### Community 14 - "Managed Forecast Comparison Policy"
Cohesion: 0.06
Nodes (49): Conditional predictions with historical driver support, Conditional driver and promotion scenarios playbook, Visitor-supplied complete future driver paths, Optional available TimesFM with complete covariate context, Shared-method baseline and alternative scenario artifacts, Chronological scenario validation and extrapolation rejection, Advanced Analysis controlled forecast fitting, Common chronological scores choose statistical or managed candidate (+41 more)

### Community 15 - "Dashboard Editing and Sharing"
Cohesion: 0.09
Nodes (29): metadata, DashboardsLibrary(), Catalog, ModelSettings(), preferenceLabels, sections, template, AppSelectProps (+21 more)

### Community 16 - "Metric and Planning Regression Tests"
Cohesion: 0.10
Nodes (41): adjust_plan(), baseline_candidate(), capture_history(), distribute(), evaluate_recipe(), fail(), Pure hierarchical revenue calculations; no model, database or executable inputs., Largest remainder allocation keeps each published branch coherent to one cent. (+33 more)

### Community 17 - "Skill Author Concurrency Tests"
Cohesion: 0.10
Nodes (21): AuthorDraft, SkillAuthor, create(), guest(), prepared(), asyncio, parametrize, setup_service() (+13 more)

### Community 18 - "TypeScript Compiler Configuration"
Cohesion: 0.05
Nodes (42): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+34 more)

### Community 19 - "Typed Fusion Regression Tests"
Cohesion: 0.14
Nodes (35): fixture_plan(), Explicit local-only sample planner. Never used as a Gemini fallback., _arrow_bytes(), fuse(), _identifier(), Any, A typed plan compiler; no model-supplied SQL or Python reaches DuckDB., _worker() (+27 more)

### Community 20 - "Accessible Motion Preferences"
Cohesion: 0.07
Nodes (30): SkillEvidence(), Empty(), EmptyContent(), EmptyDescription(), EmptyHeader(), EmptyMedia(), emptyMediaVariants, EmptyTitle() (+22 more)

### Community 21 - "Skill Selection and Snapshot Tests"
Cohesion: 0.09
Nodes (16): saved_rows(), item_identity(), validate_view(), AppError, Exception, Preserve compiled definitions when forecasts require controlled feature…, verify_forecast_values(), Metrics (+8 more)

### Community 22 - "Transactional Storage and Persistence"
Cohesion: 0.17
Nodes (28): ChartViewState, Dashboards, public(), reset_history(), MemoryStore, action(), create(), pin() (+20 more)

### Community 23 - "Scoped Cloud Provisioning"
Cohesion: 0.13
Nodes (25): main(), Build with a resource-scoped builder, then deploy as the current operator., configuration(), main(), Prepare or deploy ONLY the private report worker. Foundation/IAM are separate…, ensure_secret(), ensure_service_account(), gcloud() (+17 more)

### Community 24 - "Read-Only SQL Safety Tests"
Cohesion: 0.10
Nodes (17): Repository, test_recent_session_context_uses_newest_events(), test_shared_admission_fitting_profile_replay_and_fencing(), test_fenced_report_adk_sessions_reject_old_worker_and_survive_reset(), setup_run(), test_completion_between_status_reads_is_not_reported_as_interrupted(), test_expired_worker_cannot_append_or_release_successor(), test_fork_keeps_immutable_artifact_references() (+9 more)

### Community 25 - "Operator Maintenance Commands"
Cohesion: 0.14
Nodes (27): check_models(), cleanup_skill_authors(), cli(), dashboard_maintenance(), index_schema(), main(), operator_credentials(), Credentialed CLI only. No administrative endpoint is exposed by FastAPI. (+19 more)

### Community 26 - "Read-Only SQL Safety Tests"
Cohesion: 0.09
Nodes (24): create_app(), accepts_gzip(), Bounded transport optimizations for public JSON reads, never execution streams…, ReadPerformanceMiddleware, SavedChartCache, client(), fixture, test_production_cannot_start_with_fixture_backends() (+16 more)

### Community 27 - "Read-Only SQL Safety Tests"
Cohesion: 0.14
Nodes (25): Deterministic synthetic retail data; no real customer information., retail_data(), linked_predicate(), AST validation complements restricted database roles; it is not a SQL sandbox., Every admitted OR branch must constrain the new relation to a prior one., validate_joins(), validate_sql(), main() (+17 more)

### Community 28 - "Shared Job Admission and Leases"
Cohesion: 0.12
Nodes (4): Operation and conservative budget reservation commit in one fenced transaction., ReportRepository, Opt-in hosted forecast/scenario acceptance. Public reports; read-only retail…, run()

### Community 29 - "Static Product Preview Contract"
Cohesion: 0.07
Nodes (29): ADR 0008 landing and workspace split, Query-aware 307 compatibility redirect, Landing palette and workspace preference isolation, Local evidence-only guided preview, Server-rendered public introduction, Direct unauthenticated workspace entry, Canonical saved report version-1 links without prefetch, Historical initial landing frontend release 00012-mv5 (+21 more)

### Community 30 - "Independent Startup Reads and Nearby Saved Charts"
Cohesion: 0.14
Nodes (28): Hosted loading-speed evidence and retained outlier contract, Further loading optimization implementation and hosted release boundary, Bounded immutable saved-chart view reuse, Immutable saved-result chart presentation, Small matching initial chart metadata preview, 23 October loading optimization release and compatibility, Request-time application-only runtime bootstrap, Bounded read timing and local browser diagnostics (+20 more)

### Community 31 - "Operator Maintenance Commands"
Cohesion: 0.10
Nodes (14): FirestoreStore, main(), Explicit operator command: uv run python -m scripts.seed_metrics [--cloud]., fixture, storage_adapter(), firestore_store(), Exercise real SDK transaction decoration with a read-phase contention fault., test_business_validation_errors_are_not_retried_or_disguised() (+6 more)

### Community 32 - "Local Setup and Verification"
Cohesion: 0.13
Nodes (27): ADK planner and interpreter, Positioned chart figures containing hidden instructions, Guarded analysis and typed cross-source fusion, Revision-checked saved-result dashboard exports, Dated release records separate from implemented architecture, Implemented application architecture, Private-worker durable report orchestration, ResourceFeedback status and retries (+19 more)

### Community 33 - "Responsive Sidebar Primitives"
Cohesion: 0.09
Nodes (8): Sidebar(), SidebarContext, SidebarContextProps, SidebarMenuButton(), sidebarMenuButtonVariants, SidebarRail(), SidebarTrigger(), useSidebar()

### Community 34 - "Shared Analytical Domain Model"
Cohesion: 0.11
Nodes (25): Allocated Estimate, Analysis Brief, Backtest, Business Metric, Dashboard Build, Dashboard Proposal, Data Profile, Document (+17 more)

### Community 35 - "Analytics and Prediction Playbooks"
Cohesion: 0.09
Nodes (23): Twelve additions; 29 active hosted skills; three deleted, Ordinary analytics versus Advanced Analysis prediction fitting, Calendar trends and retail seasonality, Campaign and promotion performance, Comparable-store and target performance, Conditional driver and promotion scenarios, Skills cannot add tools or bypass analytical safeguards, Customer cohorts and repeat purchasing (+15 more)

### Community 36 - "Shadcn Component Configuration"
Cohesion: 0.09
Nodes (22): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+14 more)

### Community 37 - "Forecast Plan Reader and Controls"
Cohesion: 0.15
Nodes (8): startBuild(), loadSavedInterview(), path(), SkillVoiceAuthor(), connect(), publish(), saveReview(), LiveVoice

### Community 38 - "Frontend Development Dependencies"
Cohesion: 0.10
Nodes (21): babel-plugin-react-compiler, eslint, eslint-config-next, devDependencies, babel-plugin-react-compiler, eslint, eslint-config-next, shadcn (+13 more)

### Community 39 - "Interactive Chart Exploration"
Cohesion: 0.23
Nodes (18): categoryColor(), InsightfulChart(), content(), download(), label(), palette, Plot(), Values() (+10 more)

### Community 40 - "Release Evidence and Acceptance Boundaries"
Cohesion: 0.18
Nodes (19): Preserved warm frontend/API policy and hosted evidence, Hosted checks require actual execution and dated evidence, 22 October Singapore warm-service cost illustration, Existing distinct API/frontend billing modes, Official Cloud Run regional pricing and service-minimum guidance, Google Cloud deployment runbook, Dedicated scoped runtime and build identities, No-traffic image-only candidate verification (+11 more)

### Community 41 - "Frontend Runtime Dependencies"
Cohesion: 0.11
Nodes (19): class-variance-authority, clsx, dependencies, class-variance-authority, clsx, radix-ui, react, react-dom (+11 more)

### Community 42 - "Runtime Application Configuration"
Cohesion: 0.16
Nodes (3): RuntimeBootstrap(), RuntimeConfig(), configureBackend()

### Community 43 - "Accessible Motion Preferences"
Cohesion: 0.18
Nodes (15): active(), ConversationReports(), ReportRunCard(), cancel(), clarify(), poll(), assumptionHorizon(), assumptionRows() (+7 more)

### Community 44 - "Durable Advanced Report Contract"
Cohesion: 0.18
Nodes (18): A4 PDF and editable Word briefing, Fenced checkpoints and transactional outbox, Verified claim policy, Structured forecast and scenario evidence, Advanced analysis reports, Independent durable report execution, Chronological forecast validation, Shared report operating ceilings (+10 more)

### Community 45 - "Public Versioned Skill Contract"
Cohesion: 0.13
Nodes (18): Skills, Bounded metadata-only skill discovery, Narrow-screen Skills library header wrapping, Public versioned Markdown Skills library, Validated SKILL.md import/export and safe Markdown, No raw HTML, remote images, scripts or installed resources, Bounded author connections, turns, tools, transcript and expiry, Fresh fenced ADK author generation reconstructed from saved context (+10 more)

### Community 46 - "Transactional Storage and Persistence"
Cohesion: 0.26
Nodes (11): DashboardAction, DashboardCreate, DashboardItemPatch, DashboardLayout, DashboardPatch, DashboardPin, DashboardRequest, field_validator (+3 more)

### Community 47 - "AI Retry and Failure Tests"
Cohesion: 0.20
Nodes (16): live(), ai_service(), live_harness(), parametrize, Fault injection at the real structured-call and Live transport seams., test_analysis_finish_storage_failure_still_clears_local_task_registry(), test_expected_voice_tool_failure_is_recoverable_without_reexecuting_query(), test_long_retry_after_does_not_retry_earlier_than_provider_requests() (+8 more)

### Community 48 - "Coherent Forecast Planning Contract"
Cohesion: 0.20
Nodes (17): Document, Insert-only metric seeding, Planning fixture execution, Application-owned grain compiler, Canonical forecast-value reconciliation, Catalog-aware text and voice planning, Closed typed metric formula, Deployed public Business Metrics Catalog (+9 more)

### Community 49 - "Validation Evidence and Limits"
Cohesion: 0.12
Nodes (17): Original quota-blocked fresh report attempt, Dashboard border and spacing release, Full saved-result chart acceptance, AOV claim correction history, Saved-only dashboard lifecycle acceptance, Validation and remaining deployment gates, Hosted report and shared-dropdown release, Post-reset fresh forecast and scenario acceptance (+9 more)

### Community 50 - "Independent Startup Reads and Nearby Saved Charts"
Cohesion: 0.24
Nodes (16): Loading-contention preservation and attribution contract, Click-only AppLink application navigation, Deployed browser code scheduling correction, Parallel admitted result module and saved metadata, Stable ready result-card reuse with dynamic fallback, Deployed chart code scheduling correction, Deployed nearby dashboard card code correction, 23 October loading-contention release and preservation (+8 more)

### Community 51 - "Public API Regression Tests"
Cohesion: 0.21
Nodes (13): UI-only, 15-second successful status reuse; execution/readiness always call…, guest(), parametrize, A worker may finish after the event query but before the status read., test_analysis_replay_fork_and_provenance(), test_guest_scope_and_no_administrative_routes(), test_origin_and_payload_validation(), test_stream_drains_events_committed_between_poll_and_terminal_read() (+5 more)

### Community 52 - "Coherent Forecast Planning Contract"
Cohesion: 0.23
Nodes (15): Aggregate candidate selection, Allocated estimate disclosure, Cent-exact monetary reconciliation, Complete hierarchy evidence, Deployed Forecast Plans with quota-limited fresh hierarchy acceptance, Document, Dual revenue hierarchies, Exact-version plan pins (+7 more)

### Community 53 - "Independent Resource Loading and Retry Feedback"
Cohesion: 0.14
Nodes (14): Initial retry limited to bootstrap GETs, Catalog resolution with strict JSON metric scope, Current library documentation via Context7, Repository instructions, Architecture Mermaid authority and derived Graphify references, Shared AppSelect presentation contract, Further local loading optimization preservation contract, Dated hosted acceptance boundaries (+6 more)

### Community 54 - "Skills Library Interface"
Cohesion: 0.18
Nodes (8): metadata, contentOf(), SkillsWorkspace(), editSkill(), exportFile(), importFile(), openEditor(), sourceLabel()

### Community 55 - "Read-Only SQL Safety Tests"
Cohesion: 0.31
Nodes (10): cases(), evaluate(), main(), matches(), Numerical evaluation against independent Python aggregates of the retail seed., main(), Evaluate the public, hosted API against independent seed reference values., main() (+2 more)

### Community 56 - "Chart Tooltip and Legend Primitives"
Cohesion: 0.21
Nodes (11): ChartConfig, ChartContainer(), ChartContext, ChartContextProps, ChartLegendContent(), ChartTooltipContent(), getPayloadConfigFromPayload(), INITIAL_DIMENSION (+3 more)

### Community 57 - "Immutable Shared Dashboards"
Cohesion: 0.26
Nodes (12): Shared dashboards, Published snapshot dashboard downloads, Bounded ephemeral dashboard exports, Reference-aware maintenance fence, View and Edit presentation modes, Immutable saved-view pins, Public editable dashboards, Lazy saved-card loading (+4 more)

### Community 58 - "Frontend HTTP and Stream Recovery"
Cohesion: 0.21
Nodes (9): capabilities, faqs, metadata, OpenQuerylane(), LandingMobileNavigation(), HeroProduct(), money(), RevenueIllustration() (+1 more)

### Community 59 - "Responsive Sidebar Primitives"
Cohesion: 0.27
Nodes (7): Sheet(), SheetClose(), SheetContent(), SheetDescription(), SheetHeader(), SheetTitle(), SheetTrigger()

### Community 60 - "Shared Analytical Domain Model"
Cohesion: 0.31
Nodes (11): Atomic dashboard publication, Conditional Undo, Deployed AI Dashboard Builder with quota-limited fresh proposal acceptance, Document, Durable dashboard proposal workflow, Evidence compatibility signature, Guest-owned proposal expiry, Planning retention maintenance (+3 more)

### Community 61 - "Local Setup and Verification"
Cohesion: 0.20
Nodes (11): Memory-only operator preview tokens expire; restart to refresh, Local deterministic fixture and in-memory mode, Direct local PostgreSQL DSN with Cloud SQL selection disabled, Setup, Alternate QUERYLANE_NEXT_DIST_DIR prevents shared output collisions, Explicit ADC cloud mode uses actual shared demo data and quotas, Local-only real Gemini preview over synthetic fixtures, Local-only report dispatch over existing timeseries bundle (+3 more)

### Community 62 - "Frontend Package Scripts"
Cohesion: 0.20
Nodes (9): name, private, scripts, build, dev, lint, start, test (+1 more)

### Community 63 - "Frontend HTTP and Stream Recovery"
Cohesion: 0.27
Nodes (5): metadata, DashboardWorkspace(), refreshRemoved(), restoreItem(), unpin()

### Community 64 - "Managed Forecast Comparison Policy"
Cohesion: 0.20
Nodes (10): Advanced reports, AI dashboards and validated forecasting, Querylane product and setup entrypoint, Packaged landing previews without backend execution, Metrics, Forecast Plans, Dashboards, Reports and Skills libraries, Public conversational retail intelligence, 21 October report/dropdown release (dated), Browser-local appearance, chart, conversation and voice settings, Deployed independent startup loading and viewport workspace (+2 more)

### Community 65 - "Public Versioned Skill Contract"
Cohesion: 0.25
Nodes (9): Executive retail performance review, Decision-focused reports with verified numerical evidence, Concise spoken findings with visual evidence, Conversational business decision briefing, Metadata-first discovery with manual attachment priority, Versioned skill snapshots and explicit insert-only publication, Bounded selection followed by analysis-scoped snapshots, Shared attachments inherited by forks; busy conversations reject mutation (+1 more)

### Community 66 - "Validation Evidence and Limits"
Cohesion: 0.22
Nodes (9): Local chart exploration defaults, Workspace settings, Browser-local automatic preferences, Pinned analysis model snapshots, Unified reduced-motion behavior, Presentation precision and scope precedence, Source-correct sample questions, Preference storage and safe reset (+1 more)

### Community 67 - "Dashboard Editing and Sharing"
Cohesion: 0.36
Nodes (7): ProductTour(), views, Tabs(), TabsContent(), TabsList(), tabsListVariants, TabsTrigger()

### Community 68 - "Read-Only SQL Safety Tests"
Cohesion: 0.32
Nodes (7): error(), execute(), Private Cloud Run entrypoint. Deploy with --no-allow-unauthenticated and…, reconcile(), TaskBody, exception_handler, post

### Community 69 - "Customer Cohorts and Returns"
Cohesion: 0.36
Nodes (8): Signup cohorts and first observed purchase cohorts, Customer cohorts and repeat purchasing, Equally mature customer observation windows, Repeat purchase and activity retention denominators, Validated bounded-rate or monetary forecast domain, Explicit return-rate target and denominator, Returns and rate prediction readiness, Refund latency and cohort maturity

### Community 70 - "Data Quality and Fusion"
Cohesion: 0.32
Nodes (8): Data quality and analysis readiness, Calendar spine, unknown gaps and observed zeros, Join-key compatibility, coverage and fan-out, Independent totals reconciliation, Explicit fan-out and incomplete-input rejection, ADR: Typed bounded cross-source fusion, Gemini relationship-key and business-assumption hypotheses, Trusted compiler for typed relational fusion

### Community 71 - "Seasonality and Backtesting"
Cohesion: 0.32
Nodes (8): Dense retail calendar at consistent time grain, Shifted target-derived rolling predictors, Observed peaks with causal limitations, Calendar trends and retail seasonality, Baseline comparison and candidate promotion, Forecast validation and uncertainty, Chronological rolling-origin backtests, Supported prediction intervals and publication outcome

### Community 72 - "Durable Advanced Report Contract"
Cohesion: 0.25
Nodes (7): Default local plan and opt-in bounded billable probe, Named Firestore and private report bucket, TimesFM 3.0 Preview comparison over saved evidence, Private report worker app.report_worker:app, Public API for chat, voice and shared libraries, Separate routine releases, skill seeding and analytical upload, Saved-artifact-only dashboard download contract

### Community 73 - "Dashboard Editing and Sharing"
Cohesion: 0.29
Nodes (5): MarkdownContent(), MessageContent(), SkillMarkdown(), compiledModule, render()

### Community 74 - "Coherent Forecast Planning Contract"
Cohesion: 0.29
Nodes (7): Adaptive coherent planning, Document, End-to-end reconciliation validation, Frozen planning fit profile, Point forecast uncertainty boundary, Coherent baseline fallback, Level-balanced promotion gate

### Community 75 - "Retail Data Publication Workflow"
Cohesion: 0.29
Nodes (7): Original demo retail schema (seed evidence 2026-10-16), Fenced insert-only cloud publication, Independent bundle reconciliation, Expanded retail column dictionary (retail-timeseries-v1), Stable full-window extend workflow, Deterministic streaming Parquet bundle, Additional timeseries source profile

### Community 76 - "Controlled Analytics Architecture"
Cohesion: 0.29
Nodes (7): Cross-source actual-versus-target exploration, Five-minute competition demonstration, Landing previews and direct workspace entry, Production rehearsal and backup recording, Public conversation sharing and forks, Spoken analysis and interruption, Warehouse question with SQL evidence

### Community 77 - "Report Presentation Regression Tests"
Cohesion: 0.29
Nodes (5): base, compiled, labelModule, require, source

### Community 78 - "Named Firestore ADK Persistence"
Cohesion: 0.47
Nodes (6): Separate skill author session lease collection, Bounded fresh-transaction retries for read aborts, Custom Firestore ADK session adapter, ADR: ADK persistence in named Firestore, Loaded-session revision and conversation lease fencing, Terminal event stream sequence draining

### Community 79 - "Original Retail Source Schema"
Cohesion: 0.33
Nodes (6): Original PostgreSQL retail.customer_profiles, Original BigQuery order_items, Original BigQuery orders, Original BigQuery products, Original PostgreSQL retail.regional_targets, Original BigQuery returns

### Community 80 - "Expanded Retail Column Dictionary"
Cohesion: 0.40
Nodes (6): Dense daily calendar date spine, Time-series customer_profiles, Time-series sales_order_items, Time-series sales_orders, Time-series sales_returns, Full-month store targets

### Community 81 - "Dashboard Editing and Sharing"
Cohesion: 0.40
Nodes (4): metadata, ReportsLibrary(), change(), restore()

### Community 83 - "Reviewed Dashboard Publication Decision"
Cohesion: 0.40
Nodes (5): Document, Proposal retention, Reviewable dashboard generation, Reviewed rebase and conditional Undo, Shared durable execution

### Community 84 - "Immutable Chart Presentation Contract"
Cohesion: 0.40
Nodes (5): Deterministic bounded chart sampling, Saved-artifact chart-data endpoint, Deterministic truthful chart insights, Full saved-result CSV export, Version-2 VisualizationSpec metadata

### Community 85 - "Public Versioned Skill Contract"
Cohesion: 0.40
Nodes (5): Guest-scoped skill_author_sessions, Deterministic SkillContent draft compiler, Fresh fenced ADK connection recovery, Narrow Gemini Live requirements/draft tools, Explicit atomic reviewed publication

### Community 86 - "Repository Release Contracts"
Cohesion: 0.40
Nodes (5): Frontend contributor instructions, Guest-scoped report clarification and skill draft recovery, Installed Next.js version guides, Browser preferences and reduced-motion feedback, Explicit saved chart publication and revision checks

### Community 87 - "Responsive Sidebar Primitives"
Cohesion: 0.40
Nodes (4): Tooltip(), TooltipContent(), TooltipProvider(), TooltipTrigger()

### Community 88 - "Shared Dropdown Regression Tests"
Cohesion: 0.50
Nodes (4): { AppSelect, AppSelectItem, encodeChoice, decodeChoice }, load(), require, select

### Community 89 - "Saved Dashboard View Tests"
Cohesion: 0.50
Nodes (3): { initialChartView, describeChartView }, load(), reader()

### Community 90 - "Planning Skill Picker Tests"
Cohesion: 0.50
Nodes (3): picker(), require, skills

### Community 91 - "Planning Review and Retry Tests"
Cohesion: 0.50
Nodes (3): { dashboardChanges }, load(), require

### Community 92 - "Prediction Evidence Rendering Tests"
Cohesion: 0.40
Nodes (4): base, compiledModule, render(), require

### Community 93 - "Analytics and Prediction Playbooks"
Cohesion: 0.50
Nodes (4): Distinct-order support, directional confidence and lift, Basket composition and product affinity, Complete purchasing-population concentration shares, Customer revenue concentration and dependency

### Community 94 - "Sales Change Contribution Playbook"
Cohesion: 0.50
Nodes (4): Observed concentrations versus causal explanations, Sales change and segment contributions, Reconciled segment change contributions, Exact order-volume and AOV revenue bridge

### Community 95 - "Comparable Store Performance Playbook"
Cohesion: 0.67
Nodes (4): Comparable-store and target performance, Comparable-store eligibility, Store and regional target join grain, Weighted attainment and reconciled target gaps

### Community 96 - "Analytics and Prediction Playbooks"
Cohesion: 0.50
Nodes (4): Compatible-grain explicit-key reconciliation, Cross-source grain and join reconciliation, Dashboard evidence and comparability audit, Saved-card period, metric and completeness comparability

### Community 97 - "Weighted Retail KPI Definitions"
Cohesion: 0.67
Nodes (4): Completed-order merchandise revenue, Retail KPI definitions and weighted ratios, Overall AOV from revenue and distinct orders, Weighted margin rate and additive reconciliation

### Community 98 - "Marketing Associations and Scenarios"
Cohesion: 0.67
Nodes (4): Attributed revenue per campaign spend, Compatible campaign and period aggregation, Campaign and promotion performance, Validated future promotion scenario

### Community 99 - "Merchandise Margin and Refunds"
Cohesion: 0.67
Nodes (4): Historical line merchandise revenue and cost, Merchandise margin and returns-adjusted performance, Order-cohort refund and returned-cost adjustment, Signed margin and return-cohort maturity

### Community 100 - "Skill Author Concurrency Tests"
Cohesion: 0.67
Nodes (3): main(), Opt-in API check using existing immutable artifacts; never runs an analysis or…, run()

### Community 101 - "Skill Author Concurrency Tests"
Cohesion: 0.67
Nodes (3): main(), Opt-in hosted report acceptance; creates public verification…, run()

### Community 103 - "Public Skill Versioning Decision"
Cohesion: 0.50
Nodes (4): ADR 0004: public versioned skills (accepted 2026-10-15), Bounded metadata skill selector, Public Markdown playbooks, Analysis-scoped immutable skill snapshots

### Community 104 - "Static Product Preview Contract"
Cohesion: 0.50
Nodes (4): Versioned chart view, ADR 0005: saved-result dashboards (accepted 2026-10-16), Immutable paginated results, Retained artifact references

### Community 105 - "Public Report Evidence Boundary"
Cohesion: 0.50
Nodes (4): ADR 0007: public report evidence (accepted 2026-10-17), Requester-only in-memory Search panel, Verified numerical claims, Distinct writer and semantic reviewer

### Community 106 - "Coherent Forecast Planning Contract"
Cohesion: 0.50
Nodes (4): Document, Immutable metric lineage, Public executable metric contracts, Structural publication validation

### Community 107 - "Immutable Saved-Artifact Dashboard Cards"
Cohesion: 0.50
Nodes (4): Validated ChartViewState, Fenced reference-aware history maintenance, Revision-checked idempotent dashboard mutations, Immutable saved-artifact dashboard cards

### Community 109 - "Responsive Sidebar Primitives"
Cohesion: 0.67
Nodes (3): SidebarProvider(), subscribe(), useIsMobile()

### Community 110 - "Workspace Sample Question Probes"
Cohesion: 0.67
Nodes (3): ab(), ev(), Exercise actual card handlers under all source preferences without real…

### Community 112 - "Forecast Plan Reader and Controls"
Cohesion: 0.67
Nodes (3): load(), source(), { workspacePath }

### Community 117 - "Public Anonymous Workspace Decision"
Cohesion: 1.00
Nodes (3): Anonymous guest token attribution, quotas and cancellation, Public shared conversations, ADR: Public workspace without accounts

### Community 118 - "Controlled Analytics Architecture"
Cohesion: 0.67
Nodes (3): ADK App / Runner / Workflow, Independent durable report execution, ADR 0006: durable versioned reports (accepted 2026-10-17)

### Community 119 - "Repository Release Contracts"
Cohesion: 0.67
Nodes (3): Motion and feedback (deployed 2026-10-16), Reader-aware answer following, Unified device/application reduced motion

### Community 125 - "Scoped Cloud Build Workflow"
Cohesion: 0.67
Nodes (3): Cloud Build Docker build step, Cloud Build Docker push step, Dedicated GCS-only build logs

## Knowledge Gaps
- **243 isolated node(s):** `agentic-bi-backend`, `$schema`, `style`, `rsc`, `tsx` (+238 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **36 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AppError` connect `Skill Selection and Snapshot Tests` to `Saved Chart Data Presentation`, `Report Recovery and Export Tests`, `Retail Generation and Upload`, `TimesFM Validation and Recovery`, `Skill Selection and Snapshot Tests`, `Read-Only SQL Safety Tests`, `Evidence-Backed Report Workflow`, `Application Error Contracts`, `Evidence-Backed Report Contracts`, `Metric and Planning Regression Tests`, `Skill Author Concurrency Tests`, `Typed Fusion Regression Tests`, `Transactional Storage and Persistence`, `Read-Only SQL Safety Tests`, `Operator Maintenance Commands`, `Read-Only SQL Safety Tests`, `Read-Only SQL Safety Tests`, `Shared Job Admission and Leases`, `Operator Maintenance Commands`, `Transactional Storage and Persistence`, `AI Retry and Failure Tests`, `Read-Only SQL Safety Tests`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Why does `Public landing page guide` connect `Static Product Preview Contract` to `Local Setup and Verification`, `Release Evidence and Acceptance Boundaries`, `Durable Advanced Report Contract`, `Public Versioned Skill Contract`, `Validation Evidence and Limits`, `Independent Startup Reads and Nearby Saved Charts`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `Canonical workspace link construction` connect `Static Product Preview Contract` to `Dashboard Editing and Sharing`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Are the 88 inferred relationships involving `AppError` (e.g. with `AI` and `AnalysisService`) actually correct?**
  _`AppError` has 88 INFERRED edges - model-reasoned connections that need verification._
- **Are the 19 inferred relationships involving `Settings` (e.g. with `Connectors` and `create_app()`) actually correct?**
  _`Settings` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `MemoryStore` (e.g. with `test_every_chart_family_and_mixed_units_can_render()` and `test_complex_plan_uses_json_mode_and_still_validates_locally()`) actually correct?**
  _`MemoryStore` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 15 inferred relationships involving `Connectors` (e.g. with `Settings` and `AppError`) actually correct?**
  _`Connectors` has 15 INFERRED edges - model-reasoned connections that need verification._
## Hosted loading-contention release — 23 October 2026

The working-tree snapshot indexes click-only application links, parallel admitted chart code/metadata, synchronous ready-component reuse and exact-origin read timing/correlation. One host-session semantic agent re-extracted 9 changed documents; 60 unchanged document extractions were reused. All 252 code files passed through the local AST path. Source hashes identify 321 files. Local verification passed 456 backend tests (one existing skip) and 88 frontend tests, plus desktop/mobile checks. Hosted desktop/mobile, 29 HTTP and 24 preservation checks are recorded in the dated release assessment; graph extraction itself does not establish runtime performance. Dataset, TimesFM, warm instances and immutable exports remain unchanged. Both Submission spellings stay excluded.

- Graphify tree-sitter reported potentially partial extraction of Frontend/src/components/workspace.tsx at line 1109; 13 symbols extracted.
- Raw external import references can have no matching project node; unresolved endpoints are reported, not fabricated.
- The default undirected simple graph can combine multiple relationships between an endpoint pair; diagnostic counts retain this limitation.
- Host semantic-token usage is unavailable, not zero.
- AST extraction ran sequentially by explicit configuration; unchanged code extraction cache entries were reused.

Raw extraction: 1068 unresolved endpoint references, 0 missing endpoint fields, 0 self-loops and 591 collapsed relationships. These extraction limitations do not establish runtime failures.
