# Graph Report - 6. Google AI Builder Cup - Agentic BI  (2026-10-18)

## Corpus Check
- 276 files · ~208,899 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 2256 nodes · 6197 edges · 127 communities (99 shown, 28 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 347 edges (avg confidence: 0.91)
- Token cost: 0 separate model-API tokens; host-session semantic input/output token usage is unavailable (not measured as zero).

## Graph Freshness
- Built from commit: `e4af083a`
- Working-tree snapshot: compare per-file SHA-256 hashes in VALIDATION.json as well as the base commit.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- TimesFM Validation and Recovery
- Transactional Storage and Persistence
- Voice and Text Workspace
- Workspace Appearance and Preferences
- Frontend HTTP and Stream Recovery
- Evidence-Backed Report Workflow
- Saved Result Evidence and Charts
- Saved Chart Data Presentation
- Bounded Runtime Configuration
- Fenced Retail Data Publication
- Skill Selection and Snapshot Tests
- Application Architecture and Boundaries
- Report Reader and Downloads
- Static Product Preview Contract
- Responsive Sidebar Primitives
- Application Error Contracts
- Forecast Plan Reader and Controls
- TypeScript Compiler Configuration
- Public API Composition
- Dashboard Editing and Sharing
- Workspacepath Components
- Scoped Cloud Provisioning
- Report Recovery and Export Tests
- Conversation Persistence and Recovery
- Shared Job Admission and Leases
- Shared Job Admission and Leases
- Fenced ADK Session Persistence
- Typed Analysis and Visualization
- Skill Author Concurrency Tests
- Shared Analytical Domain Model
- Metric and Planning Regression Tests
- Shadcn Component Configuration
- Public API Composition
- Frontend Development Dependencies
- Operator Maintenance Commands
- Managed Forecast Comparison Policy
- Reviewed Skill Draft Publication
- Frontend Runtime Dependencies
- Dated Local and Hosted Acceptance
- Versioned Metrics and Controlled Compilation
- Evidence-Backed Report Workflow
- Public Metric Definition Contract
- Coherent Forecast Planning Contract
- Worker-First Release Runbook
- Coherent Hierarchical Revenue Planning
- Durable Advanced Report Contract
- Fenced Reference-Aware Maintenance
- Bounded ADK Application Harness
- Skills Library Interface
- Cases Components
- Public API Regression Tests
- Retry and Recovery Boundaries
- Application Architecture and Boundaries
- Public Retail Product Overview
- Chart Tooltip and Legend Primitives
- Packaged Metric Definitions
- Durable Dashboard and Forecast Execution
- Analytics and Prediction Playbooks
- Durable Task Dispatch and Recovery
- Reviewed AI Dashboard Contract
- Dashboard Editing and Sharing
- Smoke Dashboards
- Frontend Package Scripts
- Versioned Metrics and Controlled Compilation
- Customer Cohorts and Returns
- Data Quality and Fusion
- Seasonality and Backtesting
- Backend Runtime and Verification
- Repository Contribution Guidance
- Retail Data Publication Workflow
- Competition Demonstration Workflow
- Conditional Driver Scenario Playbook
- Revenue Forecast Playbook
- Named Firestore ADK Persistence
- Original Retail Source Schema
- Expanded Retail Column Dictionary
- Reportslibrary Components
- Evidence-Backed Report Contracts
- Managed TimesFM Architecture Decision
- Immutable Chart Presentation Contract
- Published Dashboard Views and Retention
- Frontend Contribution Guidance
- Saved Dashboard View Tests
- Planning Review and Retry Tests
- Sales Change Contribution Playbook
- Comparable Store Performance Playbook
- Weighted Retail KPI Definitions
- Marketing Associations and Scenarios
- Merchandise Margin and Refunds
- Smoke Reports Deployed
- Public Skill Versioning Decision
- Public Report Evidence Boundary
- Immutable Saved-Artifact Dashboard Cards
- Browser PCM Audio Worklet
- Chart Formatting Regression Tests
- Prediction Evidence Rendering Tests
- Versioned Skill Catalog
- Public Anonymous Workspace Decision
- Immutable Durable Report Decision
- Runtime Backend Configuration Route
- Frontend Health Route
- Safe Markdown Rendering Tests
- Accessible Table Regression Tests
- Scoped Cloud Build Workflow
- Local Social Preview Asset
- Init Components
- Cn Dependency
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
- Retail Data Publication Workflow
- BeUI License Attribution
- Backend Dependency Manifest

## God Nodes (most connected - your core abstractions)
1. `AppError` - 239 edges
2. `Settings` - 126 edges
3. `MemoryStore` - 90 edges
4. `Connectors` - 74 edges
5. `Repository` - 65 edges
6. `create_app()` - 64 edges
7. `Document` - 64 edges
8. `StrictModel` - 59 edges
9. `FirestoreSessionService` - 55 edges
10. `AI` - 49 edges

## Surprising Connections (you probably didn't know these)
- `Atomic dashboard publication` --semantically_similar_to--> `Skill Publication`  [INFERRED] [semantically similar]
  docs/ai-dashboard-builder.md → CONTEXT.md
- `Join-key compatibility, coverage and fan-out` --semantically_similar_to--> `Explicit fan-out and incomplete-input rejection`  [INFERRED] [semantically similar]
  Backend/app/skill_library/analytics-data-quality.md → docs/adr/0003-bounded-cross-source-fusion.md
- `Shared-method baseline and alternative scenario artifacts` --conceptually_related_to--> `Separate immutable scenario with same-method baseline and alternative`  [INFERRED]
  Backend/app/skill_library/prediction-driver-scenarios.md → docs/timesfm.md
- `Common chronological scores choose statistical or managed candidate` --conceptually_related_to--> `Common three-fold full-horizon measured method selection`  [INFERRED]
  Backend/app/skill_library/prediction-sales-forecast.md → docs/timesfm.md
- `foundation()` --calls--> `operator_credentials()`  [INFERRED]
  infra/provision_reports.py → Backend/app/admin.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Reviewed revision-safe dashboard publication** — docs_ai_dashboard_builder_atomic_dashboard_publication, docs_ai_dashboard_builder_revision_aware_rebase, docs_ai_dashboard_builder_conditional_undo, docs_ai_dashboard_builder_guest_owned_proposal_expiry [EXTRACTED 1.00]
- **Immutable controlled metric execution** — docs_business_metrics_closed_typed_metric_formula, docs_business_metrics_application_owned_grain_compiler, docs_business_metrics_immutable_dependency_snapshots, docs_business_metrics_canonical_forecast_value_reconciliation [EXTRACTED 1.00]
- **Validated coherent hierarchy recipe** — docs_forecast_plans_aggregate_candidate_selection, docs_forecast_plans_training_only_leaf_allocation, docs_forecast_plans_cent_exact_monetary_reconciliation, docs_forecast_plans_level_balanced_promotion_gate, docs_forecast_plans_coherent_baseline_fallback [EXTRACTED 1.00]
- **Static saved-evidence previews retain analytical and publication boundaries** — docs_landing_page_guided_preview, docs_landing_page_forecast_fixture, docs_landing_page_scenario_fixture, docs_landing_page_captured_version_links [EXTRACTED 1.00]
- **Fenced admission, stable jobs, persistent cancellation and conservative billing** — docs_timesfm_atomic_admission, docs_timesfm_stable_jobs, docs_timesfm_persistent_cancellation, docs_timesfm_conservative_billing [EXTRACTED 1.00]
- **Frozen saved input, deterministic selection, separate scenarios and immutable exports** — docs_timesfm_frozen_saved_input, docs_timesfm_candidate_selection, docs_timesfm_separate_scenario, docs_timesfm_saved_export_evidence [EXTRACTED 1.00]

## Communities (127 total, 28 thin omitted)

### Community 0 - "TimesFM Validation and Recovery"
Cohesion: 0.07
Nodes (67): item_identity(), plan_artifact(), Planning, choose(), compare(), eligible(), intervals(), Application-owned candidate selection over a frozen saved series. (+59 more)

### Community 1 - "Transactional Storage and Persistence"
Cohesion: 0.06
Nodes (54): ChartViewState, DashboardAction, DashboardCreate, DashboardItemPatch, DashboardLayout, DashboardPatch, DashboardPin, DashboardRequest (+46 more)

### Community 2 - "Voice and Text Workspace"
Cohesion: 0.04
Nodes (64): body, heading, metadata, mono, metadata, AppearanceSync(), AppProviders(), AnalysisProgress() (+56 more)

### Community 3 - "Workspace Appearance and Preferences"
Cohesion: 0.07
Nodes (53): formats, Catalog, ModelSettings(), preferenceLabels, sections, SkillMarkdown(), Phase, requirements (+45 more)

### Community 4 - "Frontend HTTP and Stream Recovery"
Cohesion: 0.05
Nodes (49): metadata, metadata, metadata, DashboardBuilder(), JobControls(), send(), ResultCard, SavedArtifactPreview() (+41 more)

### Community 5 - "Evidence-Backed Report Workflow"
Cohesion: 0.08
Nodes (51): fixture_answer(), fixture_plan(), Explicit local-only sample planner. Never used as a Gemini fallback., AnalysisService, next_date(), normalized_spec(), Bounded, deterministic presentation of immutable result pages. No SQL or model…, Called once when saving a new artifact; historical documents remain immutable. (+43 more)

### Community 6 - "Saved Result Evidence and Charts"
Cohesion: 0.06
Nodes (56): categoryColor(), InsightfulChart(), content(), download(), label(), palette, Plot(), Values() (+48 more)

### Community 7 - "Saved Chart Data Presentation"
Cohesion: 0.08
Nodes (61): change(), csv_cell(), csv_line(), date_value(), metadata(), number(), present(), Shared indices preserve extrema for all series, endpoints, and null boundaries. (+53 more)

### Community 8 - "Bounded Runtime Configuration"
Cohesion: 0.07
Nodes (29): AI, Settings, Connectors, ExportStorage, test_cancellation_failure_still_releases_conversation(), test_result_survives_interpreter_outage_and_reconnect(), test_transient_model_failure_retried_once_only(), test_unknown_cancellation_does_not_claim_database_completion() (+21 more)

### Community 9 - "Fenced Retail Data Publication"
Cohesion: 0.08
Nodes (44): demand(), generate(), money(), promotion_window(), Path, Deterministic, bounded-memory synthetic retail history; never contacts a…, read_manifest(), record_hash() (+36 more)

### Community 10 - "Skill Selection and Snapshot Tests"
Cohesion: 0.09
Nodes (37): analytics_examples(), Stable seed IDs let operators add examples without replacing public edits., Import the reviewable, source-controlled pack before any cloud writes., seed_analytics(), seed_examples(), compatible(), export_skill(), import_skill() (+29 more)

### Community 11 - "Application Architecture and Boundaries"
Cohesion: 0.05
Nodes (51): Document, Immutable metric lineage, Public executable metric contracts, Structural publication validation, Backend-only named Firestore, Controlled analysis lifecycle, Conversation lease fencing, Dated release evidence (+43 more)

### Community 12 - "Report Reader and Downloads"
Cohesion: 0.08
Nodes (32): metadata, metadata, MarkdownContent(), MessageContent(), active(), ConversationReports(), ReportRunCard(), cancel() (+24 more)

### Community 13 - "Static Product Preview Contract"
Cohesion: 0.04
Nodes (49): Versioned chart view, ADR 0005: saved-result dashboards (accepted 2026-10-16), Immutable paginated results, Retained artifact references, ADR 0008 landing and workspace split, Query-aware 307 compatibility redirect, Landing palette and workspace preference isolation, Local evidence-only guided preview (+41 more)

### Community 14 - "Responsive Sidebar Primitives"
Cohesion: 0.06
Nodes (22): Sheet(), SheetClose(), SheetContent(), SheetDescription(), SheetHeader(), SheetTitle(), SheetTrigger(), Sidebar() (+14 more)

### Community 15 - "Application Error Contracts"
Cohesion: 0.09
Nodes (34): json_value(), Any, AppError, Exception, Deterministic synthetic retail data; no real customer information., retail_data(), Preserve compiled definitions when forecasts require controlled feature…, verify_forecast_values() (+26 more)

### Community 16 - "Forecast Plan Reader and Controls"
Cohesion: 0.06
Nodes (24): metadata, metadata, startBuild(), ForecastPlans(), create(), download(), narrative(), pickNode() (+16 more)

### Community 17 - "TypeScript Compiler Configuration"
Cohesion: 0.05
Nodes (42): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+34 more)

