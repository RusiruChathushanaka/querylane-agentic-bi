# Graph Report - 6. Google AI Builder Cup - Agentic BI  (2026-10-18)

## Corpus Check
- 288 files · ~215,149 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2473 nodes · 6578 edges · 134 communities (104 shown, 30 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 347 edges (avg confidence: 0.91)
- Token cost: 0 separate model-API tokens; host-session semantic input/output usage is unavailable (not measured as zero).

## Graph Freshness
- Built from commit: `3dbebe41`
- This is a working-tree snapshot; VALIDATION.json records per-file SHA-256 hashes. Compare those hashes as well as the base commit to check freshness.
- Run `graphify update .` after code changes; use the Graphify skill for changed document semantics.

## Community Hubs (Navigation)
- TimesFM Validation and Recovery
- Application Error Contracts
- Bounded Runtime Configuration
- Accessible Motion Preferences
- Retail Generation and Upload
- Controlled Analytics Architecture
- Dashboard Editing and Sharing
- Transactional Storage and Persistence
- Forecast Plan Reader and Controls
- Saved Chart Data Presentation
- Voice and Text Workspace
- Analytics and Prediction Playbooks
- Responsive Sidebar Primitives
- Report Recovery and Export Tests
- Read-Only SQL Safety Tests
- Forecast Plan Reader and Controls
- Skill Selection and Snapshot Tests
- Static Product Preview Contract
- Workspace Appearance and Preferences
- Coherent Forecast Planning Contract
- TypeScript Compiler Configuration
- Operator Maintenance Commands
- Dated Local and Hosted Acceptance
- Shared Analytical Domain Model
- Worker-First Release Runbook
- Saved Result Evidence and Charts
- Metric and Planning Regression Tests
- Public Retail Product Overview
- Frontend HTTP and Stream Recovery
- Public Versioned Skill Contract
- Skill Author Concurrency Tests
- Report Reader and Downloads
- Scoped Cloud Provisioning
- Versioned Metrics and Controlled Compilation
- Conversation Persistence and Recovery
- Shared Job Admission and Leases
- Interactive Chart Exploration
- Hierarchical Planning and Adjustments
- Repository Contribution Guidance
- Typed Analysis and Visualization
- Shadcn Component Configuration
- Evidence-Backed Report Workflow
- Frontend Development Dependencies
- Static Landing Product Tour
- Typed Fusion Regression Tests
- Reviewed Skill Draft Publication
- Navigation and Release Preservation
- Evidence-Backed Report Contracts
- Frontend Runtime Dependencies
- Managed Forecast Comparison Policy
- Local Setup and Verification
- Durable Dashboard and Forecast Execution
- Durable Advanced Report Contract
- Public API Composition
- AI Retry and Failure Tests
- Skills Library Interface
- Reviewed Coherent Planning
- Public API Regression Tests
- Chart Tooltip and Legend Primitives
- Saved Evidence and Retention
- Dashboard Editing and Sharing
- Versioned Metrics and Controlled Compilation
- Frontend Package Scripts
- Retry and Recovery Boundaries
- Customer Cohorts and Returns
- Data Quality and Fusion
- Seasonality and Backtesting
- Backend Runtime and Verification
- Firestore Contention Regression Tests
- Skill Selection and Snapshot Tests
- Managed TimesFM Architecture Decision
- Retail Data Publication Workflow
- Competition Demonstration Workflow
- Conditional Driver Scenario Playbook
- Revenue Forecast Playbook
- Named Firestore ADK Persistence
- Original Retail Source Schema
- Expanded Retail Column Dictionary
- Public Reports Library
- Reviewed Dashboard Publication Decision
- Immutable Chart Presentation Contract
- Published Dashboard Views and Retention
- Frontend Contribution Guidance
- Saved Dashboard View Tests
- Planning Review and Retry Tests
- Prediction Evidence Rendering Tests
- Sales Change Contribution Playbook
- Comparable Store Performance Playbook
- Weighted Retail KPI Definitions
- Marketing Associations and Scenarios
- Merchandise Margin and Refunds
- Transactional Storage Contracts
- Saved Dashboard Smoke Tests
- Hosted Report Acceptance Harness
- Live Voice Test Harness
- Public Skill Versioning Decision
- Public Report Evidence Boundary
- Immutable Saved-Artifact Dashboard Cards
- Managed Forecast Comparison Policy
- Browser PCM Audio Worklet
- Chart Formatting Regression Tests
- Versioned Skill Catalog
- Live Voice Failure Recovery
- Repeated Voice Analytics Checks
- Public Anonymous Workspace Decision
- Immutable Durable Report Decision
- Runtime Backend Configuration Route
- Frontend Health Route
- Safe Markdown Rendering Tests
- Accessible Table Regression Tests
- Scoped Cloud Build Workflow
- Local Social Preview Asset
- Backend Package Entrypoint
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
- Retail Data Operator Workflow
- BeUI License Attribution
- Backend Dependency Manifest

## God Nodes (most connected - your core abstractions)
1. `AppError` - 239 edges
2. `Settings` - 126 edges
3. `Architecture` - 103 edges
4. `MemoryStore` - 90 edges
5. `Connectors` - 74 edges
6. `Repository` - 65 edges
7. `create_app()` - 64 edges
8. `StrictModel` - 59 edges
9. `FirestoreSessionService` - 55 edges
10. `Deployment Guide` - 52 edges

## Surprising Connections (you probably didn't know these)
- `Join-key compatibility, coverage and fan-out` --semantically_similar_to--> `Explicit fan-out and incomplete-input rejection`  [INFERRED] [semantically similar]
  Backend/app/skill_library/analytics-data-quality.md → docs/adr/0003-bounded-cross-source-fusion.md
- `Shared-method baseline and alternative scenario artifacts` --conceptually_related_to--> `Separate immutable scenario with same-method baseline and alternative`  [INFERRED]
  Backend/app/skill_library/prediction-driver-scenarios.md → docs/timesfm.md
- `Common chronological scores choose statistical or managed candidate` --conceptually_related_to--> `Common three-fold full-horizon measured method selection`  [INFERRED]
  Backend/app/skill_library/prediction-sales-forecast.md → docs/timesfm.md
- `Atomic dashboard publication` --semantically_similar_to--> `Skill Publication`  [INFERRED] [semantically similar]
  docs/ai-dashboard-builder.md → CONTEXT.md
- `main()` --uses--> `FirestoreSessionService`  [INFERRED]
  infra/runtime_check.py → Backend/app/adk_sessions.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Reviewed revision-safe dashboard publication** — docs_ai_dashboard_builder_atomic_dashboard_publication, docs_ai_dashboard_builder_revision_aware_rebase, docs_ai_dashboard_builder_conditional_undo, docs_ai_dashboard_builder_guest_owned_proposal_expiry [EXTRACTED 1.00]
- **Immutable controlled metric execution** — docs_business_metrics_closed_typed_metric_formula, docs_business_metrics_application_owned_grain_compiler, docs_business_metrics_immutable_dependency_snapshots, docs_business_metrics_canonical_forecast_value_reconciliation [EXTRACTED 1.00]
- **Validated coherent hierarchy recipe** — docs_forecast_plans_aggregate_candidate_selection, docs_forecast_plans_training_only_leaf_allocation, docs_forecast_plans_cent_exact_monetary_reconciliation, docs_forecast_plans_level_balanced_promotion_gate, docs_forecast_plans_coherent_baseline_fallback [EXTRACTED 1.00]
- **Static saved-evidence previews retain analytical and publication boundaries** — docs_landing_page_guided_preview, docs_landing_page_forecast_fixture, docs_landing_page_scenario_fixture, docs_landing_page_captured_version_links [EXTRACTED 1.00]
- **Fenced admission, stable jobs, persistent cancellation and conservative billing** — docs_timesfm_atomic_admission, docs_timesfm_stable_jobs, docs_timesfm_persistent_cancellation, docs_timesfm_conservative_billing [EXTRACTED 1.00]
- **Frozen saved input, deterministic selection, separate scenarios and immutable exports** — docs_timesfm_frozen_saved_input, docs_timesfm_candidate_selection, docs_timesfm_separate_scenario, docs_timesfm_saved_export_evidence [EXTRACTED 1.00]

## Communities (134 total, 30 thin omitted)

### Community 0 - "TimesFM Validation and Recovery"
Cohesion: 0.07
Nodes (79): date_value(), metadata(), next_date(), Reject unbound metadata; old artifacts get conservative, display-only defaults., validate_view(), choose(), compare(), eligible() (+71 more)

### Community 1 - "Application Error Contracts"
Cohesion: 0.06
Nodes (52): normalized_spec(), Bounded, deterministic presentation of immutable result pages. No SQL or model…, Called once when saving a new artifact; historical documents remain immutable., json_rows(), json_value(), Any, AppError, Exception (+44 more)

### Community 2 - "Bounded Runtime Configuration"
Cohesion: 0.06
Nodes (44): FirestoreSessionService, Durable ADK session adapter with ordered events and fenced state writes., index_schema(), AI, AnalysisService, get_settings(), Settings, Connectors (+36 more)

### Community 3 - "Accessible Motion Preferences"
Cohesion: 0.05
Nodes (56): body, heading, metadata, mono, metadata, AppearanceSync(), AppProviders(), AnalysisProgress() (+48 more)

### Community 4 - "Retail Generation and Upload"
Cohesion: 0.07
Nodes (55): demand(), generate(), GeneratorConfig, money(), promotion_window(), Path, Deterministic, bounded-memory synthetic retail history; never contacts a…, read_manifest() (+47 more)

### Community 5 - "Controlled Analytics Architecture"
Cohesion: 0.05
Nodes (66): Explicit-key SQL, bounded repair, distinct voice invocations and parent cancellation, Controlled metric compilation, immutable dependencies and canonical forecast targets, Ordinary analytics versus Advanced Analysis prediction fitting, Retail KPI definitions and weighted ratios, ADK typed planner and result interpreter, Controlled analysis service, Invocation-scoped query records and BigQuery job legs, Public FastAPI HTTP, SSE and WebSocket API (+58 more)

### Community 6 - "Dashboard Editing and Sharing"
Cohesion: 0.10
Nodes (37): metadata, DashboardDownload(), download(), DashboardShare(), show(), formats, DashboardEditor(), useDashboardMutation() (+29 more)

### Community 7 - "Transactional Storage and Persistence"
Cohesion: 0.11
Nodes (39): ChartViewState, DashboardAction, DashboardCreate, DashboardItemPatch, DashboardLayout, DashboardPatch, DashboardPin, DashboardRequest (+31 more)

### Community 8 - "Forecast Plan Reader and Controls"
Cohesion: 0.06
Nodes (35): metadata, metadata, metadata, DashboardBuilder(), JobControls(), send(), SavedArtifactPreview(), MetricRevision() (+27 more)

### Community 9 - "Saved Chart Data Presentation"
Cohesion: 0.09
Nodes (52): change(), csv_cell(), csv_line(), number(), present(), Shared indices preserve extrema for all series, endpoints, and null boundaries., sampled_rows(), card_image() (+44 more)

### Community 10 - "Voice and Text Workspace"
Cohesion: 0.06
Nodes (35): metadata, MarkdownContent(), MessageContent(), SkillEvidence(), SkillMarkdown(), SkillRevision(), Phase, requirements (+27 more)

### Community 11 - "Analytics and Prediction Playbooks"
Cohesion: 0.07
Nodes (48): AI dashboard objectives and card design, Reviewed dashboard proposals and matching saved evidence, Distinct-order support, directional confidence and lift, Basket composition and product affinity, Compatible-grain explicit-key reconciliation, Cross-source grain and join reconciliation, Complete purchasing-population concentration shares, Customer revenue concentration and dependency (+40 more)

### Community 12 - "Responsive Sidebar Primitives"
Cohesion: 0.06
Nodes (22): Sheet(), SheetClose(), SheetContent(), SheetDescription(), SheetHeader(), SheetTitle(), SheetTrigger(), Sidebar() (+14 more)

### Community 13 - "Report Recovery and Export Tests"
Cohesion: 0.08
Nodes (29): ReportDispatcher, ExportStorage, Graph nodes carry only a run identifier. Bodies live in fenced checkpoints., ReportPolicy, run_report_graph(), body(), fixture, setup() (+21 more)

### Community 14 - "Read-Only SQL Safety Tests"
Cohesion: 0.08
Nodes (39): cases(), matches(), Deterministic synthetic retail data; no real customer information., retail_data(), error(), execute(), Private Cloud Run entrypoint. Deploy with --no-allow-unauthenticated and…, reconcile() (+31 more)

### Community 15 - "Forecast Plan Reader and Controls"
Cohesion: 0.06
Nodes (24): metadata, metadata, startBuild(), ForecastPlans(), create(), download(), narrative(), pickNode() (+16 more)

### Community 16 - "Skill Selection and Snapshot Tests"
Cohesion: 0.10
Nodes (29): fixture_answer(), analytics_examples(), Stable seed IDs let operators add examples without replacing public edits., Import the reviewable, source-controlled pack before any cloud writes., seed_analytics(), seed_examples(), compatible(), export_skill() (+21 more)

### Community 17 - "Static Product Preview Contract"
Cohesion: 0.05
Nodes (44): Versioned chart view, ADR 0005: saved-result dashboards (accepted 2026-10-16), Immutable paginated results, Retained artifact references, ADR 0008 landing and workspace split, Query-aware 307 compatibility redirect, Landing palette and workspace preference isolation, Local evidence-only guided preview (+36 more)

### Community 18 - "Workspace Appearance and Preferences"
Cohesion: 0.09
Nodes (29): Catalog, ModelSettings(), preferenceLabels, sections, template, Card(), CardContent(), CardDescription() (+21 more)

### Community 19 - "Coherent Forecast Planning Contract"
Cohesion: 0.07
Nodes (43): Document, Insert-only metric seeding, Planning fixture execution, Document, Immutable metric lineage, Public executable metric contracts, Structural publication validation, Adaptive coherent planning (+35 more)

### Community 20 - "TypeScript Compiler Configuration"
Cohesion: 0.05
Nodes (42): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+34 more)

