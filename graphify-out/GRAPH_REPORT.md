# Graph Report - 6. Google AI Builder Cup - Agentic BI  (2026-10-21)

## Corpus Check
- 294 files · ~222,794 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2359 nodes · 6326 edges · 157 communities (118 shown, 39 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 345 edges (avg confidence: 0.91)
- Token cost: 0 separate model-API tokens; host semantic input/output usage is unavailable, not zero.

## Graph Freshness
- Built from commit: `4a355ba2`
- Working-tree snapshot: compare VALIDATION.json source hashes as well as the base commit.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- TimesFM Validation and Recovery
- Dashboard Editing and Sharing
- Accessible Motion Preferences
- Transactional Storage and Persistence
- Saved Chart Data Presentation
- Voice and Text Workspace
- Retail Generation and Upload
- Bounded Runtime Configuration
- Skill Selection and Snapshot Tests
- Bounded Runtime Configuration
- Application Error Contracts
- Managed Forecast Comparison Policy
- Forecast Plan Reader and Controls
- Frontend HTTP and Stream Recovery
- Coherent Forecast Planning Contract
- TypeScript Compiler Configuration
- Read-Only SQL Safety Tests
- Voice and Text Workspace
- Workspace Appearance and Preferences
- Shared Analytical Domain Model
- Interactive Chart Exploration
- Metric and Planning Regression Tests
- Shared Job Admission and Leases
- Report Recovery and Export Tests
- Operator Maintenance Commands
- Hierarchical Planning and Adjustments
- Typed Analysis and Visualization
- Scoped Cloud Provisioning
- Responsive Sidebar Primitives
- Controlled Analytics Architecture
- Evidence-Backed Report Contracts
- Analytics and Prediction Playbooks
- Shadcn Component Configuration
- Skill Author Concurrency Tests
- Typed Fusion Regression Tests
- Conversation Persistence and Recovery
- Frontend Development Dependencies
- Versioned Metrics and Controlled Compilation
- Application Error Contracts
- Reviewed Skill Draft Publication
- TimesFM Validation and Recovery
- Frontend Runtime Dependencies
- Static Product Preview Contract
- Worker-First Release Runbook
- Validation Evidence and Limits
- Evidence-Backed Report Workflow
- Durable Advanced Report Contract
- Public Versioned Skill Contract
- Controlled Analytics Architecture
- Forecast Plan Reader and Controls
- Forecast Plan Reader and Controls
- Repository Release Contracts
- AI Retry and Failure Tests
- Skills Library Interface
- Public API Regression Tests
- Chart Tooltip and Legend Primitives
- Immutable Shared Dashboards
- Local Setup and Verification
- Static Landing Product Tour
- Responsive Sidebar Primitives
- Dashboard Editing and Sharing
- Versioned Metrics and Controlled Compilation
- Report Recovery and Export Tests
- Frontend Package Scripts
- Forecast Plan Reader and Controls
- Forecast Plan Reader and Controls
- Read-Only SQL Safety Tests
- TimesFM Validation and Recovery
- Public Versioned Skill Contract
- Customer Cohorts and Returns
- Data Quality and Fusion
- Seasonality and Backtesting
- Backend Runtime and Verification
- Firestore Contention Regression Tests
- Workspace Preference Contracts
- Report Recovery and Export Tests
- Saved Dashboard Smoke Tests
- Retail Data Publication Workflow
- Competition Demonstration Workflow
- Report Presentation Regression Tests
- Read-Only SQL Safety Tests
- Named Firestore ADK Persistence
- Static Product Preview Contract
- Original Retail Source Schema
- Static Product Preview Contract
- Expanded Retail Column Dictionary
- Public Reports Library
- Reviewed Dashboard Publication Decision
- Immutable Chart Presentation Contract
- Public Versioned Skill Contract
- Frontend Contribution Guidance
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
- Transactional Storage Contracts
- Hosted Report Acceptance Harness
- Public Skill Versioning Decision
- Static Product Preview Contract
- Public Report Evidence Boundary
- Immutable Saved-Artifact Dashboard Cards
- Browser PCM Audio Worklet
- Responsive Sidebar Primitives
- Workspace Sample Question Probes
- Chart Formatting Regression Tests
- Forecast Plan Reader and Controls
- Durable Dashboard and Forecast Execution
- Versioned Skill Catalog
- Live Voice Failure Recovery
- Public Anonymous Workspace Decision
- Immutable Durable Report Decision
- Static Product Preview Contract
- Runtime Backend Configuration Route
- Frontend Health Route
- Forecast Plan Reader and Controls
- Safe Markdown Rendering Tests
- Accessible Table Regression Tests
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
- Retail Data Operator Workflow
- BeUI License Attribution
- Backend Dependency Manifest

## God Nodes (most connected - your core abstractions)
1. `AppError` - 239 edges
2. `Settings` - 126 edges
3. `MemoryStore` - 90 edges
4. `Connectors` - 74 edges
5. `Repository` - 65 edges
6. `create_app()` - 64 edges
7. `StrictModel` - 59 edges
8. `FirestoreSessionService` - 55 edges
9. `AI` - 49 edges
10. `api()` - 43 edges

## Surprising Connections (you probably didn't know these)
- `Join-key compatibility, coverage and fan-out` --semantically_similar_to--> `Explicit fan-out and incomplete-input rejection`  [INFERRED] [semantically similar]
  Backend/app/skill_library/analytics-data-quality.md → docs/adr/0003-bounded-cross-source-fusion.md
- `Atomic dashboard publication` --semantically_similar_to--> `Skill Publication`  [INFERRED] [semantically similar]
  docs/ai-dashboard-builder.md → CONTEXT.md
- `main()` --uses--> `FirestoreSessionService`  [INFERRED]
  infra/runtime_check.py → Backend/app/adk_sessions.py
- `foundation()` --calls--> `operator_credentials()`  [INFERRED]
  infra/provision_reports.py → Backend/app/admin.py
- `main()` --uses--> `Settings`  [INFERRED]
  infra/runtime_check.py → Backend/app/config.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Reviewed revision-safe dashboard publication** — docs_ai_dashboard_builder_atomic_dashboard_publication, docs_ai_dashboard_builder_revision_aware_rebase, docs_ai_dashboard_builder_conditional_undo, docs_ai_dashboard_builder_guest_owned_proposal_expiry [EXTRACTED 1.00]
- **Shared choice presentation and focus contract** — docs_architecture_adapter, docs_architecture_portal, docs_architecture_focus [EXTRACTED 1.00]
- **Immutable controlled metric execution** — docs_business_metrics_closed_typed_metric_formula, docs_business_metrics_application_owned_grain_compiler, docs_business_metrics_immutable_dependency_snapshots, docs_business_metrics_canonical_forecast_value_reconciliation [EXTRACTED 1.00]
- **Validated coherent hierarchy recipe** — docs_forecast_plans_aggregate_candidate_selection, docs_forecast_plans_training_only_leaf_allocation, docs_forecast_plans_cent_exact_monetary_reconciliation, docs_forecast_plans_level_balanced_promotion_gate, docs_forecast_plans_coherent_baseline_fallback [EXTRACTED 1.00]
- **Static saved-evidence previews retain analytical and publication boundaries** — docs_landing_page_guided_preview, docs_landing_page_forecast_fixture, docs_landing_page_scenario_fixture, docs_landing_page_captured_version_links [EXTRACTED 1.00]
- **Immutable briefing outputs from saved evidence** — docs_reports_versions, docs_reports_reader, docs_reports_diagnostics, docs_reports_briefing, docs_reports_zip, docs_reports_old [EXTRACTED 1.00]
- **Fenced admission, stable jobs, persistent cancellation and conservative billing** — docs_timesfm_atomic_admission, docs_timesfm_stable_jobs, docs_timesfm_persistent_cancellation, docs_timesfm_conservative_billing [EXTRACTED 1.00]
- **Frozen saved input, deterministic selection, separate scenarios and immutable exports** — docs_timesfm_frozen_saved_input, docs_timesfm_candidate_selection, docs_timesfm_separate_scenario, docs_timesfm_saved_export_evidence [EXTRACTED 1.00]
- **Distinct ordinary-report and planning acceptance gates** — docs_validation_blocked, docs_validation_fresh, docs_validation_planning [EXTRACTED 1.00]

## Communities (157 total, 39 thin omitted)

### Community 0 - "TimesFM Validation and Recovery"
Cohesion: 0.08
Nodes (56): plan_artifact(), Planning, choose(), compare(), eligible(), intervals(), Application-owned candidate selection over a frozen saved series., reserve_candidates() (+48 more)

### Community 1 - "Dashboard Editing and Sharing"
Cohesion: 0.07
Nodes (51): metadata, DashboardDownload(), download(), DashboardShare(), show(), formats, DashboardEditor(), useDashboardMutation() (+43 more)

### Community 2 - "Accessible Motion Preferences"
Cohesion: 0.05
Nodes (57): body, heading, metadata, mono, AppearanceSync(), AppProviders(), ProductTour(), AnalysisProgress() (+49 more)

### Community 3 - "Transactional Storage and Persistence"
Cohesion: 0.10
Nodes (52): ChartViewState, DashboardAction, DashboardCreate, DashboardItemPatch, DashboardLayout, DashboardPatch, DashboardPin, DashboardRequest (+44 more)

### Community 4 - "Saved Chart Data Presentation"
Cohesion: 0.07
Nodes (61): change(), csv_cell(), csv_line(), number(), present(), Shared indices preserve extrema for all series, endpoints, and null boundaries., sampled_rows(), card_image() (+53 more)

### Community 5 - "Voice and Text Workspace"
Cohesion: 0.06
Nodes (44): metadata, forecastMethodLabel(), PredictionEvidence(), active(), ConversationReports(), ReportRunCard(), cancel(), clarify() (+36 more)

### Community 6 - "Retail Generation and Upload"
Cohesion: 0.07
Nodes (52): demand(), generate(), GeneratorConfig, money(), promotion_window(), Path, Deterministic, bounded-memory synthetic retail history; never contacts a…, read_manifest() (+44 more)

### Community 7 - "Bounded Runtime Configuration"
Cohesion: 0.06
Nodes (23): FirestoreSessionService, AI, Connectors, ExportStorage, test_cancel_then_forget_during_bigquery_dry_run_prevents_late_submission(), test_cancellation_failure_still_releases_conversation(), test_raw_audio_is_not_persisted(), test_recent_session_context_uses_newest_events() (+15 more)

### Community 8 - "Skill Selection and Snapshot Tests"
Cohesion: 0.08
Nodes (40): fixture_answer(), analytics_examples(), Stable seed IDs let operators add examples without replacing public edits., Import the reviewable, source-controlled pack before any cloud writes., seed_analytics(), seed_examples(), compatible(), export_skill() (+32 more)

### Community 9 - "Bounded Runtime Configuration"
Cohesion: 0.07
Nodes (38): fixture_plan(), Explicit local-only sample planner. Never used as a Gemini fallback., Local-only Gemini preview on synthetic fixtures, using the operator's gcloud…, get_settings(), Settings, create_app(), metric_router(), live() (+30 more)

### Community 10 - "Application Error Contracts"
Cohesion: 0.11
Nodes (31): Durable ADK session adapter with ordered events and fenced state writes., AppError, Exception, StaleLease, check_maintenance(), bind_forecast(), Preserve compiled definitions when forecasts require controlled feature…, verify_forecast_values() (+23 more)

### Community 11 - "Managed Forecast Comparison Policy"
Cohesion: 0.06
Nodes (49): Conditional predictions with historical driver support, Conditional driver and promotion scenarios playbook, Visitor-supplied complete future driver paths, Optional available TimesFM with complete covariate context, Shared-method baseline and alternative scenario artifacts, Chronological scenario validation and extrapolation rejection, Advanced Analysis controlled forecast fitting, Common chronological scores choose statistical or managed candidate (+41 more)

### Community 12 - "Forecast Plan Reader and Controls"
Cohesion: 0.08
Nodes (33): metadata, DashboardBuilder(), startBuild(), JobControls(), send(), ResultCard, SavedArtifactPreview(), DashboardHeader() (+25 more)

### Community 13 - "Frontend HTTP and Stream Recovery"
Cohesion: 0.07
Nodes (34): metadata, metadata, DashboardWidget(), PinToDashboard(), create(), pin(), requestFor(), ReportEditDialog() (+26 more)

### Community 14 - "Coherent Forecast Planning Contract"
Cohesion: 0.07
Nodes (43): Document, Insert-only metric seeding, Planning fixture execution, Document, Immutable metric lineage, Public executable metric contracts, Structural publication validation, Adaptive coherent planning (+35 more)

### Community 15 - "TypeScript Compiler Configuration"
Cohesion: 0.05
Nodes (42): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+34 more)