### Community 18 - "Public API Composition"
Cohesion: 0.11
Nodes (22): Durable ADK session adapter with ordered events and fenced state writes., get_settings(), model_failure(), Public model failures and one bounded retry policy, never a tool replay policy., live(), Private Cloud Run entrypoint. Deploy with --no-allow-unauthenticated and…, check_lease(), author_router() (+14 more)

### Community 19 - "Dashboard Editing and Sharing"
Cohesion: 0.10
Nodes (26): metadata, DashboardDownload(), download(), DashboardShare(), show(), DashboardEditor(), useDashboardMutation(), ResultCard (+18 more)

### Community 20 - "Workspacepath Components"
Cohesion: 0.09
Nodes (22): metadata, capabilities, faqs, metadata, OpenQuerylane(), DashboardWidget(), LandingMobileNavigation(), HeroProduct() (+14 more)

### Community 21 - "Scoped Cloud Provisioning"
Cohesion: 0.14
Nodes (23): main(), Build with a resource-scoped builder, then deploy as the current operator., configuration(), main(), Prepare or deploy ONLY the private report worker. Foundation/IAM are separate…, ensure_secret(), ensure_service_account(), gcloud() (+15 more)

### Community 22 - "Report Recovery and Export Tests"
Cohesion: 0.17
Nodes (28): ReportClarification, factual_claims(), Claims are computed on the full saved selection, never the chart preview., body(), parametrize, sample_artifact(), setup(), started() (+20 more)

