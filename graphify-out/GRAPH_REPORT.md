# Graph Report - 6. Google AI Builder Cup - Agentic BI  (2026-10-23)

## Corpus Check
- 303 files · ~227,332 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2395 nodes · 6488 edges · 158 communities (117 shown, 41 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 344 edges (avg confidence: 0.91)
- Token cost: 0 separate model-API tokens; host semantic input/output usage is unavailable, not zero.

## Graph Freshness
- Built from commit: `221b8253`
- Working-tree snapshot: compare VALIDATION.json source hashes as well as the base commit.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- TimesFM Validation and Recovery
- Saved Chart Data Presentation
- Retail Generation and Upload
- Accessible Motion Preferences
- Dashboard Editing and Sharing
- Forecast Plan Reader and Controls
- Transactional Storage and Persistence
- Interactive Chart Exploration
- Read-Only SQL Safety Tests
- Dashboard Editing and Sharing
- Frontend HTTP and Stream Recovery
- Application Error Contracts
- Managed Forecast Comparison Policy
- Coherent Forecast Planning Contract
- Forecast Plan Reader and Controls
- TypeScript Compiler Configuration
- Metric and Planning Regression Tests
- Forecast Plan Reader and Controls
- Skill Selection and Snapshot Tests
- Shared Analytical Domain Model
- Evidence-Backed Report Workflow
- Bounded Runtime Configuration
- AI Retry and Failure Tests
- Scoped Cloud Provisioning
- Skill Selection and Snapshot Tests
- Read-Only SQL Safety Tests
- Voice and Text Workspace
- Typed Fusion Regression Tests
- Evidence-Backed Report Contracts
- Operator Maintenance Commands
- Responsive Sidebar Primitives
- Skill Author Concurrency Tests
- Local Setup and Verification
- Static Product Preview Contract
- Skill Selection and Snapshot Tests
- Analytics and Prediction Playbooks
- Shadcn Component Configuration
- Frontend Development Dependencies
- Skill Selection and Snapshot Tests
- Report Recovery and Export Tests
- Release Evidence and Acceptance Boundaries
- Evidence-Backed Report Contracts
- Typed Fusion Regression Tests
- Shared Job Admission and Leases
- Bounded Runtime Configuration
- Frontend Runtime Dependencies
- Public API Regression Tests
- Durable Advanced Report Contract
- Public Versioned Skill Contract
- Validation Evidence and Limits
- Metric and Planning Regression Tests
- Skills Library Interface
- Independent Resource Loading and Retry Feedback
- Skill Author Concurrency Tests
- Skill Selection and Snapshot Tests
- Report Recovery and Export Tests
- Independent Startup Reads and Nearby Saved Charts
- Chart Tooltip and Legend Primitives
- Immutable Shared Dashboards
- Frontend HTTP and Stream Recovery
- Responsive Sidebar Primitives
- Report Recovery and Export Tests
- Evidence-Backed Report Contracts
- Local Setup and Verification
- Dashboard Editing and Sharing
- Frontend Package Scripts
- Managed Forecast Comparison Policy
- Public Versioned Skill Contract
- Validation Evidence and Limits
- Frontend HTTP and Stream Recovery
- Customer Cohorts and Returns
- Data Quality and Fusion
- Seasonality and Backtesting
- Backend Runtime and Verification
- Skill Selection and Snapshot Tests
- Report Recovery and Export Tests
- Retail Data Publication Workflow
- Controlled Analytics Architecture
- Report Presentation Regression Tests
- Skill Author Concurrency Tests
- Named Firestore ADK Persistence
- Static Product Preview Contract
- Original Retail Source Schema
- Expanded Retail Column Dictionary
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
- Operator Maintenance Commands
- Skill Author Concurrency Tests
- Skill Author Concurrency Tests
- Public Skill Versioning Decision
- Static Product Preview Contract
- Public Report Evidence Boundary
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
- Voice and Text Workspace
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
- Report Recovery and Export Tests
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
2. `Settings` - 126 edges
3. `MemoryStore` - 90 edges
4. `Connectors` - 74 edges
5. `Repository` - 65 edges
6. `create_app()` - 64 edges
7. `StrictModel` - 59 edges
8. `api()` - 56 edges
9. `FirestoreSessionService` - 55 edges
10. `AI` - 49 edges

## Surprising Connections (you probably didn't know these)
- `Join-key compatibility, coverage and fan-out` --semantically_similar_to--> `Explicit fan-out and incomplete-input rejection`  [INFERRED] [semantically similar]
  Backend/app/skill_library/analytics-data-quality.md → docs/adr/0003-bounded-cross-source-fusion.md
- `Atomic dashboard publication` --semantically_similar_to--> `Skill Publication`  [INFERRED] [semantically similar]
  docs/ai-dashboard-builder.md → CONTEXT.md
- `foundation()` --calls--> `operator_credentials()`  [INFERRED]
  infra/provision_reports.py → Backend/app/admin.py
- `main()` --uses--> `Settings`  [INFERRED]
  infra/report_recovery_check.py → Backend/app/config.py
- `main()` --uses--> `Settings`  [INFERRED]
  infra/runtime_check.py → Backend/app/config.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Reviewed revision-safe dashboard publication** — docs_ai_dashboard_builder_atomic_dashboard_publication, docs_ai_dashboard_builder_revision_aware_rebase, docs_ai_dashboard_builder_conditional_undo, docs_ai_dashboard_builder_guest_owned_proposal_expiry [EXTRACTED 1.00]
- **Workspace viewport ownership and nearby saved evidence** — docs_architecture_scroll_controller, docs_architecture_chart_containment, docs_architecture_nearby_cards, docs_architecture_saved_loader, docs_architecture_visual_viewport [EXTRACTED 1.00]
- **Immutable controlled metric execution** — docs_business_metrics_closed_typed_metric_formula, docs_business_metrics_application_owned_grain_compiler, docs_business_metrics_immutable_dependency_snapshots, docs_business_metrics_canonical_forecast_value_reconciliation [EXTRACTED 1.00]
- **Validated coherent hierarchy recipe** — docs_forecast_plans_aggregate_candidate_selection, docs_forecast_plans_training_only_leaf_allocation, docs_forecast_plans_cent_exact_monetary_reconciliation, docs_forecast_plans_level_balanced_promotion_gate, docs_forecast_plans_coherent_baseline_fallback [EXTRACTED 1.00]
- **Static saved-evidence previews retain analytical and publication boundaries** — docs_landing_page_guided_preview, docs_landing_page_forecast_fixture, docs_landing_page_scenario_fixture, docs_landing_page_captured_version_links [EXTRACTED 1.00]
- **Immutable briefing outputs from saved evidence** — docs_reports_versions, docs_reports_reader, docs_reports_diagnostics, docs_reports_briefing, docs_reports_zip, docs_reports_old [EXTRACTED 1.00]
- **Independent cancellable resource lifecycle** — docs_startup_loading_shell_first, docs_startup_loading_parallel_workspace, docs_startup_loading_request_ownership, docs_startup_loading_get_policy, docs_startup_loading_rate_cooldown, docs_startup_loading_retained_content [EXTRACTED 1.00]
- **Fenced admission, stable jobs, persistent cancellation and conservative billing** — docs_timesfm_atomic_admission, docs_timesfm_stable_jobs, docs_timesfm_persistent_cancellation, docs_timesfm_conservative_billing [EXTRACTED 1.00]
- **Frozen saved input, deterministic selection, separate scenarios and immutable exports** — docs_timesfm_frozen_saved_input, docs_timesfm_candidate_selection, docs_timesfm_separate_scenario, docs_timesfm_saved_export_evidence [EXTRACTED 1.00]
- **Distinct ordinary-report and planning acceptance gates** — docs_validation_blocked, docs_validation_fresh, docs_validation_planning [EXTRACTED 1.00]

## Communities (158 total, 41 thin omitted)

### Community 0 - "TimesFM Validation and Recovery"
Cohesion: 0.09
Nodes (63): choose(), compare(), eligible(), intervals(), Application-owned candidate selection over a frozen saved series., reserve_candidates(), score_remote(), ForecastSpec (+55 more)

### Community 1 - "Saved Chart Data Presentation"
Cohesion: 0.07
Nodes (67): change(), csv_cell(), csv_line(), date_value(), metadata(), number(), present(), Shared indices preserve extrema for all series, endpoints, and null boundaries. (+59 more)

### Community 2 - "Retail Generation and Upload"
Cohesion: 0.07
Nodes (57): demand(), generate(), GeneratorConfig, money(), promotion_window(), Path, Deterministic, bounded-memory synthetic retail history; never contacts a…, read_manifest() (+49 more)

### Community 3 - "Accessible Motion Preferences"
Cohesion: 0.05
Nodes (54): body, heading, metadata, mono, metadata, AppearanceSync(), AppProviders(), AnalysisProgress() (+46 more)

### Community 4 - "Dashboard Editing and Sharing"
Cohesion: 0.10
Nodes (40): metadata, DashboardDownload(), download(), DashboardShare(), show(), formats, DashboardEditor(), useDashboardMutation() (+32 more)

### Community 5 - "Forecast Plan Reader and Controls"
Cohesion: 0.07
Nodes (41): metadata, metadata, metadata, DashboardBuilder(), JobControls(), SavedArtifactPreview(), DashboardHeader(), MetricRevision() (+33 more)

### Community 6 - "Transactional Storage and Persistence"
Cohesion: 0.09
Nodes (50): DashboardAction, DashboardCreate, DashboardItemPatch, DashboardLayout, DashboardPatch, DashboardPin, DashboardRequest, field_validator (+42 more)

### Community 7 - "Interactive Chart Exploration"
Cohesion: 0.07
Nodes (50): categoryColor(), InsightfulChart(), content(), download(), label(), palette, Plot(), Values() (+42 more)

### Community 8 - "Read-Only SQL Safety Tests"
Cohesion: 0.08
Nodes (31): AI, AnalysisService, get_settings(), Settings, Connectors, test_cancel_then_forget_during_bigquery_dry_run_prevents_late_submission(), test_cancellation_failure_still_releases_conversation(), test_raw_audio_is_not_persisted() (+23 more)

### Community 9 - "Dashboard Editing and Sharing"
Cohesion: 0.07
Nodes (37): Catalog, ModelSettings(), ChoiceSetting(), preferenceLabels, sections, updatePreference(), template, AppSelectProps (+29 more)

### Community 10 - "Frontend HTTP and Stream Recovery"
Cohesion: 0.06
Nodes (34): metadata, DashboardWidget(), ConversationReports(), SkillEvidence(), InputGroup(), InputGroupAddon(), inputGroupAddonVariants, InputGroupButton() (+26 more)

### Community 11 - "Application Error Contracts"
Cohesion: 0.09
Nodes (29): check_maintenance(), Operator-only, reference-aware cleanup. Failed operations stay fenced for…, model_failure(), model_retry_delay(), Public model failures and one bounded retry policy, never a tool replay policy., Respect a short Retry-After; don't retry earlier than a long provider delay., model_evidence(), Pinned text model choices; per-analysis context never mutates shared settings. (+21 more)

### Community 12 - "Managed Forecast Comparison Policy"
Cohesion: 0.06
Nodes (49): Conditional predictions with historical driver support, Conditional driver and promotion scenarios playbook, Visitor-supplied complete future driver paths, Optional available TimesFM with complete covariate context, Shared-method baseline and alternative scenario artifacts, Chronological scenario validation and extrapolation rejection, Advanced Analysis controlled forecast fitting, Common chronological scores choose statistical or managed candidate (+41 more)

### Community 13 - "Coherent Forecast Planning Contract"
Cohesion: 0.07
Nodes (43): Document, Insert-only metric seeding, Planning fixture execution, Document, Immutable metric lineage, Public executable metric contracts, Structural publication validation, Adaptive coherent planning (+35 more)

### Community 14 - "Forecast Plan Reader and Controls"
Cohesion: 0.07
Nodes (28): metadata, metadata, metadata, send(), MetricsWorkspace(), chooseMeasure(), test(), update() (+20 more)

### Community 15 - "TypeScript Compiler Configuration"
Cohesion: 0.05
Nodes (42): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+34 more)

