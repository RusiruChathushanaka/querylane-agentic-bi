"""Independent SQL reconciliation of generated source files, without model judgment."""

from pathlib import Path

import duckdb
import pyarrow.dataset as ds

from app.retail_generator import read_manifest
from app.retail_schema import TABLES


def validate_bundle(directory: Path):
    manifest = read_manifest(directory)
    checks = []
    with duckdb.connect(
        ":memory:", config={"enable_external_access": False, "threads": 2, "memory_limit": "1GB"}
    ) as db:
        for table in TABLES:
            db.register(table.name, ds.dataset(directory / f"{table.name}.parquet", format="parquet"))
            key = ",".join(f'"{k}"' for k in table.key)
            nulls = " OR ".join(f'"{c.name}" IS NULL' for c in table.columns if not c.nullable)
            count, unique, missing = db.execute(
                f'SELECT COUNT(*), COUNT(DISTINCT ({key})), COUNT(*) FILTER(WHERE {nulls}) FROM "{table.name}"'
            ).fetchone()
            checks.append(
                {"check": f"{table.name}: keys / required fields", "passed": count == unique and missing == 0}
            )

        def check(name, sql):
            invalid = db.execute(sql).fetchone()[0]
            checks.append({"check": name, "invalid_rows": invalid, "passed": invalid == 0})

        check(
            "Every order line has an order and a product",
            "SELECT COUNT(*) FROM sales_order_items i LEFT JOIN sales_orders o USING(order_id) LEFT JOIN sales_products p USING(product_id) WHERE o.order_id IS NULL OR p.product_id IS NULL OR i.order_date <> o.order_date",
        )
        check(
            "Order customers/stores/campaigns exist and customers signed up before purchase",
            "SELECT COUNT(*) FROM sales_orders o LEFT JOIN customer_profiles c USING(customer_id) LEFT JOIN stores s USING(store_id) LEFT JOIN campaigns m USING(campaign_id) WHERE c.customer_id IS NULL OR s.store_id IS NULL OR c.signup_date > o.order_date OR s.region <> o.region OR (o.campaign_id IS NOT NULL AND (m.campaign_id IS NULL OR o.order_date NOT BETWEEN m.start_date AND m.end_date OR o.region <> m.region_name))",
        )
        check(
            "Order monetary totals equal sum of lines",
            "WITH lines AS (SELECT order_id, SUM(line_revenue) revenue, SUM(gross_amount) gross, SUM(discount_amount) discount, SUM(quantity) units FROM sales_order_items GROUP BY order_id) SELECT COUNT(*) FROM sales_orders o LEFT JOIN lines i USING(order_id) WHERE i.order_id IS NULL OR o.revenue <> i.revenue OR o.gross_sales <> i.gross OR o.discount_amount <> i.discount OR o.units <> i.units OR o.revenue <> o.gross_sales-o.discount_amount OR o.total_paid <> o.revenue+o.tax_amount+o.shipping_amount",
        )
        check(
            "Line arithmetic, quantities, and historical costs",
            "SELECT COUNT(*) FROM sales_order_items WHERE quantity < 1 OR unit_price < 0 OR unit_cost < 0 OR gross_amount <> quantity*unit_price OR cost_amount <> quantity*unit_cost OR line_revenue <> gross_amount-discount_amount OR discount_amount NOT BETWEEN 0 AND gross_amount",
        )
        check(
            "Returns reference valid lines, dates, quantities and bounded refunds",
            "SELECT COUNT(*) FROM sales_returns r LEFT JOIN sales_order_items i USING(order_item_id) WHERE i.order_item_id IS NULL OR r.order_id <> i.order_id OR r.product_id <> i.product_id OR r.order_date <> i.order_date OR r.return_date <= r.order_date OR r.quantity NOT BETWEEN 1 AND i.quantity OR r.refund_amount NOT BETWEEN 0 AND i.line_revenue OR r.returned_cost <> r.quantity*i.unit_cost",
        )
        check(
            "Total returned quantity and refund do not exceed a line",
            "SELECT COUNT(*) FROM (SELECT i.order_item_id FROM sales_order_items i JOIN sales_returns r USING(order_item_id) GROUP BY i.order_item_id,i.quantity,i.line_revenue HAVING SUM(r.quantity)>i.quantity OR SUM(r.refund_amount)>i.line_revenue)",
        )
        check(
            "Promotion IDs match actual dates and regions",
            "SELECT COUNT(*) FROM sales_order_items i JOIN sales_orders o USING(order_id) LEFT JOIN promotions p USING(promotion_id) WHERE i.promotion_id IS NOT NULL AND (p.promotion_id IS NULL OR o.order_date NOT BETWEEN p.start_date AND p.end_date OR o.region <> p.region)",
        )
        check(
            "Store targets reconcile regional targets",
            "WITH t AS (SELECT month,region,SUM(target_revenue) target_total FROM store_targets GROUP BY month,region) SELECT COUNT(*) FROM t FULL OUTER JOIN regional_targets r USING(month,region) WHERE t.target_total IS DISTINCT FROM r.target_revenue",
        )
        check(
            "Orders have completed status, USD currency and matching month",
            "SELECT COUNT(*) FROM sales_orders WHERE status<>'completed' OR currency<>'USD' OR month<>strftime(order_date,'%Y-%m')",
        )
        check(
            "Calendar covers every business date exactly once",
            "SELECT COUNT(*) FROM sales_orders o LEFT JOIN calendar c ON o.order_date=c.calendar_date WHERE c.calendar_date IS NULL",
        )
        start, end = manifest["parameters"]["start"], manifest["parameters"]["end"]
        count, first, last = db.execute(
            "SELECT COUNT(*),MIN(calendar_date),MAX(calendar_date) FROM calendar"
        ).fetchone()
        from datetime import date

        checks.append(
            {
                "check": "Dense date spine and requested date bounds",
                "passed": str(first) == start
                and str(last) == end
                and count == (date.fromisoformat(end) - date.fromisoformat(start)).days + 1,
            }
        )
        check(
            "Refunds do not look ahead beyond the as-of end",
            f"SELECT COUNT(*) FROM sales_returns WHERE return_date > DATE '{end}'",
        )
        totals = db.execute(
            "SELECT SUM(revenue),SUM(gross_sales),SUM(discount_amount),SUM(units) FROM sales_orders"
        ).fetchone()
        refund = db.execute("SELECT COALESCE(SUM(refund_amount),0) FROM sales_returns").fetchone()[0]
        expected = manifest["summary_cents"]
        checks.append(
            {
                "check": "Independent SQL totals reconcile generator ledger",
                "passed": [int((v or 0) * 100) for v in totals[:3]]
                == [expected["revenue"], expected["gross_sales"], expected["discounts"]]
                and int(totals[3] or 0) == expected["units"]
                and int(refund * 100) == expected["refunds"],
            }
        )
        monthly = db.execute(
            "SELECT month,COUNT(*) orders,SUM(revenue) revenue FROM sales_orders GROUP BY month ORDER BY month"
        ).fetchall()
        checks.append(
            {
                "check": "Independent monthly aggregates reconcile ledger",
                "passed": all(
                    n == manifest["monthly"][m]["orders"]
                    and int(value * 100) == manifest["monthly"][m]["revenue_cents"]
                    for m, n, value in monthly
                ),
            }
        )
        # Numeric time-series reference SQL exercises window functions and zero filling.
        series = db.execute(
            "WITH daily AS (SELECT order_date,SUM(revenue) revenue FROM sales_orders GROUP BY order_date) SELECT c.calendar_date,COALESCE(d.revenue,0) revenue,AVG(COALESCE(d.revenue,0)) OVER(ORDER BY c.calendar_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) rolling_7d FROM calendar c LEFT JOIN daily d ON c.calendar_date=d.order_date ORDER BY c.calendar_date"
        ).fetchall()
        checks.append({"check": "Zero-filled seven-day rolling series", "passed": len(series) == count})
    report = {
        "version": manifest["version"],
        "passed": all(c["passed"] for c in checks),
        "checks": checks,
        "tables": {n: f["rows"] for n, f in manifest["files"].items()},
        "revenue": str(totals[0] or 0),
        "refunds": str(refund),
        "net_revenue_refund_date": str((totals[0] or 0) - refund),
        "monthly_revenue": [{"month": m, "orders": n, "revenue": str(value)} for m, n, value in monthly],
        "daily_points": len(series),
    }
    return report