### Community 23 - "Conversation Persistence and Recovery"
Cohesion: 0.11
Nodes (19): Repository, ai_service(), live_harness(), parametrize, Fault injection at the real structured-call and Live transport seams., test_analysis_finish_storage_failure_still_clears_local_task_registry(), test_cancel_then_forget_during_bigquery_dry_run_prevents_late_submission(), test_expected_voice_tool_failure_is_recoverable_without_reexecuting_query() (+11 more)

### Community 24 - "Shared Job Admission and Leases"
Cohesion: 0.14
Nodes (18): check_maintenance(), resolve_text_model(), field_validator, Bounded contracts shared by the report harness, API, renderer, and numerical…, ReportCreate, ReportMutation, ReportPatch, ReportRevisionCreate (+10 more)

### Community 25 - "Shared Job Admission and Leases"
Cohesion: 0.12
Nodes (4): Operation and conservative budget reservation commit in one fenced transaction., ReportRepository, Opt-in hosted forecast/scenario acceptance. Public reports; read-only retail…, run()

### Community 26 - "Fenced ADK Session Persistence"
Cohesion: 0.15
Nodes (17): FirestoreSessionService, StaleLease, test_raw_audio_is_not_persisted(), test_recent_session_context_uses_newest_events(), setup_run(), test_completion_between_status_reads_is_not_reported_as_interrupted(), test_expired_worker_cannot_append_or_release_successor(), test_fork_keeps_immutable_artifact_references() (+9 more)