### Community 16 - "Read-Only SQL Safety Tests"
Cohesion: 0.10
Nodes (33): Deterministic synthetic retail data; no real customer information., retail_data(), linked_predicate(), AST validation complements restricted database roles; it is not a SQL sandbox., Every admitted OR branch must constrain the new relation to a prior one., validate_joins(), validate_sql(), main() (+25 more)

### Community 17 - "Voice and Text Workspace"
Cohesion: 0.12
Nodes (24): views, MarkdownContent(), MessageContent(), SkillMarkdown(), Phase, requirements, template, AppSelectProps (+16 more)

### Community 18 - "Workspace Appearance and Preferences"
Cohesion: 0.09
Nodes (23): metadata, Catalog, ModelSettings(), ChoiceSetting(), preferenceLabels, sections, updatePreference(), Field() (+15 more)

### Community 19 - "Shared Analytical Domain Model"
Cohesion: 0.08
Nodes (36): Allocated Estimate, Analysis Brief, Backtest, Business Metric, Dashboard Build, Dashboard Proposal, Data Profile, Document (+28 more)

### Community 20 - "Interactive Chart Exploration"
Cohesion: 0.12
Nodes (28): categoryColor(), InsightfulChart(), content(), download(), label(), palette, Plot(), Values() (+20 more)

