# Graph Report - 6. Google AI Builder Cup - Agentic BI  (2026-10-17)

## Corpus Check
- 227 files · ~161,087 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1797 nodes · 4772 edges · 129 communities (99 shown, 30 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 250 edges (avg confidence: 0.92)
- Token cost: 0 separate model-API tokens; host-session semantic input/output token usage is unavailable (not measured as zero).

## Graph Freshness
- Built from commit: `97315c59`
- This is a working-tree snapshot; VALIDATION.json records per-file SHA-256 hashes. Compare those hashes as well as the base commit to check freshness.
- Run `graphify update .` after code changes; use the Graphify skill for changed document semantics.

## Community Hubs (Navigation)
- Dashboard Configuration and Tests
- Retail Bundle Publication
- Skill Catalog and Seeding
- Workspace Motion and Themes
- Guarded Database Queries
- Workspace Preferences and Motion
- Analytical API Boundaries
- TypeScript Compiler Configuration
- Dashboard Results and Actions
- Runtime Configuration and Sessions
- Controlled Analysis Lifecycle
- Report Reliability Tests
- Shared Analytical Domain Model
- Shared Library Navigation
- Browser Voice Client Interfaces
- Settings and Skill Forms
- Interactive Chart Formatting
- Frontend API and Live Transport
- Result Cards and Feedback
- ADK Session Fencing
- Fenced Administrative Maintenance
- Reviewed Author and Preview Tabs
- Responsive Sidebar Primitives
- Application Service Architecture
- Report Checkpoint Recovery
- Scoped Cloud Foundation
- Saved Chart Presentation
- Shadcn Component Configuration
- Skill Author Concurrency Tests
- Report Repository Leases
- Frontend Development Dependencies
- Report Statistics and Chart Presentation
- Report Analysis Contracts
- Skill Draft Publication
- Workspace and Report Progress
- Frontend Runtime Dependencies
- Typed Analysis Contracts
- Saved Chart Presentation
- Typed Analysis Contracts
- Durable Report Engine
- Fenced Report Orchestration
- Public Product and Verification
- Skills Library Editor
- Typed Analysis Contracts
- Advanced Feature Contracts
- Local Setup and Verification
- Chart Tooltip Primitives
- Report Document Export Rendering
- Public API Regression Tests
- Landing Routing and Boundaries
- Landing Product Illustrations
- Mobile Navigation and Sheets
- Hosted Library and Voice Checks
- Private Report Dispatch Architecture
- Dashboard Detail Page
- Guarded Retail Source Analysis
- Frontend Package Scripts
- Analytical Evaluation Harnesses
- Report Dispatch Recovery Tests
- Application Service Architecture
- Private Report Worker Contract
- Customer Cohorts and Returns
- Data Quality and Fusion
- Marketing Associations and Scenarios
- Seasonality and Forecast Validation
- Firestore Contention Tests
- Reports and Validated Forecasts
- Saved Charts and Preferences
- Repository Contributor Guidance
- Time Series Data Publication
- Competition Demonstration Workflow
- Named Firestore ADK Persistence
- Saved Dashboard Retention Design
- Landing Route Design
- Original Retail Source Schema
- Expanded Retail Table Dictionary
- Skill Revision Snapshots
- Reports Library Page
- Bounded Forecast Input Contracts
- Revenue Forecast Playbook
- Backend Runtime Responsibilities
- Immutable Chart Data Services
- Published Dashboard Views and Recovery
- Frontend Contribution Guidance
- Tooltip Context Primitives
- Saved Chart View Tests
- Sales Change Contribution Playbook
- Comparable Store Performance Playbook
- Weighted Retail KPI Definitions
- Merchandise Margin and Refunds
- Atomic Storage Transactions
- Public Skill Versioning Decision
- Validated Public Evidence
- Dashboard Mutation and Retention Plan
- Immutable Report Evidence Contract
- Browser PCM Audio Worklet
- Responsive Viewport Subscriptions
- Chart Formatting Regression Tests
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
- Chronological Prediction Validation
- Synthetic Retail Source Publication
- Browser Model Selection Guide
- BeUI License Attribution
- Backend Dependency Manifest

## God Nodes (most connected - your core abstractions)
1. `AppError` - 174 edges
2. `Settings` - 107 edges
3. `MemoryStore` - 76 edges
4. `Connectors` - 58 edges
5. `Repository` - 56 edges
6. `create_app()` - 54 edges
7. `FirestoreSessionService` - 50 edges
8. `Querylane implemented architecture` - 50 edges
9. `StrictModel` - 43 edges
10. `AI` - 42 edges

## Surprising Connections (you probably didn't know these)
- `Join-key compatibility, coverage and fan-out` --semantically_similar_to--> `Explicit fan-out and incomplete-input rejection`  [INFERRED] [semantically similar]
  Backend/app/skill_library/analytics-data-quality.md → docs/adr/0003-bounded-cross-source-fusion.md
- `foundation()` --calls--> `operator_credentials()`  [INFERRED]
  infra/provision_reports.py → Backend/app/admin.py
- `main()` --uses--> `Settings`  [INFERRED]
  infra/report_recovery_check.py → Backend/app/config.py
- `main()` --uses--> `Settings`  [INFERRED]
  infra/runtime_check.py → Backend/app/config.py
- `main()` --uses--> `Connectors`  [INFERRED]
  infra/runtime_check.py → Backend/app/connectors.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Durable report execution and publication** — docs_architecture_report_outbox, docs_architecture_private_report_worker, docs_architecture_report_checkpoints, docs_architecture_verified_report_claims, docs_architecture_immutable_reports [EXTRACTED 1.00]
- **Scoped ordinary analysis evidence flow** — docs_architecture_voice_bridge, docs_architecture_bounded_analysis, docs_architecture_analysis_invocation_identity, docs_architecture_parent_cancellation, docs_architecture_immutable_artifacts [EXTRACTED 1.00]
- **Isolated public product introduction** — docs_landing_page_route_split, docs_landing_page_guided_preview, docs_landing_page_fixed_palette, docs_landing_page_forecast_fixture, docs_landing_page_workspace_links, docs_landing_page_legacy_redirect [EXTRACTED 1.00]
- **Latest hosted verification and explicit boundaries** — docs_validation_current_assessment, docs_validation_historical_baselines, docs_validation_manual_competition_checks, docs_validation_zero_axe_scans [EXTRACTED 1.00]

## Communities (129 total, 30 thin omitted)

### Community 0 - "Dashboard Configuration and Tests"
Cohesion: 0.10
Nodes (49): ChartViewState, DashboardAction, DashboardCreate, DashboardItemPatch, DashboardLayout, DashboardPatch, DashboardPin, DashboardRequest (+41 more)

### Community 1 - "Retail Bundle Publication"
Cohesion: 0.07
Nodes (49): demand(), generate(), GeneratorConfig, money(), promotion_window(), Path, Deterministic, bounded-memory synthetic retail history; never contacts a…, read_manifest() (+41 more)

### Community 2 - "Skill Catalog and Seeding"
Cohesion: 0.08
Nodes (39): analytics_examples(), Stable seed IDs let operators add examples without replacing public edits., Import the reviewable, source-controlled pack before any cloud writes., seed_analytics(), seed_examples(), compatible(), export_skill(), FrontmatterLoader (+31 more)

### Community 3 - "Workspace Motion and Themes"
Cohesion: 0.06
Nodes (40): AnalysisProgress(), stages, AnimatedNumber(), AnimatedNumberProps, ColorSelector(), ColorSelectorContext, ColorSelectorContextValue, ColorSelectorItem() (+32 more)

### Community 4 - "Guarded Database Queries"
Cohesion: 0.08
Nodes (37): Connectors, AppError, Exception, Deterministic synthetic retail data; no real customer information., retail_data(), linked_predicate(), AST validation complements restricted database roles; it is not a SQL sandbox., Every admitted OR branch must constrain the new relation to a prior one. (+29 more)

### Community 5 - "Workspace Preferences and Motion"
Cohesion: 0.07
Nodes (33): body, heading, metadata, mono, metadata, AppearanceSync(), AppProviders(), ResearchPanel() (+25 more)

### Community 6 - "Analytical API Boundaries"
Cohesion: 0.15
Nodes (18): Durable ADK session adapter with ordered events and fenced state writes., get_settings(), model_evidence(), Pinned text model choices; per-analysis context never mutates shared settings., resolve_text_model(), Cloud Tasks outbox, reconciliation and an explicitly local-only development…, Transactional report lifecycle, budgets, leases, event replay, and immutable…, Transient requester-only Google Search. Never uses the public Firestore ADK… (+10 more)

### Community 7 - "TypeScript Compiler Configuration"
Cohesion: 0.05
Nodes (40): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+32 more)