### Community 27 - "Typed Analysis and Visualization"
Cohesion: 0.13
Nodes (24): artifact_summary(), MetricRef, ChartMeasure, StrictModel, DashboardCardEdit, DashboardQuestion, PlanAdjustment, PlanningAction (+16 more)

### Community 28 - "Skill Author Concurrency Tests"
Cohesion: 0.20
Nodes (23): asyncio, AuthorDraft, client(), create(), guest(), prepared(), fixture, parametrize (+15 more)

### Community 29 - "Shared Analytical Domain Model"
Cohesion: 0.11
Nodes (25): Allocated Estimate, Analysis Brief, Backtest, Business Metric, Dashboard Build, Dashboard Proposal, Data Profile, Document (+17 more)

### Community 30 - "Metric and Planning Regression Tests"
Cohesion: 0.17
Nodes (20): MetricQuery, GeneratorConfig, bundle(), coherent(), library(), plan_fixture(), fixture, parametrize (+12 more)

### Community 31 - "Shadcn Component Configuration"
Cohesion: 0.09
Nodes (22): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+14 more)

### Community 32 - "Public API Composition"
Cohesion: 0.11
Nodes (20): saved_rows(), create_app(), metric_router(), field_validator, TurnCreate, skill_router(), main(), Local-only report smoke; --gemini opts into billable model calls, never cloud… (+12 more)

### Community 33 - "Frontend Development Dependencies"
Cohesion: 0.10
Nodes (21): babel-plugin-react-compiler, eslint, eslint-config-next, devDependencies, babel-plugin-react-compiler, eslint, eslint-config-next, shadcn (+13 more)

### Community 34 - "Operator Maintenance Commands"
Cohesion: 0.21
Nodes (18): check_models(), cleanup_skill_authors(), cli(), dashboard_maintenance(), index_schema(), main(), operator_credentials(), Credentialed CLI only. No administrative endpoint is exposed by FastAPI. (+10 more)

### Community 35 - "Managed Forecast Comparison Policy"
Cohesion: 0.17
Nodes (20): Deterministic verified claims and grouped-ratio policy v2, Single fenced reservation of backtest/final jobs, tokens, bytes and fits, Common three-fold full-horizon measured method selection, Workflow 2 frozen policy and retained workflow 1 behavior, Conservative reserved seconds, token estimates and failed-work accounting, Fold-compatible shared context in multiples of 32, minimum 64, Both enablement flags and actual-worker attestation required, report_forecasting.py admission, comparison checkpoints and selection (+12 more)

### Community 37 - "Frontend Runtime Dependencies"
Cohesion: 0.11
Nodes (19): class-variance-authority, clsx, dependencies, class-variance-authority, clsx, radix-ui, react, react-dom (+11 more)