### Community 16 - "Metric and Planning Regression Tests"
Cohesion: 0.11
Nodes (34): adjust_plan(), create_app(), _insert(), Insert-only packaged definitions. Never called by startup, release or history…, seed_metrics(), compile_metric(), MetricAction, MetricDefinition (+26 more)

### Community 17 - "Forecast Plan Reader and Controls"
Cohesion: 0.07
Nodes (18): metadata, metadata, startBuild(), ForecastPlans(), create(), download(), narrative(), pickNode() (+10 more)

### Community 18 - "Skill Selection and Snapshot Tests"
Cohesion: 0.12
Nodes (13): AppError, Exception, Preserve compiled definitions when forecasts require controlled feature…, verify_forecast_values(), Metrics, Reserve once before execution; replay saved pages, never repeat an uncertain…, chart_state(), plan_artifact() (+5 more)

### Community 19 - "Shared Analytical Domain Model"
Cohesion: 0.08
Nodes (36): Allocated Estimate, Analysis Brief, Backtest, Business Metric, Dashboard Build, Dashboard Proposal, Data Profile, Document (+28 more)

### Community 20 - "Evidence-Backed Report Workflow"
Cohesion: 0.11
Nodes (17): next_date(), normalized_spec(), Bounded, deterministic presentation of immutable result pages. No SQL or model…, Called once when saving a new artifact; historical documents remain immutable., json_rows(), evidence_signature(), plan_report(), NeedsInput (+9 more)