### Community 21 - "Metric and Planning Regression Tests"
Cohesion: 0.13
Nodes (29): _insert(), Insert-only packaged definitions. Never called by startup, release or history…, seed_metrics(), MetricAction, MetricDefinition, MetricQuery, MetricWrite, field_validator (+21 more)

### Community 22 - "Shared Job Admission and Leases"
Cohesion: 0.10
Nodes (6): digest(), Same admission/lease/outbox as reports; no synthetic public conversation., Operation and conservative budget reservation commit in one fenced transaction., ReportRepository, Opt-in hosted forecast/scenario acceptance. Public reports; read-only retail…, run()

### Community 23 - "Report Recovery and Export Tests"
Cohesion: 0.13
Nodes (32): body(), fixture, parametrize, sample_artifact(), setup(), started(), storage_adapter(), test_approved_date_formatting_typed_sqlglot_alias() (+24 more)

### Community 24 - "Operator Maintenance Commands"
Cohesion: 0.12
Nodes (18): check_models(), cleanup_skill_authors(), cli(), dashboard_maintenance(), index_schema(), main(), operator_credentials(), Credentialed CLI only. No administrative endpoint is exposed by FastAPI. (+10 more)

### Community 25 - "Hierarchical Planning and Adjustments"
Cohesion: 0.12
Nodes (19): adjust_plan(), baseline_candidate(), capture_history(), distribute(), evaluate_recipe(), fail(), Pure hierarchical revenue calculations; no model, database or executable inputs., Largest remainder allocation keeps each published branch coherent to one cent. (+11 more)

### Community 26 - "Typed Analysis and Visualization"
Cohesion: 0.11
Nodes (26): artifact_summary(), MetricFormula, MetricRef, ChartMeasure, field_validator, StrictModel, TurnCreate, DashboardCardEdit (+18 more)

### Community 27 - "Scoped Cloud Provisioning"
Cohesion: 0.14
Nodes (23): main(), Build with a resource-scoped builder, then deploy as the current operator., configuration(), main(), Prepare or deploy ONLY the private report worker. Foundation/IAM are separate…, ensure_secret(), ensure_service_account(), gcloud() (+15 more)

### Community 28 - "Responsive Sidebar Primitives"
Cohesion: 0.09
Nodes (8): Sidebar(), SidebarContext, SidebarContextProps, SidebarMenuButton(), sidebarMenuButtonVariants, SidebarRail(), SidebarTrigger(), useSidebar()