### Community 8 - "Dashboard Results and Actions"
Cohesion: 0.19
Nodes (22): formats, ResearchResult, SkillEvidence(), Alert(), AlertDescription(), AlertTitle(), alertVariants, Button() (+14 more)

### Community 9 - "Runtime Configuration and Sessions"
Cohesion: 0.09
Nodes (28): Settings, create_app(), ConversationCreate, live(), author_router(), skill_router(), MemoryStore, client() (+20 more)

### Community 10 - "Controlled Analysis Lifecycle"
Cohesion: 0.09
Nodes (16): AI, fixture_answer(), AnalysisService, evaluate(), main(), Numerical evaluation against independent Python aggregates of the retail seed., Answer, ResultArtifact (+8 more)

### Community 11 - "Report Reliability Tests"
Cohesion: 0.13
Nodes (36): ForecastSpec, ReportClarification, factual_claims(), _forecast(), Claims are computed on the full saved selection, never the chart preview., body(), fixture, parametrize (+28 more)

### Community 12 - "Shared Analytical Domain Model"
Cohesion: 0.09
Nodes (37): Analysis Brief, Analysis Run, Backtest, Chart Presentation, Connection, Conversation, Dashboard, Dashboard Item (+29 more)

### Community 13 - "Shared Library Navigation"
Cohesion: 0.11
Nodes (21): metadata, DashboardShare(), show(), DashboardEditor(), DashboardHeader(), useDashboardMutation(), DashboardWidget(), DashboardsLibrary() (+13 more)