### Community 21 - "Operator Maintenance Commands"
Cohesion: 0.10
Nodes (29): check_models(), cleanup_skill_authors(), cli(), dashboard_maintenance(), main(), operator_credentials(), Credentialed CLI only. No administrative endpoint is exposed by FastAPI., Remove only expired, inactive author interviews and their scoped ADK sessions. (+21 more)

### Community 22 - "Dated Local and Hosted Acceptance"
Cohesion: 0.06
Nodes (39): Planning workflow 3 preserves report workflows 1 and 2, Fenced report events, stage checkpoints and workflow versions, Transactional conversation leases and fencing generations, Backend-only named Firestore persistence, Fresh TimesFM forecast and scenario acceptance: 31 checks, Fresh AI dashboard and hierarchical-plan worker acceptance unverified, Persisted SSE event replay without reexecution, Immutable saved-result charts and dashboards (+31 more)

### Community 23 - "Shared Analytical Domain Model"
Cohesion: 0.08
Nodes (36): Allocated Estimate, Analysis Brief, Backtest, Business Metric, Dashboard Build, Dashboard Proposal, Data Profile, Document (+28 more)

### Community 24 - "Worker-First Release Runbook"
Cohesion: 0.07
Nodes (35): Runbook guides authorized operations but is not operation authorization, Validate exact model/location using actual workload identity, Query/instance limits and alerts are not monetary spending caps, Verify exact candidate readiness/digest before explicit traffic promotion, User-specified builder with dedicated source/log bucket and image repository, Dedicated demo project resources; existing workloads excluded, Dedicated workload identities, Deployment Guide (+27 more)