### Community 29 - "Controlled Analytics Architecture"
Cohesion: 0.15
Nodes (25): Dated release and acceptance boundaries, AppSelect value adapter, Controlled analysis lifecycle, Reviewed conversational skill author, Application service boundaries, Saved-evidence report briefing, Saved-result chart presentation, Coherent hierarchy and assumption versions (+17 more)

### Community 30 - "Evidence-Backed Report Contracts"
Cohesion: 0.15
Nodes (15): AnalysisTask, EvidenceClaim, ForecastInputs, field_validator, model_validator, Bounded contracts shared by the report harness, API, renderer, and numerical…, ReportClarification, ReportCreate (+7 more)

### Community 31 - "Analytics and Prediction Playbooks"
Cohesion: 0.09
Nodes (23): Twelve additions; 29 active hosted skills; three deleted, Ordinary analytics versus Advanced Analysis prediction fitting, Calendar trends and retail seasonality, Campaign and promotion performance, Comparable-store and target performance, Conditional driver and promotion scenarios, Skills cannot add tools or bypass analytical safeguards, Customer cohorts and repeat purchasing (+15 more)

### Community 32 - "Shadcn Component Configuration"
Cohesion: 0.09
Nodes (22): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+14 more)

### Community 33 - "Skill Author Concurrency Tests"
Cohesion: 0.24
Nodes (20): asyncio, AuthorDraft, create(), guest(), prepared(), parametrize, setup_service(), test_competing_publish_and_review_cannot_silently_publish_a_stale_draft() (+12 more)

### Community 34 - "Typed Fusion Regression Tests"
Cohesion: 0.25
Nodes (19): _arrow_bytes(), fuse(), _identifier(), Any, A typed plan compiler; no model-supplied SQL or Python reaches DuckDB., _worker(), Calculation, FusionPlan (+11 more)

### Community 35 - "Conversation Persistence and Recovery"
Cohesion: 0.14
Nodes (11): Repository, test_shared_admission_fitting_profile_replay_and_fencing(), setup_run(), test_completion_between_status_reads_is_not_reported_as_interrupted(), test_expired_worker_cannot_append_or_release_successor(), test_fork_keeps_immutable_artifact_references(), test_idempotent_start_charges_once(), test_session_round_trip_order_state_and_partial_events() (+3 more)

### Community 36 - "Frontend Development Dependencies"
Cohesion: 0.10
Nodes (21): babel-plugin-react-compiler, eslint, eslint-config-next, devDependencies, babel-plugin-react-compiler, eslint, eslint-config-next, shadcn (+13 more)

### Community 37 - "Versioned Metrics and Controlled Compilation"
Cohesion: 0.21
Nodes (17): Approved same-grain target comparison over a frozen revenue definition., target_plan(), catalog_plan(), compile_metric(), MetricScope, Versioned public business definitions and a closed, application-owned SQL…, Compile aggregate-at-source scalar subqueries; joins and operands are fixed., An explicit opt-out may bypass the catalog; a negated mention may not. (+9 more)

### Community 38 - "Application Error Contracts"
Cohesion: 0.17
Nodes (11): AnalysisService, json_rows(), json_value(), Any, evaluate(), main(), Numerical evaluation against independent Python aggregates of the retail seed., model_evidence() (+3 more)

### Community 40 - "TimesFM Validation and Recovery"
Cohesion: 0.20
Nodes (15): date_value(), metadata(), next_date(), normalized_spec(), Bounded, deterministic presentation of immutable result pages. No SQL or model…, Called once when saving a new artifact; historical documents remain immutable., Reject unbound metadata; old artifacts get conservative, display-only defaults., saved_rows() (+7 more)

### Community 41 - "Frontend Runtime Dependencies"
Cohesion: 0.11
Nodes (19): class-variance-authority, clsx, dependencies, class-variance-authority, clsx, radix-ui, react, react-dom (+11 more)

### Community 42 - "Static Product Preview Contract"
Cohesion: 0.12
Nodes (19): Immutable saved-result chart presentation, Canonical saved report version-1 links without prefetch, Historical initial landing frontend release 00012-mv5, Fixed landing palette and saved appearance isolation, Versioned fixture cannot silently reread mutable live source data, Verified monthly TimesFM version-1 forecast fixture, Homepage publication is a frontend release and not a data operation, Local guided preview boundary (+11 more)

### Community 43 - "Worker-First Release Runbook"
Cohesion: 0.11
Nodes (18): Dated runtime acceptance, Insert-only analytical publication, Deployment guide: Google Cloud Run and supporting services, Dashboard saved-only export acceptance, First-time foundation, Dedicated build and runtime identities, Explicit fenced data maintenance, Planning workflow compatibility gate (+10 more)

### Community 44 - "Validation Evidence and Limits"
Cohesion: 0.11
Nodes (18): Original quota-blocked fresh report attempt, Dashboard border and spacing release, Full saved-result chart acceptance, AOV claim correction history, Saved-only dashboard lifecycle acceptance, Validation and remaining deployment gates, Hosted report and shared-dropdown release, Post-reset fresh forecast and scenario acceptance (+10 more)

### Community 45 - "Evidence-Backed Report Workflow"
Cohesion: 0.24
Nodes (5): ReportEngine, ReportDraft, ReportPlan, ReportSection, test_report_writer_cannot_invent_numbers_or_references()