### Community 14 - "Browser Voice Client Interfaces"
Cohesion: 0.08
Nodes (16): metadata, path(), SkillVoiceAuthor(), connect(), publish(), saveReview(), Workspace(), ask() (+8 more)

### Community 15 - "Settings and Skill Forms"
Cohesion: 0.10
Nodes (23): Catalog, ModelSettings(), preferenceLabels, sections, DialogClose(), DialogTrigger(), Field(), FieldContent() (+15 more)

### Community 16 - "Interactive Chart Formatting"
Cohesion: 0.12
Nodes (29): categoryColor(), InsightfulChart(), content(), download(), label(), palette, Plot(), Values() (+21 more)

### Community 17 - "Frontend API and Live Transport"
Cohesion: 0.09
Nodes (20): metadata, metadata, DashboardDownload(), download(), ReportEditDialog(), save(), ReportWorkspace(), download() (+12 more)

### Community 18 - "Result Cards and Feedback"
Cohesion: 0.09
Nodes (27): SavedCsvDownload(), download(), ResultCard, PinToDashboard(), create(), pin(), requestFor(), ResultCard (+19 more)

### Community 19 - "ADK Session Fencing"
Cohesion: 0.13
Nodes (20): FirestoreSessionService, StaleLease, test_raw_audio_is_not_persisted(), test_recent_session_context_uses_newest_events(), test_transient_model_failure_retried_once_only(), test_model_access_failure_is_explicit_and_never_falls_back(), test_vector_query_uses_pinned_sdk_signature_and_dimensions(), setup_run() (+12 more)

### Community 20 - "Fenced Administrative Maintenance"
Cohesion: 0.13
Nodes (19): check_models(), cleanup_skill_authors(), cli(), dashboard_maintenance(), index_schema(), main(), operator_credentials(), Credentialed CLI only. No administrative endpoint is exposed by FastAPI. (+11 more)

### Community 21 - "Reviewed Author and Preview Tabs"
Cohesion: 0.12
Nodes (18): views, MarkdownContent(), MessageContent(), SkillMarkdown(), Phase, requirements, Checkbox(), Select() (+10 more)

### Community 22 - "Responsive Sidebar Primitives"
Cohesion: 0.09
Nodes (8): Sidebar(), SidebarContext, SidebarContextProps, SidebarMenuButton(), sidebarMenuButtonVariants, SidebarRail(), SidebarTrigger(), useSidebar()

### Community 23 - "Application Service Architecture"
Cohesion: 0.18
Nodes (25): Analyst SQL and voice regression invariants, Per-invocation analysis identity, Querylane implemented architecture, Guest-private author recovery, Controlled text and voice analysis service, Fenced conversation lease, Persisted event replay, Backend-only named Firestore storage (+17 more)

### Community 24 - "Report Checkpoint Recovery"
Cohesion: 0.09
Nodes (11): ExportStorage, digest(), Repository, test_default_retry_reuses_original_model_after_operator_default_changes(), test_checkpointed_queries_are_not_reexecuted_after_worker_recovery(), test_export_storage_immutable_integrity_and_path_traversal(), test_recovery_uses_saved_sql_repair_and_its_attempt_identity(), test_time_series_pipeline_matches_independent_daily_monthly_and_yoy_values() (+3 more)

### Community 25 - "Scoped Cloud Foundation"
Cohesion: 0.18
Nodes (19): main(), Build with a resource-scoped builder, then deploy as the current operator., configuration(), main(), Prepare or deploy ONLY the private report worker. Foundation/IAM are separate…, ensure_secret(), ensure_service_account(), gcloud() (+11 more)

### Community 26 - "Saved Chart Presentation"
Cohesion: 0.24
Nodes (21): metadata(), Reject unbound metadata; old artifacts get conservative, display-only defaults., card_image(), card_notes(), display_value(), download(), manifest(), plot_images() (+13 more)

### Community 27 - "Shadcn Component Configuration"
Cohesion: 0.09
Nodes (22): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+14 more)

