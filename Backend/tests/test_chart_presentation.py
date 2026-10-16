import csv
import io
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

from app.chart_presentation import csv_line, metadata, present, sampled_rows
from app.config import Settings
from app.main import create_app
from app.storage import MemoryStore


def artifact(rows, **overrides):
    return {
        "id": "chart-test",
        "row_count": len(rows),
        "page_count": (len(rows) + 249) // 250,
        "complete": True,
        "columns": [{"name": "month", "type": "STRING"}, {"name": "revenue", "type": "NUMERIC"}],
        "visualization": {
            "type": "line",
            "title": "Sales",
            "x": "month",
            "y": ["revenue"],
            "version": 2,
            "dimension_kind": "temporal",
            "granularity": "month",
            "measures": [{"field": "revenue", "unit": "currency", "currency": "USD", "additive": True}],
        },
        **overrides,
    }


def test_full_month_history_and_exact_comparisons():
    rows = [{"month": f"{2023 + i // 12}-{i % 12 + 1:02}", "revenue": str(i * 10)} for i in range(45)]
    result = present(artifact(rows), rows)
    assert len(result["rows"]) == 45
    assert result["stats"]["sum"] == 9900
    assert result["insights"][1]["previous_label"] == "2026-08"
    assert result["insights"][1]["delta"] == 10
    assert result["rows"][-1]["_detail"]["revenue"]["previous_label"] == "2026-08"


def test_daily_history_includes_zero_and_range_summaries():
    rows = [
        {"month": (date(2023, 1, 1) + timedelta(days=i)).isoformat(), "revenue": 0 if i == 424 else 10}
        for i in range(1369)
    ]
    art = artifact(rows)
    art["visualization"]["granularity"] = "day"
    result = present(art, rows)
    assert len(result["rows"]) == 1369
    assert result["stats"]["sum"] == 13680
    assert result["rows"][424]["revenue"] == 0
    scoped = present(art, rows, start=date(2024, 2, 29), end=date(2024, 2, 29))
    assert scoped["stats"]["sum"] == 0 and len(scoped["rows"]) == 1


def test_missing_periods_nulls_and_partial_periods():
    rows = [
        {"month": "2024-01", "revenue": 10},
        {"month": "2024-03", "revenue": None},
        {"month": "2024-04", "revenue": 20},
    ]
    result = present(artifact(rows), rows)
    assert result["rows"][1]["_gap"] and result["rows"][1]["revenue"] is None
    assert all(i["kind"] != "change" for i in result["insights"])
    rows = [
        {"month": "2024-01", "revenue": 0},
        {"month": "2024-02", "revenue": 10},
        {"month": "2024-03", "revenue": 20},
    ]
    art = artifact(rows, data_coverage=["2024-01-01", "2024-03-15"])
    result = present(art, rows)
    assert result["insights"][1]["label"] == "2024-02"
    assert result["insights"][1]["percent"] is None
    assert not result["rows"][-1]["_detail"]["revenue"]


def test_partial_result_suppresses_totals_and_changes():
    rows = [{"month": "2024-01", "revenue": 10}, {"month": "2024-02", "revenue": 20}]
    result = present(artifact(rows, complete=False), rows)
    assert result["stats"]["sum"] is None
    assert [i["kind"] for i in result["insights"]] == ["peak"]


def test_sampling_keeps_extrema_endpoints_and_null_boundaries():
    rows = [{"a": i, "b": -i} for i in range(9000)]
    rows[4321]["a"] = 100_000
    rows[3200]["a"] = None
    selected, sampled = sampled_rows(rows, ["a", "b"])
    assert sampled and len(selected) <= 2000
    assert selected[0] == rows[0] and selected[-1] == rows[-1]
    assert rows[4321] in selected and rows[3200] in selected
    assert selected == sampled_rows(rows, ["a", "b"])[0]
    alternating = [{"a": None if i % 2 else i} for i in range(4000)]
    assert sampled_rows(alternating, ["a"])[0] == []


def test_duplicate_dates_do_not_generate_period_comparisons():
    rows = [{"month": "2024-01", "revenue": 10}, {"month": "2024-01", "revenue": 20}]
    assert len(present(artifact(rows), rows)["insights"]) == 1


def test_categories_top_n_shares_negative_and_tied_values():
    rows = [{"month": f"Category {i}", "revenue": 10} for i in range(25)]
    art = artifact(rows)
    art["visualization"].update(type="bar", dimension_kind="category", granularity=None)
    result = present(art, rows, top=5)
    assert len(result["rows"]) == 5 and result["coverage"]["omitted_categories"] == 20
    assert result["insights"][1]["value"] == 4 and result["stats"]["sum"] == 250
    assert not result["composition"]
    rows = rows[:4]
    assert present(artifact(rows, visualization=art["visualization"]), rows)["composition"]
    rows[0]["revenue"] = -2
    assert not present(artifact(rows, visualization=art["visualization"]), rows)["composition"]


def test_fractional_percent_points_and_units():
    rows = [{"month": "2024-01", "revenue": 0.1}, {"month": "2024-02", "revenue": 0.15}]
    art = artifact(rows)
    art["visualization"]["measures"] = [{"field": "revenue", "unit": "percent", "percent_scale": "fraction"}]
    result = present(art, rows)
    assert result["insights"][1]["percentage_points"] == 5
    assert result["stats"]["sum"] is None


