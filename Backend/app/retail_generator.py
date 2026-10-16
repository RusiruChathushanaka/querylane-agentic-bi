"""Deterministic, bounded-memory synthetic retail history; never contacts a database."""

import bisect
import calendar
import hashlib
import json
import random
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from app.retail_schema import BY_NAME, TABLES, VERSION, schema_export

REGIONS = ("North", "South", "East", "West")
ANCHOR = date(2023, 1, 1)
ANOMALIES = {
    date(2024, 2, 29): (0.0, "Synthetic full-day closure"),
    date(2025, 6, 10): (0.25, "Synthetic demand outage"),
    date(2025, 11, 28): (2.0, "Synthetic promotion surge"),
    date(2026, 3, 15): (1.8, "Synthetic demand spike"),
}


@dataclass(frozen=True)
class GeneratorConfig:
    start: date = date(2023, 1, 1)
    end: date = date(2026, 9, 30)
    orders_per_day: int = 300
    customers: int = 25_000
    products: int = 200
    stores: int = 24
    seed: int = 42

    def validate(self):
        if not date(2020, 1, 1) <= self.start <= self.end <= date(2035, 12, 31):
            raise ValueError("Choose an inclusive date range between 2020 and 2035.")
        if not 1 <= self.orders_per_day <= 2000 or not 32 <= self.customers <= 100_000:
            raise ValueError("Use 1–2000 orders/day and 32–100000 customers.")
        if not 8 <= self.products <= 2000 or not 4 <= self.stores <= 200 or self.stores % 4:
            raise ValueError("Use 8–2000 products and a multiple of four stores (4–200).")
        if (self.end - self.start).days * self.orders_per_day > 5_000_000:
            raise ValueError("This batch exceeds five million base orders; choose a smaller range/rate.")


def money(cents):
    return (Decimal(cents) / 100).quantize(Decimal("0.01"))


def serialized(value):
    return value.isoformat() if isinstance(value, (date, datetime)) else str(value)


def record_hash(row):
    return hashlib.sha256(
        json.dumps(row, sort_keys=True, default=serialized, separators=(",", ":")).encode()
    ).hexdigest()


def seeded(seed, key):
    return random.Random(int.from_bytes(hashlib.sha256(f"{seed}:{key}".encode()).digest()[:8], "big"))


def promotion_window(month):
    last = calendar.monthrange(month.year, month.month)[1]
    start, end = (25, last) if month.month == 11 else (20, 26) if month.month == 12 else (10, 15)
    return month.replace(day=start), month.replace(day=end)


def demand(day):
    seasonal = (0.8, 0.8, 0.95, 1.0, 1.0, 0.95, 1.0, 1.05, 1.1, 1.1, 1.65, 1.5)[day.month - 1]
    growth = max(0.4, 1 + ((day - ANCHOR).days / 365.25) * 0.10)
    return seasonal * growth * (1.18 if day.weekday() >= 5 else 1.0)


class Writer:
    def __init__(self, directory, table):
        self.table, self.path = table, directory / f"{table.name}.parquet"
        self.writer = pq.ParquetWriter(self.path, table.arrow_schema(), compression="zstd")
        self.buffer, self.count = [], 0

    def add(self, row):
        row = row | {"record_hash": record_hash(row)}
        self.buffer.append(row)
        self.count += 1
        if len(self.buffer) >= 4096:
            self.flush()

    def flush(self):
        if self.buffer:
            self.writer.write_table(pa.Table.from_pylist(self.buffer, schema=self.table.arrow_schema()))
            self.buffer.clear()

    def close(self):
        self.flush()
        self.writer.close()
        with self.path.open("rb") as stream:
            digest = hashlib.file_digest(stream, "sha256").hexdigest()
        return {
            "file": self.path.name,
            "rows": self.count,
            "bytes": self.path.stat().st_size,
            "sha256": digest,
        }