### Community 38 - "Dated Local and Hosted Acceptance"
Cohesion: 0.16
Nodes (18): Deployed availability and fresh worker acceptance boundary, Planning worker, API and frontend deployed release boundary, Planning release and fresh acceptance boundary, Deployed Forecast Plans with quota-limited fresh hierarchy acceptance, Accessibility verification boundary, Document, Final hosted acceptance quota block, Historical versus hosted validation (+10 more)

### Community 39 - "Versioned Metrics and Controlled Compilation"
Cohesion: 0.18
Nodes (14): Approved same-grain target comparison over a frozen revenue definition., target_plan(), catalog_plan(), compile_metric(), matched_metrics(), MetricFormula, MetricScope, Versioned public business definitions and a closed, application-owned SQL… (+6 more)

### Community 40 - "Evidence-Backed Report Workflow"
Cohesion: 0.24
Nodes (5): ReportEngine, ReportDraft, ReportPlan, ReportSection, test_report_writer_cannot_invent_numbers_or_references()

### Community 41 - "Public Metric Definition Contract"
Cohesion: 0.20
Nodes (17): Document, Insert-only metric seeding, Planning fixture execution, Application-owned grain compiler, Canonical forecast-value reconciliation, Catalog-aware text and voice planning, Closed typed metric formula, Deployed public Business Metrics Catalog (+9 more)

### Community 42 - "Coherent Forecast Planning Contract"
Cohesion: 0.19
Nodes (17): End-to-end reconciliation validation, Aggregate candidate selection, Allocated estimate disclosure, Cent-exact monetary reconciliation, Coherent baseline fallback, Complete hierarchy evidence, Document, Dual revenue hierarchies (+9 more)

### Community 43 - "Worker-First Release Runbook"
Cohesion: 0.18
Nodes (17): Actual workload identity verification, Credential context separation, Dedicated workload identities, Document, Exact-origin runtime configuration, Fenced reference-aware maintenance, First-time foundation path, Hosted acceptance evidence (+9 more)

### Community 44 - "Coherent Hierarchical Revenue Planning"
Cohesion: 0.23
Nodes (15): adjust_plan(), baseline_candidate(), capture_history(), distribute(), evaluate_recipe(), fail(), Pure hierarchical revenue calculations; no model, database or executable inputs., Largest remainder allocation keeps each published branch coherent to one cent. (+7 more)

### Community 45 - "Durable Advanced Report Contract"
Cohesion: 0.21
Nodes (14): Three-origin full-horizon backtests and baseline/domain gates, Transactional outbox, private OIDC worker and checkpoint reuse, Workflow 2 with enabled verified hosted TimesFM and disabled local defaults, Captured report source, model, completed context, schema and skill revisions, Visitor-supplied complete baseline and alternative driver paths, Same saved document drives web, PDF, Word and full CSV ZIP, Public immutable report versions and prediction caveats, Independent report lease and initiating-guest controls (+6 more)

### Community 46 - "Fenced Reference-Aware Maintenance"
Cohesion: 0.31
Nodes (12): clear_maintenance(), enter_maintenance(), purge_dashboards(), purge_planning(), purge_reports(), Operator-only, reference-aware cleanup. Failed operations stay fenced for…, Explicit operator purge after recovery expires; preserve dashboard references., Operator-only expiry; keep whole plan families referenced by saved public… (+4 more)

### Community 47 - "Bounded ADK Application Harness"
Cohesion: 0.14
Nodes (8): NeedsInput, Exception, Graph nodes carry only a run identifier. Bodies live in fenced checkpoints., ReportPolicy, run_report_graph(), test_graph_preserves_clarification_without_running_downstream_stages(), test_policy_blocks_tools_and_enforces_model_budget(), BasePlugin

### Community 48 - "Skills Library Interface"
Cohesion: 0.18
Nodes (8): metadata, contentOf(), SkillsWorkspace(), editSkill(), exportFile(), importFile(), openEditor(), sourceLabel()

### Community 49 - "Cases Components"
Cohesion: 0.23
Nodes (11): cases(), matches(), execute(), reconcile(), TaskBody, main(), Evaluate the public, hosted API against independent seed reference values., main() (+3 more)

### Community 50 - "Public API Regression Tests"
Cohesion: 0.28
Nodes (12): guest(), parametrize, A worker may finish after the event query but before the status read., test_analysis_replay_fork_and_provenance(), test_guest_scope_and_no_administrative_routes(), test_origin_and_payload_validation(), test_stream_drains_events_committed_between_poll_and_terminal_read(), test_voice_does_not_fake_model_in_fixture_mode() (+4 more)

