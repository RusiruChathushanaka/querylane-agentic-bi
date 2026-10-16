# Insightful charts and saved-result exploration

Charts present an immutable analysis artifact. They do not execute SQL, call Gemini, change source filters, or modify shared evidence. Text and voice answers use the same renderer.

## Visitor workflow

- Inspect exact values with hover or arrow keys. Click/tap a mark, or choose **Inspect observation**, to pin its details.
- **Explore this** drafts a follow-up for review. It never submits automatically. An existing composer draft is preserved; the visitor can copy the proposed chart question instead.
- Change the primary measure, show/hide series, choose a date range, or reorder/select Top 5/10/20 category observations. Reset restores the original view. Range selection operates on returned calendar buckets; it cannot request a new SQL grain.
- Expand opens the same controls in a larger dialog. Currency and percentage series appear in separate plots. Target/comparison lines use dashes and explicit labels.
- Settings → Analysis & charts contains **Automatic chart highlights** and **Show chart comparisons**, both enabled by default. Preferences remain browser-local; old storage gains the defaults automatically.
- PNG confirmation describes the current visible chart and includes units, series labels, selected scope, sampling, omissions, and partial-result notes. CSV confirmation describes the **full saved result**, independent of chart range, Top N, or downsampling. Text cells that could execute spreadsheet formulas are escaped.

## Presentation contract

`VisualizationSpec` accepts optional version-2 metadata: dimension kind, calendar granularity, known partial periods, and up to four measure definitions. Measures declare their column, label, unit, currency, percentage scale, additivity, comparator relationship, and established business direction. References are checked against actual final columns. Unknown rate scales are shown as ordinary numbers and cannot enable additive totals or composition. Existing artifacts are never rewritten and use conservative legacy defaults.

New artifacts also capture available published source date boundaries. A known partial first/last calendar bucket is excluded from period-change comparisons. Query-specific partial buckets must be declared by the planner; the presentation service cannot reconstruct arbitrary SQL filters from a result alone. Unknown business direction does not receive good/bad colors.

- `GET /api/v1/artifacts/{id}/chart-data`: returns versioned presentation rows, validated metadata, deterministic insights, annotations, selected scope, and coverage.
- Parameters: `start`/`end` ISO dates, a valid `primary` measure, `order=value_desc|value_asc|label|original`, `top=5|10|20`, and an existing chart `view`.
- `GET /api/v1/artifacts/{id}/export.csv`: validates saved pages before streaming a CSV response; missing pages produce an error instead of an apparently successful partial download.

Both endpoints use the existing backend-only artifact store. No database migration, Firestore index, new IAM grant, model call, or charting dependency is required.

## Truthful coverage and calculations

The presentation service reads every saved artifact page, bounded to 50,000 rows / 64 MiB / 1,024 pages, with two concurrent materializations per instance. Existing connector scan/row/byte and fusion controls are unchanged. Result-page count discrepancies or missing pages fail explicitly.

The old first-60-row rule is removed. Up to 2,000 observations render directly; larger time series use deterministic shared-index min/max buckets that retain endpoints and null boundaries across series. Sampling never sums or interpolates data. Excessive gap boundaries, ambiguous time-series grains, or oversized labels produce a table/narrow-range explanation. Plot payloads are capped at 2 MiB. Summaries use all selected saved rows before sampling or Top N.

Insight chips are deterministic, limited to three, and describe observed peaks/leaders, an adjacent complete period comparison, a valid category share, or an explicit target comparison. Decimal calculations precede JSON serialization. Rates use percentage-point labels for absolute movement. Zero baselines have no percentage change. Missing observations remain gaps; zero sales remain zero. Duplicate category labels retain additional available dimensions (for example region and month) without reaggregation; ambiguous duplicates require a clearer query.

Composition requires 2–6 unique categories, one nonnegative additive measure, a positive denominator, and complete inputs. No omitted categories are silently grouped into Other. Partial source results suppress population totals, shares, and period-change claims, while retaining explicitly labeled observed values. A peak is not a statistical anomaly or a causal explanation.

## Verification and release

Backend tests cover full histories, calendar gaps, partial results/buckets, rate scales, targets, sampling, compound category labels, invalid parameters, missing pages, and CSV injection. Frontend tests cover formatting, comparison labels, coverage notes, follow-up drafts, and preference migration. Browser verification checks the generated retail dataset, exports, keyboard access, draft preservation, range controls, themes, and narrow layouts.

Follow the [deployment guide](deployment-guide.md) for a requested release, explicitly preserving the intended data profile. This feature does not authorize data uploads, history reset, Cloud Run deployment, or GitHub publication.
