# Graph Report - 6. Google AI Builder Cup - Agentic BI  (2026-10-17)

## Corpus Check
- 214 files · ~153,033 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 1650 nodes · 4426 edges · 119 communities (89 shown, 30 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 244 edges (avg confidence: 0.92)
- Token cost: 0 separate model-API tokens; host-session semantic input/output token usage is unavailable (not measured as zero).

## Graph Freshness
- Built from commit: `19cafa98`
- This is a working-tree snapshot; VALIDATION.json records per-file SHA-256 hashes. Compare those hashes as well as the base commit to check freshness.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Saved Chart Presentation
- Durable Report Execution
- Retail Bundle Publication
- Settings and Skill Forms
- Guarded Database Queries
- Typed Analysis Contracts
- Versioned Skill Selection
- Dashboard Library Interface
- TypeScript Compiler Configuration
- Responsive Sidebar Primitives
- Fenced Administrative Maintenance
- Dashboard Sharing and Downloads
- Typed Fusion and Visualization
- Public API Composition
- ADK Session Fencing
- Dashboard Configuration and Tests
- Result Cards and Pinning
- Conversation Persistence and Recovery
- Report Reader and Progress
- Workspace UI Controls
- Execution Policy and Errors
- Frontend API and Saved Results
- Skill Author Concurrency Tests
- Interactive Chart Formatting
- Scoped Cloud Foundation
- Shadcn Component Configuration
- Dashboard HTTP Contracts
- Report Repository Leases
- Accent and Motion Tokens
- Frontend Development Dependencies
- Skill Draft Publication
- Live Voice Workspace
- Frontend Runtime Dependencies
- API Compatibility Smoke Tests
- Browser Preference Synchronization
- AI Planning and Repairs
- Controlled Analysis Execution
- Public API Regression Tests
- Skills Library Editor
- Reduced Motion Components
- Chart Tooltip Primitives
- Safe Markdown and Revisions
- Voice Skill Author Interface
- Frontend Package Scripts
- Dashboard Detail Page
- Saved Charts and Preferences
- Application Theme Providers
- Customer Cohorts and Returns
- Data Quality and Fusion
- Marketing Associations and Scenarios
- Seasonality and Forecast Validation
- Hosted Dashboard Report Probes
- Durable Public Report Decisions
- Application Layout and Fonts
- Shared Analytical Domain Model
- Reviewed Skill Authoring Contract
- Application Service Boundaries
- Time Series Data Publication
- Scoped Routine Release Workflow
- Public Retail Product Overview
- Repository Contributor Guidance
- Private Report Worker Routes
- Named Firestore ADK Persistence
- Saved Dashboard Retention Design
- Analytics Playbooks and Prediction Gates
- Published Dashboard Views and Recovery
- Original Retail Source Schema
- Local Fixtures and Cloud Preview
- Expanded Retail Table Dictionary
- Skill Revision Snapshots
- Reports Library Page
- Dashboard Saved Metadata Reads
- Revenue Forecast Playbook
- Backend Runtime Responsibilities
- Immutable Chart Data Services
- Competition Demonstration Workflow
- Frontend Contribution Guidance
- Frontend Routes and Verification
- Saved Chart View Tests
- Sales Change Contribution Playbook
- Comparable Store Performance Playbook
- Weighted Retail KPI Definitions
- Merchandise Margin and Refunds
- Atomic Storage Adapter Protocol
- Public Skill Versioning Decision
- Dashboard Mutation and Retention Plan
- Immutable Report Evidence Contract
- Dated Hosted Acceptance Evidence
- Browser PCM Audio Worklet
- Chart Formatting Regression Tests
- Public Anonymous Workspace Decision
- Runtime Backend Configuration Route
- Frontend Health Route
- Settings Application Page
- Markdown Rendering Regression Tests
- Backend Package Description
- Classname Utility Dependency
- Report Revision Retention Decision
- Stage Feedback and Toasts
- Frontend ESLint Configuration
- Next Standalone Configuration
- Lucide Icon Dependency
- Motion Animation Dependency
- Next Framework Dependency
- Theme Provider Dependency
- GFM Markdown Dependency
- Tailwind Merge Dependency
- Model Preference Regression Tests
- Report Assumption Regression Tests
- Dated Architecture Overview
- Chronological Prediction Validation
- Browser Model Selection Guide
- Analytics Skill Seed Evidence
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
10. `AnalysisService` - 33 edges

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

## Communities (119 total, 30 thin omitted)

### Community 0 - "Saved Chart Presentation"
Cohesion: 0.07
Nodes (67): change(), csv_cell(), csv_line(), date_value(), metadata(), next_date(), normalized_spec(), number() (+59 more)

### Community 1 - "Durable Report Execution"
Cohesion: 0.06
Nodes (46): ReportDispatcher, NeedsInput, Exception, ReportEngine, ExportStorage, format_axis(), ForecastSpec, ReportDraft (+38 more)

### Community 2 - "Retail Bundle Publication"
Cohesion: 0.07
Nodes (54): demand(), generate(), GeneratorConfig, money(), promotion_window(), Path, Deterministic, bounded-memory synthetic retail history; never contacts a…, read_manifest() (+46 more)

### Community 3 - "Settings and Skill Forms"
Cohesion: 0.08
Nodes (35): Catalog, ModelSettings(), preferenceLabels, sections, Phase, requirements, template, Checkbox() (+27 more)

### Community 4 - "Guarded Database Queries"
Cohesion: 0.08
Nodes (33): Connectors, cases(), evaluate(), main(), matches(), Numerical evaluation against independent Python aggregates of the retail seed., retail_data(), validate_sql() (+25 more)

### Community 5 - "Typed Analysis Contracts"
Cohesion: 0.08
Nodes (36): check_maintenance(), ChartMeasure, ConversationCreate, StrictModel, Report specialists use existing guarded SQL/fusion; all numerical work is…, AnalysisTask, EvidenceClaim, ForecastInputs (+28 more)

### Community 6 - "Versioned Skill Selection"
Cohesion: 0.09
Nodes (37): analytics_examples(), Stable seed IDs let operators add examples without replacing public edits., Import the reviewable, source-controlled pack before any cloud writes., seed_analytics(), seed_examples(), compatible(), export_skill(), import_skill() (+29 more)

### Community 7 - "Dashboard Library Interface"
Cohesion: 0.12
Nodes (25): metadata, DashboardEditor(), DashboardHeader(), useDashboardMutation(), DashboardsLibrary(), Alert(), AlertDescription(), AlertTitle() (+17 more)

### Community 8 - "TypeScript Compiler Configuration"
Cohesion: 0.05
Nodes (36): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+28 more)