### Community 21 - "Bounded Runtime Configuration"
Cohesion: 0.12
Nodes (20): FirestoreSessionService, Durable ADK session adapter with ordered events and fenced state writes., StaleLease, check_lease(), test_recent_session_context_uses_newest_events(), test_fenced_report_adk_sessions_reject_old_worker_and_survive_reset(), setup_run(), test_completion_between_status_reads_is_not_reported_as_interrupted() (+12 more)

### Community 22 - "AI Retry and Failure Tests"
Cohesion: 0.11
Nodes (21): live(), MemoryStore, Small document interface with atomic, retry-safe read/modify/write operations., voice_session(), main(), Explicit operator command: uv run python -m scripts.seed_metrics [--cloud]., ai_service(), live_harness() (+13 more)

### Community 23 - "Scoped Cloud Provisioning"
Cohesion: 0.13
Nodes (25): main(), Build with a resource-scoped builder, then deploy as the current operator., configuration(), main(), Prepare or deploy ONLY the private report worker. Foundation/IAM are separate…, ensure_secret(), ensure_service_account(), gcloud() (+17 more)

### Community 24 - "Skill Selection and Snapshot Tests"
Cohesion: 0.14
Nodes (25): fixture_answer(), field_validator, SkillAttachments, SkillContent, client(), create(), guest(), fixture (+17 more)

### Community 25 - "Read-Only SQL Safety Tests"
Cohesion: 0.14
Nodes (26): json_value(), Any, Deterministic synthetic retail data; no real customer information., retail_data(), linked_predicate(), AST validation complements restricted database roles; it is not a SQL sandbox., Every admitted OR branch must constrain the new relation to a prior one., validate_joins() (+18 more)

### Community 26 - "Voice and Text Workspace"
Cohesion: 0.12
Nodes (22): MarkdownContent(), MessageContent(), forecastMethodLabel(), PredictionEvidence(), active(), ReportRunCard(), cancel(), clarify() (+14 more)

### Community 27 - "Typed Fusion Regression Tests"
Cohesion: 0.18
Nodes (23): fixture_plan(), Explicit local-only sample planner. Never used as a Gemini fallback., bind_forecast(), Approved same-grain target comparison over a frozen revenue definition., target_plan(), catalog_plan(), matched_metrics(), metric_router() (+15 more)

### Community 28 - "Evidence-Backed Report Contracts"
Cohesion: 0.12
Nodes (24): ChartViewState, MetricRef, ChartMeasure, ConversationCreate, field_validator, StrictModel, TurnCreate, DashboardBlueprint (+16 more)

### Community 29 - "Operator Maintenance Commands"
Cohesion: 0.15
Nodes (16): check_models(), cleanup_skill_authors(), cli(), dashboard_maintenance(), index_schema(), main(), operator_credentials(), Credentialed CLI only. No administrative endpoint is exposed by FastAPI. (+8 more)