### Community 25 - "Saved Result Evidence and Charts"
Cohesion: 0.09
Nodes (28): SavedCsvDownload(), download(), ResultCard, ResultCard, MetricEvidence(), PinToDashboard(), create(), pin() (+20 more)

### Community 26 - "Metric and Planning Regression Tests"
Cohesion: 0.13
Nodes (28): _insert(), Insert-only packaged definitions. Never called by startup, release or history…, seed_metrics(), MetricAction, MetricDefinition, MetricQuery, MetricWrite, field_validator (+20 more)

### Community 27 - "Public Retail Product Overview"
Cohesion: 0.06
Nodes (33): Per-run Gemini analysis-model snapshot, Pinned model choices captured per task and voice handshake, Google ADK and Gemini, Architecture source-code map, FastAPI backend, BigQuery retail source, CLI-only seed/reset and isolated cloud release helpers, Operator-authenticated cloud preview (+25 more)

### Community 28 - "Frontend HTTP and Stream Recovery"
Cohesion: 0.10
Nodes (21): metadata, metadata, ReportEditDialog(), save(), ReportWorkspace(), download(), SkillAttachments(), load() (+13 more)

### Community 29 - "Public Versioned Skill Contract"
Cohesion: 0.08
Nodes (32): Guest-bound unpublished author recovery and model-free publication authority, Metadata-first discovery with manual attachment priority, Six-hour logical author expiry and explicit scoped cleanup, Atomic reviewed skill publication outside model tools, Guest-scoped author brief, draft and fenced connection generation, Three immutable skill revisions per analytical invocation, Bounded selection followed by analysis-scoped snapshots, Skills (+24 more)

