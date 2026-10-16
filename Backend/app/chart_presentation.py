"""Bounded, deterministic presentation of immutable result pages. No SQL or model access."""

import csv
import io
import json
import math
import re
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation

from app.errors import AppError
from app.models import VisualizationSpec

MAX_POINTS = 2000
MAX_ROWS = 50_000
MAX_BYTES = 64 * 1024 * 1024
NUMERIC = re.compile(r"int|float|double|decimal|numeric|number|real", re.I)


def number(value):
    if value is None or isinstance(value, bool) or value == "":
        return None
    try:
        result = Decimal(str(value))
        return result if result.is_finite() else None
    except (InvalidOperation, ValueError):
        return None


def date_value(value):
    text = str(value)
    if not re.fullmatch(r"\d{4}(-\d{2}(-\d{2})?)?([T ].*)?", text):
        return None
    try:
        if len(text) == 4:
            return date(int(text), 1, 1)
        if len(text) == 7:
            return date.fromisoformat(text + "-01")
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def metadata(spec, columns, rows):
    """Reject unbound metadata; old artifacts get conservative, display-only defaults."""
    spec = VisualizationSpec.model_validate(spec).model_dump(mode="json")
    numeric = [c["name"] for c in columns if NUMERIC.search(c["type"])]
    names = {c["name"] for c in columns}
    x = (
        spec["x"]
        if spec["x"] in names
        else next((c["name"] for c in columns if c["name"] not in numeric), None)
    )
    ys = [y for y in spec["y"] if y in numeric] or [n for n in numeric if n != x][:4]
    if any(
        m["field"] not in ys
        or m["compares_to"]
        and (m["compares_to"] not in ys or m["compares_to"] == m["field"])
        for m in spec["measures"]
    ):
        raise AppError(
            "Visualization metadata references an unavailable measure.", 422, "chart_metadata_invalid"
        )
    if len({m["field"] for m in spec["measures"]}) != len(spec["measures"]):
        raise AppError("Visualization measures must be unique.", 422, "chart_metadata_invalid")
    measures = {m["field"]: m for m in spec["measures"]}
    for y in ys:
        if y not in measures:
            unit = spec["format"] if len(ys) == 1 else "number"
            measures[y] = {
                "field": y,
                "label": y.replace("_", " "),
                "unit": unit,
                "currency": "USD" if unit == "currency" else None,
                "percent_scale": "whole" if unit == "percent" else None,
                "additive": False,
                "role": "measure",
                "compares_to": None,
                "direction": "neutral",
            }
    for m in measures.values():
        m["label"] = m["label"] or m["field"].replace("_", " ")
        if m["unit"] == "percent":
            m["additive"] = False
        if m["unit"] != "currency":
            m["currency"] = None
        if m["unit"] == "percent" and m["percent_scale"] is None:
            m["unit"] = "number"  # A missing scale must never silently multiply a rate.
        if m["unit"] == "currency" and not m["currency"]:
            m["unit"] = "number"
    temporal = bool(
        x
        and rows
        and all(r.get(x) is None or date_value(r[x]) for r in rows)
        and any(r.get(x) is not None for r in rows)
    )
    kind = spec["dimension_kind"] or ("temporal" if temporal else "category")
    if kind == "temporal" and not temporal:
        kind = "category"
    granularity = spec["granularity"]
    if kind == "temporal" and not granularity:
        lengths = {len(str(r[x])) for r in rows if r.get(x) is not None}
        granularity = "month" if lengths == {7} else "year" if lengths == {4} else None
    return spec | {
        "x": x,
        "y": ys,
        "dimension_kind": kind,
        "granularity": granularity,
        "measures": list(measures.values()),
    }


def normalized_spec(spec, columns, rows):
    """Called once when saving a new artifact; historical documents remain immutable."""
    try:
        normalized = metadata(spec.model_dump(mode="json"), columns, rows)
        return VisualizationSpec.model_validate(normalized)
    except AppError:
        return VisualizationSpec(type="table", title=spec.title)


async def saved_rows(store, artifact):
    count, size = 0, 0
    pages = artifact.get("page_count", 0)
    if not isinstance(pages, int) or not 0 <= pages <= 1024:
        raise AppError("Saved result exceeds the presentation budget.", 413, "chart_too_large")
    for index in range(pages):
        page = await store.get(f"artifacts/{artifact['id']}/pages", str(index))
        if page is None:
            raise AppError(
                "The saved result is missing a page. Try again after the run completes.",
                409,
                "artifact_incomplete",
            )
        rows = page["rows"]
        count += len(rows)
        size += len(json.dumps(rows).encode())
        if count > MAX_ROWS or size > MAX_BYTES:
            raise AppError(
                "Saved result exceeds the presentation budget. Use the table or narrow the analysis.",
                413,
                "chart_too_large",
            )
        for row in rows:
            yield row
    if count != artifact["row_count"]:
        raise AppError("Saved result rows do not match its evidence.", 409, "artifact_incomplete")