### Community 30 - "Responsive Sidebar Primitives"
Cohesion: 0.09
Nodes (8): Sidebar(), SidebarContext, SidebarContextProps, SidebarMenuButton(), sidebarMenuButtonVariants, SidebarRail(), SidebarTrigger(), useSidebar()

### Community 31 - "Skill Author Concurrency Tests"
Cohesion: 0.20
Nodes (23): asyncio, AuthorDraft, client(), create(), guest(), prepared(), fixture, parametrize (+15 more)

### Community 32 - "Local Setup and Verification"
Cohesion: 0.14
Nodes (25): ADK planner and interpreter, Positioned chart figures containing hidden instructions, Guarded analysis and typed cross-source fusion, Revision-checked saved-result dashboard exports, Dated release records separate from implemented architecture, Implemented application architecture, Private-worker durable report orchestration, ResourceFeedback status and retries (+17 more)

### Community 33 - "Static Product Preview Contract"
Cohesion: 0.09
Nodes (24): Immutable saved-result chart presentation, Canonical saved report version-1 links without prefetch, Historical initial landing frontend release 00012-mv5, Fixed landing palette and saved appearance isolation, Versioned fixture cannot silently reread mutable live source data, Verified monthly TimesFM version-1 forecast fixture, Homepage publication is a frontend release and not a data operation, Local guided preview boundary (+16 more)

### Community 34 - "Skill Selection and Snapshot Tests"
Cohesion: 0.16
Nodes (14): analytics_examples(), Stable seed IDs let operators add examples without replacing public edits., Import the reviewable, source-controlled pack before any cloud writes., seed_analytics(), seed_examples(), compatible(), export_skill(), import_skill() (+6 more)

### Community 35 - "Analytics and Prediction Playbooks"
Cohesion: 0.09
Nodes (23): Twelve additions; 29 active hosted skills; three deleted, Ordinary analytics versus Advanced Analysis prediction fitting, Calendar trends and retail seasonality, Campaign and promotion performance, Comparable-store and target performance, Conditional driver and promotion scenarios, Skills cannot add tools or bypass analytical safeguards, Customer cohorts and repeat purchasing (+15 more)

### Community 36 - "Shadcn Component Configuration"
Cohesion: 0.09
Nodes (22): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+14 more)

### Community 37 - "Frontend Development Dependencies"
Cohesion: 0.10
Nodes (21): babel-plugin-react-compiler, eslint, eslint-config-next, devDependencies, babel-plugin-react-compiler, eslint, eslint-config-next, shadcn (+13 more)

### Community 39 - "Report Recovery and Export Tests"
Cohesion: 0.20
Nodes (20): factual_claims(), Claims are computed on the full saved selection, never the chart preview., parametrize, sample_artifact(), started(), test_approved_date_formatting_typed_sqlglot_alias(), test_artifact_checkpoint_never_rewrites_saved_pages(), test_budgets_survive_worker_recovery_and_prevent_overspend() (+12 more)

### Community 40 - "Release Evidence and Acceptance Boundaries"
Cohesion: 0.16
Nodes (20): Preserved warm frontend/API policy and hosted evidence, Hosted checks require actual execution and dated evidence, 22 October Singapore warm-service cost illustration, Existing distinct API/frontend billing modes, Official Cloud Run regional pricing and service-minimum guidance, Google Cloud deployment runbook, Dedicated scoped runtime and build identities, No-traffic image-only candidate verification (+12 more)

### Community 41 - "Evidence-Backed Report Contracts"
Cohesion: 0.19
Nodes (17): saved_rows(), AnalysisTask, EvidenceClaim, ForecastInputs, Bounded contracts shared by the report harness, API, renderer, and numerical…, ReportCreate, ReportMutation, ReportPatch (+9 more)

### Community 42 - "Typed Fusion Regression Tests"
Cohesion: 0.23
Nodes (18): _arrow_bytes(), fuse(), _identifier(), Any, A typed plan compiler; no model-supplied SQL or Python reaches DuckDB., _worker(), Calculation, QueryResult (+10 more)

### Community 44 - "Bounded Runtime Configuration"
Cohesion: 0.13
Nodes (7): Repository, main(), Opt-in real Gemini Live/tool integration check; no microphone is recorded. Run…, VoiceHarness, test_recovery_uses_saved_sql_repair_and_its_attempt_identity(), test_shared_limit_applies_across_repository_instances(), test_simultaneous_turns_have_one_winner()

### Community 45 - "Frontend Runtime Dependencies"
Cohesion: 0.11
Nodes (19): class-variance-authority, clsx, dependencies, class-variance-authority, clsx, radix-ui, react, react-dom (+11 more)

### Community 46 - "Public API Regression Tests"
Cohesion: 0.19
Nodes (15): client(), guest(), fixture, parametrize, A worker may finish after the event query but before the status read., test_analysis_replay_fork_and_provenance(), test_guest_scope_and_no_administrative_routes(), test_origin_and_payload_validation() (+7 more)

### Community 47 - "Durable Advanced Report Contract"
Cohesion: 0.19
Nodes (17): A4 PDF and editable Word briefing, Fenced checkpoints and transactional outbox, Verified claim policy, Structured forecast and scenario evidence, Advanced analysis reports, Independent durable report execution, Chronological forecast validation, Shared report operating ceilings (+9 more)