### Community 30 - "Skill Author Concurrency Tests"
Cohesion: 0.14
Nodes (28): asyncio, live(), AuthorDraft, Small document interface with atomic, retry-safe read/modify/write operations., main(), Explicit operator command: uv run python -m scripts.seed_metrics [--cloud]., client(), create() (+20 more)

### Community 31 - "Report Reader and Downloads"
Cohesion: 0.13
Nodes (21): DashboardHeader(), active(), ConversationReports(), ReportRunCard(), cancel(), clarify(), poll(), ResearchPanel() (+13 more)

### Community 32 - "Scoped Cloud Provisioning"
Cohesion: 0.14
Nodes (23): main(), Build with a resource-scoped builder, then deploy as the current operator., configuration(), main(), Prepare or deploy ONLY the private report worker. Foundation/IAM are separate…, ensure_secret(), ensure_service_account(), gcloud() (+15 more)

### Community 33 - "Versioned Metrics and Controlled Compilation"
Cohesion: 0.17
Nodes (23): fixture_plan(), Explicit local-only sample planner. Never used as a Gemini fallback., Approved same-grain target comparison over a frozen revenue definition., target_plan(), catalog_plan(), compile_metric(), metric_router(), MetricScope (+15 more)

### Community 34 - "Conversation Persistence and Recovery"
Cohesion: 0.12
Nodes (16): StaleLease, Repository, test_shared_admission_fitting_profile_replay_and_fencing(), test_fenced_report_adk_sessions_reject_old_worker_and_survive_reset(), setup_run(), test_completion_between_status_reads_is_not_reported_as_interrupted(), test_expired_worker_cannot_append_or_release_successor(), test_fork_keeps_immutable_artifact_references() (+8 more)

### Community 35 - "Shared Job Admission and Leases"
Cohesion: 0.12
Nodes (4): Operation and conservative budget reservation commit in one fenced transaction., ReportRepository, Opt-in hosted forecast/scenario acceptance. Public reports; read-only retail…, run()

### Community 36 - "Interactive Chart Exploration"
Cohesion: 0.16
Nodes (23): categoryColor(), InsightfulChart(), content(), download(), label(), palette, Plot(), Values() (+15 more)

### Community 37 - "Hierarchical Planning and Adjustments"
Cohesion: 0.14
Nodes (16): item_identity(), adjust_plan(), baseline_candidate(), capture_history(), distribute(), evaluate_recipe(), fail(), Pure hierarchical revenue calculations; no model, database or executable inputs. (+8 more)

### Community 38 - "Repository Contribution Guidance"
Cohesion: 0.08
Nodes (25): docs/architecture.md, Authoritative Mermaid with derived Graphify exports, Context7 CLI for current library/service documentation, Dated deployment evidence, docs/deployment-guide.md, CONTEXT.md, Forecast Plan fit budget, Frontend/AGENTS.md (+17 more)

### Community 39 - "Typed Analysis and Visualization"
Cohesion: 0.12
Nodes (23): MetricFormula, MetricRef, ChartMeasure, ConversationCreate, field_validator, StrictModel, TurnCreate, DashboardCardEdit (+15 more)

### Community 40 - "Shadcn Component Configuration"
Cohesion: 0.09
Nodes (22): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+14 more)

### Community 41 - "Evidence-Backed Report Workflow"
Cohesion: 0.16
Nodes (7): ReportEngine, ForecastInputs, model_validator, ReportDraft, ReportPlan, ReportSection, test_report_writer_cannot_invent_numbers_or_references()

