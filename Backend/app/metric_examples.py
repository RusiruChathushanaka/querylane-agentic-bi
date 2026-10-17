"""Insert-only packaged definitions. Never called by startup, release or history reset."""

import hashlib

from app.metrics import MetricAction, MetricDefinition, Metrics, MetricWrite


async def seed_metrics(store, settings):
    library = Metrics(store, settings)
    created, ids = [], {}
    all_dims = ["region", "store", "category", "product", "channel"]

    async def insert(slug, definition):
        await _insert(library, store, ids[slug], definition, created)

    examples = [
        (
            "revenue",
            "Merchandise revenue",
            "After discounts, before refunds, tax and shipping.",
            "sum",
            "revenue",
            "currency",
            "order_date",
            all_dims,
            ["sales revenue", "revenue"],
        ),
        (
            "gross",
            "Gross merchandise sales",
            "Merchandise sales before discounts.",
            "sum",
            "gross_sales",
            "currency",
            "order_date",
            all_dims,
            [],
        ),
        (
            "discounts",
            "Discounts",
            "Allocated merchandise discounts.",
            "sum",
            "discounts",
            "currency",
            "order_date",
            all_dims,
            [],
        ),
        (
            "orders",
            "Orders",
            "Completed orders, counted at order grain.",
            "count",
            "orders",
            "count",
            "order_date",
            ["region", "store", "channel"],
            [],
        ),
        (
            "units",
            "Units sold",
            "Purchased units before returns.",
            "sum",
            "units",
            "count",
            "order_date",
            all_dims,
            [],
        ),
        (
            "customers",
            "Active purchasing customers",
            "Distinct customers with a completed purchase in the selected period.",
            "distinct_count",
            "customers",
            "count",
            "order_date",
            ["region", "store", "channel"],
            [],
        ),
        (
            "cost",
            "Merchandise cost",
            "Historical purchased merchandise cost; excludes operating expenses.",
            "sum",
            "cost",
            "currency",
            "order_date",
            all_dims,
            [],
        ),
        (
            "line_revenue",
            "Line merchandise revenue",
            "Merchandise revenue at item grain, reconciling to order revenue.",
            "sum",
            "line_revenue",
            "currency",
            "order_date",
            all_dims,
            [],
        ),
        (
            "refunds",
            "Refund-date refunds",
            "Merchandise refunded on refund date, not order-cohort returns.",
            "sum",
            "refunds",
            "currency",
            "refund_date",
            all_dims,
            [],
        ),
        (
            "returned_cost",
            "Returned merchandise cost",
            "Cost reversals on refund date.",
            "sum",
            "returned_cost",
            "currency",
            "refund_date",
            all_dims,
            [],
        ),
        (
            "event_revenue",
            "Refund-date sales basis",
            "Order-date merchandise sales on the refund-date reporting calendar; paired with refunds occurring on that date.",
            "sum",
            "revenue",
            "currency",
            "refund_date",
            all_dims,
            [],
        ),
    ]
    for slug, name, desc, op, measure, unit, basis, dims, aliases in examples:
        ids[slug] = hashlib.sha256(f"querylane:metric:{slug}".encode()).hexdigest()[:32]
        definition = MetricDefinition(
            name=name,
            description=desc,
            aliases=aliases,
            formula={"operation": op, "measure": measure},
            unit=unit,
            time_basis=basis,
            dimensions=dims,
        )
        await insert(slug, definition)

    async def derived(slug, name, desc, op, left, right, unit, dims, basis="order_date"):
        ids[slug] = hashlib.sha256(f"querylane:metric:{slug}".encode()).hexdigest()[:32]
        # Packaged dependencies deliberately remain on version 1.
        await insert(
            slug,
            MetricDefinition(
                name=name,
                description=desc,
                formula={
                    "operation": op,
                    "left": {"id": ids[left], "version": 1},
                    "right": {"id": ids[right], "version": 1},
                },
                unit=unit,
                time_basis=basis,
                dimensions=dims,
            ),
        )

    await derived(
        "aov",
        "Average order value",
        "Revenue divided by completed orders; aggregate original components, not monthly ratios.",
        "ratio",
        "revenue",
        "orders",
        "currency",
        ["region", "store", "channel"],
    )
    await derived(
        "margin",
        "Merchandise margin",
        "Before-return merchandise revenue less historical cost. Not accounting profit.",
        "subtract",
        "line_revenue",
        "cost",
        "currency",
        all_dims,
    )
    await derived(
        "margin_rate",
        "Merchandise margin percentage",
        "Before-return merchandise margin divided by revenue.",
        "ratio",
        "margin",
        "line_revenue",
        "percent",
        all_dims,
    )
    await derived(
        "discount_rate",
        "Discount percentage",
        "Discounts divided by gross merchandise sales.",
        "ratio",
        "discounts",
        "gross",
        "percent",
        all_dims,
    )
    await derived(
        "net",
        "Refund-date net revenue",
        "Sales occurring in the period less refunds occurring in the period; not order-cohort net revenue.",
        "subtract",
        "event_revenue",
        "refunds",
        "currency",
        all_dims,
        "refund_date",
    )
    return created


# Defined outside the seed function so the insertion path can be tested independently.
async def _insert(library, store, metric_id, definition, created):
    if await store.get("metrics", metric_id):
        return
    value = await library.mutate(
        f"seed_{metric_id}",
        "create",
        MetricWrite(definition=definition, request_id=f"seed_{metric_id}_create"),
        metric_id,
    )
    await library.mutate(
        f"seed_{metric_id}",
        "publish",
        MetricAction(expected_revision=value["revision"], request_id=f"seed_{metric_id}_publish"),
        metric_id,
    )
    created.append(metric_id)