### Community 28 - "Skill Author Concurrency Tests"
Cohesion: 0.24
Nodes (20): asyncio, AuthorDraft, create(), guest(), prepared(), parametrize, setup_service(), test_competing_publish_and_review_cannot_silently_publish_a_stale_draft() (+12 more)

### Community 30 - "Frontend Development Dependencies"
Cohesion: 0.10
Nodes (21): babel-plugin-react-compiler, eslint, eslint-config-next, devDependencies, babel-plugin-react-compiler, eslint, eslint-config-next, shadcn (+13 more)

### Community 31 - "Report Statistics and Chart Presentation"
Cohesion: 0.13
Nodes (18): change(), csv_cell(), csv_line(), date_value(), next_date(), normalized_spec(), number(), Bounded, deterministic presentation of immutable result pages. No SQL or model… (+10 more)

### Community 32 - "Report Analysis Contracts"
Cohesion: 0.19
Nodes (15): saved_rows(), check_maintenance(), field_validator, Bounded contracts shared by the report harness, API, renderer, and numerical…, ReportCreate, ReportMutation, ReportPatch, ReportRevisionCreate (+7 more)

### Community 34 - "Workspace and Report Progress"
Cohesion: 0.16
Nodes (16): active(), ConversationReports(), ReportRunCard(), cancel(), clarify(), poll(), assumptionHorizon(), assumptionRows() (+8 more)

### Community 35 - "Frontend Runtime Dependencies"
Cohesion: 0.11
Nodes (19): class-variance-authority, clsx, dependencies, class-variance-authority, clsx, radix-ui, react, react-dom (+11 more)

### Community 36 - "Typed Analysis Contracts"
Cohesion: 0.29
Nodes (16): _arrow_bytes(), fuse(), _identifier(), Any, A typed plan compiler; no model-supplied SQL or Python reaches DuckDB., _worker(), Calculation, FusionPlan (+8 more)

### Community 37 - "Saved Chart Presentation"
Cohesion: 0.32
Nodes (16): present(), artifact(), test_ambiguous_temporal_grain_falls_back_instead_of_connecting_cohorts(), test_categories_top_n_shares_negative_and_tied_values(), test_daily_history_includes_zero_and_range_summaries(), test_duplicate_dates_do_not_generate_period_comparisons(), test_explicit_targets_and_legacy_conservative_metadata(), test_fractional_percent_points_and_units() (+8 more)

### Community 38 - "Typed Analysis Contracts"
Cohesion: 0.14
Nodes (15): ChartMeasure, field_validator, StrictModel, TurnCreate, AnalysisTask, EvidenceClaim, ReviewResult, AuthorBrief (+7 more)

### Community 39 - "Durable Report Engine"
Cohesion: 0.25
Nodes (5): ReportEngine, ReportDraft, ReportPlan, ReportSection, test_report_writer_cannot_invent_numbers_or_references()

### Community 40 - "Fenced Report Orchestration"
Cohesion: 0.14
Nodes (9): NeedsInput, Exception, ADK graph orchestration with global policy and explicit application checkpoints., Graph nodes carry only a run identifier. Bodies live in fenced checkpoints., ReportPolicy, run_report_graph(), test_graph_preserves_clarification_without_running_downstream_stages(), test_policy_blocks_tools_and_enforces_model_budget() (+1 more)

### Community 41 - "Public Product and Verification"
Cohesion: 0.19
Nodes (14): Title-specific accessible table regions, Dated evidence and verification boundaries, 17 October fix release assessment, Historical validation baselines, Verified landing network boundary, Remaining manual competition verification, Validation and remaining release gates, Automated accessibility evidence (+6 more)

### Community 42 - "Skills Library Editor"
Cohesion: 0.18
Nodes (8): metadata, contentOf(), SkillsWorkspace(), editSkill(), exportFile(), importFile(), openEditor(), sourceLabel()

### Community 43 - "Typed Analysis Contracts"
Cohesion: 0.35
Nodes (11): fixture_plan(), Explicit local-only sample planner. Never used as a Gemini fallback., AnalysisPlan, JoinKey, Projection, SourceQuery, VisualizationSpec, Explicit local sample plans for the larger dataset, never a Gemini fallback. (+3 more)

### Community 44 - "Advanced Feature Contracts"
Cohesion: 0.15
Nodes (13): Advanced Analysis prediction gates, Analytics and prediction playbook catalog, Insert-only seed-analysis-skills operation, Twelve analytics and prediction playbooks, Three-skill analysis budget, Advanced Analysis durable report contract (deployed), Isolated requester-only Search research, Public versioned Skills library (+5 more)