### Community 9 - "Responsive Sidebar Primitives"
Cohesion: 0.07
Nodes (15): Sidebar(), SidebarContext, SidebarContextProps, SidebarMenuButton(), sidebarMenuButtonVariants, SidebarProvider(), SidebarRail(), SidebarTrigger() (+7 more)

### Community 10 - "Fenced Administrative Maintenance"
Cohesion: 0.13
Nodes (26): check_models(), cleanup_skill_authors(), cli(), dashboard_maintenance(), index_schema(), main(), operator_credentials(), Credentialed CLI only. No administrative endpoint is exposed by FastAPI. (+18 more)

### Community 11 - "Dashboard Sharing and Downloads"
Cohesion: 0.10
Nodes (23): download(), SavedCsvDownload(), download(), DashboardDownload(), download(), DashboardShare(), show(), formats (+15 more)

### Community 12 - "Typed Fusion and Visualization"
Cohesion: 0.18
Nodes (29): fixture_answer(), fixture_plan(), Explicit local-only sample planner. Never used as a Gemini fallback., _arrow_bytes(), fuse(), _identifier(), Any, A typed plan compiler; no model-supplied SQL or Python reaches DuckDB. (+21 more)

### Community 13 - "Public API Composition"
Cohesion: 0.14
Nodes (15): Durable ADK session adapter with ordered events and fenced state writes., Local-only Gemini preview on synthetic fixtures, using the operator's gcloud…, get_settings(), Deterministic synthetic retail data; no real customer information., Cloud Tasks outbox, reconciliation and an explicitly local-only development…, check_lease(), snapshot(), Gemini Live interview with requirements/draft tools, never a publication or SQL… (+7 more)

### Community 14 - "ADK Session Fencing"
Cohesion: 0.11
Nodes (23): FirestoreSessionService, StaleLease, test_cancellation_failure_still_releases_conversation(), test_raw_audio_is_not_persisted(), test_recent_session_context_uses_newest_events(), test_transient_model_failure_retried_once_only(), test_model_access_failure_is_explicit_and_never_falls_back(), test_selected_identifier_reaches_adk_without_mutating_default() (+15 more)

