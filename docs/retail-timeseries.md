# Expanded retail history: generation, validation, and upload

The expanded dataset is an **additional source profile**, leaving the original nine-month demo and its historical result evidence intact. Data is synthetic, denominated in USD, and reproducible from a seed. No customer information is real.

The initial large bundle covers **2023-01-01 through 2026-09-30**:

| Source | Table | Rows |
| --- | --- | ---: |
| BigQuery | `sales_orders` | 573,348 |
| BigQuery | `sales_order_items` | 1,317,941 |
| BigQuery | `sales_returns` | 97,122 |
| BigQuery | `sales_products` | 200 |
| BigQuery | `calendar` | 1,369 |
| PostgreSQL | `retail_timeseries.customer_profiles` | 25,000 |
| PostgreSQL | `retail_timeseries.stores` | 24 |
| PostgreSQL | `retail_timeseries.regional_targets` | 180 |
| PostgreSQL | `retail_timeseries.store_targets` | 1,080 |
| PostgreSQL | `retail_timeseries.campaigns` | 180 |
| PostgreSQL | `retail_timeseries.promotions` | 180 |

The BigQuery tables live in the existing `project-e8b1593d-009a-4822-abf.agentic_bi_demo` dataset. PostgreSQL uses the existing `agentic-bi-demo-pg` instance and `agentic_bi` database with the new schema `retail_timeseries`. The original BigQuery `orders`, `order_items`, `products`, and `returns`, and PostgreSQL `retail.*`, are not modified.

See [the complete column/type dictionary](retail-timeseries-schema.md), generated bundle `schema.json`, and the canonical definitions in `Backend/app/retail_schema.py`. [The original schema guide](database-schema.md) remains a reference for the original demo.

## What makes this useful for time-series work

- Daily observations across 45 months, including several comparisons against the previous year.
- Weekly and annual demand patterns, deterministic growth, varying product mix, channels, discounts, and dated regional promotions.
- Multiple lines and quantities per order, historical sale prices/costs, and partial line refunds arriving 3–35 days after purchase.
- Customer signup dates, transaction region versus home region, stores, and full-month store/regional targets.
- A dense calendar with zero-sales days, Monday week starts, and paired ISO week/year fields.
- Explicitly injected synthetic anomalies: a zero-sales closure on 2024-02-29, reduced demand on 2025-06-10, a surge on 2025-11-28, and a spike on 2026-03-15. These are generated scenarios, not discoveries about real businesses or public holidays.

This supports descriptive trends, MoM/YoY growth, rolling averages, cohorts, product mix, merchandise margins, and analysis of refund timing. It does not itself train or deploy a forecasting model. Chronological train/validation/test splits and a stated forecast method are still required for forecasting; do not randomly split time-series rows or leak later refunds into earlier observation windows.

## 1. Generate an offline bundle

From `Backend/`, with dependencies installed through `uv sync --frozen`:

```bash
uv run python -m scripts.retail_data generate \
  --output ../data/retail-timeseries-20260930 \
  --start 2023-01-01 --end 2026-09-30 \
  --orders-per-day 300 --customers 25000 --products 200 --stores 24 --seed 42
```

The default parameters are those above. The base daily rate is modified by seasonality, growth, promotions, and deterministic variation, so it is not the final count per day. Dates are inclusive. Store count must be a multiple of four. Maximum supported settings and a five-million-base-order batch bound are checked before writing.

Generation streams batches to typed, compressed Parquet files rather than building the full fact tables in memory. The initial bundle is approximately **105 MB**. It contains one file per table, `manifest.json` with counts/checksums/ledger/date coverage, and `schema.json` with column definitions and logical keys. `data/` is Git-ignored; no large generated files or credentials are committed.

An existing output directory is never overwritten. Use a new dated directory for every generation attempt or extension. Generation and validation do not need cloud credentials or a model API.

## 2. Validate before uploading

```bash
uv run python -m scripts.retail_data validate \
  --bundle ../data/retail-timeseries-20260930 \
  --report ../docs/evaluation/retail-timeseries-local.json
```

