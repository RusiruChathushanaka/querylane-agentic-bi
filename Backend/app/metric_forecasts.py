"""Preserve compiled definitions when forecasts require controlled feature evidence."""

import re
from decimal import Decimal

from app.errors import AppError


def bind_forecast(plan, spec):
    if (
        len(plan.metric_snapshots) != 1
        or plan.metric_scope.get("dimension")
        or plan.metric_scope.get("grain") != spec.grain
        or len(plan.queries) != 1
    ):
        raise AppError(
            "Forecast a single published metric at its requested time grain without a category breakdown.",
            422,
            "metric_forecast_scope",
        )
    if not all(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value) for value in (spec.date_column, spec.target)):
        raise AppError("Forecast aliases must be simple identifiers.", 422, "metric_forecast_scope")
    partials = plan.visualization.partial_periods
    exclusions = (
        " WHERE date NOT IN (" + ", ".join("DATE '" + v + "'" for v in partials) + ")" if partials else ""
    )
    plan.queries[
        0
    ].sql = f"SELECT date AS {spec.date_column}, value AS {spec.target} FROM ({plan.queries[0].sql}) AS canonical_metric{exclusions} ORDER BY {spec.date_column}"
    plan.visualization.x, plan.visualization.y = spec.date_column, [spec.target]
    plan.visualization.measures[0].field = spec.target
    return plan


def verify_forecast_values(rows, canonical, date_column, target):
    expected = {str(r[date_column])[:10]: r[target] for r in canonical}
    if len(expected) != len(canonical) or len(rows) != len(canonical):
        raise AppError(
            "Forecast features changed the published metric grain or coverage.", 422, "metric_mismatch"
        )
    seen = set()
    for row in rows:
        key = str(row.get(date_column))[:10]
        if key not in expected or key in seen or row.get(target) is None or expected[key] is None:
            raise AppError(
                "Forecast metric dates/values do not match saved canonical evidence.", 422, "metric_mismatch"
            )
        seen.add(key)
        a, b = Decimal(str(row[target])), Decimal(str(expected[key]))
        if not a.is_finite() or not b.is_finite() or abs(a - b) > Decimal("0.000001"):
            raise AppError(
                "Forecast target differs from the published metric definition. No prediction was produced.",
                422,
                "metric_mismatch",
            )