### Community 45 - "Local Setup and Verification"
Cohesion: 0.15
Nodes (13): Operator-token Gemini fixture preview, ADC local cloud-service development, In-memory deterministic fixture mode, Loopback Firestore emulator tests, Independent Next.js output directories, Local landing and workspace entry, Local development setup, Isolated voice-author preview (+5 more)

### Community 46 - "Chart Tooltip Primitives"
Cohesion: 0.21
Nodes (11): ChartConfig, ChartContainer(), ChartContext, ChartContextProps, ChartLegendContent(), ChartTooltipContent(), getPayloadConfigFromPayload(), INITIAL_DIMENSION (+3 more)

### Community 47 - "Report Document Export Rendering"
Cohesion: 0.24
Nodes (9): chart_image(), chart_images(), format_axis(), Immutable report files. Rendering accepts saved evidence, never SQL or model…, _render(), _render_entry(), zip_entry(), Table (+1 more)

### Community 48 - "Public API Regression Tests"
Cohesion: 0.30
Nodes (11): guest(), parametrize, A worker may finish after the event query but before the status read., test_analysis_replay_fork_and_provenance(), test_guest_scope_and_no_administrative_routes(), test_origin_and_payload_validation(), test_stream_drains_events_committed_between_poll_and_terminal_read(), test_voice_does_not_fake_model_in_fixture_mode() (+3 more)

### Community 49 - "Landing Routing and Boundaries"
Cohesion: 0.26
Nodes (12): Landing frontend release 00012-mv5, Fixed landing palette and saved appearance isolation, Verified saved forecast fixture, Local guided preview boundary, Public landing page guide, Fixed same-origin legacy 307 redirect, Evidence-backed BI product story, Verified synthetic retail totals (+4 more)

### Community 50 - "Landing Product Illustrations"
Cohesion: 0.20
Nodes (9): capabilities, faqs, metadata, OpenQuerylane(), LandingMobileNavigation(), HeroProduct(), money(), RevenueIllustration() (+1 more)

### Community 51 - "Mobile Navigation and Sheets"
Cohesion: 0.27
Nodes (7): Sheet(), SheetClose(), SheetContent(), SheetDescription(), SheetHeader(), SheetTitle(), SheetTrigger()

### Community 52 - "Hosted Library and Voice Checks"
Cohesion: 0.18
Nodes (7): main(), Opt-in API check using existing immutable artifacts; never runs an analysis or…, run(), main(), Opt-in hosted report acceptance; creates public verification…, run(), Opt-in hosted repeated Live analysis; public test chat, read-only source…

### Community 53 - "Private Report Dispatch Architecture"
Cohesion: 0.24
Nodes (11): Private Cloud Run report worker, Fenced report checkpoints, Operator, local ADC and workload credentials, Primary deployment runbook, Compatibility-aware traffic rollback, Private worker task and scheduler OIDC, Dated deployment and rollback records, Routine application release (+3 more)

### Community 54 - "Dashboard Detail Page"
Cohesion: 0.24
Nodes (6): metadata, DashboardWorkspace(), refreshRemoved(), restoreItem(), setMode(), unpin()

### Community 55 - "Guarded Retail Source Analysis"
Cohesion: 0.22
Nodes (10): Timeseries profile and source limits, Nested explicit-key SQL join validation, Keyed join validation boundary, Restricted BigQuery and PostgreSQL connectors, Insert-only fenced retail data publication, Bounded SQL repair, Independent hosted source reconciliation, Dedicated runtime and build identities (+2 more)

### Community 56 - "Frontend Package Scripts"
Cohesion: 0.20
Nodes (9): name, private, scripts, build, dev, lint, start, test (+1 more)

### Community 57 - "Analytical Evaluation Harnesses"
Cohesion: 0.39
Nodes (7): cases(), matches(), main(), Evaluate the public, hosted API against independent seed reference values., main(), Opt-in public deployment checks. Creates visible demo conversations; never…, run()

### Community 58 - "Report Dispatch Recovery Tests"
Cohesion: 0.31
Nodes (3): ReportDispatcher, test_expired_waiting_report_releases_conversation_slot(), test_outbox_recovers_abandoned_workers_and_queued_cancellation()

### Community 59 - "Application Service Architecture"
Cohesion: 0.28
Nodes (9): Reference-aware artifact retention, Saved-result chart presentation, Bounded whole-dashboard exports, Immutable report revisions and downloads, Operator maintenance fence, Shared saved-result dashboards, Explicit maintenance and purge operations, Analytical and export resource controls (+1 more)

### Community 60 - "Private Report Worker Contract"
Cohesion: 0.32
Nodes (7): error(), execute(), Private Cloud Run entrypoint. Deploy with --no-allow-unauthenticated and…, reconcile(), TaskBody, exception_handler, post