### Community 15 - "Dashboard Configuration and Tests"
Cohesion: 0.23
Nodes (28): Settings, ChartViewState, Dashboards, action(), create(), pin(), request(), saved() (+20 more)

### Community 16 - "Result Cards and Pinning"
Cohesion: 0.11
Nodes (26): ResultCard, PinToDashboard(), create(), pin(), requestFor(), ResultCard, display(), human() (+18 more)

### Community 17 - "Conversation Persistence and Recovery"
Cohesion: 0.08
Nodes (10): Repository, MemoryStore, main(), VoiceHarness, test_maintenance_scans_more_than_one_page_without_skipping_deleted_cursors(), test_result_survives_interpreter_outage_and_reconnect(), test_concurrent_analyses_isolate_models_across_selection_planning_and_answers(), test_default_retry_reuses_original_model_after_operator_default_changes() (+2 more)

### Community 18 - "Report Reader and Progress"
Cohesion: 0.13
Nodes (21): active(), ReportRunCard(), cancel(), clarify(), poll(), ResearchResult, SkillEvidence(), Badge() (+13 more)

### Community 19 - "Workspace UI Controls"
Cohesion: 0.11
Nodes (17): ConversationReports(), Button(), buttonVariants, InputGroup(), InputGroupAddon(), inputGroupAddonVariants, InputGroupButton(), inputGroupButtonVariants (+9 more)

### Community 20 - "Execution Policy and Errors"
Cohesion: 0.12
Nodes (20): AppError, Exception, resolve_text_model(), ADK graph orchestration with global policy and explicit application checkpoints., Graph nodes carry only a run identifier. Bodies live in fenced checkpoints., ReportPolicy, run_report_graph(), digest() (+12 more)

### Community 21 - "Frontend API and Saved Results"
Cohesion: 0.11
Nodes (19): metadata, DashboardWidget(), ReportEditDialog(), save(), ReportWorkspace(), download(), SkillAttachments(), load() (+11 more)

### Community 22 - "Skill Author Concurrency Tests"
Cohesion: 0.18
Nodes (25): asyncio, live(), AuthorDraft, client(), create(), guest(), prepared(), fixture (+17 more)

### Community 23 - "Interactive Chart Formatting"
Cohesion: 0.16
Nodes (24): categoryColor(), InsightfulChart(), content(), label(), palette, Plot(), Values(), changeLabel() (+16 more)

### Community 24 - "Scoped Cloud Foundation"
Cohesion: 0.18
Nodes (19): main(), Build with a resource-scoped builder, then deploy as the current operator., configuration(), main(), Prepare or deploy ONLY the private report worker. Foundation/IAM are separate…, ensure_secret(), ensure_service_account(), gcloud() (+11 more)

### Community 25 - "Shadcn Component Configuration"
Cohesion: 0.09
Nodes (22): aliases, components, hooks, lib, ui, utils, iconLibrary, menuAccent (+14 more)

### Community 26 - "Dashboard HTTP Contracts"
Cohesion: 0.18
Nodes (13): DashboardAction, DashboardCreate, DashboardItemPatch, DashboardLayout, DashboardPatch, DashboardPin, DashboardRequest, field_validator (+5 more)

### Community 28 - "Accent and Motion Tokens"
Cohesion: 0.10
Nodes (19): ColorSelector(), ColorSelectorContext, ColorSelectorContextValue, ColorSelectorItem(), ColorSelectorItemProps, ColorSelectorLabelProps, ColorSelectorList(), ColorSelectorListProps (+11 more)

### Community 29 - "Frontend Development Dependencies"
Cohesion: 0.10
Nodes (21): babel-plugin-react-compiler, eslint, eslint-config-next, devDependencies, babel-plugin-react-compiler, eslint, eslint-config-next, shadcn (+13 more)

### Community 31 - "Live Voice Workspace"
Cohesion: 0.15
Nodes (6): Workspace(), ask(), cancelAnalysis(), ensureConversation(), startVoice(), LiveVoice

### Community 32 - "Frontend Runtime Dependencies"
Cohesion: 0.11
Nodes (19): class-variance-authority, clsx, dependencies, class-variance-authority, clsx, radix-ui, react, react-dom (+11 more)

