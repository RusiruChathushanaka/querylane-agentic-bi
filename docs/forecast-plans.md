# Hierarchical Forecast Plans

Deployed in the [18 October release](evaluation/planning-release-20261018.md). Fresh hosted 237-node generation remains unverified at the existing daily quota; local numerical evidence is separately recorded. `/forecast-plans` offers public search, status filters, immutable versions, renaming, 30-day recoverable deletion/restoration, downloads and saved-chart preparation/pinning.

## Scope and captured evidence

The initial metric is published order-date merchandise revenue in USD. Monthly horizon defaults to three and is bounded at six. Three full-horizon backtests require at least two annual cycles at the earliest origin. Requests outside complete source coverage, partial-month boundaries, insufficient history and incompatible definitions are rejected.

Both views use one company total: Company → Region → Store, and Company → Category → Product. The current larger dataset has 237 nodes: one company, four regions, 24 stores, eight categories and 200 products. The selected view guides exploration; both are computed to retain one common total. No crossed store-by-product model is implied.

Five bounded reads capture monthly store sales, monthly product sales, store and product mappings, and dense calendar coverage. Every result must be complete. Order and line revenue must reconcile exactly before forecasting. Source/mapping/schema versions, independent timestamps, metric revision, input hash and policy are saved. Zero aggregate cells are filled only after complete calendar/source/mapping coverage is established. Unknown dates, mappings, nulls and incompatible profiles cannot become successful plans.

## Numerical policy v1

Company, regions and categories compare approved statistical candidates. Company and at most one prioritized aggregate can compare TimesFM 3.0 Preview, through the existing verified gate and fixed parameterized saved-input adapter. Actual forecast selection remains numerical. Three common chronological folds use the existing ≥5% MAE improvement and majority-fold gate. Jobs, targets, model tokens, bytes and fits are charged individually even when series are batched.

Reconciliation normalizes nonnegative aggregate siblings to the company prediction. Stores/products use each child's trailing-twelve-complete-training-month share; weights are recomputed inside every fold. A positive parent with unsupported zero child weights cannot be allocated. Largest-remainder monetary allocation makes every displayed/exported branch sum to its parent to the cent, including after rounding.

The adaptive recipe is backtested end to end against coherent seasonal-naive predictions. The score equally weights five levels, averaging node MAE normalized by training-only mean absolute revenue, floored at USD 0.01. Promotion requires ≥5% improvement, wins in at least two folds, and no level worsening above 10%. Otherwise the coherent baseline is retained. Excessive company-level held-out error withholds predictions. Exhausted fitting capacity can retain explicitly documented deterministic baselines.

Store/product allocations are not independently modeled predictions. Scores concern historical validation, not guaranteed future accuracy. Point forecasts only are published: independent model intervals are not added or presented as joint hierarchical uncertainty. MinT, joint geography×product reconciliation, independent fitting of every leaf and hierarchy driver scenarios are deferred. Existing advanced-report driver scenarios remain available separately.

## Adjustments and saved evidence

Each adjustment version records one set-value or percentage operation and a business reason. Set applies the same entered USD amount to each future month. Changes redistribute descendants, update ancestors and proportionally reallocate the other view to the common company total. Zero-history branches cannot receive unsupported positive allocations. All adjustments remain planning assumptions, separate from statistical forecasts and learned scenarios; original statistical values are preserved alongside the planned values.

Versions can build on earlier adjustments, with a maximum twenty completed versions per family. Recompute explicitly starts new source/model work. Version links include the version parameter; historical dashboard pins never follow a latest-version pointer.

PDF summaries, CSV ZIP and JSON derive from immutable saved evidence. JSON records hierarchy/metric versions, methods, mappings, adjustments, hashes and export checksums. CSV ZIP includes all node/period rows and provenance. Do not sum across hierarchy levels or across the two views: their aggregate rows repeat the same economic revenue. Static documents preview tables and charts rather than claiming every CSV row is printed.

Preparing a selected node chart is an explicit saved-only action. Its artifact records plan version, cutoff, modeled/reconciled/allocated status and metric snapshot. Pins use the existing dashboard retention protocol. Advanced Analysis can write a Business/Technical narrative from a saved plan through `forecast_plan_id`/`forecast_plan_version`; report writing consumes admission/model allowance but does not reread sources or rerun forecasts.

## Worker and interfaces

`/api/v1/forecast-plans` supplies creation and public metadata operations. Revision routes read saved versions, request explicit recomputation, prepare node artifacts and download PDF/data/JSON; `/adjustments` publishes revision-checked planning assumptions. The existing report-run surfaces provide progress, replay, initiating-guest clarification/cancellation and terminal outcomes.

Workflow version 3 uses the existing private worker/outbox/queue and report lease registry. Original report workflows 1 and 2 remain supported. Daily admission and two-workspace-job concurrency are shared; ordinary chat keeps its separate lease. A frozen planning policy allows at most 128 fits and 120 fitting seconds; ordinary reports retain 64 fits. Other existing report and TimesFM ceilings remain unchanged. Numerical baselines/allocation are bounded deterministic work, not hidden model fits.

`PLANNING_ENABLED=false` disables new job admission during a staged release. `FORECAST_PLAN_FIT_LIMIT` defaults to 128 and can reduce fitting capacity. Keep verified TimesFM flags and the larger `timeseries` profile unchanged. Release the compatible private worker before enabling public API admission, then release the frontend, following the deployment runbook. Example metric publication is separate from deployment.

## Explicit retention maintenance

The operator-only `uv run python -m app.admin purge-planning --confirm-demo-reset` command expires unpublished proposals after seven days and deleted forecast-plan families after their 30-day recovery period. It drains/fences workers and preserves plan families referenced by saved reports or dashboard pins. It is never run by startup, routine deployment or history reset. Inspect the deployment runbook before using operator credentials.