### Community 42 - "Frontend Development Dependencies"
Cohesion: 0.10
Nodes (21): babel-plugin-react-compiler, eslint, eslint-config-next, devDependencies, babel-plugin-react-compiler, eslint, eslint-config-next, shadcn (+13 more)

### Community 43 - "Static Landing Product Tour"
Cohesion: 0.15
Nodes (16): capabilities, faqs, metadata, OpenQuerylane(), LandingMobileNavigation(), HeroProduct(), money(), RevenueIllustration() (+8 more)

### Community 44 - "Typed Fusion Regression Tests"
Cohesion: 0.24
Nodes (18): _arrow_bytes(), fuse(), _identifier(), Any, A typed plan compiler; no model-supplied SQL or Python reaches DuckDB., _worker(), Calculation, Projection (+10 more)

### Community 46 - "Navigation and Release Preservation"
Cohesion: 0.12
Nodes (19): Shared desktop/mobile decorative Target and TrendingUp navigation icons, Wait for sheet transitions before settled layout and contrast assertions, Deterministic Parquet generation and fenced insert-only upload, Navigation icon deployment: frontend 00019-gvr; API and worker unchanged, Lucide Target for Business metrics and TrendingUp for Forecast plans, Versioned sales facts and retail_timeseries import-ready profile, Retained opening-fade observations and passing settled navigation rechecks, Enabled and verified TimesFM runtime gates (+11 more)

### Community 47 - "Evidence-Backed Report Contracts"
Cohesion: 0.20
Nodes (14): AnalysisTask, EvidenceClaim, field_validator, Bounded contracts shared by the report harness, API, renderer, and numerical…, ReportClarification, ReportCreate, ReportMutation, ReportPatch (+6 more)

### Community 48 - "Frontend Runtime Dependencies"
Cohesion: 0.11
Nodes (19): class-variance-authority, clsx, dependencies, class-variance-authority, clsx, radix-ui, react, react-dom (+11 more)

### Community 49 - "Managed Forecast Comparison Policy"
Cohesion: 0.18
Nodes (18): Deterministic verified claims and grouped-ratio policy v2, Single fenced reservation of backtest/final jobs, tokens, bytes and fits, Common three-fold full-horizon measured method selection, Workflow 2 frozen policy and retained workflow 1 behavior, Conservative reserved seconds, token estimates and failed-work accounting, Fold-compatible shared context in multiples of 32, minimum 64, report_forecasting.py admission, comparison checkpoints and selection, Complete immutable pages and exact validated-series hash (+10 more)

### Community 50 - "Local Setup and Verification"
Cohesion: 0.15
Nodes (17): Composer query source selection, Header Sources sheet and schema inspection, History-focused workspace sidebar, Single New exploration reset to /app, Schema request-generation guard, Separate operator CLI, local ADC and workload ADC identities, Sidebar release checks use saved history and schema reads, Memory-only operator preview tokens expire; restart to refresh (+9 more)

### Community 51 - "Durable Dashboard and Forecast Execution"
Cohesion: 0.18
Nodes (6): chart_state(), PlanningEngine, DashboardBlueprint, model_validator, NeedsInput, Exception

### Community 52 - "Durable Advanced Report Contract"
Cohesion: 0.21
Nodes (14): Three-origin full-horizon backtests and baseline/domain gates, Transactional outbox, private OIDC worker and checkpoint reuse, Workflow 2 with enabled verified hosted TimesFM and disabled local defaults, Captured report source, model, completed context, schema and skill revisions, Visitor-supplied complete baseline and alternative driver paths, Same saved document drives web, PDF, Word and full CSV ZIP, Public immutable report versions and prediction caveats, Independent report lease and initiating-guest controls (+6 more)

### Community 53 - "Public API Composition"
Cohesion: 0.19
Nodes (13): saved_rows(), create_app(), main(), Local-only report smoke; --gemini opts into billable model calls, never cloud…, run(), client(), fixture, test_production_cannot_start_with_fixture_backends() (+5 more)

### Community 54 - "AI Retry and Failure Tests"
Cohesion: 0.26
Nodes (13): ai_service(), live_harness(), parametrize, Fault injection at the real structured-call and Live transport seams., test_analysis_finish_storage_failure_still_clears_local_task_registry(), test_expected_voice_tool_failure_is_recoverable_without_reexecuting_query(), test_long_retry_after_does_not_retry_earlier_than_provider_requests(), test_metric_scope_avoids_sdk_map_schema_conversion_but_validates_locally() (+5 more)

### Community 55 - "Skills Library Interface"
Cohesion: 0.18
Nodes (8): metadata, contentOf(), SkillsWorkspace(), editSkill(), exportFile(), importFile(), openEditor(), sourceLabel()

### Community 56 - "Reviewed Coherent Planning"
Cohesion: 0.18
Nodes (13): Allocated leaves and management adjustments are not independently validated predictions, Conditional driver and promotion scenarios, Forecast validation and uncertainty, Separate versioned management assumptions preserve statistical predictions, Three full-horizon chronological-fold numerical method selection, Coherent aggregate forecast recipe with shared company total, Explicit full-horizon baseline and alternative future driver paths, Forecast Plans 128-fit profile; reports remain at 64 fits (+5 more)