### Community 33 - "API Compatibility Smoke Tests"
Cohesion: 0.17
Nodes (15): saved_rows(), create_app(), field_validator, TurnCreate, author_router(), main(), Local-only report smoke; --gemini opts into billable model calls, never cloud…, run() (+7 more)

### Community 34 - "Browser Preference Synchronization"
Cohesion: 0.16
Nodes (16): ChoiceSetting(), reset(), updatePreference(), getSnapshot(), resetPreferences(), save(), serverSnapshot, Snapshot (+8 more)

### Community 35 - "AI Planning and Repairs"
Cohesion: 0.20
Nodes (5): AI, json_rows(), json_value(), Any, test_sql_repair_keeps_selected_model_and_read_only_guards()

### Community 36 - "Controlled Analysis Execution"
Cohesion: 0.20
Nodes (6): AnalysisService, model_evidence(), Pinned text model choices; per-analysis context never mutates shared settings., ResultArtifact, skill_reference(), BaseModel

### Community 37 - "Public API Regression Tests"
Cohesion: 0.22
Nodes (14): client(), guest(), fixture, parametrize, A worker may finish after the event query but before the status read., test_analysis_replay_fork_and_provenance(), test_guest_scope_and_no_administrative_routes(), test_origin_and_payload_validation() (+6 more)

### Community 38 - "Skills Library Editor"
Cohesion: 0.18
Nodes (8): metadata, contentOf(), SkillsWorkspace(), editSkill(), exportFile(), importFile(), openEditor(), sourceLabel()

### Community 39 - "Reduced Motion Components"
Cohesion: 0.25
Nodes (9): AnalysisProgress(), stages, AnimatedNumber(), AnimatedNumberProps, Reveal(), SettingsWorkspace(), useAppMotion(), useHydrated() (+1 more)

### Community 40 - "Chart Tooltip Primitives"
Cohesion: 0.21
Nodes (11): ChartConfig, ChartContainer(), ChartContext, ChartContextProps, ChartLegendContent(), ChartTooltipContent(), getPayloadConfigFromPayload(), INITIAL_DIMENSION (+3 more)

### Community 41 - "Safe Markdown and Revisions"
Cohesion: 0.24
Nodes (6): metadata, MarkdownContent(), MessageContent(), SkillMarkdown(), SkillRevision(), Skill

### Community 42 - "Voice Skill Author Interface"
Cohesion: 0.25
Nodes (6): loadSavedInterview(), path(), SkillVoiceAuthor(), connect(), publish(), saveReview()

### Community 43 - "Frontend Package Scripts"
Cohesion: 0.20
Nodes (9): name, private, scripts, build, dev, lint, start, test (+1 more)

### Community 44 - "Dashboard Detail Page"
Cohesion: 0.27
Nodes (5): metadata, DashboardWorkspace(), refreshRemoved(), restoreItem(), unpin()

### Community 45 - "Saved Charts and Preferences"
Cohesion: 0.22
Nodes (9): Immutable saved-result chart presentation, Motion and feedback (deployed 2026-10-16), Reader-aware answer following, Unified device/application reduced motion, Versioned browser-local preferences, Local chart exploration defaults, Pinned analysis model catalog, Task-local captured analysis model (+1 more)

### Community 46 - "Application Theme Providers"
Cohesion: 0.28
Nodes (6): AppearanceSync(), ResearchPanel(), Toaster(), subscribe(), usePreferences(), THEME_KEY

### Community 47 - "Customer Cohorts and Returns"
Cohesion: 0.36
Nodes (8): Signup cohorts and first observed purchase cohorts, Customer cohorts and repeat purchasing, Equally mature customer observation windows, Repeat purchase and activity retention denominators, Validated bounded-rate or monetary forecast domain, Explicit return-rate target and denominator, Returns and rate prediction readiness, Refund latency and cohort maturity

### Community 48 - "Data Quality and Fusion"
Cohesion: 0.32
Nodes (8): Data quality and analysis readiness, Calendar spine, unknown gaps and observed zeros, Join-key compatibility, coverage and fan-out, Independent totals reconciliation, Explicit fan-out and incomplete-input rejection, ADR: Typed bounded cross-source fusion, Gemini relationship-key and business-assumption hypotheses, Trusted compiler for typed relational fusion

### Community 49 - "Marketing Associations and Scenarios"
Cohesion: 0.36
Nodes (8): Attributed revenue per campaign spend, Compatible campaign and period aggregation, Campaign and promotion performance, Validated future promotion scenario, Bounded regression/SARIMAX scenario predictions, Conditional driver and promotion scenarios, Visitor-supplied future driver paths, Historically supported driver model