Validation checks schemas, SHA-256 file checksums, row counts, unique keys, required fields, references, quantities, line/order arithmetic, refund bounds, customer acquisition dates, promotion matching, target reconciliation, complete calendar coverage, as-of refund cutoffs, and independent SQL totals. It also exercises a zero-filled rolling seven-day series. An unsuccessful check exits nonzero. Uploads repeat validation before making any database mutation.

The initial bundle has **$354,425,112.20** in merchandise revenue, **$19,558,027.70** in refunds through the as-of end, and **$334,867,084.50** in revenue minus those refunds. These are after-discount merchandise figures, not full accounting profit.

## 3. Review the upload plan

```bash
uv run python -m scripts.retail_data upload \
  --bundle ../data/retail-timeseries-20260930
```

Without `--apply`, this reads only local files and prints exact targets/counts. It does not request credentials, connect to a database, or create resources. The uploader targets only the existing dedicated demo project/dataset/instance and the new time-series namespaces. It has no public HTTP endpoint.

## 4. Upload to the dedicated cloud sources

Follow [the deployment guide](deployment-guide.md) for operator authentication and resource boundaries. The current user's request authorizes the initial new data load; the script remains an explicit operator action for future use.

```bash
uv run python -m scripts.retail_data upload \
  --bundle ../data/retail-timeseries-20260930 \
  --apply \
  --report ../docs/evaluation/retail-timeseries-cloud.json
```

The tool captures the existing signed-in `gcloud` operator's short-lived credentials in memory, reads the existing demo PostgreSQL administrator secret, and connects with the Cloud SQL Python Connector. It never resets database passwords or writes credential files. No project IAM binding is added. The existing BigQuery dataset reader access is reused; the existing `bi_reader` receives only schema USAGE and table SELECT on `retail_timeseries`. No role is created and no old permissions are removed.

BigQuery facts/calendar are partitioned by their business/event date; facts are clustered by relevant region/store/customer or product/order keys. Products are clustered by category. Temporary staging tables are uniquely owned and expire after 24 hours; known staging tables are deleted after an attempt. Operator MERGE queries have a 2 GiB maximum billed-byte setting; application query budgets remain separate.

PostgreSQL dimensions load through temporary COPY staging tables inside one transaction, with primary keys, appropriate foreign keys, and analytic indexes. Existing IDs with different record hashes cause rejection. BigQuery publishes its five data tables in one insert-only MERGE transaction. Repeating a completed bundle must not add duplicates or replace records.

There is no distributed transaction across the two services. A fenced BigQuery ingestion state marks the new profile `loading`, `failed`, or `ready`. A failure can leave one source ahead; rerun the same bundle to finish. New-profile application queries reject non-ready state. Stop traffic to this profile while importing: queries already running at the moment an import begins cannot be recalled, and independent database reads are not a global snapshot. Other profiles remain independent.

Keep the generation settings and initial start date fixed for an existing upload namespace. The registry rejects changing those settings or moving the as-of end backward. The uploader does not delete rows, truncate tables, or silently alter existing data-table schemas. A new generator/schema version needs an explicit migration or a new namespace.

For a **local PostgreSQL** copy of the operational dimensions, set `RETAIL_POSTGRES_ADMIN_DSN` in the environment and add `--target postgres-local --apply`. The local target creates `retail_timeseries` without granting a reader role. The same Parquet bundle can be used to query both logical sources locally through the application; the local target does not emulate the BigQuery cloud service.

## 5. Add more dates later

Regenerate from the same original start through a later as-of end, then validate and upload:

```bash
uv run python -m scripts.retail_data extend \
  --from-bundle ../data/retail-timeseries-20260930 \
  --end 2026-12-31 \
  --output ../data/retail-timeseries-20261231

uv run python -m scripts.retail_data validate \
  --bundle ../data/retail-timeseries-20261231

uv run python -m scripts.retail_data upload \
  --bundle ../data/retail-timeseries-20261231

uv run python -m scripts.retail_data upload \
  --bundle ../data/retail-timeseries-20261231 --apply
```

The `extend` command carries forward seed, dimensions, daily rate, and start date. Each day has its own deterministic random stream, and timestamps/record hashes for previously generated rows remain stable. A later as-of end adds new orders and late-arriving refunds for earlier orders. Regenerating the full window is deliberate: generating only future order dates would miss those delayed refunds. Dates beyond today are synthetic scenarios, not observed history.