### Community 61 - "Customer Cohorts and Returns"
Cohesion: 0.36
Nodes (8): Signup cohorts and first observed purchase cohorts, Customer cohorts and repeat purchasing, Equally mature customer observation windows, Repeat purchase and activity retention denominators, Validated bounded-rate or monetary forecast domain, Explicit return-rate target and denominator, Returns and rate prediction readiness, Refund latency and cohort maturity

### Community 62 - "Data Quality and Fusion"
Cohesion: 0.32
Nodes (8): Data quality and analysis readiness, Calendar spine, unknown gaps and observed zeros, Join-key compatibility, coverage and fan-out, Independent totals reconciliation, Explicit fan-out and incomplete-input rejection, ADR: Typed bounded cross-source fusion, Gemini relationship-key and business-assumption hypotheses, Trusted compiler for typed relational fusion

### Community 63 - "Marketing Associations and Scenarios"
Cohesion: 0.36
Nodes (8): Attributed revenue per campaign spend, Compatible campaign and period aggregation, Campaign and promotion performance, Validated future promotion scenario, Bounded regression/SARIMAX scenario predictions, Conditional driver and promotion scenarios, Visitor-supplied future driver paths, Historically supported driver model

### Community 64 - "Seasonality and Forecast Validation"
Cohesion: 0.32
Nodes (8): Dense retail calendar at consistent time grain, Shifted target-derived rolling predictors, Observed peaks with causal limitations, Calendar trends and retail seasonality, Baseline comparison and candidate promotion, Forecast validation and uncertainty, Chronological rolling-origin backtests, Supported prediction intervals and publication outcome

### Community 65 - "Firestore Contention Tests"
Cohesion: 0.43
Nodes (7): firestore_store(), Exercise real SDK transaction decoration with a read-phase contention fault., test_business_validation_errors_are_not_retried_or_disguised(), test_exhausted_sdk_commit_budget_is_not_multiplied(), test_read_abort_retries_then_reports_conversation_busy(), test_read_retries_are_bounded_and_exhaustion_is_a_busy_response(), test_read_retry_commits_mutation_only_once()

### Community 66 - "Reports and Validated Forecasts"
Cohesion: 0.25
Nodes (8): Independent Advanced Analysis reports, Bounded ADK report workflow, Transactional report outbox, Requester-only isolated Search research, Chronologically validated forecasts, Verified numerical report claims, Non-additive report claim policy v2, Reviewed report with validated ETS prediction

### Community 67 - "Saved Charts and Preferences"
Cohesion: 0.25
Nodes (8): Immutable saved-result chart presentation, Motion and feedback (deployed 2026-10-16), Reader-aware answer following, Unified device/application reduced motion, Versioned browser-local preferences, Local chart exploration defaults, Pinned analysis model catalog, Task-local captured analysis model

### Community 68 - "Repository Contributor Guidance"
Cohesion: 0.33
Nodes (7): Authoritative architecture and derived graphs, Separate authorized deployment and data operations, Context7 CLI documentation policy, Graphify code and document semantic refresh, Repository instructions, Triggered feature documentation, Documentation-only verification scope

### Community 69 - "Time Series Data Publication"
Cohesion: 0.29
Nodes (7): Original demo retail schema (seed evidence 2026-10-16), Fenced insert-only cloud publication, Independent bundle reconciliation, Expanded retail column dictionary (retail-timeseries-v1), Stable full-window extend workflow, Deterministic streaming Parquet bundle, Additional timeseries source profile

### Community 70 - "Competition Demonstration Workflow"
Cohesion: 0.29
Nodes (7): Cross-source actual-versus-target exploration, Five-minute competition demonstration, Landing previews and direct workspace entry, Production rehearsal and backup recording, Public conversation sharing and forks, Spoken analysis and interruption, Warehouse question with SQL evidence

### Community 71 - "Named Firestore ADK Persistence"
Cohesion: 0.47
Nodes (6): Separate skill author session lease collection, Bounded fresh-transaction retries for read aborts, Custom Firestore ADK session adapter, ADR: ADK persistence in named Firestore, Loaded-session revision and conversation lease fencing, Terminal event stream sequence draining

### Community 72 - "Saved Dashboard Retention Design"
Cohesion: 0.33
Nodes (6): Versioned chart view, ADR 0005: saved-result dashboards (accepted 2026-10-16), Immutable paginated results, Retained artifact references, Shared dashboard implementation plan (implemented/deployed 2026-10-16), Public shared dashboards and saved-view downloads

### Community 73 - "Landing Route Design"
Cohesion: 0.33
Nodes (6): ADR 0008 landing and workspace split, Query-aware 307 compatibility redirect, Landing palette and workspace preference isolation, Local evidence-only guided preview, Server-rendered public introduction, Direct unauthenticated workspace entry

