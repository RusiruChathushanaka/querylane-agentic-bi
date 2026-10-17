"""Approved same-grain target comparison over a frozen revenue definition."""

import calendar
from datetime import date

from app.metrics import compile_metric
from app.models import AnalysisPlan, FusionPlan, SourceQuery, VisualizationSpec


def target_plan(ai, selected, scope, source):
    def clarify(message):
        return AnalysisPlan(
            title="Clarify target comparison",
            visualization=VisualizationSpec(type="table", title="Target comparison"),
            clarification=message,
        )

    if (
        source != "all"
        or len(selected) != 1
        or selected[0]["definition"]["formula"].get("measure") != "revenue"
        or selected[0]["definition"]["time_basis"] != "order_date"
    ):
        return clarify(
            "Revenue target comparisons require both sources and the published order-date merchandise revenue definition."
        )
    if (
        scope.dimension not in {None, "region", "store"}
        or scope.grain not in {"month", "total"}
        or scope.filters
    ):
        return clarify(
            "Choose an unfiltered monthly, regional or store revenue target comparison. More specific comparisons can be requested explicitly as ad hoc analysis."
        )
    coverage = ai.connectors.coverage
    if not coverage:
        return clarify("Source coverage is required before comparing full-month targets.")
    start, end = scope.start or date.fromisoformat(coverage[0]), scope.end or date.fromisoformat(coverage[1])
    if start.day != 1 or end.day != calendar.monthrange(end.year, end.month)[1]:
        return clarify(
            "Targets cover full months. Select month-start through month-end to compare equivalent periods."
        )
    actual = compile_metric(
        selected[0],
        ai.settings.bigquery_dataset,
        start=start,
        end=end,
        dimension=scope.dimension,
        grain=scope.grain,
    )
    keys, fields = [], []
    if scope.grain == "month":
        fields.append("FORMAT_DATE('%Y-%m', date) AS month")
        keys.append("month")
    if scope.dimension:
        fields.append("dimension AS dimension")
        keys.append("dimension")
    if not keys:
        return clarify("Choose monthly totals or a region/store breakdown for the target comparison.")
    actual = "SELECT " + ", ".join(fields + ["value AS actual"]) + f" FROM ({actual}) AS compiled_actual"
    target_fields = (["month"] if scope.grain == "month" else []) + (
        ["store_id AS dimension" if scope.dimension == "store" else "region AS dimension"]
        if scope.dimension
        else []
    )
    table = "store_targets" if scope.dimension == "store" else "regional_targets"
    grouping = (["month"] if scope.grain == "month" else []) + (
        ["store_id" if scope.dimension == "store" else "region"] if scope.dimension else []
    )
    target = (
        "SELECT "
        + ", ".join(target_fields + ["SUM(target_revenue) AS target"])
        + f" FROM retail_timeseries.{table} WHERE month >= '{start:%Y-%m}' AND month <= '{end:%Y-%m}' GROUP BY "
        + ", ".join(grouping)
    )
    fusion = FusionPlan(
        keys=[{"left": k, "right": k} for k in keys],
        join_type="left",
        projections=[{"side": "left", "column": k, "alias": k} for k in keys]
        + [
            {"side": "left", "column": "actual", "alias": "actual"},
            {"side": "right", "column": "target", "alias": "target"},
        ],
        relationship="Published actual revenue and full-month targets joined at identical month/region/store grain; independent source timestamps. Missing targets remain null.",
        confidence="declared",
        expected_cardinality="one-to-one",
    )
    viz = VisualizationSpec(
        version=2,
        type="table" if len(keys) > 1 else "line" if "month" in keys else "bar",
        title="Revenue compared with targets",
        x=keys[0],
        y=["actual", "target"],
        dimension_kind="temporal" if keys == ["month"] else "category",
        granularity="month" if keys == ["month"] else None,
        measures=[
            {
                "field": "actual",
                "label": selected[0]["definition"]["name"],
                "unit": "currency",
                "currency": "USD",
                "additive": True,
            },
            {
                "field": "target",
                "label": "Full-month target",
                "unit": "currency",
                "currency": "USD",
                "additive": True,
                "role": "target",
                "compares_to": "actual",
            },
        ],
    )
    plan = AnalysisPlan(
        title="Revenue target comparison",
        queries=[
            SourceQuery(source="bigquery", sql=actual, purpose="Published revenue actuals"),
            SourceQuery(source="postgres", sql=target, purpose="Full-month targets at the same grain"),
        ],
        fusion=fusion,
        visualization=viz,
        assumptions=["Targets are full calendar months; sources have independent timestamps."],
    )
    plan.metric_snapshots, plan.metric_scope = selected, scope.model_dump(mode="json")
    return plan
