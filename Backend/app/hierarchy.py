"""Pure hierarchical revenue calculations; no model, database or executable inputs."""

import copy
import math
from datetime import date
from decimal import ROUND_FLOOR, Decimal, InvalidOperation

from app.errors import AppError
from app.timesfm import digest

LEVELS = ("company", "region", "store", "category", "product")


def fail(message):
    raise AppError(message, 422, "hierarchy_invalid")


def revenue(value):
    try:
        parsed = Decimal(str(value))
    except (InvalidOperation, ValueError):
        fail("Revenue contains null or invalid values.")
    if not parsed.is_finite() or parsed < 0:
        fail("Revenue must be finite and nonnegative.")
    return parsed


def capture_history(store_rows, product_rows, stores, months, products=None):
    """Missing aggregate cells become zero only with proved complete source/calendar coverage."""
    if not months or len(months) > 120 or len(set(months)) != len(months):
        fail("Choose up to 120 unique complete calendar months.")
    try:
        dates = [date.fromisoformat(month + "-01") for month in months]
    except (ValueError, TypeError):
        fail("Use complete, ordered monthly observations.")
    if any((b.year * 12 + b.month) - (a.year * 12 + a.month) != 1 for a, b in zip(dates, dates[1:])):
        fail("Monthly history has missing or unordered periods.")
    for rows, fields in ((stores, ("store_id", "region")), (products or [], ("product_id", "category"))):
        if any(
            any(row.get(field) is None or not str(row[field]).strip() for field in fields) for row in rows
        ):
            fail("Hierarchy mappings contain missing identifiers or parent keys.")
    if len(stores) > 200 or len(product_rows) > 30000 or len(store_rows) > 30000:
        fail("Hierarchy input exceeds bounded source limits.")
    nodes = {
        "company": {
            "id": "company",
            "name": "Company",
            "level": "company",
            "parent": None,
            "history": ["0"] * len(months),
        }
    }
    mapping = {}
    for row in stores:
        sid, region = str(row["store_id"]), str(row["region"])
        if sid in mapping:
            fail("Store mappings must be unique.")
        mapping[sid] = region
        rid = "region:" + region
        nodes.setdefault(
            rid,
            {
                "id": rid,
                "name": region,
                "level": "region",
                "parent": "company",
                "history": ["0"] * len(months),
            },
        )
        nodes["store:" + sid] = {
            "id": "store:" + sid,
            "name": row.get("store_name", sid),
            "level": "store",
            "parent": rid,
            "history": ["0"] * len(months),
        }
    seen = set()
    for row in store_rows:
        month, sid = str(row["month"])[:7], str(row["store_id"])
        if month not in months or sid not in mapping or (month, sid) in seen:
            fail("Duplicate, out-of-scope or unmapped store observation.")
        seen.add((month, sid))
        i, value = months.index(month), revenue(row["value"])
        nodes["store:" + sid]["history"][i] = str(value)
        rid = "region:" + mapping[sid]
        nodes[rid]["history"][i] = str(Decimal(nodes[rid]["history"][i]) + value)
        nodes["company"]["history"][i] = str(Decimal(nodes["company"]["history"][i]) + value)
    product_totals, seen, product_mapping = [Decimal(0)] * len(months), set(), {}
    for row in products or []:
        pid, category = str(row["product_id"]), str(row["category"])
        if pid in product_mapping:
            fail("Product mappings must be unique.")
        product_mapping[pid] = category
        cid, nid = "category:" + category, "product:" + pid
        nodes.setdefault(
            cid,
            {
                "id": cid,
                "name": category,
                "level": "category",
                "parent": "company",
                "history": ["0"] * len(months),
            },
        )
        nodes[nid] = {
            "id": nid,
            "name": row.get("product_name", pid),
            "level": "product",
            "parent": cid,
            "history": ["0"] * len(months),
        }
    for row in product_rows:
        month, pid, category = str(row["month"])[:7], str(row["product_id"]), str(row["category"])
        if (
            month not in months
            or (month, pid) in seen
            or (pid in product_mapping and product_mapping[pid] != category)
            or (products is not None and pid not in product_mapping)
        ):
            fail("Duplicate product observations or conflicting category mappings.")
        seen.add((month, pid))
        product_mapping[pid] = category
        cid, nid = "category:" + category, "product:" + pid
        nodes.setdefault(
            cid,
            {
                "id": cid,
                "name": category,
                "level": "category",
                "parent": "company",
                "history": ["0"] * len(months),
            },
        )
        nodes.setdefault(
            nid,
            {
                "id": nid,
                "name": row.get("product_name", pid),
                "level": "product",
                "parent": cid,
                "history": ["0"] * len(months),
            },
        )
        i, value = months.index(month), revenue(row["value"])
        nodes[nid]["history"][i] = str(value)
        nodes[cid]["history"][i] = str(Decimal(nodes[cid]["history"][i]) + value)
        product_totals[i] += value
    if not mapping or not product_mapping or len(nodes) > 500:
        fail("Choose a complete hierarchy with at most 500 nodes.")
    if any(Decimal(v) != total for v, total in zip(nodes["company"]["history"], product_totals)):
        fail(
            "Order revenue and product line revenue do not reconcile exactly. Complete planning was withheld."
        )
    return {
        "months": months,
        "nodes": nodes,
        "input_hash": digest([store_rows, product_rows, stores, months, products]),
        "policy_version": 1,
    }