### Community 48 - "Public Versioned Skill Contract"
Cohesion: 0.14
Nodes (17): Skills, Bounded metadata-only skill discovery, Public versioned Markdown Skills library, Validated SKILL.md import/export and safe Markdown, No raw HTML, remote images, scripts or installed resources, Bounded author connections, turns, tools, transcript and expiry, Fresh fenced ADK author generation reconstructed from saved context, 409 skill_conflict preserves the editor draft (+9 more)

### Community 49 - "Validation Evidence and Limits"
Cohesion: 0.12
Nodes (17): Original quota-blocked fresh report attempt, Dashboard border and spacing release, Full saved-result chart acceptance, AOV claim correction history, Saved-only dashboard lifecycle acceptance, Validation and remaining deployment gates, Hosted report and shared-dropdown release, Post-reset fresh forecast and scenario acceptance (+9 more)

### Community 50 - "Metric and Planning Regression Tests"
Cohesion: 0.26
Nodes (13): baseline_candidate(), capture_history(), distribute(), evaluate_recipe(), fail(), Pure hierarchical revenue calculations; no model, database or executable inputs., Largest remainder allocation keeps each published branch coherent to one cent., Missing aggregate cells become zero only with proved complete source/calendar… (+5 more)

### Community 51 - "Skills Library Interface"
Cohesion: 0.18
Nodes (8): metadata, contentOf(), SkillsWorkspace(), editSkill(), exportFile(), importFile(), openEditor(), sourceLabel()

### Community 52 - "Independent Resource Loading and Retry Feedback"
Cohesion: 0.15
Nodes (13): Initial retry limited to bootstrap GETs, Catalog resolution with strict JSON metric scope, Current library documentation via Context7, Repository instructions, Architecture Mermaid authority and derived Graphify references, Shared AppSelect presentation contract, Dated hosted acceptance boundaries, Immutable report export contract (+5 more)

### Community 53 - "Skill Author Concurrency Tests"
Cohesion: 0.31
Nodes (10): cases(), evaluate(), main(), matches(), Numerical evaluation against independent Python aggregates of the retail seed., main(), Evaluate the public, hosted API against independent seed reference values., main() (+2 more)

### Community 54 - "Skill Selection and Snapshot Tests"
Cohesion: 0.15
Nodes (6): Graph nodes carry only a run identifier. Bodies live in fenced checkpoints., ReportPolicy, run_report_graph(), test_graph_preserves_clarification_without_running_downstream_stages(), test_policy_blocks_tools_and_enforces_model_budget(), BasePlugin

### Community 55 - "Report Recovery and Export Tests"
Cohesion: 0.15
Nodes (5): ExportStorage, Opt-in hosted forecast/scenario acceptance. Public reports; read-only retail…, run(), test_export_storage_immutable_integrity_and_path_traversal(), test_source_profile_mismatch_fails_before_model_or_queries()

### Community 56 - "Independent Startup Reads and Nearby Saved Charts"
Cohesion: 0.26
Nodes (13): Concurrent analytical-source availability checks, Startup feedback and resource loading, One bounded initial idempotent GET retry, Resource-specific local retry with five-second feedback, 150px nearby chart loading with stable identity, Concurrent BigQuery and PostgreSQL availability checks, Independent history, sources, report config and deep links, Retry-After manual/polling cooldown (+5 more)

### Community 57 - "Chart Tooltip and Legend Primitives"
Cohesion: 0.21
Nodes (11): ChartConfig, ChartContainer(), ChartContext, ChartContextProps, ChartLegendContent(), ChartTooltipContent(), getPayloadConfigFromPayload(), INITIAL_DIMENSION (+3 more)

### Community 58 - "Immutable Shared Dashboards"
Cohesion: 0.26
Nodes (12): Shared dashboards, Published snapshot dashboard downloads, Bounded ephemeral dashboard exports, Reference-aware maintenance fence, View and Edit presentation modes, Immutable saved-view pins, Public editable dashboards, Lazy saved-card loading (+4 more)

### Community 59 - "Frontend HTTP and Stream Recovery"
Cohesion: 0.21
Nodes (9): capabilities, faqs, metadata, OpenQuerylane(), LandingMobileNavigation(), HeroProduct(), money(), RevenueIllustration() (+1 more)

### Community 60 - "Responsive Sidebar Primitives"
Cohesion: 0.27
Nodes (7): Sheet(), SheetClose(), SheetContent(), SheetDescription(), SheetHeader(), SheetTitle(), SheetTrigger()

### Community 61 - "Report Recovery and Export Tests"
Cohesion: 0.24
Nodes (8): body(), setup(), test_daily_report_quota_atomic_and_preserved_after_reset(), test_fencing_expiry_concurrency_and_checkpoint_replay(), test_full_fixture_report_api_downloads_revisions_pins_and_reset(), test_genuine_queue_backlog_is_not_mistaken_for_lost_delivery(), test_idempotency_and_separate_chat_lease(), test_report_cleanup_read_failure_always_resets_model_and_lease_context()

### Community 62 - "Evidence-Backed Report Contracts"
Cohesion: 0.18
Nodes (5): field_validator, model_validator, ReportClarification, test_owner_clarifications_busy_rules_and_cancellation(), test_structured_future_assumptions_are_preserved_without_model_defaults()

### Community 63 - "Local Setup and Verification"
Cohesion: 0.20
Nodes (11): Memory-only operator preview tokens expire; restart to refresh, Local deterministic fixture and in-memory mode, Direct local PostgreSQL DSN with Cloud SQL selection disabled, Setup, Alternate QUERYLANE_NEXT_DIST_DIR prevents shared output collisions, Explicit ADC cloud mode uses actual shared demo data and quotas, Local-only real Gemini preview over synthetic fixtures, Local-only report dispatch over existing timeseries bundle (+3 more)