def next_date(value, grain):
    if grain == "day":
        return value + timedelta(days=1)
    if grain == "week":
        return value + timedelta(days=7)
    months = {"month": 1, "quarter": 3, "year": 12}.get(grain)
    if months:
        total = value.year * 12 + value.month - 1 + months
        return date(total // 12, total % 12 + 1, 1)
    return None


def change(current, previous, unit):
    delta = current - previous
    return {
        "delta": float(delta),
        "percent": float(delta / abs(previous) * 100) if previous else None,
        "percentage_points": float(delta * (100 if unit.get("percent_scale") == "fraction" else 1))
        if unit["unit"] == "percent"
        else None,
    }


def sampled_rows(rows, fields, limit=MAX_POINTS):
    """Shared indices preserve extrema for all series, endpoints, and null boundaries."""
    if len(rows) <= limit:
        return rows, False
    mandatory = {0, len(rows) - 1}
    for field in fields:
        for i in range(1, len(rows)):
            if (number(rows[i].get(field)) is None) != (number(rows[i - 1].get(field)) is None):
                mandatory.update((i - 1, i))
    if len(mandatory) > limit - 2 * len(fields):
        return [], True
    buckets = max(1, (limit - len(mandatory)) // (2 * max(1, len(fields))))
    width = math.ceil(len(rows) / buckets)
    chosen = set(mandatory)
    for start in range(0, len(rows), width):
        for field in fields:
            pairs = [(i, number(rows[i].get(field))) for i in range(start, min(start + width, len(rows)))]
            valid = [(i, v) for i, v in pairs if v is not None]
            if valid:
                chosen.update((min(valid, key=lambda p: p[1])[0], max(valid, key=lambda p: p[1])[0]))
    return [rows[i] for i in sorted(chosen)], True


def present(artifact, rows, *, start=None, end=None, primary=None, order="value_desc", top=10, view=None):
    spec = metadata(artifact["visualization"], artifact["columns"], rows)
    x, ys = spec["x"], spec["y"]
    primary = (
        primary
        or next((m["field"] for m in spec["measures"] if m["role"] == "primary"), None)
        or next(iter(ys), None)
    )
    if primary and primary not in ys:
        raise AppError("Choose a measure from this saved result.", 422, "chart_field_invalid")
    if start and end and start > end:
        raise AppError("The start date must precede the end date.", 422, "chart_range_invalid")
    temporal = spec["dimension_kind"] == "temporal"
    if (start or end) and not temporal:
        raise AppError("A date range requires a temporal dimension.", 422, "chart_range_invalid")
    rows = list(rows)
    if temporal:
        rows = [r for r in rows if r.get(x) is not None]
        rows.sort(key=lambda r: date_value(r[x]))
        rows = [
            r
            for r in rows
            if (not start or date_value(r[x]) >= start) and (not end or date_value(r[x]) <= end)
        ]
    dimension_label = x.replace("_", " ") if x else "observation"
    if x and not temporal and len({str(r.get(x)) for r in rows}) != len(rows):
        context = [c["name"] for c in artifact["columns"] if c["name"] != x and not NUMERIC.search(c["type"])]
        if context and len({tuple(str(r.get(c)) for c in [x, *context]) for r in rows}) == len(rows):
            original_x = x
            dimension_label = " · ".join(c.replace("_", " ") for c in [x, *context])
            rows = [
                r | {"_dimension": " · ".join(str(r.get(c, "Missing")) for c in [original_x, *context])}
                for r in rows
            ]
            x = spec["x"] = "_dimension"
    selected_count = len(rows)
    unit = next((m for m in spec["measures"] if m["field"] == primary), {})
    unique_x = bool(x and len({str(r.get(x)) for r in rows}) == len(rows))
    insights, annotations, stats = [], [], {}
    valid = [(r, number(r.get(primary))) for r in rows] if primary else []
    valid = [(r, v) for r, v in valid if v is not None]
    total = sum((v for _, v in valid), Decimal(0))
    partials = set(spec["partial_periods"])
    # Published source boundaries can independently establish partial first/last buckets.
    bounds = artifact.get("data_coverage")
    if temporal and bounds and spec["granularity"] in {"month", "quarter", "year", "week"}:
        for r in rows:
            d = date_value(r[x])
            following = next_date(d, spec["granularity"])
            if d < date.fromisoformat(bounds[0]) or following - timedelta(days=1) > date.fromisoformat(
                bounds[1]
            ):
                partials.add(str(r[x]))
    spec["partial_periods"] = sorted(partials)
    if valid:
        low, high = min(valid, key=lambda p: p[1]), max(valid, key=lambda p: p[1])
        stats = {
            "min": float(low[1]),
            "max": float(high[1]),
            "sum": float(total) if unit.get("additive") and artifact["complete"] else None,
        }
        insights.append(
            {
                "kind": "peak" if temporal else "leader",
                "field": primary,
                "label": str(high[0].get(x, "Result")),
                "value": float(high[1]),
            }
        )
        annotations.append({"kind": "peak", "x": high[0].get(x), "field": primary, "value": float(high[1])})
        if temporal and rows:
            latest = rows[-1]
            annotations.append(
                {
                    "kind": "latest",
                    "x": latest.get(x),
                    "field": primary,
                    "value": float(number(latest.get(primary)))
                    if number(latest.get(primary)) is not None
                    else None,
                }
            )
            eligible = [r for r in rows if str(r[x]) not in partials]
            if artifact["complete"] and unique_x and len(eligible) >= 2 and spec["granularity"]:
                previous, current = eligible[-2:]
                a, b = number(current.get(primary)), number(previous.get(primary))
                if (
                    a is not None
                    and b is not None
                    and next_date(date_value(previous[x]), spec["granularity"]) == date_value(current[x])
                ):
                    insights.append(
                        {
                            "kind": "change",
                            "field": primary,
                            "label": str(current[x]),
                            "previous_label": str(previous[x]),
                            "value": float(a),
                            **change(a, b, unit),
                        }
                    )
        if (
            unit.get("additive")
            and artifact["complete"]
            and unique_x
            and all(number(r.get(primary)) is not None and number(r[primary]) >= 0 for r in rows)
            and stats.get("sum", 0)
            and not temporal
        ):
            insights.append(
                {
                    "kind": "share",
                    "field": primary,
                    "label": str(high[0].get(x)),
                    "value": float(high[1] / total * 100),
                }
            )
        for target in spec["measures"]:
            if (
                target["compares_to"] == primary
                and target["role"] in {"target", "comparison"}
                and target["unit"] == unit["unit"]
                and target.get("currency") == unit.get("currency")
                and target.get("percent_scale") == unit.get("percent_scale")
            ):
                row = rows[-1] if temporal else high[0]
                a, b = number(row.get(primary)), number(row.get(target["field"]))
                if a is not None and b is not None:
                    insights.append(
                        {
                            "kind": "target",
                            "field": primary,
                            "target_field": target["field"],
                            "label": str(row.get(x, "Result")),
                            "value": float(a),
                            "target": float(b),
                            **change(a, b, unit),
                        }
                    )
                    break
    if not x:
        insights = [item for item in insights if item["kind"] == "target"]
    nonnegative_complete = len(valid) == len(rows) and all(v >= 0 for _, v in valid)
    for index, row in enumerate(rows):
        detail = {}
        for measure in spec["measures"]:
            field = measure["field"]
            value = number(row.get(field))
            info = {}
            if (
                temporal
                and unique_x
                and artifact["complete"]
                and index
                and spec["granularity"]
                and str(row.get(x)) not in partials
                and str(rows[index - 1].get(x)) not in partials
            ):
                previous = rows[index - 1]
                old = number(previous.get(field))
                if (
                    value is not None
                    and old is not None
                    and next_date(date_value(previous[x]), spec["granularity"]) == date_value(row[x])
                ):
                    info = {"previous_label": str(previous[x]), **change(value, old, measure)}
            if measure["compares_to"] and value is not None:
                actual_meta = next(
                    (m for m in spec["measures"] if m["field"] == measure["compares_to"]), None
                )
                actual = number(row.get(measure["compares_to"]))
                if (
                    actual is not None
                    and actual_meta
                    and all(
                        measure.get(k) == actual_meta.get(k) for k in ("unit", "currency", "percent_scale")
                    )
                ):
                    info["variance"] = change(actual, value, measure)
                    info["actual_field"] = measure["compares_to"]
            if (
                field == primary
                and stats.get("sum")
                and not temporal
                and unit.get("additive")
                and artifact["complete"]
                and nonnegative_complete
            ):
                info["share"] = float(value / total * 100) if value is not None else None
            detail[field] = info
        rows[index] = row | {"_detail": detail, "_key": index}
    scope = {
        "start": str(rows[0].get(x)) if temporal and rows else None,
        "end": str(rows[-1].get(x)) if temporal and rows else None,
    }
    category_total = stats.get("sum")
    composition = bool(
        not temporal
        and unique_x
        and 1 < len(rows) <= 6
        and len(ys) == 1
        and unit.get("additive")
        and artifact["complete"]
        and all(number(r.get(primary)) is not None and number(r[primary]) >= 0 for r in rows)
        and category_total
        and category_total > 0
    )
    omitted, sampled, warning = (
        0,
        False,
        None
        if valid or not rows
        else "This result has no finite values for the selected measure. Choose another measure or inspect the table.",
    )
    if (
        not temporal
        and spec["dimension_kind"] != "numeric"
        and (view or artifact["visualization"]["type"]) != "scatter"
        and primary
    ):
        if order == "label":
            rows.sort(key=lambda r: str(r.get(x, "")))
        elif order != "original":
            rows.sort(
                key=lambda r: (
                    number(r.get(primary)) is None,
                    -(number(r.get(primary)) or Decimal(0))
                    if order == "value_desc"
                    else (number(r.get(primary)) or Decimal(0)),
                )
            )
        omitted = max(0, len(rows) - top)
        rows = rows[:top]
    # Insert explicit missing-period breaks, never fabricated zeroes or interpolation.
    if temporal and unique_x and spec["granularity"]:
        dense = []
        for row in rows:
            if dense and next_date(date_value(dense[-1][x]), spec["granularity"]) < date_value(row[x]):
                missing = next_date(date_value(dense[-1][x]), spec["granularity"])
                dense.append(
                    {
                        x: missing.isoformat()[:7] if spec["granularity"] == "month" else missing.isoformat(),
                        **dict.fromkeys(ys),
                        "_gap": True,
                    }
                )
            dense.append(row)
        rows = dense
    if temporal and not unique_x:
        rows = []
        warning = "Multiple observations share a time bucket. Use the table or ask for one aggregate per date or separate series."
    elif not temporal and x and not unique_x and selected_count > 1 and (view or spec["type"]) != "scatter":
        rows = []
        warning = "Multiple observations share a category. Use the table or ask for an aggregate at a clear category grain."
    elif temporal:
        rows, sampled = sampled_rows(rows, ys)
        if sampled and not rows:
            warning = (
                "Too many missing-data boundaries to plot faithfully. Narrow the date range or use the table."
            )
    elif len(rows) > MAX_POINTS:
        rows = []
        warning = "Too many observations to plot faithfully. Narrow the analysis or use the table."
    # Keep only presentation columns, with a hard payload budget for oversized dimension labels.
    numeric_fields = [c["name"] for c in artifact["columns"] if NUMERIC.search(c["type"])]
    identity = next(
        (c["name"] for c in artifact["columns"] if c["name"] not in numeric_fields and c["name"] != x), None
    )
    fields = set(
        ys
        + numeric_fields[:4]
        + ([x] if x else [])
        + ([identity] if identity else [])
        + ["_gap", "_detail", "_key"]
    )
    plotted = [
        {
            k: (
                float(number(v))
                if k in numeric_fields and number(v) is not None
                else None
                if k in numeric_fields
                else v
            )
            for k, v in r.items()
            if k in fields
        }
        for r in rows
    ]
    if len(json.dumps(plotted).encode()) > 2 * 1024 * 1024:
        plotted, warning = (
            [],
            "Chart labels exceed the presentation budget. Use the table or narrow the analysis.",
        )
    return {
        "version": 2,
        "visualization": spec,
        "primary": primary,
        "rows": plotted,
        "insights": insights[:3],
        "annotations": annotations,
        "stats": stats,
        "scope": scope,
        "coverage": {
            "result_rows": artifact["row_count"],
            "selected_rows": selected_count,
            "plotted_rows": len(plotted),
            "sampled": sampled,
            "omitted_categories": omitted,
            "complete": artifact["complete"],
            "unique_dimension": unique_x,
        },
        "composition": composition,
        "identity": identity,
        "dimension_label": dimension_label,
        "warning": warning,
    }


def csv_cell(value):
    if value is None:
        return ""
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")):
        # JSON Decimal strings are numbers only if strictly numeric, not formulas.
        if number(value) is None:
            return "'" + value
    return value


def csv_line(values):
    buffer = io.StringIO(newline="")
    csv.writer(buffer).writerow([csv_cell(v) for v in values])
    return buffer.getvalue()