def test_explicit_targets_and_legacy_conservative_metadata():
    rows = [{"month": "2024-01", "revenue": 12, "target": 10}]
    art = artifact(rows)
    art["columns"].append({"name": "target", "type": "NUMERIC"})
    art["visualization"]["y"].append("target")
    art["visualization"]["measures"].append(
        {"field": "target", "unit": "currency", "currency": "USD", "role": "target", "compares_to": "revenue"}
    )
    result = present(art, rows)
    assert result["insights"][-1]["delta"] == 2
    assert result["rows"][0]["_detail"]["target"]["variance"]["percent"] == 20
    art["visualization"] = {
        "type": "line",
        "title": "Old",
        "x": "month",
        "y": ["revenue", "target"],
        "format": "currency",
    }
    assert all(
        m["unit"] == "number" and not m["additive"]
        for m in metadata(art["visualization"], art["columns"], rows)["measures"]
    )


@pytest.mark.parametrize("value", ['=WEBSERVICE("evil")', " +cmd", "-1+2", "@SUM(A1)", "\t=1+2", "\r=1+2"])
def test_csv_formula_injection(value):
    exported = next(csv.reader(io.StringIO(csv_line([value, "-12.50", None, 'a,b"c']))))
    assert exported == ["'" + value, "-12.50", "", 'a,b"c']


def test_api_reads_all_pages_exports_and_validates_without_connector_calls():
    rows = [{"month": (date(2023, 1, 1) + timedelta(days=i)).isoformat(), "revenue": i} for i in range(1369)]
    art = artifact(rows)
    art["visualization"]["granularity"] = "day"
    store = MemoryStore()
    store.documents[("artifacts", art["id"])] = art
    for index in range(art["page_count"]):
        store.documents[(f"artifacts/{art['id']}/pages", str(index))] = {
            "rows": rows[index * 250 : (index + 1) * 250]
        }
    with TestClient(create_app(Settings(environment="test"), store_override=store)) as client:
        path = f"/api/v1/artifacts/{art['id']}"
        result = client.get(path + "/chart-data?top=5")
        assert result.status_code == 200 and len(result.json()["rows"]) == 1369
        response = client.get(path + "/export.csv")
        assert response.status_code == 200
        assert len(list(csv.reader(io.StringIO(response.text.lstrip("\ufeff"))))) == 1370
        for query in [
            "primary=not_real",
            "start=bad",
            "start=2025-01-01&end=2024-01-01",
            "top=7",
            "order=sql",
        ]:
            assert client.get(path + "/chart-data?" + query).status_code == 422
        assert client.get("/api/v1/artifacts/missing/chart-data").status_code == 404
        del store.documents[(f"artifacts/{art['id']}/pages", "1")]
        assert client.get(path + "/chart-data").status_code == 409
        assert client.get(path + "/export.csv").status_code == 409


def test_scatter_switch_does_not_apply_top_n_to_a_category_artifact():
    rows = [{"month": f"item-{i}", "revenue": i, "quantity": i * 2} for i in range(80)]
    art = artifact(rows)
    art["visualization"].update(type="bar", dimension_kind="category", granularity=None)
    art["columns"].append({"name": "quantity", "type": "INT64"})
    result = present(art, rows, view="scatter")
    assert len(result["rows"]) == 80 and result["coverage"]["omitted_categories"] == 0


def test_unknown_rate_scale_is_not_summed_or_used_for_composition():
    rows = [{"month": "A", "revenue": 0.1}, {"month": "B", "revenue": 0.2}]
    art = artifact(rows)
    art["visualization"].update(
        type="bar",
        dimension_kind="category",
        granularity=None,
        measures=[{"field": "revenue", "unit": "percent", "additive": True}],
    )
    result = present(art, rows)
    assert result["stats"]["sum"] is None and not result["composition"]


def test_sampling_stats_and_tooltip_changes_use_full_unsampled_rows():
    rows = [
        {"month": (date(2020, 1, 1) + timedelta(days=i)).isoformat(), "revenue": i % 29} for i in range(4000)
    ]
    art = artifact(rows)
    art["visualization"]["granularity"] = "day"
    result = present(art, rows)
    assert result["coverage"]["sampled"] and len(result["rows"]) <= 2000
    assert result["stats"]["sum"] == sum(r["revenue"] for r in rows)
    for row in result["rows"][1:]:
        assert (
            row["_detail"]["revenue"]["previous_label"]
            == (date.fromisoformat(row["month"]) - timedelta(days=1)).isoformat()
        )


def test_multi_dimension_categories_keep_month_context_without_reaggregation():
    rows = [
        {"month": "2024-01", "region": "North", "revenue": 10},
        {"month": "2024-02", "region": "North", "revenue": 20},
    ]
    art = artifact(rows)
    art["columns"].append({"name": "region", "type": "STRING"})
    art["visualization"].update(type="bar", x="region", dimension_kind="category", granularity=None)
    result = present(art, rows)
    assert result["visualization"]["x"] == "_dimension"
    assert result["rows"][0]["_dimension"] == "North · 2024-02"
    assert result["stats"]["sum"] == 30


def test_ambiguous_temporal_grain_falls_back_instead_of_connecting_cohorts():
    rows = [{"month": "2024-01", "revenue": 10}, {"month": "2024-01", "revenue": 20}]
    result = present(artifact(rows), rows)
    assert result["rows"] == [] and "time bucket" in result["warning"]


def test_single_kpi_is_not_described_as_a_leading_category():
    rows = [{"revenue": 10}]
    art = artifact(rows)
    art["columns"] = [{"name": "revenue", "type": "NUMERIC"}]
    art["visualization"].update(type="kpi", x=None, dimension_kind="category", granularity=None)
    assert present(art, rows)["insights"] == []