def generate(config: GeneratorConfig, output: Path, progress=lambda message: None):
    config.validate()
    if output.exists():
        raise ValueError(
            "Output already exists. Use a new batch directory; existing files are never overwritten."
        )
    output.mkdir(parents=True)
    writers = {t.name: Writer(output, t) for t in TABLES}
    products, stores, customer_groups = [], [], {r: [] for r in REGIONS}
    summary = {"revenue": 0, "gross_sales": 0, "discounts": 0, "refunds": 0, "units": 0}
    monthly = {}
    try:
        categories = (
            "Accessories",
            "Electronics",
            "Footwear",
            "Apparel",
            "Home",
            "Beauty",
            "Outdoor",
            "Toys",
        )
        for index in range(config.products):
            rng = seeded(config.seed, f"product:{index}")
            price = rng.randint(15, 250) * 100
            row = {
                "product_id": f"TP{index + 1:05}",
                "product_name": f"{categories[index % 8]} product {index + 1:03}",
                "category": categories[index % 8],
                "brand": f"Demo brand {index % 12 + 1:02}",
                "unit_price": money(price),
                "unit_cost": money(price * rng.randint(40, 70) // 100),
                "launched_on": date(2019, 1, 1),
            }
            products.append(row)
            writers["sales_products"].add(row)
        for index in range(config.stores):
            row = {
                "store_id": f"TS{index + 1:03}",
                "store_name": f"{REGIONS[index % 4]} store {index // 4 + 1}",
                "region": REGIONS[index % 4],
                "store_format": ("Flagship", "Mall", "Outlet")[index % 3],
                "opened_on": date(2019, 1, 1),
            }
            stores.append(row)
            writers["stores"].add(row)
        for index in range(config.customers):
            rng = seeded(config.seed, f"customer:{index}")
            # The early cohort is always available; other signup dates do not depend on batch end.
            signup = (
                date(2019, 1, 1) if index < 32 else date(2022, 1, 1) + timedelta(days=rng.randrange(1460))
            )
            row = {
                "customer_id": f"TC{index + 1:06}",
                "customer_name": f"Synthetic customer {index + 1:06}",
                "region": REGIONS[index % 4],
                "segment": "Returning" if index % 3 else "New",
                "loyalty_tier": "Gold" if index % 5 == 0 else "Standard",
                "signup_date": signup,
                "acquisition_channel": ("Organic", "Paid search", "Referral", "Social")[index % 4],
            }
            customer_groups[row["region"]].append((signup, row["customer_id"]))
            if signup <= config.end:
                writers["customer_profiles"].add(row)
        for group in customer_groups.values():
            group.sort()
        signup_dates = {region: [c[0] for c in group] for region, group in customer_groups.items()}
        cursor = config.start.replace(day=1)
        while cursor <= config.end:
            month = cursor.strftime("%Y-%m")
            last = cursor.replace(day=calendar.monthrange(cursor.year, cursor.month)[1])
            promo_start, promo_end = promotion_window(cursor)
            for r, region in enumerate(REGIONS):
                campaign_id = f"CM{month.replace('-', '')}{r}"
                writers["campaigns"].add(
                    {
                        "campaign_id": campaign_id,
                        "campaign_name": f"{month} {region} retail push",
                        "region_name": region,
                        "start_date": cursor,
                        "end_date": last,
                        "channel": ("Search", "Social", "Email", "Mixed")[r],
                        "spend": money((250_000 + r * 30_000) * (120 if cursor.month >= 11 else 100) // 100),
                    }
                )
                writers["promotions"].add(
                    {
                        "promotion_id": f"PM{month.replace('-', '')}{r}",
                        "campaign_id": campaign_id,
                        "region": region,
                        "start_date": promo_start,
                        "end_date": promo_end,
                        "discount_percent": money(1000 + r * 250),
                        "promotion_name": "Synthetic seasonal offer",
                    }
                )
                total = 0
                for store in (s for s in stores if s["region"] == region):
                    cents = round(
                        config.orders_per_day
                        * demand(cursor.replace(day=15))
                        * last.day
                        * 30_000
                        / config.stores
                    )
                    total += cents
                    writers["store_targets"].add(
                        {
                            "month": month,
                            "store_id": store["store_id"],
                            "region": region,
                            "target_revenue": money(cents),
                        }
                    )
                writers["regional_targets"].add(
                    {"month": month, "region": region, "target_revenue": money(total)}
                )
            cursor = last + timedelta(days=1)
        day = config.start
        while day <= config.end:
            rng = seeded(config.seed, f"day:{day}")
            month = day.strftime("%Y-%m")
            p_start, p_end = promotion_window(day.replace(day=1))
            promotion = p_start <= day <= p_end
            iso_year, iso_week, _ = day.isocalendar()
            writers["calendar"].add(
                {
                    "calendar_date": day,
                    "year": day.year,
                    "quarter": (day.month - 1) // 3 + 1,
                    "month": month,
                    "month_start": day.replace(day=1),
                    "week_start": day - timedelta(days=day.weekday()),
                    "iso_year": iso_year,
                    "iso_week": iso_week,
                    "day_of_week": day.isoweekday(),
                    "is_weekend": day.weekday() >= 5,
                    "is_promotion_day": promotion,
                }
            )
            count = round(
                config.orders_per_day
                * demand(day)
                * rng.uniform(0.88, 1.12)
                * (1.3 if promotion else 1.0)
                * ANOMALIES.get(day, (1.0, ""))[0]
            )
            monthly.setdefault(month, {"orders": 0, "revenue_cents": 0, "refund_cents": 0})
            for order_index in range(count):
                order_id = f"TO{day:%Y%m%d}{order_index:06}"
                store = stores[rng.randrange(len(stores))]
                region = store["region"]
                home = region if rng.random() < 0.85 else rng.choice(REGIONS)
                eligible = bisect.bisect_right(signup_dates[home], day)
                customer_id = customer_groups[home][rng.randrange(eligible)][1]
                channel = rng.choices(("store", "web", "mobile"), weights=(0.45, 0.3, 0.25))[0]
                r = REGIONS.index(region)
                campaign_id = f"CM{day:%Y%m}{r}" if rng.random() < 0.65 else None
                items = rng.choices((1, 2, 3, 4), weights=(0.2, 0.4, 0.3, 0.1))[0]
                gross = discounts = units = 0
                for line in range(items):
                    product = products[min(config.products - 1, int(rng.random() ** 2 * config.products))]
                    quantity = rng.randint(1, 3)
                    # Historical price drift is distinct from today's catalogue price.
                    unit_price = int(product["unit_price"] * 100) * (10000 + (day.year - 2023) * 250) // 10000
                    unit_cost = int(product["unit_cost"] * 100)
                    amount = unit_price * quantity
                    promo_id = f"PM{day:%Y%m}{r}" if promotion and rng.random() < 0.7 else None
                    discount_bps = (1000 + r * 250) if promo_id else 500 if rng.random() < 0.08 else 0
                    discount = amount * discount_bps // 10000
                    line_id = f"{order_id}L{line + 1:02}"
                    writers["sales_order_items"].add(
                        {
                            "order_item_id": line_id,
                            "order_id": order_id,
                            "order_date": day,
                            "product_id": product["product_id"],
                            "quantity": quantity,
                            "unit_price": money(unit_price),
                            "unit_cost": money(unit_cost),
                            "gross_amount": money(amount),
                            "discount_amount": money(discount),
                            "line_revenue": money(amount - discount),
                            "cost_amount": money(unit_cost * quantity),
                            "promotion_id": promo_id,
                        }
                    )
                    gross += amount
                    discounts += discount
                    units += quantity
                    if rng.random() < 0.075:
                        refund_day = day + timedelta(days=rng.randint(3, 35))
                        returned = rng.randint(1, quantity)
                        refund = (amount - discount) * returned // quantity
                        reason = rng.choice(("Size or fit", "Changed mind", "Damaged", "Not as expected"))
                        if refund_day <= config.end:
                            writers["sales_returns"].add(
                                {
                                    "return_id": f"RT{line_id}",
                                    "order_id": order_id,
                                    "order_item_id": line_id,
                                    "product_id": product["product_id"],
                                    "order_date": day,
                                    "return_date": refund_day,
                                    "quantity": returned,
                                    "refund_amount": money(refund),
                                    "returned_cost": money(unit_cost * returned),
                                    "reason": reason,
                                }
                            )
                            summary["refunds"] += refund
                            refund_month = refund_day.strftime("%Y-%m")
                            monthly.setdefault(
                                refund_month, {"orders": 0, "revenue_cents": 0, "refund_cents": 0}
                            )
                            monthly[refund_month]["refund_cents"] += refund
                revenue = gross - discounts
                tax = revenue * 7 // 100
                shipping = 0 if channel == "store" or revenue >= 15000 else 599
                writers["sales_orders"].add(
                    {
                        "order_id": order_id,
                        "customer_id": customer_id,
                        "store_id": store["store_id"],
                        "order_timestamp": datetime(
                            day.year, day.month, day.day, rng.randrange(1, 15), rng.randrange(60), tzinfo=UTC
                        ),
                        "order_date": day,
                        "month": month,
                        "region": region,
                        "channel": channel,
                        "currency": "USD",
                        "gross_sales": money(gross),
                        "discount_amount": money(discounts),
                        "revenue": money(revenue),
                        "tax_amount": money(tax),
                        "shipping_amount": money(shipping),
                        "total_paid": money(revenue + tax + shipping),
                        "units": units,
                        "status": "completed",
                        "campaign_id": campaign_id,
                    }
                )
                summary["revenue"] += revenue
                summary["gross_sales"] += gross
                summary["discounts"] += discounts
                summary["units"] += units
                monthly[month]["orders"] += 1
                monthly[month]["revenue_cents"] += revenue
            if day.day == calendar.monthrange(day.year, day.month)[1] or day == config.end:
                progress(f"Generated through {day}: {writers['sales_orders'].count:,} orders")
            day += timedelta(days=1)
        files = {name: writer.close() for name, writer in writers.items()}
    except BaseException:
        for writer in writers.values():
            try:
                writer.writer.close()
            except Exception:
                pass
        raise
    parameters = json.loads(json.dumps(asdict(config), default=serialized))
    stable = {k: v for k, v in parameters.items() if k not in ("start", "end")}
    manifest = {
        "version": VERSION,
        "parameters": parameters,
        "configuration_id": record_hash(stable),
        "files": files,
        "summary_cents": summary,
        "monthly": dict(sorted(monthly.items())),
        "anomalies": [
            {"date": str(d), "multiplier": factor, "description": label}
            for d, (factor, label) in ANOMALIES.items()
            if config.start <= d <= config.end
        ],
    }
    (output / "schema.json").write_text(json.dumps(schema_export(), indent=2) + "\n")
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def read_manifest(directory: Path, verify_hashes=True):
    manifest = json.loads((directory / "manifest.json").read_text())
    if manifest.get("version") != VERSION or set(manifest["files"]) != set(BY_NAME):
        raise ValueError("Unsupported or incomplete retail bundle.")
    GeneratorConfig(
        **{
            k: date.fromisoformat(v) if k in ("start", "end") else v
            for k, v in manifest["parameters"].items()
        }
    ).validate()
    stable = {k: v for k, v in manifest["parameters"].items() if k not in ("start", "end")}
    if manifest["configuration_id"] != record_hash(stable):
        raise ValueError("Configuration fingerprint does not match the manifest.")
    for name, entry in manifest["files"].items():
        if entry["file"] != f"{name}.parquet":
            raise ValueError("Unexpected file path in bundle.")
        path = directory / entry["file"]
        if path.is_symlink() or not pq.read_schema(path).equals(BY_NAME[name].arrow_schema()):
            raise ValueError(f"Unexpected schema or symlink: {name}")
        if pq.ParquetFile(path).metadata.num_rows != entry["rows"]:
            raise ValueError(f"Row count mismatch: {name}")
        if verify_hashes:
            with path.open("rb") as stream:
                if hashlib.file_digest(stream, "sha256").hexdigest() != entry["sha256"]:
                    raise ValueError(f"Checksum mismatch: {name}")
    return manifest