def shares(nodes, children, origin):
    totals = [sum(float(v) for v in nodes[c]["history"][max(0, origin - 12) : origin]) for c in children]
    total = sum(totals)
    return [v / total for v in totals] if total > 0 else None


def distribute(total, weights):
    """Largest remainder allocation keeps each published branch coherent to one cent."""
    if not math.isfinite(float(total)) or total < 0:
        fail("A prediction or planning value is negative or nonfinite.")
    total = Decimal(str(total)).quantize(Decimal("0.01"))
    if not weights or sum(weights) <= 0:
        if total:
            fail("A positive parent has no supported child allocation.")
        return [0.0] * len(weights)
    weights = [Decimal(str(w)) for w in weights]
    if any(not w.is_finite() or w < 0 for w in weights):
        fail("Invalid allocation weights.")
    exact = [total * w / sum(weights) for w in weights]
    cents = [v.quantize(Decimal("0.01"), rounding=ROUND_FLOOR) for v in exact]
    remainder = int((total - sum(cents)) * 100)
    order = sorted(range(len(weights)), key=lambda i: (-(exact[i] - cents[i]), i))
    for i in order[:remainder]:
        cents[i] += Decimal("0.01")
    return [float(v) for v in cents]


def reconcile(history, aggregate, origin, horizon, baseline=False):
    nodes = history["nodes"]
    root = (
        [float(nodes["company"]["history"][origin - 12 + i % 12]) for i in range(horizon)]
        if baseline
        else aggregate["company"]
    )
    output = {"company": [float(Decimal(str(v)).quantize(Decimal("0.01"))) for v in root]}
    for level in ("region", "category"):
        children = sorted(k for k, v in nodes.items() if v["level"] == level)
        for i in range(horizon):
            values = (
                [float(nodes[c]["history"][origin - 12 + i % 12]) for c in children]
                if baseline
                else [aggregate[c][i] for c in children]
            )
            weights = values if sum(values) > 0 else shares(nodes, children, origin)
            allocated = distribute(output["company"][i], weights or [0] * len(children))
            for child, value in zip(children, allocated):
                output.setdefault(child, []).append(value)
        for parent in children:
            leaves = sorted(k for k, v in nodes.items() if v["parent"] == parent)
            for i in range(horizon):
                weights = (
                    [float(nodes[c]["history"][origin - 12 + i % 12]) for c in leaves]
                    if baseline
                    else shares(nodes, leaves, origin)
                )
                values = distribute(output[parent][i], weights or [0] * len(leaves))
                for child, value in zip(leaves, values):
                    output.setdefault(child, []).append(value)
    return output


def baseline_candidate(node, months, horizon):
    y, n = [float(v) for v in node["history"]], len(months)
    errors, folds = [], []
    for origin in (n - 3 * horizon, n - 2 * horizon, n - horizon):
        residuals = [y[origin + i] - y[origin - 12 + i] for i in range(horizon)]
        errors.extend(residuals)
        folds.append(
            {
                "train_end": months[origin - 1],
                "test_start": months[origin],
                "test_end": months[origin + horizon - 1],
                "mae": sum(abs(v) for v in residuals) / horizon,
            }
        )
    score = {
        "mae": sum(abs(v) for v in errors) / len(errors),
        "rmse": math.sqrt(sum(v * v for v in errors) / len(errors)),
        "folds": folds,
    }
    return {
        "method": "seasonal_naive",
        "policy_fallback": True,
        "rows": [{"forecast": y[n - 12 + i]} for i in range(horizon)],
        "evaluation": {"seasonal_naive": score | {"errors": errors}},
        "scores": {"seasonal_naive": score},
        "limitations": [
            "The remaining fitting budget cannot admit a complete model comparison; the coherent seasonal-naive baseline was retained."
        ],
    }