### Community 50 - "Seasonality and Forecast Validation"
Cohesion: 0.32
Nodes (8): Dense retail calendar at consistent time grain, Shifted target-derived rolling predictors, Observed peaks with causal limitations, Calendar trends and retail seasonality, Baseline comparison and candidate promotion, Forecast validation and uncertainty, Chronological rolling-origin backtests, Supported prediction intervals and publication outcome

### Community 51 - "Hosted Dashboard Report Probes"
Cohesion: 0.29
Nodes (6): main(), Opt-in API check using existing immutable artifacts; never runs an analysis or…, run(), main(), Opt-in hosted report acceptance; creates public verification…, run()

### Community 52 - "Durable Public Report Decisions"
Cohesion: 0.25
Nodes (8): ADK App / Runner / Workflow, Independent durable report execution, ADR 0006: durable versioned reports (accepted 2026-10-17), ADR 0007: public report evidence (accepted 2026-10-17), Requester-only in-memory Search panel, Verified numerical claims, Distinct writer and semantic reviewer, Private report infrastructure foundation

### Community 53 - "Application Layout and Fonts"
Cohesion: 0.25
Nodes (6): body, heading, metadata, mono, AppProviders(), appearanceScript

### Community 54 - "Shared Analytical Domain Model"
Cohesion: 0.43
Nodes (7): Agentic BI domain language, Validated Forecast, conditional Scenario and Backtest, Immutable Report Revision and Evidence Claims, Immutable Result Artifact, Retained Artifact protected through history cleanup, Saved Chart View over immutable artifacts, Skill snapshots of immutable selected revisions

### Community 55 - "Reviewed Skill Authoring Contract"
Cohesion: 0.29
Nodes (7): Analytics and prediction playbook catalog, Public versioned Skills library, Guest-scoped skill_author_sessions, Deterministic SkillContent draft compiler, Fresh fenced ADK connection recovery, Narrow Gemini Live requirements/draft tools, Explicit atomic reviewed publication

### Community 56 - "Application Service Boundaries"
Cohesion: 0.33
Nodes (7): Controlled analysis service, Named Firestore application database, Private durable report worker, Public FastAPI API, Saved-result charts and dashboards, Guest-scoped conversational skill author, Expanded synthetic retail generation, validation and upload

### Community 57 - "Time Series Data Publication"
Cohesion: 0.29
Nodes (7): Original demo retail schema (seed evidence 2026-10-16), Fenced insert-only cloud publication, Independent bundle reconciliation, Expanded retail column dictionary (retail-timeseries-v1), Stable full-window extend workflow, Deterministic streaming Parquet bundle, Additional timeseries source profile

### Community 58 - "Scoped Routine Release Workflow"
Cohesion: 0.29
Nodes (7): Dedicated scoped runtime and build identities, Time-series profile preservation, Routine backend-before-frontend release, Hosted runtime identity and persistence acceptance, Cloud Build Docker build step, Cloud Build Docker push step, Dedicated GCS-only build logs

### Community 59 - "Public Retail Product Overview"
Cohesion: 0.38
Nodes (7): Advanced Analysis immutable report workflow, Guarded queries and inferred cross-source fusion, Public workspace without registration, Querylane public retail analytics, Verified cloud release dated 17 October 2026, Public saved dashboard library, Expanded timeseries retail data profile

### Community 60 - "Repository Contributor Guidance"
Cohesion: 0.33
Nodes (6): Controlled analytics and prediction playbooks, Authoritative architecture and derived graph references, Deployment guide and dated release evidence, Immutable saved evidence and revision-checked public edits, Repository instructions, Insert-only fenced retail data operations

### Community 61 - "Private Report Worker Routes"
Cohesion: 0.47
Nodes (5): execute(), Private Cloud Run entrypoint. Deploy with --no-allow-unauthenticated and…, reconcile(), TaskBody, post

### Community 62 - "Named Firestore ADK Persistence"
Cohesion: 0.47
Nodes (6): Separate skill author session lease collection, Bounded fresh-transaction retries for read aborts, Custom Firestore ADK session adapter, ADR: ADK persistence in named Firestore, Loaded-session revision and conversation lease fencing, Terminal event stream sequence draining

