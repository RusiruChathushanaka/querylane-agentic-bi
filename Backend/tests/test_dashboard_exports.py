import copy
import csv
import hashlib
import io
import json
import zipfile
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.config import Settings
from app.dashboard_exports import card_notes, display_value, download, prepare_card, render_file, snapshot
from app.dashboard_models import ChartViewState
from app.dashboards import Dashboards
from app.errors import AppError
from app.main import create_app
from app.storage import MemoryStore


async def example(store):
    rows = [
        {
            "month": f"{2020 + i // 12:04}-{i % 12 + 1:02}",
            "revenue": str(Decimal(i) + Decimal("0.25")),
            "label": "=HYPERLINK(unsafe)" if i == 0 else "normal",
        }
        for i in range(75)
    ]
    artifact = {
        "id": "series",
        "title": "Revenue",
        "columns": [
            {"name": "month", "type": "STRING"},
            {"name": "revenue", "type": "NUMERIC"},
            {"name": "label", "type": "STRING"},
        ],
        "row_count": 75,
        "page_count": 2,
        "complete": False,
        "created_at": "2026-01-01T00:00:00Z",
        "visualization": {
            "type": "line",
            "title": "Revenue",
            "x": "month",
            "y": ["revenue"],
            "dimension_kind": "temporal",
            "granularity": "month",
            "measures": [{"field": "revenue", "unit": "currency", "currency": "USD", "additive": True}],
        },
        "provenance": [{"source": "bigquery", "executed_at": "2026-01-01T00:00:00Z", "sql": "SELECT saved"}],
        "assumptions": ["Synthetic fixture"],
    }
    item = {
        "id": "card",
        "artifact_id": "series",
        "conversation_id": "gone",
        "title": "2024 saved scope",
        "note": "Observed values, including zero and missing data.",
        "width": "standard",
        "removed": False,
        "view": ChartViewState(
            view="line", start="2024-01-01", end="2024-12-31", primary="revenue", visible_measures=["revenue"]
        ).model_dump(mode="json"),
    }
    board = {
        "id": "board",
        "name": "Export verification",
        "description": "Saved charts",
        "revision": 2,
        "deleted": False,
        "item_ids": ["card"],
        "card_count": 1,
    }
    await store.put("dashboards", "board", board)
    await store.put("dashboards/board/items", "card", item)
    await store.put("artifacts", "series", artifact)
    await store.put("artifacts/series/pages", "0", {"rows": rows[:40]})
    await store.put("artifacts/series/pages", "1", {"rows": rows[40:]})
    return Dashboards(store, Settings(environment="test")), artifact, rows, item


async def test_saved_scope_full_csvs_formula_protection_and_read_only_snapshot():
    store = MemoryStore()
    service, artifact, rows, item = await example(store)
    before = copy.deepcopy(store.documents)
    board, datasets = await snapshot(service, "board", 2)
    prepared = prepare_card(item, artifact, rows)
    assert prepared["coverage"]["selected_rows"] == 12
    assert prepared["rows"][0]["month"] == "2024-01"
    assert prepared["rows"][-1]["month"] == "2024-12"
    assert "PARTIAL" in " ".join(card_notes(item, artifact, prepared))
    with zipfile.ZipFile(io.BytesIO(render_file(board, datasets, "data"))) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        data = archive.read("series.csv")
        assert manifest["dashboard"]["revision"] == 2
        assert manifest["datasets"][0]["sha256"] == hashlib.sha256(data).hexdigest()
        records = list(csv.DictReader(io.StringIO(data.decode("utf-8-sig"))))
        assert len(records) == 75
        assert records[0]["label"].startswith("'=HYPERLINK")
        assert sum(Decimal(r["revenue"]) for r in records) == Decimal("2793.75")
    manifest = json.loads(render_file(board, datasets, "json"))
    assert manifest["datasets"][0]["row_count"] == 75
    assert "rows" not in manifest["datasets"][0]
    assert store.documents == before


async def test_conflicts_deleted_missing_pages_and_export_busy_are_actionable():
    store = MemoryStore()
    service, *_ = await example(store)
    with pytest.raises(AppError) as stale:
        await snapshot(service, "board", 1)
    assert stale.value.code == "dashboard_conflict"
    await service.export_slot.acquire()
    try:
        with pytest.raises(AppError) as busy:
            await download(service, "board", 2, "png")
        assert busy.value.status == 429
    finally:
        service.export_slot.release()
    await store.delete("artifacts/series/pages", "1")
    with pytest.raises(AppError) as missing:
        await snapshot(service, "board", 2)
    assert missing.value.code == "artifact_incomplete"
    board = await store.get("dashboards", "board")
    await store.put("dashboards", "board", board | {"deleted": True})
    with pytest.raises(AppError) as deleted:
        await snapshot(service, "board", 2)
    assert deleted.value.code == "dashboard_deleted"


