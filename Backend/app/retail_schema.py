"""Versioned, explicit sales schema shared by generation, validation, and ingestion."""

from dataclasses import dataclass

import pyarrow as pa

VERSION = "retail-timeseries-v1"
PG_SCHEMA = "retail_timeseries"


@dataclass(frozen=True)
class Column:
    name: str
    kind: str = "STRING"
    nullable: bool = False


@dataclass(frozen=True)
class Table:
    name: str
    source: str
    key: tuple[str, ...]
    description: str
    columns: tuple[Column, ...]
    partition: str | None = None
    cluster: tuple[str, ...] = ()

    def arrow_schema(self):
        kinds = {
            "STRING": pa.string(),
            "INT64": pa.int64(),
            "NUMERIC": pa.decimal128(18, 2),
            "DATE": pa.date32(),
            "TIMESTAMP": pa.timestamp("us", tz="UTC"),
            "BOOL": pa.bool_(),
        }
        return pa.schema([pa.field(c.name, kinds[c.kind], nullable=c.nullable) for c in self.columns])


def cols(*values):
    result = []
    for value in values:
        parts = value.split(":")
        result.append(Column(parts[0], parts[1] if len(parts) > 1 else "STRING", len(parts) > 2))
    return tuple(result + [Column("record_hash")])


