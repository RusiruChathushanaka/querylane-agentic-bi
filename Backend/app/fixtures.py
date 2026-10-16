"""Deterministic synthetic retail data; no real customer information."""

from datetime import date
from decimal import Decimal


def retail_data() -> dict[str, list[dict]]:
    regions = ["North", "South", "East", "West"]
    products = [
        {
            "product_id": "P001",
            "product_name": "Everyday tote",
            "category": "Accessories",
            "unit_price": Decimal("48.00"),
        },
        {
            "product_id": "P002",
            "product_name": "Studio headphones",
            "category": "Electronics",
            "unit_price": Decimal("129.00"),
        },
        {
            "product_id": "P003",
            "product_name": "Trail sneaker",
            "category": "Footwear",
            "unit_price": Decimal("89.00"),
        },
        {
            "product_id": "P004",
            "product_name": "Linen shirt",
            "category": "Apparel",
            "unit_price": Decimal("65.00"),
        },
    ]
    customers = [
        {
            "customer_id": f"C{i:03}",
            "customer_name": f"Demo customer {i:03}",
            "region": regions[(i - 1) % 4],
            "segment": "Returning" if i % 3 else "New",
            "loyalty_tier": "Gold" if i % 5 == 0 else "Standard",
        }
        for i in range(1, 81)
    ]
    orders, items, returns = [], [], []
    for month in range(1, 10):
        for i in range(1, 81):
            product = products[(i + month) % 4]
            quantity = 1 + (i + month) % 3
            amount = product["unit_price"] * quantity
            order_id = f"O{month:02}{i:03}"
            orders.append(
                {
                    "order_id": order_id,
                    "customer_id": f"C{i:03}",
                    "order_date": date(2026, month, 1 + i % 27),
                    "month": f"2026-{month:02}",
                    "region": regions[(i - 1) % 4],
                    "revenue": amount,
                    "status": "completed",
                }
            )
            items.append(
                {
                    "order_id": order_id,
                    "product_id": product["product_id"],
                    "quantity": quantity,
                    "line_revenue": amount,
                }
            )
            if (i + month) % 17 == 0:
                returns.append(
                    {
                        "return_id": f"R{order_id}",
                        "order_id": order_id,
                        "refund_amount": amount,
                        "reason": "Size or fit" if i % 2 else "Changed mind",
                    }
                )
    targets = [
        {
            "month": f"2026-{month:02}",
            "region": region,
            "target_revenue": Decimal(3200 + month * 100 + r * 200),
        }
        for month in range(1, 10)
        for r, region in enumerate(regions)
    ]
    campaigns = [
        {
            "campaign_id": f"M{i + 1:03}",
            "region_name": region,
            "campaign_name": name,
            "spend": Decimal(750 + i * 125),
        }
        for i, (region, name) in enumerate(
            zip(regions, ["Fresh start", "City essentials", "Outside together", "The daily edit"])
        )
    ]
    # Deliberate ambiguity/fan-out fixtures: not canonical relationships.
    aliases = [
        {"region_label": "North", "market": "N1"},
        {"region_label": "North", "market": "N2"},
        {"region_label": "South", "market": "S1"},
        {"region_label": None, "market": "Unknown"},
    ]
    return {
        "orders": orders,
        "order_items": items,
        "products": products,
        "returns": returns,
        "customer_profiles": customers,
        "regional_targets": targets,
        "campaigns": campaigns,
        "region_aliases": aliases,
    }


SOURCE_TABLES = {
    "bigquery": ["orders", "order_items", "products", "returns"],
    "postgres": ["customer_profiles", "regional_targets", "campaigns", "region_aliases"],
}

DESCRIPTIONS = {
    "orders": "Completed retail orders, Jan–Sep 2026. All seeded rows have status='completed' (lowercase, case-sensitive); do not invent other status literals. revenue is gross order revenue in USD, before refunds. month is YYYY-MM. customer_id is a candidate relationship to PostgreSQL customer_profiles.",
    "order_items": "Order lines; line_revenue is USD. Join orders on order_id and products on product_id. One line per order in this synthetic seed.",
    "products": "Product catalogue, category, and current unit price in USD. product_id is unique.",
    "returns": "Returned orders and refund_amount in USD. Net revenue = gross order revenue minus refunds, with correct order-level joins.",
    "customer_profiles": "Synthetic customer profiles, region, segment, loyalty tier. customer_id is unique. Names are not reliable keys.",
    "regional_targets": "Monthly revenue targets in USD. Composite grain: month AND region; both are needed to match aggregated BigQuery actuals.",
    "campaigns": "Campaign spend in USD by region_name. region_name may be inferred to correspond to orders.region; no attribution/causation is established.",
    "region_aliases": "Intentionally ambiguous region aliases. Duplicate North and null labels demonstrate unsafe relationship fan-out. Do not use as a canonical region dimension.",
}