### Community 46 - "Durable Advanced Report Contract"
Cohesion: 0.19
Nodes (17): A4 PDF and editable Word briefing, Fenced checkpoints and transactional outbox, Verified claim policy, Structured forecast and scenario evidence, Advanced analysis reports, Independent durable report execution, Chronological forecast validation, Shared report operating ceilings (+9 more)

### Community 47 - "Public Versioned Skill Contract"
Cohesion: 0.14
Nodes (17): Skills, Bounded metadata-only skill discovery, Public versioned Markdown Skills library, Validated SKILL.md import/export and safe Markdown, No raw HTML, remote images, scripts or installed resources, Bounded author connections, turns, tools, transcript and expiry, Fresh fenced ADK author generation reconstructed from saved context, 409 skill_conflict preserves the editor draft (+9 more)

### Community 48 - "Controlled Analytics Architecture"
Cohesion: 0.12
Nodes (17): Reviewed AI Dashboard Builder, Business Metrics Catalog, Saved-result shared dashboards, Expanded synthetic retail history, Querylane · Agentic BI, Measured TimesFM comparison, Post-reset TimesFM acceptance, Hierarchical Forecast Plans (+9 more)

### Community 49 - "Forecast Plan Reader and Controls"
Cohesion: 0.14
Nodes (10): metadata, ForecastPlans(), create(), download(), narrative(), pickNode(), recompute(), tree() (+2 more)

### Community 50 - "Forecast Plan Reader and Controls"
Cohesion: 0.14
Nodes (8): metadata, metadata, MetricsWorkspace(), chooseMeasure(), test(), update(), validate(), status()

### Community 51 - "Repository Release Contracts"
Cohesion: 0.14
Nodes (14): Separate acceptance scopes, Guarded analysis and voice regression policy, Catalog-guided intent and JSON scope validation, Repository instructions, Architecture and derived Graphify synchronization, Shared AppSelect and Radix dropdown policy, Packaged landing preview boundaries, Controlled metric and planning invariants (+6 more)

### Community 52 - "AI Retry and Failure Tests"
Cohesion: 0.26
Nodes (13): ai_service(), live_harness(), parametrize, Fault injection at the real structured-call and Live transport seams., test_analysis_finish_storage_failure_still_clears_local_task_registry(), test_expected_voice_tool_failure_is_recoverable_without_reexecuting_query(), test_long_retry_after_does_not_retry_earlier_than_provider_requests(), test_metric_scope_avoids_sdk_map_schema_conversion_but_validates_locally() (+5 more)

### Community 53 - "Skills Library Interface"
Cohesion: 0.18
Nodes (8): metadata, contentOf(), SkillsWorkspace(), editSkill(), exportFile(), importFile(), openEditor(), sourceLabel()

### Community 54 - "Public API Regression Tests"
Cohesion: 0.28
Nodes (12): guest(), parametrize, A worker may finish after the event query but before the status read., test_analysis_replay_fork_and_provenance(), test_guest_scope_and_no_administrative_routes(), test_origin_and_payload_validation(), test_stream_drains_events_committed_between_poll_and_terminal_read(), test_voice_does_not_fake_model_in_fixture_mode() (+4 more)

### Community 55 - "Chart Tooltip and Legend Primitives"
Cohesion: 0.21
Nodes (11): ChartConfig, ChartContainer(), ChartContext, ChartContextProps, ChartLegendContent(), ChartTooltipContent(), getPayloadConfigFromPayload(), INITIAL_DIMENSION (+3 more)

### Community 56 - "Immutable Shared Dashboards"
Cohesion: 0.26
Nodes (12): Shared dashboards, Published snapshot dashboard downloads, Bounded ephemeral dashboard exports, Reference-aware maintenance fence, View and Edit presentation modes, Immutable saved-view pins, Public editable dashboards, Lazy saved-card loading (+4 more)

### Community 57 - "Local Setup and Verification"
Cohesion: 0.18
Nodes (12): Memory-only operator preview tokens expire; restart to refresh, Local deterministic fixture and in-memory mode, Direct local PostgreSQL DSN with Cloud SQL selection disabled, Setup, Loopback demo Firestore emulator for persistence adapters, Alternate QUERYLANE_NEXT_DIST_DIR prevents shared output collisions, Explicit ADC cloud mode uses actual shared demo data and quotas, Local-only real Gemini preview over synthetic fixtures (+4 more)

### Community 58 - "Static Landing Product Tour"
Cohesion: 0.21
Nodes (9): capabilities, faqs, metadata, OpenQuerylane(), LandingMobileNavigation(), HeroProduct(), money(), RevenueIllustration() (+1 more)

### Community 59 - "Responsive Sidebar Primitives"
Cohesion: 0.27
Nodes (7): Sheet(), SheetClose(), SheetContent(), SheetDescription(), SheetHeader(), SheetTitle(), SheetTrigger()

### Community 60 - "Dashboard Editing and Sharing"
Cohesion: 0.24
Nodes (6): metadata, DashboardWorkspace(), refreshRemoved(), restoreItem(), setMode(), unpin()

### Community 61 - "Versioned Metrics and Controlled Compilation"
Cohesion: 0.33
Nodes (3): matched_metrics(), Metrics, Reserve once before execution; replay saved pages, never repeat an uncertain…

### Community 62 - "Report Recovery and Export Tests"
Cohesion: 0.22
Nodes (5): ADK graph orchestration with global policy and explicit application checkpoints., Graph nodes carry only a run identifier. Bodies live in fenced checkpoints., ReportPolicy, run_report_graph(), BasePlugin

### Community 63 - "Frontend Package Scripts"
Cohesion: 0.20
Nodes (9): name, private, scripts, build, dev, lint, start, test (+1 more)