### Community 74 - "Original Retail Source Schema"
Cohesion: 0.33
Nodes (6): Original PostgreSQL retail.customer_profiles, Original BigQuery order_items, Original BigQuery orders, Original BigQuery products, Original PostgreSQL retail.regional_targets, Original BigQuery returns

### Community 75 - "Expanded Retail Table Dictionary"
Cohesion: 0.40
Nodes (6): Dense daily calendar date spine, Time-series customer_profiles, Time-series sales_order_items, Time-series sales_orders, Time-series sales_returns, Full-month store targets

### Community 76 - "Skill Revision Snapshots"
Cohesion: 0.33
Nodes (6): Per-analysis skill snapshots, Bounded metadata-only skill discovery, Public optimistic skill mutations, Immutable skill revisions and recovery, Conversational voice author (documented local implementation), Conversational voice skill author plan and contracts

### Community 77 - "Reports Library Page"
Cohesion: 0.40
Nodes (4): metadata, ReportsLibrary(), change(), restore()

### Community 79 - "Revenue Forecast Playbook"
Cohesion: 0.60
Nodes (5): Approved naive, ETS, SARIMAX and regression candidates, Complete observed series and actual forecast cutoff, Forecast horizons and fit budgets, Candidate promotion, baseline retention or withholding, Revenue and demand forecasting

### Community 80 - "Backend Runtime Responsibilities"
Cohesion: 0.50
Nodes (5): Querylane backend, Named Firestore and private report bucket, Private report worker with Cloud Tasks checkpoints, Public chat, voice and analytical libraries API, Saved-artifact dashboard download contract

### Community 81 - "Immutable Chart Data Services"
Cohesion: 0.40
Nodes (5): Deterministic bounded chart sampling, Saved-artifact chart-data endpoint, Deterministic truthful chart insights, Full saved-result CSV export, Version-2 VisualizationSpec metadata

### Community 82 - "Published Dashboard Views and Recovery"
Cohesion: 0.40
Nodes (5): Active and recoverable artifact retention, Canonical public dashboard sharing, Public revision-checked editing, Published saved chart views, Revision-checked whole-dashboard exports

### Community 83 - "Frontend Contribution Guidance"
Cohesion: 0.40
Nodes (5): Frontend contributor instructions, Guest-scoped report clarification and skill draft recovery, Installed Next.js version guides, Browser preferences and reduced-motion feedback, Explicit saved chart publication and revision checks

### Community 84 - "Tooltip Context Primitives"
Cohesion: 0.40
Nodes (4): Tooltip(), TooltipContent(), TooltipProvider(), TooltipTrigger()

### Community 85 - "Saved Chart View Tests"
Cohesion: 0.50
Nodes (3): { initialChartView, describeChartView }, load(), reader()

### Community 86 - "Sales Change Contribution Playbook"
Cohesion: 0.50
Nodes (4): Observed concentrations versus causal explanations, Sales change and segment contributions, Reconciled segment change contributions, Exact order-volume and AOV revenue bridge

### Community 87 - "Comparable Store Performance Playbook"
Cohesion: 0.67
Nodes (4): Comparable-store and target performance, Comparable-store eligibility, Store and regional target join grain, Weighted attainment and reconciled target gaps

### Community 88 - "Weighted Retail KPI Definitions"
Cohesion: 0.67
Nodes (4): Completed-order merchandise revenue, Retail KPI definitions and weighted ratios, Overall AOV from revenue and distinct orders, Weighted margin rate and additive reconciliation

### Community 89 - "Merchandise Margin and Refunds"
Cohesion: 0.67
Nodes (4): Historical line merchandise revenue and cost, Merchandise margin and returns-adjusted performance, Order-cohort refund and returned-cost adjustment, Signed margin and return-cohort maturity

### Community 91 - "Public Skill Versioning Decision"
Cohesion: 0.50
Nodes (4): ADR 0004: public versioned skills (accepted 2026-10-15), Bounded metadata skill selector, Public Markdown playbooks, Analysis-scoped immutable skill snapshots

### Community 92 - "Validated Public Evidence"
Cohesion: 0.50
Nodes (4): ADR 0007: public report evidence (accepted 2026-10-17), Requester-only in-memory Search panel, Verified numerical claims, Distinct writer and semantic reviewer

### Community 93 - "Dashboard Mutation and Retention Plan"
Cohesion: 0.50
Nodes (4): Validated ChartViewState, Fenced reference-aware history maintenance, Revision-checked idempotent dashboard mutations, Immutable saved-artifact dashboard cards

### Community 94 - "Immutable Report Evidence Contract"
Cohesion: 0.50
Nodes (4): Verified-claim policy v2, Fenced transactional outbox and application checkpoints, Immutable PDF / DOCX / CSV ZIP exports, Immutable report families and revisions