## 6. Use the expanded profile in the application

For an offline local backend, run from the repository root:

```bash
DATA_PROFILE=timeseries \
RETAIL_BUNDLE_PATH="$PWD/data/retail-timeseries-20260930" \
SOURCE_ROW_LIMIT=30000 \
Backend/.venv/bin/python -m uvicorn app.main:app --app-dir Backend \
  --host 127.0.0.1 --port 8003
```

The backend's explicit sample mode supports monthly/daily revenue, MoM/YoY, rolling averages, category sales, refunds, customer segments, and targets. Enable Gemini separately for open-ended analysis. Parquet is scanned through Arrow/DuckDB without loading the full fact tables into Python lists. Configure the frontend's runtime `BACKEND_URL` to reach that backend and include its origin in `ALLOWED_ORIGINS`.

For cloud source access, use `DATA_PROFILE=timeseries`, `DATA_BACKEND=cloud`, and the existing source credentials. The profile derives PostgreSQL schema `retail_timeseries`, advertises five BigQuery and six PostgreSQL tables, and restricts SQL to that profile's allowlist. The UI's date label and agent/voice/skill-author context reflect the active profile. Runs/artifacts record their data profile; previously stored results remain unchanged.

Use `SOURCE_ROW_LIMIT=30000` for the 25,000-customer cross-source dimension. This is an explicit increase from the original profile's 10,000-row setting. The 16 MiB byte bounds, incomplete-input rejection, 50,000-row fusion output cap, 10-second fusion deadline, preview pagination, read-only SQL guards, and BigQuery scan limit remain in force. Aggregate facts in source SQL; do not retrieve hundreds of thousands of raw orders for fusion. Large queries without filtering/aggregation can still fail those controls.

An authorized Cloud Run release uses:

```bash
python3 infra/deploy.py --service backend \
  --frontend-url https://agentic-bi-frontend-wekihucn7q-as.a.run.app \
  --data-profile timeseries
```

Uploading data **does not deploy application code or switch the serving Cloud Run revision**. Deploy the backend profile and frontend changes through the deployment guide when requested. The helper's default profile remains `legacy`; pass `--data-profile timeseries` on subsequent releases to retain the new source selection. Optional schema-embedding refresh is `DATA_PROFILE=timeseries uv run python -m app.admin index-schema` from `Backend/`; it writes separate profile-tagged chunks in the existing named Firestore database, and is not part of generation/upload. Full-schema retrieval remains the documented fallback.

Once the cloud application is running the time-series profile, ordinary later date extensions do not require a code deployment. The same source tables gain new records, and the analysis service reads the published as-of range from ingestion metadata. A local Parquet preview instead needs restarting with the new bundle path. The local Gemini preview uses temporary operator credentials in memory and requires a restart after they expire; its chats are ephemeral and model calls are billable.

## Queries and definitions

Try these questions in the expanded workspace:

1. Show monthly revenue and year-over-year growth.
2. Show daily revenue with a seven-day rolling average, including zero-sales dates.
3. Compare monthly regional sales with their targets.
4. Compare revenue by product category across years.
5. Compare refunds by refund month versus original purchase month.
6. Show customer signup cohorts and first-purchase dates.
7. Calculate merchandise margin by channel before returns, then state the return treatment.

`gross_sales`/`gross_amount` are before discounts. `revenue`/`line_revenue` are after discounts and before tax/shipping/refunds. `total_paid` adds tax and shipping. Refund-date net revenue subtracts refunds processed in the same date window; purchase-cohort net revenue follows refunds for orders purchased in the window. Margin requires a stated return/cost reversal treatment and excludes operating expenses.

Segment and loyalty are fixed synthetic profile attributes, not historical customer-state snapshots. A customer’s first order in this dataset is a first observed purchase, not proof of their lifetime first purchase; some signups predate the sales history. Campaign IDs indicate synthetic last-touch association; campaign effects are not causal proof. Targets and campaign spend are full-month values even when an as-of end creates a partial observed month. ISO week comparisons require the matching ISO year. Leading rolling windows contain fewer observations; leading YoY periods without a prior year should remain NULL.