### Community 64 - "Dashboard Editing and Sharing"
Cohesion: 0.24
Nodes (6): metadata, DashboardWorkspace(), refreshRemoved(), restoreItem(), setMode(), unpin()

### Community 65 - "Frontend Package Scripts"
Cohesion: 0.20
Nodes (9): name, private, scripts, build, dev, lint, start, test (+1 more)

### Community 66 - "Managed Forecast Comparison Policy"
Cohesion: 0.20
Nodes (10): Advanced reports, AI dashboards and validated forecasting, Querylane product and setup entrypoint, Packaged landing previews without backend execution, Metrics, Forecast Plans, Dashboards, Reports and Skills libraries, Public conversational retail intelligence, 21 October report/dropdown release (dated), Browser-local appearance, chart, conversation and voice settings, Deployed independent startup loading and viewport workspace (+2 more)

### Community 67 - "Public Versioned Skill Contract"
Cohesion: 0.25
Nodes (9): Executive retail performance review, Decision-focused reports with verified numerical evidence, Concise spoken findings with visual evidence, Conversational business decision briefing, Metadata-first discovery with manual attachment priority, Versioned skill snapshots and explicit insert-only publication, Bounded selection followed by analysis-scoped snapshots, Shared attachments inherited by forks; busy conversations reject mutation (+1 more)

### Community 68 - "Validation Evidence and Limits"
Cohesion: 0.22
Nodes (9): Local chart exploration defaults, Workspace settings, Browser-local automatic preferences, Pinned analysis model snapshots, Unified reduced-motion behavior, Presentation precision and scope precedence, Source-correct sample questions, Preference storage and safe reset (+1 more)

### Community 69 - "Frontend HTTP and Stream Recovery"
Cohesion: 0.36
Nodes (7): ProductTour(), views, Tabs(), TabsContent(), TabsList(), tabsListVariants, TabsTrigger()

### Community 70 - "Customer Cohorts and Returns"
Cohesion: 0.36
Nodes (8): Signup cohorts and first observed purchase cohorts, Customer cohorts and repeat purchasing, Equally mature customer observation windows, Repeat purchase and activity retention denominators, Validated bounded-rate or monetary forecast domain, Explicit return-rate target and denominator, Returns and rate prediction readiness, Refund latency and cohort maturity

### Community 71 - "Data Quality and Fusion"
Cohesion: 0.32
Nodes (8): Data quality and analysis readiness, Calendar spine, unknown gaps and observed zeros, Join-key compatibility, coverage and fan-out, Independent totals reconciliation, Explicit fan-out and incomplete-input rejection, ADR: Typed bounded cross-source fusion, Gemini relationship-key and business-assumption hypotheses, Trusted compiler for typed relational fusion

### Community 72 - "Seasonality and Backtesting"
Cohesion: 0.32
Nodes (8): Dense retail calendar at consistent time grain, Shifted target-derived rolling predictors, Observed peaks with causal limitations, Calendar trends and retail seasonality, Baseline comparison and candidate promotion, Forecast validation and uncertainty, Chronological rolling-origin backtests, Supported prediction intervals and publication outcome

### Community 73 - "Backend Runtime and Verification"
Cohesion: 0.25
Nodes (7): Default local plan and opt-in bounded billable probe, Named Firestore and private report bucket, TimesFM 3.0 Preview comparison over saved evidence, Private report worker app.report_worker:app, Public API for chat, voice and shared libraries, Separate routine releases, skill seeding and analytical upload, Saved-artifact-only dashboard download contract

### Community 74 - "Skill Selection and Snapshot Tests"
Cohesion: 0.43
Nodes (7): firestore_store(), Exercise real SDK transaction decoration with a read-phase contention fault., test_business_validation_errors_are_not_retried_or_disguised(), test_exhausted_sdk_commit_budget_is_not_multiplied(), test_read_abort_retries_then_reports_conversation_busy(), test_read_retries_are_bounded_and_exhaustion_is_a_busy_response(), test_read_retry_commits_mutation_only_once()

### Community 76 - "Retail Data Publication Workflow"
Cohesion: 0.29
Nodes (7): Original demo retail schema (seed evidence 2026-10-16), Fenced insert-only cloud publication, Independent bundle reconciliation, Expanded retail column dictionary (retail-timeseries-v1), Stable full-window extend workflow, Deterministic streaming Parquet bundle, Additional timeseries source profile

### Community 77 - "Controlled Analytics Architecture"
Cohesion: 0.29
Nodes (7): Cross-source actual-versus-target exploration, Five-minute competition demonstration, Landing previews and direct workspace entry, Production rehearsal and backup recording, Public conversation sharing and forks, Spoken analysis and interruption, Warehouse question with SQL evidence

### Community 78 - "Report Presentation Regression Tests"
Cohesion: 0.29
Nodes (5): base, compiled, labelModule, require, source

### Community 79 - "Skill Author Concurrency Tests"
Cohesion: 0.47
Nodes (5): execute(), Private Cloud Run entrypoint. Deploy with --no-allow-unauthenticated and…, reconcile(), TaskBody, post

### Community 80 - "Named Firestore ADK Persistence"
Cohesion: 0.47
Nodes (6): Separate skill author session lease collection, Bounded fresh-transaction retries for read aborts, Custom Firestore ADK session adapter, ADR: ADK persistence in named Firestore, Loaded-session revision and conversation lease fencing, Terminal event stream sequence draining

