from decimal import Decimal

import pytest

from app.config import Settings
from app.connectors import Connectors
from app.errors import AppError
from app.fixtures import retail_data
from app.sql_guard import validate_sql

PROJECT = "project-e8b1593d-009a-4822-abf"
DATASET = "agentic_bi_demo"


@pytest.mark.parametrize(
    "source,sql",
    [
        ("postgres", "DELETE FROM retail.customer_profiles"),
        ("postgres", "SELECT * FROM retail.customer_profiles; DROP TABLE retail.customer_profiles"),
        (
            "postgres",
            "WITH changed AS (DELETE FROM retail.customer_profiles RETURNING *) SELECT * FROM changed",
        ),
        ("postgres", "SELECT pg_read_file('/etc/passwd') FROM retail.customer_profiles"),
        ("postgres", "SELECT pg_sleep(100) FROM retail.customer_profiles"),
        ("postgres", "SELECT * FROM information_schema.tables"),
        ("postgres", "SELECT * INTO stolen FROM retail.customer_profiles"),
        ("postgres", "SELECT * FROM retail.customer_profiles FOR UPDATE"),
        ("postgres", "SELECT * FROM public.customer_profiles"),
        ("postgres", "SELECT * FROM read_csv('/etc/passwd')"),
        ("postgres", "SELECT public.sum(customer_id) FROM retail.customer_profiles"),
        ("bigquery", "SELECT * FROM enterprise_bi.orders"),
        ("bigquery", "SELECT * FROM `other-project.agentic_bi_demo.orders`"),
        ("bigquery", "SELECT EXTERNAL_QUERY('connection', 'SELECT 1') FROM orders"),
        ("bigquery", "EXPORT DATA OPTIONS(uri='gs://example/*') AS SELECT * FROM orders"),
        ("bigquery", "SELECT * FROM orders_2026*"),
        ("bigquery", "CALL dangerous()"),
        ("bigquery", "SELECT 1"),
    ],
)
def test_forbidden_sql(source, sql):
    with pytest.raises(AppError):
        validate_sql(sql, source, PROJECT, DATASET)


def test_ctes_cannot_hide_external_tables():
    with pytest.raises(AppError):
        validate_sql(
            "WITH approved AS (SELECT * FROM enterprise_bi.orders) SELECT * FROM approved",
            "bigquery",
            PROJECT,
            DATASET,
        )


@pytest.mark.parametrize("month", range(1, 10))
async def test_monthly_totals_against_independent_python_calculation(month):
    data = retail_data()
    month_key = f"2026-{month:02}"
    expected = sum(row["revenue"] for row in data["orders"] if row["month"] == month_key)
    result = await Connectors(Settings()).query(
        "bigquery", f"SELECT SUM(revenue) AS revenue FROM orders WHERE month='{month_key}'", f"test{month}"
    )
    assert result.complete
    assert result.rows[0]["revenue"] == expected


@pytest.mark.parametrize("region", ["North", "South", "East", "West"])
async def test_region_totals(region):
    expected = sum(row["revenue"] for row in retail_data()["orders"] if row["region"] == region)
    result = await Connectors(Settings()).query(
        "bigquery", f"SELECT SUM(revenue) AS revenue FROM orders WHERE region='{region}'", "region"
    )
    assert result.rows[0]["revenue"] == expected


@pytest.mark.parametrize("month", range(1, 10))
async def test_monthly_targets(month):
    key = f"2026-{month:02}"
    expected = sum(row["target_revenue"] for row in retail_data()["regional_targets"] if row["month"] == key)
    result = await Connectors(Settings()).query(
        "postgres",
        f"SELECT SUM(target_revenue) AS target_revenue FROM regional_targets WHERE month='{key}'",
        "targets",
    )
    assert result.rows[0]["target_revenue"] == expected


@pytest.mark.parametrize("category", ["Accessories", "Electronics", "Footwear", "Apparel"])
async def test_category_totals(category):
    data = retail_data()
    products = {p["product_id"] for p in data["products"] if p["category"] == category}
    expected = sum(item["line_revenue"] for item in data["order_items"] if item["product_id"] in products)
    query = f"SELECT SUM(i.line_revenue) AS revenue FROM order_items i JOIN products p ON i.product_id=p.product_id WHERE p.category='{category}'"
    result = await Connectors(Settings()).query("bigquery", query, "category")
    assert result.rows[0]["revenue"] == expected


@pytest.mark.parametrize("segment", ["New", "Returning"])
async def test_customer_segment_counts(segment):
    expected = sum(customer["segment"] == segment for customer in retail_data()["customer_profiles"])
    result = await Connectors(Settings()).query(
        "postgres",
        f"SELECT COUNT(*) AS customers FROM customer_profiles WHERE segment='{segment}'",
        "segment",
    )
    assert result.rows[0]["customers"] == expected


async def test_refunds_and_order_count():
    data = retail_data()
    connector = Connectors(Settings())
    returns = await connector.query(
        "bigquery", "SELECT SUM(refund_amount) AS refunds FROM returns", "refunds"
    )
    count = await connector.query("bigquery", "SELECT COUNT(*) AS orders FROM orders", "orders")
    assert returns.rows[0]["refunds"] == sum(row["refund_amount"] for row in data["returns"])
    assert count.rows[0]["orders"] == 720
    assert sum(row["revenue"] for row in data["orders"]) == Decimal("118951.00")


async def test_row_limit_is_explicit_and_no_billing_assumption():
    result = await Connectors(Settings(source_row_limit=2)).query(
        "bigquery", "SELECT order_id FROM orders", "bounded"
    )
    assert result.row_count == 2
    assert not result.complete


async def test_empty_results_are_complete():
    result = await Connectors(Settings()).query(
        "bigquery", "SELECT order_id FROM orders WHERE month='1900-01'", "empty"
    )
    assert result.complete and result.rows == []


@pytest.mark.parametrize("source,table", [("bigquery", "orders"), ("postgres", "customer_profiles")])
def test_logical_filters_are_operators_not_unapproved_functions(source, table):
    sql = (
        f"SELECT * FROM {table} WHERE (customer_id = 'C1' OR customer_id = 'C2') AND customer_id IS NOT NULL"
    )
    guarded = validate_sql(sql, source, PROJECT, DATASET)
    assert " AND " in guarded and " OR " in guarded


@pytest.mark.parametrize(
    "predicate",
    [
        "customer_id = 'C1' AND pg_sleep(10) = 0",
        "customer_id = 'C1' OR pg_read_file('/etc/passwd') IS NOT NULL",
    ],
)
def test_logical_filters_do_not_hide_unsafe_nested_calls(predicate):
    with pytest.raises(AppError, match="not approved"):
        validate_sql(f"SELECT * FROM customer_profiles WHERE {predicate}", "postgres", PROJECT, DATASET)