### Community 64 - "Forecast Plan Reader and Controls"
Cohesion: 0.27
Nodes (5): path(), SkillVoiceAuthor(), connect(), publish(), saveReview()

### Community 66 - "Read-Only SQL Safety Tests"
Cohesion: 0.39
Nodes (7): cases(), matches(), main(), Evaluate the public, hosted API against independent seed reference values., main(), Opt-in public deployment checks. Creates visible demo conversations; never…, run()

### Community 67 - "TimesFM Validation and Recovery"
Cohesion: 0.42
Nodes (9): ForecastSpec, _entry(), _forecast(), series(), test_driver_scenarios_require_supported_nonleaking_explicit_paths(), test_forecast_full_horizon_independent_seasonal_fixture(), test_forecast_rejects_invalid_inputs(), test_learned_scenario_uses_explicit_supported_paths_and_passes_baseline_gate() (+1 more)

### Community 68 - "Public Versioned Skill Contract"
Cohesion: 0.25
Nodes (9): Executive retail performance review, Decision-focused reports with verified numerical evidence, Concise spoken findings with visual evidence, Conversational business decision briefing, Metadata-first discovery with manual attachment priority, Immutable curated skill snapshots, Bounded selection followed by analysis-scoped snapshots, Shared attachments inherited by forks; busy conversations reject mutation (+1 more)

### Community 69 - "Customer Cohorts and Returns"
Cohesion: 0.36
Nodes (8): Signup cohorts and first observed purchase cohorts, Customer cohorts and repeat purchasing, Equally mature customer observation windows, Repeat purchase and activity retention denominators, Validated bounded-rate or monetary forecast domain, Explicit return-rate target and denominator, Returns and rate prediction readiness, Refund latency and cohort maturity

### Community 70 - "Data Quality and Fusion"
Cohesion: 0.32
Nodes (8): Data quality and analysis readiness, Calendar spine, unknown gaps and observed zeros, Join-key compatibility, coverage and fan-out, Independent totals reconciliation, Explicit fan-out and incomplete-input rejection, ADR: Typed bounded cross-source fusion, Gemini relationship-key and business-assumption hypotheses, Trusted compiler for typed relational fusion

### Community 71 - "Seasonality and Backtesting"
Cohesion: 0.32
Nodes (8): Dense retail calendar at consistent time grain, Shifted target-derived rolling predictors, Observed peaks with causal limitations, Calendar trends and retail seasonality, Baseline comparison and candidate promotion, Forecast validation and uncertainty, Chronological rolling-origin backtests, Supported prediction intervals and publication outcome

### Community 72 - "Backend Runtime and Verification"
Cohesion: 0.25
Nodes (7): Default local plan and opt-in bounded billable probe, Named Firestore and private report bucket, TimesFM 3.0 Preview comparison over saved evidence, Private report worker app.report_worker:app, Public API for chat, voice and shared libraries, Separate routine releases, skill seeding and analytical upload, Saved-artifact-only dashboard download contract

### Community 73 - "Firestore Contention Regression Tests"
Cohesion: 0.43
Nodes (7): firestore_store(), Exercise real SDK transaction decoration with a read-phase contention fault., test_business_validation_errors_are_not_retried_or_disguised(), test_exhausted_sdk_commit_budget_is_not_multiplied(), test_read_abort_retries_then_reports_conversation_busy(), test_read_retries_are_bounded_and_exhaustion_is_a_busy_response(), test_read_retry_commits_mutation_only_once()

### Community 74 - "Workspace Preference Contracts"
Cohesion: 0.25
Nodes (8): Local chart exploration defaults, Workspace settings, Pinned analysis model snapshots, Unified reduced-motion behavior, Presentation precision and scope precedence, Source-correct sample questions, Preference storage and safe reset, Voice preference capture

### Community 76 - "Saved Dashboard Smoke Tests"
Cohesion: 0.29
Nodes (4): main(), Opt-in API check using existing immutable artifacts; never runs an analysis or…, run(), Opt-in hosted repeated Live analysis; public test chat, read-only source…

### Community 77 - "Retail Data Publication Workflow"
Cohesion: 0.29
Nodes (7): Original demo retail schema (seed evidence 2026-10-16), Fenced insert-only cloud publication, Independent bundle reconciliation, Expanded retail column dictionary (retail-timeseries-v1), Stable full-window extend workflow, Deterministic streaming Parquet bundle, Additional timeseries source profile

### Community 78 - "Competition Demonstration Workflow"
Cohesion: 0.29
Nodes (7): Cross-source actual-versus-target exploration, Five-minute competition demonstration, Landing previews and direct workspace entry, Production rehearsal and backup recording, Public conversation sharing and forks, Spoken analysis and interruption, Warehouse question with SQL evidence

### Community 79 - "Report Presentation Regression Tests"
Cohesion: 0.29
Nodes (5): base, compiled, labelModule, require, source

### Community 80 - "Read-Only SQL Safety Tests"
Cohesion: 0.47
Nodes (5): execute(), Private Cloud Run entrypoint. Deploy with --no-allow-unauthenticated and…, reconcile(), TaskBody, post

### Community 81 - "Named Firestore ADK Persistence"
Cohesion: 0.47
Nodes (6): Separate skill author session lease collection, Bounded fresh-transaction retries for read aborts, Custom Firestore ADK session adapter, ADR: ADK persistence in named Firestore, Loaded-session revision and conversation lease fencing, Terminal event stream sequence draining