### Community 63 - "Saved Dashboard Retention Design"
Cohesion: 0.33
Nodes (6): Versioned chart view, ADR 0005: saved-result dashboards (accepted 2026-10-16), Immutable paginated results, Retained artifact references, Shared dashboard implementation plan (implemented/deployed 2026-10-16), Public shared dashboards and saved-view downloads

### Community 64 - "Analytics Playbooks and Prediction Gates"
Cohesion: 0.33
Nodes (6): Advanced Analysis prediction gates, Insert-only seed-analysis-skills operation, Twelve analytics and prediction playbooks, Three-skill analysis budget, Advanced Analysis durable report contract (deployed), Isolated requester-only Search research

### Community 65 - "Published Dashboard Views and Recovery"
Cohesion: 0.33
Nodes (6): Active and recoverable artifact retention, Canonical public dashboard sharing, Public revision-checked editing, Published saved chart views, Revision-checked whole-dashboard exports, Explicit fenced history reset and purge

### Community 66 - "Original Retail Source Schema"
Cohesion: 0.33
Nodes (6): Original PostgreSQL retail.customer_profiles, Original BigQuery order_items, Original BigQuery orders, Original BigQuery products, Original PostgreSQL retail.regional_targets, Original BigQuery returns

### Community 67 - "Local Fixtures and Cloud Preview"
Cohesion: 0.33
Nodes (6): Primary deployment runbook (reviewed 2026-10-17), Isolated Firestore emulator persistence tests, Deterministic local fixture mode, Local-only real Gemini cloud_preview, Local development setup and isolated previews, Runtime frontend BACKEND_URL configuration

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

### Community 75 - "Competition Demonstration Workflow"
Cohesion: 0.40
Nodes (5): Independent source relationship demonstration, Five-minute competition demonstration, Public sharing and immutable forked results, Live voice analytical demonstration, Executed SQL and source evidence inspection

### Community 76 - "Frontend Contribution Guidance"
Cohesion: 0.40
Nodes (5): Frontend contributor instructions, Guest-scoped report clarification and skill draft recovery, Installed Next.js version guides, Browser preferences and reduced-motion feedback, Explicit saved chart publication and revision checks

### Community 77 - "Frontend Routes and Verification"
Cohesion: 0.50
Nodes (5): Conversation, dashboard, report, skill and settings routes, Loaded-screen browser verification, URL-driven dashboard View/Edit presentation state, Querylane frontend, Cloud Run standalone container and runtime API configuration

### Community 78 - "Saved Chart View Tests"
Cohesion: 0.50
Nodes (3): { initialChartView, describeChartView }, load(), reader()

### Community 79 - "Sales Change Contribution Playbook"
Cohesion: 0.50
Nodes (4): Observed concentrations versus causal explanations, Sales change and segment contributions, Reconciled segment change contributions, Exact order-volume and AOV revenue bridge

### Community 80 - "Comparable Store Performance Playbook"
Cohesion: 0.67
Nodes (4): Comparable-store and target performance, Comparable-store eligibility, Store and regional target join grain, Weighted attainment and reconciled target gaps

### Community 81 - "Weighted Retail KPI Definitions"
Cohesion: 0.67
Nodes (4): Completed-order merchandise revenue, Retail KPI definitions and weighted ratios, Overall AOV from revenue and distinct orders, Weighted margin rate and additive reconciliation

### Community 82 - "Merchandise Margin and Refunds"
Cohesion: 0.67
Nodes (4): Historical line merchandise revenue and cost, Merchandise margin and returns-adjusted performance, Order-cohort refund and returned-cost adjustment, Signed margin and return-cohort maturity

### Community 84 - "Public Skill Versioning Decision"
Cohesion: 0.50
Nodes (4): ADR 0004: public versioned skills (accepted 2026-10-15), Bounded metadata skill selector, Public Markdown playbooks, Analysis-scoped immutable skill snapshots

### Community 85 - "Dashboard Mutation and Retention Plan"
Cohesion: 0.50
Nodes (4): Validated ChartViewState, Fenced reference-aware history maintenance, Revision-checked idempotent dashboard mutations, Immutable saved-artifact dashboard cards

### Community 86 - "Immutable Report Evidence Contract"
Cohesion: 0.50
Nodes (4): Verified-claim policy v2, Fenced transactional outbox and application checkpoints, Immutable PDF / DOCX / CSV ZIP exports, Immutable report families and revisions