### Community 81 - "Static Product Preview Contract"
Cohesion: 0.33
Nodes (6): ADR 0008 landing and workspace split, Query-aware 307 compatibility redirect, Landing palette and workspace preference isolation, Local evidence-only guided preview, Server-rendered public introduction, Direct unauthenticated workspace entry

### Community 82 - "Original Retail Source Schema"
Cohesion: 0.33
Nodes (6): Original PostgreSQL retail.customer_profiles, Original BigQuery order_items, Original BigQuery orders, Original BigQuery products, Original PostgreSQL retail.regional_targets, Original BigQuery returns

### Community 83 - "Expanded Retail Column Dictionary"
Cohesion: 0.40
Nodes (6): Dense daily calendar date spine, Time-series customer_profiles, Time-series sales_order_items, Time-series sales_orders, Time-series sales_returns, Full-month store targets

### Community 85 - "Reviewed Dashboard Publication Decision"
Cohesion: 0.40
Nodes (5): Document, Proposal retention, Reviewable dashboard generation, Reviewed rebase and conditional Undo, Shared durable execution

### Community 86 - "Immutable Chart Presentation Contract"
Cohesion: 0.40
Nodes (5): Deterministic bounded chart sampling, Saved-artifact chart-data endpoint, Deterministic truthful chart insights, Full saved-result CSV export, Version-2 VisualizationSpec metadata

### Community 87 - "Public Versioned Skill Contract"
Cohesion: 0.40
Nodes (5): Guest-scoped skill_author_sessions, Deterministic SkillContent draft compiler, Fresh fenced ADK connection recovery, Narrow Gemini Live requirements/draft tools, Explicit atomic reviewed publication

### Community 88 - "Repository Release Contracts"
Cohesion: 0.40
Nodes (5): Frontend contributor instructions, Guest-scoped report clarification and skill draft recovery, Installed Next.js version guides, Browser preferences and reduced-motion feedback, Explicit saved chart publication and revision checks

### Community 89 - "Responsive Sidebar Primitives"
Cohesion: 0.40
Nodes (4): Tooltip(), TooltipContent(), TooltipProvider(), TooltipTrigger()

### Community 90 - "Shared Dropdown Regression Tests"
Cohesion: 0.50
Nodes (4): { AppSelect, AppSelectItem, encodeChoice, decodeChoice }, load(), require, select

### Community 91 - "Saved Dashboard View Tests"
Cohesion: 0.50
Nodes (3): { initialChartView, describeChartView }, load(), reader()

### Community 92 - "Planning Skill Picker Tests"
Cohesion: 0.50
Nodes (3): picker(), require, skills

### Community 93 - "Planning Review and Retry Tests"
Cohesion: 0.50
Nodes (3): { dashboardChanges }, load(), require

### Community 94 - "Prediction Evidence Rendering Tests"
Cohesion: 0.40
Nodes (4): base, compiledModule, render(), require

### Community 95 - "Analytics and Prediction Playbooks"
Cohesion: 0.50
Nodes (4): Distinct-order support, directional confidence and lift, Basket composition and product affinity, Complete purchasing-population concentration shares, Customer revenue concentration and dependency

### Community 96 - "Sales Change Contribution Playbook"
Cohesion: 0.50
Nodes (4): Observed concentrations versus causal explanations, Sales change and segment contributions, Reconciled segment change contributions, Exact order-volume and AOV revenue bridge

### Community 97 - "Comparable Store Performance Playbook"
Cohesion: 0.67
Nodes (4): Comparable-store and target performance, Comparable-store eligibility, Store and regional target join grain, Weighted attainment and reconciled target gaps

### Community 98 - "Analytics and Prediction Playbooks"
Cohesion: 0.50
Nodes (4): Compatible-grain explicit-key reconciliation, Cross-source grain and join reconciliation, Dashboard evidence and comparability audit, Saved-card period, metric and completeness comparability

### Community 99 - "Weighted Retail KPI Definitions"
Cohesion: 0.67
Nodes (4): Completed-order merchandise revenue, Retail KPI definitions and weighted ratios, Overall AOV from revenue and distinct orders, Weighted margin rate and additive reconciliation

### Community 100 - "Marketing Associations and Scenarios"
Cohesion: 0.67
Nodes (4): Attributed revenue per campaign spend, Compatible campaign and period aggregation, Campaign and promotion performance, Validated future promotion scenario

### Community 101 - "Merchandise Margin and Refunds"
Cohesion: 0.67
Nodes (4): Historical line merchandise revenue and cost, Merchandise margin and returns-adjusted performance, Order-cohort refund and returned-cost adjustment, Signed margin and return-cohort maturity

### Community 103 - "Skill Author Concurrency Tests"
Cohesion: 0.67
Nodes (3): main(), Opt-in API check using existing immutable artifacts; never runs an analysis or…, run()

### Community 104 - "Skill Author Concurrency Tests"
Cohesion: 0.67
Nodes (3): main(), Opt-in hosted report acceptance; creates public verification…, run()

### Community 105 - "Public Skill Versioning Decision"
Cohesion: 0.50
Nodes (4): ADR 0004: public versioned skills (accepted 2026-10-15), Bounded metadata skill selector, Public Markdown playbooks, Analysis-scoped immutable skill snapshots

### Community 106 - "Static Product Preview Contract"
Cohesion: 0.50
Nodes (4): Versioned chart view, ADR 0005: saved-result dashboards (accepted 2026-10-16), Immutable paginated results, Retained artifact references