### Community 82 - "Static Product Preview Contract"
Cohesion: 0.33
Nodes (6): ADR 0008 landing and workspace split, Query-aware 307 compatibility redirect, Landing palette and workspace preference isolation, Local evidence-only guided preview, Server-rendered public introduction, Direct unauthenticated workspace entry

### Community 83 - "Original Retail Source Schema"
Cohesion: 0.33
Nodes (6): Original PostgreSQL retail.customer_profiles, Original BigQuery order_items, Original BigQuery orders, Original BigQuery products, Original PostgreSQL retail.regional_targets, Original BigQuery returns

### Community 84 - "Static Product Preview Contract"
Cohesion: 0.33
Nodes (6): Scoped Cloud Run deployment runbook, Next.js App Router, Landing and application routes, Querylane frontend, Frontend verification, Runtime API configuration

### Community 85 - "Expanded Retail Column Dictionary"
Cohesion: 0.40
Nodes (6): Dense daily calendar date spine, Time-series customer_profiles, Time-series sales_order_items, Time-series sales_orders, Time-series sales_returns, Full-month store targets

### Community 86 - "Public Reports Library"
Cohesion: 0.40
Nodes (4): metadata, ReportsLibrary(), change(), restore()

### Community 87 - "Reviewed Dashboard Publication Decision"
Cohesion: 0.40
Nodes (5): Document, Proposal retention, Reviewable dashboard generation, Reviewed rebase and conditional Undo, Shared durable execution

### Community 88 - "Immutable Chart Presentation Contract"
Cohesion: 0.40
Nodes (5): Deterministic bounded chart sampling, Saved-artifact chart-data endpoint, Deterministic truthful chart insights, Full saved-result CSV export, Version-2 VisualizationSpec metadata

### Community 89 - "Public Versioned Skill Contract"
Cohesion: 0.40
Nodes (5): Guest-scoped skill_author_sessions, Deterministic SkillContent draft compiler, Fresh fenced ADK connection recovery, Narrow Gemini Live requirements/draft tools, Explicit atomic reviewed publication

### Community 90 - "Frontend Contribution Guidance"
Cohesion: 0.40
Nodes (5): Frontend contributor instructions, Guest-scoped report clarification and skill draft recovery, Installed Next.js version guides, Browser preferences and reduced-motion feedback, Explicit saved chart publication and revision checks

### Community 91 - "Responsive Sidebar Primitives"
Cohesion: 0.40
Nodes (4): Tooltip(), TooltipContent(), TooltipProvider(), TooltipTrigger()

### Community 92 - "Shared Dropdown Regression Tests"
Cohesion: 0.50
Nodes (4): { AppSelect, AppSelectItem, encodeChoice, decodeChoice }, load(), require, select

### Community 93 - "Saved Dashboard View Tests"
Cohesion: 0.50
Nodes (3): { initialChartView, describeChartView }, load(), reader()

### Community 94 - "Planning Skill Picker Tests"
Cohesion: 0.50
Nodes (3): picker(), require, skills

### Community 95 - "Planning Review and Retry Tests"
Cohesion: 0.50
Nodes (3): { dashboardChanges }, load(), require

### Community 96 - "Prediction Evidence Rendering Tests"
Cohesion: 0.40
Nodes (4): base, compiledModule, render(), require

### Community 97 - "Analytics and Prediction Playbooks"
Cohesion: 0.50
Nodes (4): Distinct-order support, directional confidence and lift, Basket composition and product affinity, Complete purchasing-population concentration shares, Customer revenue concentration and dependency

### Community 98 - "Sales Change Contribution Playbook"
Cohesion: 0.50
Nodes (4): Observed concentrations versus causal explanations, Sales change and segment contributions, Reconciled segment change contributions, Exact order-volume and AOV revenue bridge

### Community 99 - "Comparable Store Performance Playbook"
Cohesion: 0.67
Nodes (4): Comparable-store and target performance, Comparable-store eligibility, Store and regional target join grain, Weighted attainment and reconciled target gaps

### Community 100 - "Analytics and Prediction Playbooks"
Cohesion: 0.50
Nodes (4): Compatible-grain explicit-key reconciliation, Cross-source grain and join reconciliation, Dashboard evidence and comparability audit, Saved-card period, metric and completeness comparability

### Community 101 - "Weighted Retail KPI Definitions"
Cohesion: 0.67
Nodes (4): Completed-order merchandise revenue, Retail KPI definitions and weighted ratios, Overall AOV from revenue and distinct orders, Weighted margin rate and additive reconciliation

### Community 102 - "Marketing Associations and Scenarios"
Cohesion: 0.67
Nodes (4): Attributed revenue per campaign spend, Compatible campaign and period aggregation, Campaign and promotion performance, Validated future promotion scenario

### Community 103 - "Merchandise Margin and Refunds"
Cohesion: 0.67
Nodes (4): Historical line merchandise revenue and cost, Merchandise margin and returns-adjusted performance, Order-cohort refund and returned-cost adjustment, Signed margin and return-cohort maturity

### Community 105 - "Hosted Report Acceptance Harness"
Cohesion: 0.67
Nodes (3): main(), Opt-in hosted report acceptance; creates public verification…, run()

### Community 106 - "Public Skill Versioning Decision"
Cohesion: 0.50
Nodes (4): ADR 0004: public versioned skills (accepted 2026-10-15), Bounded metadata skill selector, Public Markdown playbooks, Analysis-scoped immutable skill snapshots

### Community 107 - "Static Product Preview Contract"
Cohesion: 0.50
Nodes (4): Versioned chart view, ADR 0005: saved-result dashboards (accepted 2026-10-16), Immutable paginated results, Retained artifact references