### Community 57 - "Public API Regression Tests"
Cohesion: 0.28
Nodes (12): guest(), parametrize, A worker may finish after the event query but before the status read., test_analysis_replay_fork_and_provenance(), test_guest_scope_and_no_administrative_routes(), test_origin_and_payload_validation(), test_stream_drains_events_committed_between_poll_and_terminal_read(), test_voice_does_not_fake_model_in_fixture_mode() (+4 more)

### Community 58 - "Chart Tooltip and Legend Primitives"
Cohesion: 0.21
Nodes (11): ChartConfig, ChartContainer(), ChartContext, ChartContextProps, ChartLegendContent(), ChartTooltipContent(), getPayloadConfigFromPayload(), INITIAL_DIMENSION (+3 more)

### Community 59 - "Saved Evidence and Retention"
Cohesion: 0.17
Nodes (12): Independent dashboard/report artifact-retention references, Title-specific keyboard-scrollable table regions with native captions, Saved-result chart service with full-scope summaries and 2000 plotted observations, Bounded isolated dashboard image/PDF renderer and full CSV/JSON exports, Public dashboard parent revisions, idempotent requests and immutable artifact references, Operator maintenance fence and reference-aware history reset, Explicit fenced reset and expiry purge preserve referenced artifacts, 45 monthly and 1369 daily values with exact zero and full CSV totals (+4 more)

### Community 60 - "Dashboard Editing and Sharing"
Cohesion: 0.24
Nodes (6): metadata, DashboardWorkspace(), refreshRemoved(), restoreItem(), setMode(), unpin()

### Community 61 - "Versioned Metrics and Controlled Compilation"
Cohesion: 0.33
Nodes (3): matched_metrics(), Metrics, Reserve once before execution; replay saved pages, never repeat an uncertain…

### Community 62 - "Frontend Package Scripts"
Cohesion: 0.20
Nodes (9): name, private, scripts, build, dev, lint, start, test (+1 more)

### Community 63 - "Retry and Recovery Boundaries"
Cohesion: 0.22
Nodes (9): Retry and recovery policy, Disabled TimesFM same-job recovery and statistical fallback, Permanent access/request failures fail fast without substitution, Fenced report redelivery with shared budgets and three-delivery cap, Bounded persisted-cursor SSE replay without query restart, Thread-held cancellation survives delayed query responses, At-most-two structured model attempts with bounded jitter, Expected analyst tool errors remain nonfatal (+1 more)

### Community 64 - "Customer Cohorts and Returns"
Cohesion: 0.36
Nodes (8): Signup cohorts and first observed purchase cohorts, Customer cohorts and repeat purchasing, Equally mature customer observation windows, Repeat purchase and activity retention denominators, Validated bounded-rate or monetary forecast domain, Explicit return-rate target and denominator, Returns and rate prediction readiness, Refund latency and cohort maturity

### Community 65 - "Data Quality and Fusion"
Cohesion: 0.32
Nodes (8): Data quality and analysis readiness, Calendar spine, unknown gaps and observed zeros, Join-key compatibility, coverage and fan-out, Independent totals reconciliation, Explicit fan-out and incomplete-input rejection, ADR: Typed bounded cross-source fusion, Gemini relationship-key and business-assumption hypotheses, Trusted compiler for typed relational fusion

### Community 66 - "Seasonality and Backtesting"
Cohesion: 0.32
Nodes (8): Dense retail calendar at consistent time grain, Shifted target-derived rolling predictors, Observed peaks with causal limitations, Calendar trends and retail seasonality, Baseline comparison and candidate promotion, Forecast validation and uncertainty, Chronological rolling-origin backtests, Supported prediction intervals and publication outcome

### Community 67 - "Backend Runtime and Verification"
Cohesion: 0.25
Nodes (7): Default local plan and opt-in bounded billable probe, Named Firestore and private report bucket, TimesFM 3.0 Preview comparison over saved evidence, Private report worker app.report_worker:app, Public API for chat, voice and shared libraries, Separate routine releases, skill seeding and analytical upload, Saved-artifact-only dashboard download contract

### Community 68 - "Firestore Contention Regression Tests"
Cohesion: 0.43
Nodes (7): firestore_store(), Exercise real SDK transaction decoration with a read-phase contention fault., test_business_validation_errors_are_not_retried_or_disguised(), test_exhausted_sdk_commit_budget_is_not_multiplied(), test_read_abort_retries_then_reports_conversation_busy(), test_read_retries_are_bounded_and_exhaustion_is_a_busy_response(), test_read_retry_commits_mutation_only_once()

### Community 69 - "Skill Selection and Snapshot Tests"
Cohesion: 0.43
Nodes (7): create(), guest(), parametrize, test_attachments_busy_rules_forks_and_deleted_skill(), test_content_validation(), test_import_export_roundtrip_is_preview_only(), test_public_crud_revisions_conflicts_and_restore()

### Community 70 - "Managed TimesFM Architecture Decision"
Cohesion: 0.29
Nodes (7): Disabled until managed and actual-worker access verification, ADR 0009: Managed TimesFM comparison, Fenced immutable input/configuration and operation checkpoints, Fixed parameterized managed TimesFM 3.0 Preview adapter, Agent relevance and priority, deterministic numerical selection, Same-method scenarios in separate artifacts, timesfm.py fixed queries, job identity and cancellation