### Community 51 - "Retry and Recovery Boundaries"
Cohesion: 0.17
Nodes (13): Fixed parameterized managed TimesFM 3.0 Preview adapter, Retry and recovery policy, Disabled TimesFM same-job recovery and statistical fallback, Permanent access/request failures fail fast without substitution, Fenced report redelivery with shared budgets and three-delivery cap, Bounded persisted-cursor SSE replay without query restart, Thread-held cancellation survives delayed query responses, At-most-two structured model attempts with bounded jitter (+5 more)

### Community 52 - "Application Architecture and Boundaries"
Cohesion: 0.17
Nodes (13): Document, Proposal retention, Reviewable dashboard generation, Reviewed rebase and conditional Undo, Shared durable execution, Adaptive coherent planning, Document, Frozen planning fit profile (+5 more)

### Community 53 - "Public Retail Product Overview"
Cohesion: 0.15
Nodes (13): Cloud preview token isolation, Credential-free default fixtures, Document, Isolated dashboard emulator verification, Local planning execution, Runtime backend URL, Document, Landing workspace route split (+5 more)

### Community 54 - "Chart Tooltip and Legend Primitives"
Cohesion: 0.21
Nodes (11): ChartConfig, ChartContainer(), ChartContext, ChartContextProps, ChartLegendContent(), ChartTooltipContent(), getPayloadConfigFromPayload(), INITIAL_DIMENSION (+3 more)

### Community 55 - "Packaged Metric Definitions"
Cohesion: 0.30
Nodes (9): _insert(), Insert-only packaged definitions. Never called by startup, release or history…, seed_metrics(), MetricAction, MetricDefinition, MetricWrite, field_validator, test_competing_public_aliases_require_clarification() (+1 more)

### Community 56 - "Durable Dashboard and Forecast Execution"
Cohesion: 0.23
Nodes (4): chart_state(), PlanningEngine, DashboardBlueprint, model_validator

### Community 57 - "Analytics and Prediction Playbooks"
Cohesion: 0.17
Nodes (12): Advanced Analysis tools and evidence gates, Analytics and prediction playbook catalog, Separate insert-only transactional playbook seeding, Twelve curated analytics and prediction playbooks, Packaged TimesFM templates do not overwrite published skills, Combined automatic/manual selection budget of three, Public versioned Skills library, Guest-scoped skill_author_sessions (+4 more)

### Community 58 - "Durable Task Dispatch and Recovery"
Cohesion: 0.24
Nodes (4): Cloud Tasks outbox, reconciliation and an explicitly local-only development…, ReportDispatcher, test_expired_waiting_report_releases_conversation_slot(), test_outbox_recovers_abandoned_workers_and_queued_cancellation()

### Community 59 - "Reviewed AI Dashboard Contract"
Cohesion: 0.31
Nodes (11): Atomic dashboard publication, Conditional Undo, Deployed AI Dashboard Builder with quota-limited fresh proposal acceptance, Document, Durable dashboard proposal workflow, Evidence compatibility signature, Guest-owned proposal expiry, Planning retention maintenance (+3 more)

### Community 60 - "Dashboard Editing and Sharing"
Cohesion: 0.24
Nodes (6): metadata, DashboardWorkspace(), refreshRemoved(), restoreItem(), setMode(), unpin()

### Community 61 - "Smoke Dashboards"
Cohesion: 0.18
Nodes (5): main(), Opt-in API check using existing immutable artifacts; never runs an analysis or…, run(), Opt-in hosted Live recovery check; creates and soft-deletes one probe skill.…, Opt-in hosted repeated Live analysis; public test chat, read-only source…

### Community 62 - "Frontend Package Scripts"
Cohesion: 0.20
Nodes (9): name, private, scripts, build, dev, lint, start, test (+1 more)

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

### Community 68 - "Repository Contribution Guidance"
Cohesion: 0.29
Nodes (7): Authoritative architecture diagrams, Context7 documentation workflow, Deployment authorization boundary, Document, Immutable planning evidence, Separate operator data operations, Worker-first planning release

### Community 69 - "Retail Data Publication Workflow"
Cohesion: 0.29
Nodes (7): Original demo retail schema (seed evidence 2026-10-16), Fenced insert-only cloud publication, Independent bundle reconciliation, Expanded retail column dictionary (retail-timeseries-v1), Stable full-window extend workflow, Deterministic streaming Parquet bundle, Additional timeseries source profile

### Community 70 - "Competition Demonstration Workflow"
Cohesion: 0.29
Nodes (7): Cross-source actual-versus-target exploration, Five-minute competition demonstration, Landing previews and direct workspace entry, Production rehearsal and backup recording, Public conversation sharing and forks, Spoken analysis and interruption, Warehouse question with SQL evidence