### Community 107 - "Public Report Evidence Boundary"
Cohesion: 0.50
Nodes (4): ADR 0007: public report evidence (accepted 2026-10-17), Requester-only in-memory Search panel, Verified numerical claims, Distinct writer and semantic reviewer

### Community 108 - "Immutable Saved-Artifact Dashboard Cards"
Cohesion: 0.50
Nodes (4): Validated ChartViewState, Fenced reference-aware history maintenance, Revision-checked idempotent dashboard mutations, Immutable saved-artifact dashboard cards

### Community 110 - "Responsive Sidebar Primitives"
Cohesion: 0.67
Nodes (3): SidebarProvider(), subscribe(), useIsMobile()

### Community 111 - "Workspace Sample Question Probes"
Cohesion: 0.67
Nodes (3): ab(), ev(), Exercise actual card handlers under all source preferences without real…

### Community 113 - "Forecast Plan Reader and Controls"
Cohesion: 0.67
Nodes (3): load(), source(), { workspacePath }

### Community 118 - "Public Anonymous Workspace Decision"
Cohesion: 1.00
Nodes (3): Anonymous guest token attribution, quotas and cancellation, Public shared conversations, ADR: Public workspace without accounts

### Community 119 - "Controlled Analytics Architecture"
Cohesion: 0.67
Nodes (3): ADK App / Runner / Workflow, Independent durable report execution, ADR 0006: durable versioned reports (accepted 2026-10-17)

### Community 120 - "Repository Release Contracts"
Cohesion: 0.67
Nodes (3): Motion and feedback (deployed 2026-10-16), Reader-aware answer following, Unified device/application reduced motion

### Community 127 - "Scoped Cloud Build Workflow"
Cohesion: 0.67
Nodes (3): Cloud Build Docker build step, Cloud Build Docker push step, Dedicated GCS-only build logs

## Knowledge Gaps
- **243 isolated node(s):** `agentic-bi-backend`, `$schema`, `style`, `rsc`, `tsx` (+238 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **41 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Public landing page guide` connect `Static Product Preview Contract` to `Local Setup and Verification`, `Release Evidence and Acceptance Boundaries`, `Durable Advanced Report Contract`, `Public Versioned Skill Contract`, `Static Product Preview Contract`, `Validation Evidence and Limits`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Why does `Canonical workspace link construction` connect `Static Product Preview Contract` to `Frontend HTTP and Stream Recovery`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Why does `AppError` connect `Skill Selection and Snapshot Tests` to `TimesFM Validation and Recovery`, `Saved Chart Data Presentation`, `Retail Generation and Upload`, `Transactional Storage and Persistence`, `Read-Only SQL Safety Tests`, `Application Error Contracts`, `Metric and Planning Regression Tests`, `Evidence-Backed Report Workflow`, `Bounded Runtime Configuration`, `AI Retry and Failure Tests`, `Skill Selection and Snapshot Tests`, `Read-Only SQL Safety Tests`, `Typed Fusion Regression Tests`, `Evidence-Backed Report Contracts`, `Operator Maintenance Commands`, `Skill Author Concurrency Tests`, `Skill Selection and Snapshot Tests`, `Skill Selection and Snapshot Tests`, `Report Recovery and Export Tests`, `Evidence-Backed Report Contracts`, `Typed Fusion Regression Tests`, `Shared Job Admission and Leases`, `Bounded Runtime Configuration`, `Metric and Planning Regression Tests`, `Skill Selection and Snapshot Tests`, `Report Recovery and Export Tests`, `Report Recovery and Export Tests`, `Evidence-Backed Report Contracts`, `Skill Selection and Snapshot Tests`, `Report Recovery and Export Tests`, `Skill Author Concurrency Tests`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Are the 88 inferred relationships involving `AppError` (e.g. with `AI` and `AnalysisService`) actually correct?**
  _`AppError` has 88 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `Settings` (e.g. with `Connectors` and `create_app()`) actually correct?**
  _`Settings` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `MemoryStore` (e.g. with `test_every_chart_family_and_mixed_units_can_render()` and `test_complex_plan_uses_json_mode_and_still_validates_locally()`) actually correct?**
  _`MemoryStore` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `Connectors` (e.g. with `Settings` and `AppError`) actually correct?**
  _`Connectors` has 14 INFERRED edges - model-reasoned connections that need verification._
## Documentation refresh scope

This hosted-release documentation snapshot indexes viewport scroll containment, nearby saved charts, unchanged-read identity, independent resource loading, concurrent source checks and configured warm frontend/API policy. 7 documents were re-extracted by one host-session semantic agent; 62 unchanged document extractions were reused. All 234 code files were processed through the local AST path. Graph generation performed no deployment or analytical/model call. Local application tests are recorded separately; historical release records remain unchanged. Source hashes identify all 303 indexed files. Both Submission spellings remain excluded.

- Graphify tree-sitter reported potentially partial extraction of Frontend/src/components/workspace.tsx at line 1101; 14 symbols extracted.
- Raw external import references can have no matching project node; unresolved endpoints are reported, not fabricated.
- The default undirected simple graph can combine multiple relationships between an endpoint pair; diagnostic counts retain this limitation.
- Host semantic-token usage is unavailable, not zero.
- AST extraction ran sequentially by explicit configuration; unchanged code extraction cache entries were reused.

Raw extraction: 1016 unresolved endpoint references, 0 missing endpoint fields, 0 self-loops and 585 collapsed same-endpoint relationships in the undirected projection. These are extraction limitations, not runtime failures.