### Community 87 - "Dated Hosted Acceptance Evidence"
Cohesion: 0.67
Nodes (4): Chart/time-series cloud release 2026-10-16, Dashboard actions cloud release 2026-10-17, Remaining microphone and screen-reader acceptance, Advanced reports cloud release 2026-10-17

### Community 90 - "Public Anonymous Workspace Decision"
Cohesion: 1.00
Nodes (3): Anonymous guest token attribution, quotas and cancellation, Public shared conversations, ADR: Public workspace without accounts

## Knowledge Gaps
- **183 isolated node(s):** `agentic-bi-backend`, `$schema`, `style`, `rsc`, `tsx` (+178 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **30 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `AppError` connect `Execution Policy and Errors` to `Saved Chart Presentation`, `Durable Report Execution`, `Retail Bundle Publication`, `Guarded Database Queries`, `Typed Analysis Contracts`, `Versioned Skill Selection`, `Fenced Administrative Maintenance`, `Typed Fusion and Visualization`, `Public API Composition`, `ADK Session Fencing`, `Dashboard Configuration and Tests`, `Conversation Persistence and Recovery`, `Skill Author Concurrency Tests`, `Dashboard HTTP Contracts`, `Report Repository Leases`, `Skill Draft Publication`, `API Compatibility Smoke Tests`, `AI Planning and Repairs`, `Controlled Analysis Execution`, `Private Report Worker Routes`, `Dashboard Saved Metadata Reads`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **Why does `MemoryStore` connect `Conversation Persistence and Recovery` to `Saved Chart Presentation`, `API Compatibility Smoke Tests`, `Durable Report Execution`, `AI Planning and Repairs`, `Guarded Database Queries`, `Retail Bundle Publication`, `Versioned Skill Selection`, `Public API Composition`, `ADK Session Fencing`, `Dashboard Configuration and Tests`, `Atomic Storage Adapter Protocol`, `Skill Author Concurrency Tests`?**
  _High betweenness centrality (0.020) - this node is a cross-community bridge._
- **Why does `Settings` connect `Dashboard Configuration and Tests` to `Saved Chart Presentation`, `API Compatibility Smoke Tests`, `Durable Report Execution`, `AI Planning and Repairs`, `Guarded Database Queries`, `Public API Regression Tests`, `Versioned Skill Selection`, `Retail Bundle Publication`, `Fenced Administrative Maintenance`, `Public API Composition`, `ADK Session Fencing`, `Conversation Persistence and Recovery`, `Execution Policy and Errors`, `Skill Author Concurrency Tests`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Are the 62 inferred relationships involving `AppError` (e.g. with `AI` and `AnalysisService`) actually correct?**
  _`AppError` has 62 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `Settings` (e.g. with `Connectors` and `create_app()`) actually correct?**
  _`Settings` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `MemoryStore` (e.g. with `test_every_chart_family_and_mixed_units_can_render()` and `test_complex_plan_uses_json_mode_and_still_validates_locally()`) actually correct?**
  _`MemoryStore` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `Connectors` (e.g. with `Settings` and `AppError`) actually correct?**
  _`Connectors` has 11 INFERRED edges - model-reasoned connections that need verification._
## Extraction Integrity and Scope

Generated with Graphify 0.9.51. All 44 detected documents produced semantic nodes. Code extraction used the installed local parser; semantic extraction used two host-session agents. No separate model API, analytical database or cloud deployment was invoked.

- Graphify tree-sitter reported potentially partial extraction of Frontend/src/components/workspace.tsx at line 1064; 13 symbols extracted.
- Raw external import references can have no matching project node; unresolved endpoints are reported, not fabricated.
- The default undirected simple graph can combine multiple relationships between an endpoint pair; diagnostic counts retain this limitation.
- Host semantic-token usage is unavailable, not zero.

Raw-extraction diagnostic: **704 dangling-endpoint references**, **0 missing endpoint fields**, **0 self-loops**, and **432 same-endpoint relationships collapsed** in the default undirected projection. These counts are an extraction limitation, not a runtime defect report. Sample dangling endpoints include external imports such as hashlib and Google SDK modules; unverified project entities are not fabricated.

Generated node centrality, communities and suggested questions are navigation heuristics; they do not prove correctness, causality or a vulnerability. Dated release/plan statements retain their document context. See [VALIDATION.json](VALIDATION.json) and [the graph guide](../docs/graphify/README.md).