async def test_image_pdf_formats_use_saved_evidence_and_escape_labels(tmp_path):
    store = MemoryStore()
    service, *_ = await example(store)
    board, datasets = await snapshot(service, "board", 2)
    for kind in ["png", "jpeg", "pdf"]:
        content = render_file(board, datasets, kind)
        if kind == "pdf":
            assert content.startswith(b"%PDF-")
        else:
            image = Image.open(io.BytesIO(content))
            assert image.width == 1800 and image.height > 500
        (tmp_path / f"dashboard.{kind}").write_bytes(content)
    assert display_value("10.20", {"unit": "currency", "currency": "USD"}, 2) == "USD 10.20"
    assert display_value("0.125", {"unit": "percent", "percent_scale": "fraction"}, 1) == "12.5%"
    assert display_value("12.5", {"unit": "percent", "percent_scale": "whole"}, 1) == "12.5%"
    assert display_value(None, {"unit": "count"}, 2) == "Not available"


def test_download_api_uses_no_source_or_model_calls_and_preserves_attachment_headers():
    store = MemoryStore()
    with TestClient(create_app(Settings(environment="test"), store_override=store)) as client:
        client.portal.call(example, store)
        services = client.app.state.services
        services.connectors.query = AsyncMock(side_effect=AssertionError("SQL forbidden"))
        services.ai.choose_skills = AsyncMock(side_effect=AssertionError("Model forbidden"))
        response = client.get("/api/v1/dashboards/board/downloads/data?expected_revision=2")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/zip"
        assert 'filename="querylane-dashboard-board-r2.zip"' in response.headers["content-disposition"]
        assert response.headers["cache-control"] == "no-store"
        assert client.get("/api/v1/dashboards/board/downloads/png?expected_revision=1").status_code == 409
        assert client.get("/api/v1/dashboards/board/downloads/html?expected_revision=2").status_code == 422
        services.connectors.query.assert_not_called()
        services.ai.choose_skills.assert_not_called()


@pytest.mark.parametrize("kind", ["bar", "area", "pie", "scatter", "table", "kpi"])
async def test_every_chart_family_and_mixed_units_can_render(kind):
    store = MemoryStore()
    _, artifact, _, item = await example(store)
    rows = [
        {"category": "Long category A", "revenue": "10.20", "units": 2},
        {"category": "Category B", "revenue": "20.40", "units": 3},
    ]
    if kind == "kpi":
        rows = rows[:1]
    artifact = artifact | {
        "columns": [
            {"name": "category", "type": "STRING"},
            {"name": "revenue", "type": "NUMERIC"},
            {"name": "units", "type": "INT64"},
        ],
        "row_count": len(rows),
        "complete": True,
        "visualization": {
            "type": kind,
            "title": "Mixed units",
            "x": "category",
            "y": ["revenue"] if kind == "pie" else ["revenue", "units"],
            "measures": [{"field": "revenue", "unit": "currency", "currency": "USD", "additive": True}]
            + ([] if kind == "pie" else [{"field": "units", "unit": "count", "additive": True}]),
        },
    }
    item = item | {
        "view": ChartViewState(
            view=kind,
            primary="revenue",
            visible_measures=artifact["visualization"]["y"],
            scatter_x="units" if kind == "scatter" else None,
            scatter_y="revenue" if kind == "scatter" else None,
        ).model_dump(mode="json")
    }
    board = {
        "id": "formats",
        "name": "Mixed units",
        "description": "",
        "revision": 1,
        "card_count": 1,
        "items": [item],
    }
    content = render_file(board, {"series": (artifact, rows)}, "png")
    assert Image.open(io.BytesIO(content)).width == 1800


async def test_concurrent_snapshot_edits_and_combined_budgets_fail_without_partial_export(monkeypatch):
    from app import dashboard_exports

    store = MemoryStore()
    service, *_ = await example(store)
    original = store.get

    async def interleaved(collection, key):
        if collection == "artifacts/series/pages":
            board = await original("dashboards", "board")
            await store.put("dashboards", "board", board | {"revision": 3})
        return await original(collection, key)

    monkeypatch.setattr(store, "get", interleaved)
    with pytest.raises(AppError) as changed:
        await snapshot(service, "board", 2)
    assert changed.value.code == "dashboard_conflict"
    monkeypatch.setattr(store, "get", original)
    monkeypatch.setattr(dashboard_exports, "MAX_BYTES", 10)
    with pytest.raises(AppError) as too_big:
        await snapshot(service, "board", 3)
    assert too_big.value.status == 413