def evaluate_recipe(history, adaptive_folds, horizon):
    n, nodes = len(history["months"]), history["nodes"]
    folds, node_errors = [], {}
    for fold, origin in enumerate((n - 3 * horizon, n - 2 * horizon, n - horizon)):
        base = reconcile(history, {}, origin, horizon, baseline=True)
        adaptive = reconcile(history, adaptive_folds[fold], origin, horizon)
        levels = {}
        for level in LEVELS:
            pairs = []
            for key, node in nodes.items():
                if node["level"] != level:
                    continue
                truth = [float(v) for v in node["history"][origin : origin + horizon]]
                scale = sum(abs(float(v)) for v in node["history"][:origin]) / origin
                # USD scale floor of one cent; a zero series isn't silently removed.
                scale = max(scale, 0.01)
                bm = sum(abs(a - b) for a, b in zip(truth, base[key])) / horizon
                am = sum(abs(a - b) for a, b in zip(truth, adaptive[key])) / horizon
                pairs.append((bm / scale, am / scale))
                node_errors.setdefault(key, []).append({"baseline_mae": bm, "adaptive_mae": am})
            levels[level] = {
                "baseline": sum(p[0] for p in pairs) / len(pairs),
                "adaptive": sum(p[1] for p in pairs) / len(pairs),
            }
        folds.append(
            {
                "train_end": history["months"][origin - 1],
                "test_start": history["months"][origin],
                "test_end": history["months"][origin + horizon - 1],
                "levels": levels,
                "baseline": sum(v["baseline"] for v in levels.values()) / 5,
                "adaptive": sum(v["adaptive"] for v in levels.values()) / 5,
            }
        )
    baseline, adaptive = (sum(f[k] for f in folds) / 3 for k in ("baseline", "adaptive"))
    level_gate = all(
        sum(f["levels"][level]["adaptive"] for f in folds)
        <= 1.1 * sum(f["levels"][level]["baseline"] for f in folds) + 1e-12
        for level in LEVELS
    )
    passing = (
        baseline > 0
        and adaptive <= baseline * 0.95
        and sum(f["adaptive"] < f["baseline"] for f in folds) >= 2
        and level_gate
    )
    return {
        "selected": "adaptive" if passing else "coherent_seasonal_naive",
        "baseline": baseline,
        "adaptive": adaptive,
        "level_gate": level_gate,
        "folds": folds,
        "node_errors": node_errors,
        "zero_scale_rule": "training mean absolute value, floored at USD 0.01",
    }


def adjust_plan(document, node_id, operation, value, reason):
    result = copy.deepcopy(document)
    result["statistical_predictions"] = copy.deepcopy(
        document.get("statistical_predictions", document["predictions"])
    )
    nodes, predicted = result["history"]["nodes"], result["predictions"]
    if (
        node_id not in nodes
        or not math.isfinite(value)
        or (operation == "percent" and value < -100)
        or (operation == "set" and value < 0)
    ):
        fail("Choose an existing node and nonnegative planning values.")
    before = copy.deepcopy(predicted)
    node, h = nodes[node_id], result["horizon"]
    adjusted = [value if operation == "set" else v * (1 + value / 100) for v in predicted[node_id]]
    adjusted = [float(Decimal(str(v)).quantize(Decimal("0.01"))) for v in adjusted]
    if any(a > 0 and b == 0 for a, b in zip(adjusted, predicted[node_id])):
        fail("Cannot allocate a positive adjustment from a zero-history branch.")

    def children(parent):
        return sorted(k for k, v in nodes.items() if v["parent"] == parent)

    def spread(parent, chosen_children=None):
        cs = chosen_children or children(parent)
        for i in range(h):
            vals = distribute(predicted[parent][i], [before[c][i] for c in cs])
            for c, val in zip(cs, vals):
                predicted[c][i] = val
        for c in cs:
            if children(c):
                spread(c)

    predicted[node_id] = adjusted
    if node_id == "company":
        for level in ("region", "category"):
            spread("company", sorted(k for k, v in nodes.items() if v["level"] == level))
    else:
        if children(node_id):
            spread(node_id)
        parent = node["parent"]
        while parent and parent != "company":
            predicted[parent] = [
                float(sum(Decimal(str(predicted[c][i])) for c in children(parent))) for i in range(h)
            ]
            parent = nodes[parent]["parent"]
        same_level = "region" if node["level"] in {"region", "store"} else "category"
        roots = sorted(k for k, v in nodes.items() if v["level"] == same_level)
        predicted["company"] = [float(sum(Decimal(str(predicted[c][i])) for c in roots)) for i in range(h)]
        other = "category" if same_level == "region" else "region"
        spread("company", sorted(k for k, v in nodes.items() if v["level"] == other))
    result["adjustments"] = result.get("adjustments", []) + [
        {
            "node_id": node_id,
            "operation": operation,
            "value": value,
            "reason": reason,
            "previous": before[node_id],
            "result": adjusted,
            "cross_view_reallocation": True,
        }
    ]
    result["kind"] = "adjusted_plan"
    return result