### Community 71 - "Retail Data Publication Workflow"
Cohesion: 0.29
Nodes (7): Original demo retail schema (seed evidence 2026-10-16), Fenced insert-only cloud publication, Independent bundle reconciliation, Expanded retail column dictionary (retail-timeseries-v1), Stable full-window extend workflow, Deterministic streaming Parquet bundle, Additional timeseries source profile

### Community 72 - "Competition Demonstration Workflow"
Cohesion: 0.29
Nodes (7): Cross-source actual-versus-target exploration, Five-minute competition demonstration, Landing previews and direct workspace entry, Production rehearsal and backup recording, Public conversation sharing and forks, Spoken analysis and interruption, Warehouse question with SQL evidence

### Community 73 - "Conditional Driver Scenario Playbook"
Cohesion: 0.33
Nodes (6): Conditional predictions with historical driver support, Conditional driver and promotion scenarios playbook, Visitor-supplied complete future driver paths, Optional available TimesFM with complete covariate context, Shared-method baseline and alternative scenario artifacts, Chronological scenario validation and extrapolation rejection

### Community 74 - "Revenue Forecast Playbook"
Cohesion: 0.33
Nodes (6): Advanced Analysis controlled forecast fitting, Common chronological scores choose statistical or managed candidate, Complete series and actual latest-observation cutoff, Revenue and demand forecasting playbook, Observed-versus-predicted values and retained method evidence, Five-percent MAE improvement and majority-fold promotion

### Community 75 - "Named Firestore ADK Persistence"
Cohesion: 0.47
Nodes (6): Separate skill author session lease collection, Bounded fresh-transaction retries for read aborts, Custom Firestore ADK session adapter, ADR: ADK persistence in named Firestore, Loaded-session revision and conversation lease fencing, Terminal event stream sequence draining

### Community 76 - "Original Retail Source Schema"
Cohesion: 0.33
Nodes (6): Original PostgreSQL retail.customer_profiles, Original BigQuery order_items, Original BigQuery orders, Original BigQuery products, Original PostgreSQL retail.regional_targets, Original BigQuery returns

### Community 77 - "Expanded Retail Column Dictionary"
Cohesion: 0.40
Nodes (6): Dense daily calendar date spine, Time-series customer_profiles, Time-series sales_order_items, Time-series sales_orders, Time-series sales_returns, Full-month store targets

### Community 78 - "Public Reports Library"
Cohesion: 0.40
Nodes (4): metadata, ReportsLibrary(), change(), restore()

### Community 79 - "Reviewed Dashboard Publication Decision"
Cohesion: 0.40
Nodes (5): Document, Proposal retention, Reviewable dashboard generation, Reviewed rebase and conditional Undo, Shared durable execution

### Community 80 - "Immutable Chart Presentation Contract"
Cohesion: 0.40
Nodes (5): Deterministic bounded chart sampling, Saved-artifact chart-data endpoint, Deterministic truthful chart insights, Full saved-result CSV export, Version-2 VisualizationSpec metadata

### Community 81 - "Published Dashboard Views and Retention"
Cohesion: 0.40
Nodes (5): Active and recoverable artifact retention, Canonical public dashboard sharing, Public revision-checked editing, Published saved chart views, Revision-checked whole-dashboard exports

### Community 82 - "Frontend Contribution Guidance"
Cohesion: 0.40
Nodes (5): Frontend contributor instructions, Guest-scoped report clarification and skill draft recovery, Installed Next.js version guides, Browser preferences and reduced-motion feedback, Explicit saved chart publication and revision checks

### Community 83 - "Saved Dashboard View Tests"
Cohesion: 0.50
Nodes (3): { initialChartView, describeChartView }, load(), reader()

### Community 84 - "Planning Review and Retry Tests"
Cohesion: 0.50
Nodes (3): { dashboardChanges }, load(), require

### Community 85 - "Prediction Evidence Rendering Tests"
Cohesion: 0.40
Nodes (4): base, compiledModule, render(), require

### Community 86 - "Sales Change Contribution Playbook"
Cohesion: 0.50
Nodes (4): Observed concentrations versus causal explanations, Sales change and segment contributions, Reconciled segment change contributions, Exact order-volume and AOV revenue bridge

### Community 87 - "Comparable Store Performance Playbook"
Cohesion: 0.67
Nodes (4): Comparable-store and target performance, Comparable-store eligibility, Store and regional target join grain, Weighted attainment and reconciled target gaps

### Community 88 - "Weighted Retail KPI Definitions"
Cohesion: 0.67
Nodes (4): Completed-order merchandise revenue, Retail KPI definitions and weighted ratios, Overall AOV from revenue and distinct orders, Weighted margin rate and additive reconciliation

### Community 89 - "Marketing Associations and Scenarios"
Cohesion: 0.67
Nodes (4): Attributed revenue per campaign spend, Compatible campaign and period aggregation, Campaign and promotion performance, Validated future promotion scenario

### Community 90 - "Merchandise Margin and Refunds"
Cohesion: 0.67
Nodes (4): Historical line merchandise revenue and cost, Merchandise margin and returns-adjusted performance, Order-cohort refund and returned-cost adjustment, Signed margin and return-cohort maturity

### Community 92 - "Saved Dashboard Smoke Tests"
Cohesion: 0.67
Nodes (3): main(), Opt-in API check using existing immutable artifacts; never runs an analysis or…, run()

