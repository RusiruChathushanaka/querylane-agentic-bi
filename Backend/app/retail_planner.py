"""Explicit local sample plans for the larger dataset, never a Gemini fallback."""

import re

from app.models import (
    AnalysisPlan,
    FusionPlan,
    JoinKey,
    Projection,
    SourceQuery,
    VisualizationSpec,
)


def timeseries_plan(question, history, source):
    q = question.lower()
    years = re.findall(r"\b20[23][0-9]\b", q)
    year = years[0] if len(set(years)) == 1 else None
    previous = next(
        (
            m["text"].lower()
            for m in reversed(history)
            if m["role"] == "user" and m["text"].strip().lower() != q.strip()
        ),
        "",
    )
    if year is None and not years:
        prior_years = re.findall(r"\b20[23][0-9]\b", previous)
        year = prior_years[0] if len(set(prior_years)) == 1 else None
    if years and not any(
        w in q
        for w in (
            "revenue",
            "sales",
            "refund",
            "return",
            "target",
            "segment",
            "loyalty",
            "product",
            "categor",
            "rolling",
            "average",
        )
    ):
        q = previous + " " + q
    where = f" WHERE EXTRACT(YEAR FROM order_date)={year}" if year else ""
    month_where = f" WHERE month LIKE '{year}-%'" if year else ""
    queries, fusion = [], None
    title, chart, x, ys = "Monthly sales revenue", "line", "month", ["revenue"]
    assumptions = [
        "Local sample mode: deterministic read-only templates, not AI planning.",
        "Synthetic multi-year retail history; USD. Revenue is after discounts and before refunds/tax/shipping.",
        "The final month and latest refund/cohort observation windows may be incomplete.",
    ]

    def query(sql, database="bigquery"):
        return SourceQuery(source=database, sql=sql, purpose="Retrieve bounded time-series retail metrics")

    if source == "postgres":
        title, chart, x, ys = "Customers by segment", "bar", "segment", ["customers"]
        queries = [
            query(
                "SELECT segment,COUNT(*) customers FROM customer_profiles GROUP BY segment ORDER BY segment",
                "postgres",
            )
        ]
    elif "target" in q:
        title, chart, x, ys = (
            "Monthly regional revenue and targets",
            "table",
            "month",
            ["revenue", "target_revenue"],
        )
        queries = [
            query(f"SELECT month,region,SUM(revenue) revenue FROM sales_orders{where} GROUP BY month,region"),
            query(f"SELECT month,region,target_revenue FROM regional_targets{month_where}", "postgres"),
        ]
        fusion = FusionPlan(
            keys=[JoinKey(left="month", right="month"), JoinKey(left="region", right="region")],
            projections=[
                Projection(side="left", column="month", alias="month"),
                Projection(side="left", column="region", alias="region"),
                Projection(side="left", column="revenue", alias="revenue"),
                Projection(side="right", column="target_revenue", alias="target_revenue"),
            ],
            relationship="Declared business grain month AND region; full-month targets versus actual coverage.",
            confidence="declared",
            expected_cardinality="one-to-one",
        )
    elif "segment" in q or "loyalty" in q:
        field = "loyalty_tier" if "loyalty" in q else "segment"
        title, chart, x, ys = f"Revenue by {field.replace('_', ' ')}", "bar", field, ["revenue"]
        queries = [
            query(f"SELECT customer_id,SUM(revenue) revenue FROM sales_orders{where} GROUP BY customer_id"),
            query(f"SELECT customer_id,{field} FROM customer_profiles", "postgres"),
        ]
        fusion = FusionPlan(
            keys=[JoinKey(left="customer_id", right="customer_id")],
            projections=[
                Projection(side="right", column=field, alias=field),
                Projection(side="left", column="revenue", alias="revenue", aggregate="sum"),
            ],
            relationship="Customer identifier; profiles are current fixed synthetic attributes.",
            confidence="declared",
            expected_cardinality="one-to-one",
        )
    elif any(
        word in q
        for word in ("year over year", "year-over-year", "yoy", "month over month", "month-over-month", "mom")
    ):
        lag = 12 if any(w in q for w in ("year over year", "year-over-year", "yoy")) else 1
        label = "yoy" if lag == 12 else "mom"
        title, ys = f"Monthly revenue and {label.upper()} growth", ["revenue"]
        queries = [
            query(f"""WITH months AS (SELECT DISTINCT month FROM calendar), actual AS (
            SELECT month,SUM(revenue) revenue FROM sales_orders GROUP BY month), dense AS (
            SELECT m.month,COALESCE(a.revenue,0) revenue FROM months m LEFT JOIN actual a ON m.month=a.month), comparison AS (
            SELECT month,revenue,LAG(revenue,{lag}) OVER(ORDER BY month) previous_revenue FROM dense)
            SELECT month,revenue,previous_revenue,ROUND(100.0*(revenue-previous_revenue)/NULLIF(previous_revenue,0),2) {label}_percent
            FROM comparison{month_where} ORDER BY month""")
        ]
    elif any(word in q for word in ("rolling", "moving average", "7-day")):
        title, x, ys = "Daily revenue and seven-day average", "order_date", ["revenue", "rolling_7d"]
        output_filter = f" WHERE EXTRACT(YEAR FROM order_date)={year}" if year else ""
        queries = [
            query(f"""WITH actual AS (SELECT order_date,SUM(revenue) revenue FROM sales_orders GROUP BY order_date), dense AS (
            SELECT c.calendar_date order_date,COALESCE(a.revenue,0) revenue FROM calendar c LEFT JOIN actual a ON c.calendar_date=a.order_date), smoothed AS (
            SELECT order_date,revenue,AVG(revenue) OVER(ORDER BY order_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) rolling_7d FROM dense)
            SELECT order_date,revenue,rolling_7d FROM smoothed{output_filter} ORDER BY order_date""")
        ]
    elif "refund" in q or "return" in q:
        title, x, ys = "Monthly refunds by refund date", "month", ["refund_amount"]
        filter_ = f" WHERE EXTRACT(YEAR FROM return_date)={year}" if year else ""
        queries = [
            query(
                f"SELECT CAST(DATE_TRUNC(return_date,MONTH) AS STRING) month,SUM(refund_amount) refund_amount FROM sales_returns{filter_} GROUP BY month ORDER BY month"
            )
        ]
        assumptions.append("Refunds grouped by return_date, not the original order date.")
    elif "category" in q or "categor" in q or "product" in q:
        title, chart, x = "Revenue by product category", "bar", "category"
        queries = [
            query(
                f"SELECT p.category,SUM(i.line_revenue) revenue FROM sales_order_items i JOIN sales_products p ON i.product_id=p.product_id{where} GROUP BY p.category ORDER BY revenue DESC"
            )
        ]
    elif "total" in q or "kpi" in q:
        title, chart, x = "Total merchandise revenue", "kpi", None
        queries = [query(f"SELECT SUM(revenue) revenue,COUNT(*) orders FROM sales_orders{where}")]
    elif "daily" in q or "day" in q:
        title, x = "Daily merchandise revenue", "order_date"
        queries = [
            query(
                "WITH actual AS (SELECT order_date,SUM(revenue) revenue FROM sales_orders GROUP BY order_date) SELECT c.calendar_date order_date,COALESCE(a.revenue,0) revenue FROM calendar c LEFT JOIN actual a ON c.calendar_date=a.order_date"
                + (f" WHERE EXTRACT(YEAR FROM c.calendar_date)={year}" if year else "")
                + " ORDER BY order_date"
            )
        ]
    elif any(word in q for word in ("revenue", "sales", "month", "trend")):
        queries = [
            query(f"SELECT month,SUM(revenue) revenue FROM sales_orders{where} GROUP BY month ORDER BY month")
        ]
    else:
        return AnalysisPlan(
            title="Try a time-series sample",
            queries=[],
            clarification="Local sample mode supports monthly/daily sales, MoM/YoY, seven-day rolling averages, category revenue, refunds, customer segments, and regional targets. Enable Gemini for open-ended questions.",
            visualization=VisualizationSpec(type="table", title="Time-series sample questions"),
        )
    if source == "bigquery" and any(item.source == "postgres" for item in queries):
        return AnalysisPlan(
            title="Two sources required",
            queries=[],
            clarification="Choose All sources for this cross-database question.",
            visualization=VisualizationSpec(type="table", title="Source selection"),
        )
    return AnalysisPlan(
        title=title,
        queries=queries,
        fusion=fusion,
        assumptions=assumptions,
        visualization=VisualizationSpec(
            type=chart, title=title, x=x, y=ys, format="number" if "customers" in ys else "currency"
        ),
    )