### Community 96 - "Responsive Viewport Subscriptions"
Cohesion: 0.67
Nodes (3): SidebarProvider(), subscribe(), useIsMobile()

### Community 98 - "Public Anonymous Workspace Decision"
Cohesion: 1.00
Nodes (3): Anonymous guest token attribution, quotas and cancellation, Public shared conversations, ADR: Public workspace without accounts

### Community 99 - "Durable Report Execution Decision"
Cohesion: 0.67
Nodes (3): ADK App / Runner / Workflow, Independent durable report execution, ADR 0006: durable versioned reports (accepted 2026-10-17)

### Community 105 - "Cloud Build Workflow"
Cohesion: 0.67
Nodes (3): Cloud Build Docker build step, Cloud Build Docker push step, Dedicated GCS-only build logs

## Knowledge Gaps
- **214 isolated node(s):** `agentic-bi-backend`, `$schema`, `style`, `rsc`, `tsx` (+209 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **30 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AppError` connect `Guarded Database Queries` to `Dashboard Configuration and Tests`, `Skill Catalog and Seeding`, `Analytical API Boundaries`, `Runtime Configuration and Sessions`, `Controlled Analysis Lifecycle`, `Report Reliability Tests`, `ADK Session Fencing`, `Fenced Administrative Maintenance`, `Report Checkpoint Recovery`, `Saved Chart Presentation`, `Skill Author Concurrency Tests`, `Report Repository Leases`, `Report Statistics and Chart Presentation`, `Report Analysis Contracts`, `Skill Draft Publication`, `Typed Analysis Contracts`, `Saved Chart Presentation`, `Typed Analysis Contracts`, `Durable Report Engine`, `Fenced Report Orchestration`, `Report Document Export Rendering`, `Report Dispatch Recovery Tests`, `Private Report Worker Contract`, `Firestore Contention Tests`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Why does `Settings` connect `Runtime Configuration and Sessions` to `Report Analysis Contracts`, `Dashboard Configuration and Tests`, `Skill Catalog and Seeding`, `Guarded Database Queries`, `Saved Chart Presentation`, `Analytical API Boundaries`, `Controlled Analysis Lifecycle`, `Report Reliability Tests`, `Public API Regression Tests`, `ADK Session Fencing`, `Fenced Administrative Maintenance`, `Report Checkpoint Recovery`, `Saved Chart Presentation`, `Skill Author Concurrency Tests`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Why does `MemoryStore` connect `Runtime Configuration and Sessions` to `Dashboard Configuration and Tests`, `Skill Catalog and Seeding`, `Saved Chart Presentation`, `Saved Chart Presentation`, `Analytical API Boundaries`, `Controlled Analysis Lifecycle`, `Report Reliability Tests`, `ADK Session Fencing`, `Fenced Administrative Maintenance`, `Report Checkpoint Recovery`, `Atomic Storage Transactions`, `Skill Author Concurrency Tests`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Are the 64 inferred relationships involving `AppError` (e.g. with `AI` and `AnalysisService`) actually correct?**
  _`AppError` has 64 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `Settings` (e.g. with `Connectors` and `create_app()`) actually correct?**
  _`Settings` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `MemoryStore` (e.g. with `test_every_chart_family_and_mixed_units_can_render()` and `test_complex_plan_uses_json_mode_and_still_validates_locally()`) actually correct?**
  _`MemoryStore` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `Connectors` (e.g. with `Settings` and `AppError`) actually correct?**
  _`Connectors` has 11 INFERRED edges - model-reasoned connections that need verification._
## Extraction Integrity and Scope

Generated with Graphify 0.9.51. All 46 detected documents have semantic nodes: 41 cached and 5 re-extracted in one host-session agent. Code extraction is local AST analysis. No separate model API, analytical database or cloud deployment was invoked.

- Graphify tree-sitter reported potentially partial extraction of Frontend/src/components/workspace.tsx at line 1075; 13 symbols extracted.
- Raw external import references can have no matching project node; unresolved endpoints are reported, not fabricated.
- The default undirected simple graph can combine multiple relationships between an endpoint pair; diagnostic counts retain this limitation.
- Host semantic-token usage is unavailable, not zero.
- The initial AST multiprocessing attempt from stdin failed to spawn; Graphify automatically completed the extraction sequentially.

Raw extraction contains **750 unresolved endpoint references**, **0 missing endpoint fields**, **0 self-loops** and **438 same-endpoint relationships collapsed** by the default undirected graph. Many unresolved references are external SDK/module imports; absent entities are not invented. These are extraction limits, not runtime defects.

Community names, centrality and cross-document links are navigation heuristics. Dated deployment/plan statements retain their scope. [VALIDATION.json](VALIDATION.json) records source hashes; [the graph guide](../docs/graphify/README.md) explains maintenance.