### Community 93 - "Hosted Report Acceptance Harness"
Cohesion: 0.67
Nodes (3): main(), Opt-in hosted report acceptance; creates public verification…, run()

### Community 95 - "Public Skill Versioning Decision"
Cohesion: 0.50
Nodes (4): ADR 0004: public versioned skills (accepted 2026-10-15), Bounded metadata skill selector, Public Markdown playbooks, Analysis-scoped immutable skill snapshots

### Community 96 - "Public Report Evidence Boundary"
Cohesion: 0.50
Nodes (4): ADR 0007: public report evidence (accepted 2026-10-17), Requester-only in-memory Search panel, Verified numerical claims, Distinct writer and semantic reviewer

### Community 97 - "Immutable Saved-Artifact Dashboard Cards"
Cohesion: 0.50
Nodes (4): Validated ChartViewState, Fenced reference-aware history maintenance, Revision-checked idempotent dashboard mutations, Immutable saved-artifact dashboard cards

### Community 98 - "Managed Forecast Comparison Policy"
Cohesion: 0.67
Nodes (4): Both enablement flags and actual-worker attestation required, TimesFM hosted enablement after 17 October worker-identity verification, Parameterized inputs, output shapes, recovery, billing and private-worker access, Actual worker identity probe through temporary Cloud Run execution

### Community 104 - "Public Anonymous Workspace Decision"
Cohesion: 1.00
Nodes (3): Anonymous guest token attribution, quotas and cancellation, Public shared conversations, ADR: Public workspace without accounts

### Community 105 - "Immutable Durable Report Decision"
Cohesion: 0.67
Nodes (3): ADK App / Runner / Workflow, Independent durable report execution, ADR 0006: durable versioned reports (accepted 2026-10-17)

### Community 111 - "Scoped Cloud Build Workflow"
Cohesion: 0.67
Nodes (3): Cloud Build Docker build step, Cloud Build Docker push step, Dedicated GCS-only build logs

## Knowledge Gaps
- **242 isolated node(s):** `agentic-bi-backend`, `$schema`, `style`, `rsc`, `tsx` (+237 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **30 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Public landing page guide` connect `Static Product Preview Contract` to `Worker-First Release Runbook`, `Public Versioned Skill Contract`, `Durable Advanced Report Contract`, `Controlled Analytics Architecture`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Why does `Canonical workspace link construction` connect `Static Product Preview Contract` to `Report Reader and Downloads`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Why does `AppError` connect `Application Error Contracts` to `TimesFM Validation and Recovery`, `Bounded Runtime Configuration`, `Retail Generation and Upload`, `Transactional Storage and Persistence`, `Saved Chart Data Presentation`, `Report Recovery and Export Tests`, `Read-Only SQL Safety Tests`, `Skill Selection and Snapshot Tests`, `Operator Maintenance Commands`, `Metric and Planning Regression Tests`, `Skill Author Concurrency Tests`, `Versioned Metrics and Controlled Compilation`, `Conversation Persistence and Recovery`, `Shared Job Admission and Leases`, `Hierarchical Planning and Adjustments`, `Evidence-Backed Report Workflow`, `Typed Fusion Regression Tests`, `Reviewed Skill Draft Publication`, `Evidence-Backed Report Contracts`, `Durable Dashboard and Forecast Execution`, `Public API Composition`, `AI Retry and Failure Tests`, `Versioned Metrics and Controlled Compilation`, `Firestore Contention Regression Tests`?**
  _High betweenness centrality (0.066) - this node is a cross-community bridge._
- **Are the 88 inferred relationships involving `AppError` (e.g. with `AI` and `AnalysisService`) actually correct?**
  _`AppError` has 88 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `Settings` (e.g. with `Connectors` and `create_app()`) actually correct?**
  _`Settings` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `MemoryStore` (e.g. with `test_every_chart_family_and_mixed_units_can_render()` and `test_complex_plan_uses_json_mode_and_still_validates_locally()`) actually correct?**
  _`MemoryStore` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `Connectors` (e.g. with `Settings` and `AppError`) actually correct?**
  _`Connectors` has 14 INFERRED edges - model-reasoned connections that need verification._
## Extraction Integrity and Scope

Generated with Graphify 0.9.51. All 68 detected documents have semantic nodes: 64 cached and 4 refreshed by one host-session agent. Code extraction is local AST analysis. No separate model API, analytical database or deployment was invoked.

- Graphify tree-sitter reported potentially partial extraction of Frontend/src/components/workspace.tsx at line 1127; 13 symbols extracted.
- Raw external import references can have no matching project node; unresolved endpoints are reported, not fabricated.
- The default undirected simple graph can combine multiple relationships between an endpoint pair; diagnostic counts retain this limitation.
- Host semantic-token usage is unavailable, not zero.

Raw extraction contains **916 unresolved endpoint references**, **0 missing endpoint fields**, **0 self-loops** and **587 same-endpoint relationships collapsed** by the default undirected graph. Many unresolved references are external imports; absent entities are not invented. These are extraction limitations rather than runtime defects.

The graph includes history-focused workspace navigation, header source inspection, decorative library-navigation icons, all 24 packaged playbooks, managed TimesFM comparison and static previews. Dated release records remain separate from implementation contracts. [VALIDATION.json](VALIDATION.json) records source hashes; [the graph guide](../docs/graphify/README.md) explains maintenance.