TABLES = (
    Table(
        "sales_products",
        "bigquery",
        ("product_id",),
        "Product dimension: one product. unit_price is catalogue price; use sales_order_items.unit_price for historical prices. Categories, brands, and unit_cost enable product mix and merchandise margin, not full business profit.",
        cols(
            "product_id",
            "product_name",
            "category",
            "brand",
            "unit_price:NUMERIC",
            "unit_cost:NUMERIC",
            "launched_on:DATE",
        ),
        cluster=("category",),
    ),
    Table(
        "calendar",
        "bigquery",
        ("calendar_date",),
        "Dense daily date spine, including zero-sales dates. Join calendar_date to order_date; LEFT JOIN daily aggregates and COALESCE missing sales to zero. week_start is Monday, ISO week/year are paired, fiscal year begins January. is_promotion_day marks the synthetic promotion calendar, not national holidays.",
        cols(
            "calendar_date:DATE",
            "year:INT64",
            "quarter:INT64",
            "month",
            "month_start:DATE",
            "week_start:DATE",
            "iso_year:INT64",
            "iso_week:INT64",
            "day_of_week:INT64",
            "is_weekend:BOOL",
            "is_promotion_day:BOOL",
        ),
        "calendar_date",
    ),
    Table(
        "sales_orders",
        "bigquery",
        ("order_id",),
        "One completed order; status is exactly lowercase 'completed'. Multi-year daily synthetic history with weekly/annual seasonality, growth, promotions and named anomalies. order_timestamp is UTC; order_date/month are Singapore business dates. revenue is merchandise sales AFTER discounts, BEFORE refunds/tax/shipping. gross_sales is before discounts; total_paid includes tax/shipping. region is transaction/store region, not necessarily the customer's home region. All currency USD. Never sum order revenue after a many-line item join without re-aggregation.",
        cols(
            "order_id",
            "customer_id",
            "store_id",
            "order_timestamp:TIMESTAMP",
            "order_date:DATE",
            "month",
            "region",
            "channel",
            "currency",
            "gross_sales:NUMERIC",
            "discount_amount:NUMERIC",
            "revenue:NUMERIC",
            "tax_amount:NUMERIC",
            "shipping_amount:NUMERIC",
            "total_paid:NUMERIC",
            "units:INT64",
            "status",
            "campaign_id:STRING:nullable",
        ),
        "order_date",
        ("region", "store_id", "customer_id"),
    ),
    Table(
        "sales_order_items",
        "bigquery",
        ("order_item_id",),
        "One line per order/product occurrence, with multiple lines per order. quantity, historical unit_price/unit_cost, gross_amount, allocated line discount, line_revenue and cost_amount. Sum line_revenue for category/channel product analysis; order_date duplicates the parent's business date for partition pruning. promotion_id may be null. Merchandise margin before returns = line_revenue-cost_amount; this is not accounting profit.",
        cols(
            "order_item_id",
            "order_id",
            "order_date:DATE",
            "product_id",
            "quantity:INT64",
            "unit_price:NUMERIC",
            "unit_cost:NUMERIC",
            "gross_amount:NUMERIC",
            "discount_amount:NUMERIC",
            "line_revenue:NUMERIC",
            "cost_amount:NUMERIC",
            "promotion_id:STRING:nullable",
        ),
        "order_date",
        ("product_id", "order_id"),
    ),
    Table(
        "sales_returns",
        "bigquery",
        ("return_id",),
        "One partial/full line refund. Links to order_item_id and order_id. return_date is the actual refund business date; order_date is original purchase date. refund_amount refunds discounted merchandise only, excluding tax/shipping. returned_cost reverses cost for returned units. Refund-date net revenue differs from order-cohort net revenue; clarify which is requested. Later generated snapshots add delayed returns without changing existing sales.",
        cols(
            "return_id",
            "order_id",
            "order_item_id",
            "product_id",
            "order_date:DATE",
            "return_date:DATE",
            "quantity:INT64",
            "refund_amount:NUMERIC",
            "returned_cost:NUMERIC",
            "reason",
        ),
        "return_date",
        ("order_id", "product_id"),
    ),
    Table(
        "stores",
        "postgres",
        ("store_id",),
        "One fulfillment/retail store, with region, store_format and opened_on. Online orders also have a fulfillment store. Join store_id; never use region as a unique store key.",
        cols("store_id", "store_name", "region", "store_format", "opened_on:DATE"),
    ),
    Table(
        "customer_profiles",
        "postgres",
        ("customer_id",),
        "One synthetic customer, with signup_date, home region, acquisition_channel, segment and loyalty_tier. segment/tier are fixed synthetic attributes, not as-of historical snapshots. For cohorts use signup_date; calculate first observed purchase from actual orders if asked; this is not necessarily the lifetime first purchase. customer_id is the cross-source key; names are not keys.",
        cols(
            "customer_id",
            "customer_name",
            "region",
            "segment",
            "loyalty_tier",
            "signup_date:DATE",
            "acquisition_channel",
        ),
    ),
    Table(
        "regional_targets",
        "postgres",
        ("month", "region"),
        "One full calendar-month target per region. Join sales aggregated at month AND region; targets for a partial final month remain full-month targets. Revenue target is after discounts and before refunds, tax and shipping.",
        cols("month", "region", "target_revenue:NUMERIC"),
    ),
    Table(
        "store_targets",
        "postgres",
        ("month", "store_id"),
        "One full-month target per store. Sum store targets to reconcile regional_targets. Join sales at month AND store_id; partial-month actuals are not comparable to full-month targets without disclosure.",
        cols("month", "store_id", "region", "target_revenue:NUMERIC"),
    ),
    Table(
        "campaigns",
        "postgres",
        ("campaign_id",),
        "One monthly regional synthetic campaign with start/end dates and spend. Explicit campaign_id on orders represents last-touch synthetic association only, not proven incremental/causal marketing impact. Campaign spend is full-month even if generated order coverage ends mid-month.",
        cols(
            "campaign_id",
            "campaign_name",
            "region_name",
            "start_date:DATE",
            "end_date:DATE",
            "channel",
            "spend:NUMERIC",
        ),
    ),
    Table(
        "promotions",
        "postgres",
        ("promotion_id",),
        "One dated regional promotion. discount_percent is 0-100, not a fraction. Join order-item promotion_id to avoid range-join fan-out. Promotion calendars are synthetic and do not identify public holidays.",
        cols(
            "promotion_id",
            "campaign_id",
            "region",
            "start_date:DATE",
            "end_date:DATE",
            "discount_percent:NUMERIC",
            "promotion_name",
        ),
    ),
)

BY_NAME = {table.name: table for table in TABLES}
SOURCE_TABLES = {
    source: [t.name for t in TABLES if t.source == source] for source in ("bigquery", "postgres")
}


def schema_export():
    from dataclasses import asdict

    return {"version": VERSION, "postgres_schema": PG_SCHEMA, "tables": [asdict(t) for t in TABLES]}