### Community 71 - "Conditional Driver Scenario Playbook"
Cohesion: 0.33
Nodes (6): Conditional predictions with historical driver support, Conditional driver and promotion scenarios playbook, Visitor-supplied complete future driver paths, Optional available TimesFM with complete covariate context, Shared-method baseline and alternative scenario artifacts, Chronological scenario validation and extrapolation rejection

### Community 72 - "Revenue Forecast Playbook"
Cohesion: 0.33
Nodes (6): Advanced Analysis controlled forecast fitting, Common chronological scores choose statistical or managed candidate, Complete series and actual latest-observation cutoff, Revenue and demand forecasting playbook, Observed-versus-predicted values and retained method evidence, Five-percent MAE improvement and majority-fold promotion

### Community 73 - "Named Firestore ADK Persistence"
Cohesion: 0.47
Nodes (6): Separate skill author session lease collection, Bounded fresh-transaction retries for read aborts, Custom Firestore ADK session adapter, ADR: ADK persistence in named Firestore, Loaded-session revision and conversation lease fencing, Terminal event stream sequence draining

### Community 74 - "Original Retail Source Schema"
Cohesion: 0.33
Nodes (6): Original PostgreSQL retail.customer_profiles, Original BigQuery order_items, Original BigQuery orders, Original BigQuery products, Original PostgreSQL retail.regional_targets, Original BigQuery returns

### Community 75 - "Expanded Retail Column Dictionary"
Cohesion: 0.40
Nodes (6): Dense daily calendar date spine, Time-series customer_profiles, Time-series sales_order_items, Time-series sales_orders, Time-series sales_returns, Full-month store targets

### Community 76 - "Reportslibrary Components"
Cohesion: 0.40
Nodes (4): metadata, ReportsLibrary(), change(), restore()

### Community 78 - "Managed TimesFM Architecture Decision"
Cohesion: 0.40
Nodes (5): Disabled until managed and actual-worker access verification, ADR 0009: Managed TimesFM comparison, Fenced immutable input/configuration and operation checkpoints, Agent relevance and priority, deterministic numerical selection, Same-method scenarios in separate artifacts

### Community 79 - "Immutable Chart Presentation Contract"
Cohesion: 0.40
Nodes (5): Deterministic bounded chart sampling, Saved-artifact chart-data endpoint, Deterministic truthful chart insights, Full saved-result CSV export, Version-2 VisualizationSpec metadata

### Community 80 - "Published Dashboard Views and Retention"
Cohesion: 0.40
Nodes (5): Active and recoverable artifact retention, Canonical public dashboard sharing, Public revision-checked editing, Published saved chart views, Revision-checked whole-dashboard exports

### Community 81 - "Frontend Contribution Guidance"
Cohesion: 0.40
Nodes (5): Frontend contributor instructions, Guest-scoped report clarification and skill draft recovery, Installed Next.js version guides, Browser preferences and reduced-motion feedback, Explicit saved chart publication and revision checks

### Community 82 - "Saved Dashboard View Tests"
Cohesion: 0.50
Nodes (3): { initialChartView, describeChartView }, load(), reader()

### Community 83 - "Planning Review and Retry Tests"
Cohesion: 0.50
Nodes (3): { dashboardChanges }, load(), require

### Community 84 - "Sales Change Contribution Playbook"
Cohesion: 0.50
Nodes (4): Observed concentrations versus causal explanations, Sales change and segment contributions, Reconciled segment change contributions, Exact order-volume and AOV revenue bridge

### Community 85 - "Comparable Store Performance Playbook"
Cohesion: 0.67
Nodes (4): Comparable-store and target performance, Comparable-store eligibility, Store and regional target join grain, Weighted attainment and reconciled target gaps

### Community 86 - "Weighted Retail KPI Definitions"
Cohesion: 0.67
Nodes (4): Completed-order merchandise revenue, Retail KPI definitions and weighted ratios, Overall AOV from revenue and distinct orders, Weighted margin rate and additive reconciliation

### Community 87 - "Marketing Associations and Scenarios"
Cohesion: 0.67
Nodes (4): Attributed revenue per campaign spend, Compatible campaign and period aggregation, Campaign and promotion performance, Validated future promotion scenario

### Community 88 - "Merchandise Margin and Refunds"
Cohesion: 0.67
Nodes (4): Historical line merchandise revenue and cost, Merchandise margin and returns-adjusted performance, Order-cohort refund and returned-cost adjustment, Signed margin and return-cohort maturity

### Community 89 - "Smoke Reports Deployed"
Cohesion: 0.67
Nodes (3): main(), Opt-in hosted report acceptance; creates public verification…, run()