### Community 108 - "Public Report Evidence Boundary"
Cohesion: 0.50
Nodes (4): ADR 0007: public report evidence (accepted 2026-10-17), Requester-only in-memory Search panel, Verified numerical claims, Distinct writer and semantic reviewer

### Community 109 - "Immutable Saved-Artifact Dashboard Cards"
Cohesion: 0.50
Nodes (4): Validated ChartViewState, Fenced reference-aware history maintenance, Revision-checked idempotent dashboard mutations, Immutable saved-artifact dashboard cards

### Community 111 - "Responsive Sidebar Primitives"
Cohesion: 0.67
Nodes (3): SidebarProvider(), subscribe(), useIsMobile()

### Community 112 - "Workspace Sample Question Probes"
Cohesion: 0.67
Nodes (3): ab(), ev(), Exercise actual card handlers under all source preferences without real…

### Community 114 - "Forecast Plan Reader and Controls"
Cohesion: 0.67
Nodes (3): load(), source(), { workspacePath }

### Community 118 - "Public Anonymous Workspace Decision"
Cohesion: 1.00
Nodes (3): Anonymous guest token attribution, quotas and cancellation, Public shared conversations, ADR: Public workspace without accounts

### Community 119 - "Immutable Durable Report Decision"
Cohesion: 0.67
Nodes (3): ADK App / Runner / Workflow, Independent durable report execution, ADR 0006: durable versioned reports (accepted 2026-10-17)

### Community 120 - "Static Product Preview Contract"
Cohesion: 0.67
Nodes (3): Motion and feedback (deployed 2026-10-16), Reader-aware answer following, Unified device/application reduced motion

### Community 127 - "Scoped Cloud Build Workflow"
Cohesion: 0.67
Nodes (3): Cloud Build Docker build step, Cloud Build Docker push step, Dedicated GCS-only build logs

## Knowledge Gaps
- **240 isolated node(s):** `agentic-bi-backend`, `$schema`, `style`, `rsc`, `tsx` (+235 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **39 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AppError` connect `Application Error Contracts` to `TimesFM Validation and Recovery`, `Transactional Storage and Persistence`, `Saved Chart Data Presentation`, `Bounded Runtime Configuration`, `Skill Selection and Snapshot Tests`, `Bounded Runtime Configuration`, `Read-Only SQL Safety Tests`, `Metric and Planning Regression Tests`, `Shared Job Admission and Leases`, `Report Recovery and Export Tests`, `Operator Maintenance Commands`, `Hierarchical Planning and Adjustments`, `Typed Analysis and Visualization`, `Evidence-Backed Report Contracts`, `Skill Author Concurrency Tests`, `Typed Fusion Regression Tests`, `Conversation Persistence and Recovery`, `Versioned Metrics and Controlled Compilation`, `Application Error Contracts`, `Reviewed Skill Draft Publication`, `TimesFM Validation and Recovery`, `Evidence-Backed Report Workflow`, `AI Retry and Failure Tests`, `Versioned Metrics and Controlled Compilation`, `Report Recovery and Export Tests`, `TimesFM Validation and Recovery`, `Firestore Contention Regression Tests`, `Report Recovery and Export Tests`, `Read-Only SQL Safety Tests`?**
  _High betweenness centrality (0.081) - this node is a cross-community bridge._
- **Why does `Public landing page guide` connect `Static Product Preview Contract` to `Worker-First Release Runbook`, `Validation Evidence and Limits`, `Durable Advanced Report Contract`, `Public Versioned Skill Contract`, `Static Product Preview Contract`, `Static Product Preview Contract`, `Controlled Analytics Architecture`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Why does `Canonical workspace link construction` connect `Static Product Preview Contract` to `Voice and Text Workspace`?**
  _High betweenness centrality (0.063) - this node is a cross-community bridge._
- **Are the 88 inferred relationships involving `AppError` (e.g. with `AI` and `AnalysisService`) actually correct?**
  _`AppError` has 88 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `Settings` (e.g. with `Connectors` and `create_app()`) actually correct?**
  _`Settings` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `MemoryStore` (e.g. with `test_every_chart_family_and_mixed_units_can_render()` and `test_complex_plan_uses_json_mode_and_still_validates_locally()`) actually correct?**
  _`MemoryStore` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `Connectors` (e.g. with `Settings` and `AppError`) actually correct?**
  _`Connectors` has 14 INFERRED edges - model-reasoned connections that need verification._
## Extraction scope and limitations

Code uses local AST extraction. Eight documents were re-extracted by one host-session agent; 60 cached documents were reused. No separate model API or cloud/database operation was performed by graph generation. Source hashes capture the indexed working tree. Re-extraction uses named concepts rather than retaining obsolete semantic fragments; counts may decrease.

- Graphify tree-sitter reported potentially partial extraction of Frontend/src/components/workspace.tsx at line 1141; 13 symbols extracted.
- Raw external import references can have no matching project node; unresolved endpoints are reported, not fabricated.
- The default undirected simple graph can combine multiple relationships between an endpoint pair; diagnostic counts retain this limitation.
- Host semantic-token usage is unavailable, not zero.
- The initial AST multiprocessing attempt from stdin failed to spawn; Graphify automatically completed the extraction sequentially.

Raw extraction: 993 unresolved endpoint edges, 0 missing endpoint fields, 0 self-loops, 592 same-endpoint relationships collapsed in the undirected projection. External SDK imports are not fabricated as project entities. These are extraction limits, not runtime failures.