### Community 90 - "Public Skill Versioning Decision"
Cohesion: 0.50
Nodes (4): ADR 0004: public versioned skills (accepted 2026-10-15), Bounded metadata skill selector, Public Markdown playbooks, Analysis-scoped immutable skill snapshots

### Community 91 - "Public Report Evidence Boundary"
Cohesion: 0.50
Nodes (4): ADR 0007: public report evidence (accepted 2026-10-17), Requester-only in-memory Search panel, Verified numerical claims, Distinct writer and semantic reviewer

### Community 92 - "Immutable Saved-Artifact Dashboard Cards"
Cohesion: 0.50
Nodes (4): Validated ChartViewState, Fenced reference-aware history maintenance, Revision-checked idempotent dashboard mutations, Immutable saved-artifact dashboard cards

### Community 95 - "Prediction Evidence Rendering Tests"
Cohesion: 0.50
Nodes (3): base, compiledModule, require

### Community 97 - "Public Anonymous Workspace Decision"
Cohesion: 1.00
Nodes (3): Anonymous guest token attribution, quotas and cancellation, Public shared conversations, ADR: Public workspace without accounts

### Community 98 - "Immutable Durable Report Decision"
Cohesion: 0.67
Nodes (3): ADK App / Runner / Workflow, Independent durable report execution, ADR 0006: durable versioned reports (accepted 2026-10-17)

### Community 104 - "Scoped Cloud Build Workflow"
Cohesion: 0.67
Nodes (3): Cloud Build Docker build step, Cloud Build Docker push step, Dedicated GCS-only build logs

## Knowledge Gaps
- **263 isolated node(s):** `agentic-bi-backend`, `$schema`, `style`, `rsc`, `tsx` (+258 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AppError` connect `Application Error Contracts` to `TimesFM Validation and Recovery`, `Transactional Storage and Persistence`, `Evidence-Backed Report Workflow`, `Saved Chart Data Presentation`, `Bounded Runtime Configuration`, `Skill Selection and Snapshot Tests`, `Public API Composition`, `Report Recovery and Export Tests`, `Conversation Persistence and Recovery`, `Shared Job Admission and Leases`, `Shared Job Admission and Leases`, `Fenced ADK Session Persistence`, `Typed Analysis and Visualization`, `Skill Author Concurrency Tests`, `Metric and Planning Regression Tests`, `Public API Composition`, `Reviewed Skill Draft Publication`, `Versioned Metrics and Controlled Compilation`, `Evidence-Backed Report Workflow`, `Coherent Hierarchical Revenue Planning`, `Fenced Reference-Aware Maintenance`, `Bounded ADK Application Harness`, `Packaged Metric Definitions`, `Durable Dashboard and Forecast Execution`, `Durable Task Dispatch and Recovery`, `Versioned Metrics and Controlled Compilation`?**
  _High betweenness centrality (0.080) - this node is a cross-community bridge._
- **Why does `Public landing page guide` connect `Static Product Preview Contract` to `Dated Local and Hosted Acceptance`, `Worker-First Release Runbook`, `Application Architecture and Boundaries`, `Durable Advanced Report Contract`, `Analytics and Prediction Playbooks`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `Canonical workspace link construction` connect `Static Product Preview Contract` to `Workspacepath Components`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Are the 88 inferred relationships involving `AppError` (e.g. with `AI` and `AnalysisService`) actually correct?**
  _`AppError` has 88 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `Settings` (e.g. with `Connectors` and `create_app()`) actually correct?**
  _`Settings` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `MemoryStore` (e.g. with `test_every_chart_family_and_mixed_units_can_render()` and `test_complex_plan_uses_json_mode_and_still_validates_locally()`) actually correct?**
  _`MemoryStore` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 14 inferred relationships involving `Connectors` (e.g. with `Settings` and `AppError`) actually correct?**
  _`Connectors` has 14 INFERRED edges - model-reasoned connections that need verification._
## Extraction Integrity and Scope

All 56 detected documents have semantic representation; 4 were refreshed by one host-session agent. No separate model API or cloud operation was used for graph generation.

- Graphify tree-sitter reported potentially partial extraction of Frontend/src/components/workspace.tsx at line 1082; 13 symbols extracted.
- Raw external import references can have no matching project node; unresolved endpoints are reported, not fabricated.
- The default undirected simple graph can combine multiple relationships between an endpoint pair; diagnostic counts retain this limitation.
- Host semantic-token usage is unavailable, not zero.

Raw extraction: 906 dangling endpoint references, 0 missing endpoint fields, 0 self-loops and 583 same-endpoint relationships collapsed in the undirected projection. These are extraction limitations, not application runtime findings. Source files remain authoritative.
