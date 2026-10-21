"""Report presentation must remain a pure, immutable-evidence transformation."""

import hashlib
import io
import json
import zipfile
from copy import deepcopy
from xml.etree import ElementTree as ET

import pytest

from app.report_exports import _render


def example(style="technical"):
    prediction = {
        "kind": "scenario",
        "method": "timesfm_3",
        "model": "TimesFM 3.0",
        "provider": "bigquery",
        "preview": True,
        "cutoff": "2026-09-30",
        "horizon": 2,
        "grain": "month",
        "target": "revenue",
        "selection_reason": "Lowest passing chronological MAE.",
        "interval": None,
        "limitations": ["Conditional assumptions, not causal lift."],
        "scores": {
            "timesfm_3": {
                "mae": 10.25,
                "rmse": 12.5,
                "folds": [
                    {
                        "train_end": "2026-05-31",
                        "test_start": "2026-06-01",
                        "test_end": "2026-07-31",
                        "mae": 10.25,
                    }
                ],
            },
            "seasonal_naive": {"mae": 30.0, "rmse": 32.0, "folds": []},
        },
        "drivers": ["promotion"],
        "assumptions": ["Baseline promotion 0; alternative promotion 1."],
        "future_drivers": [{"promotion": 0}, {"promotion": 0}],
        "scenario_drivers": [{"promotion": 1}, {"promotion": 1}],
        "comparison": {
            "context": 64,
            "input_hash": "frozen-input",
            "status": "evaluated",
            "selection_policy_version": 2,
        },
    }
    artifact = {
        "id": "saved-sales",
        "title": "Revenue & assumptions <not executable>",
        "columns": [
            {"name": "month", "type": "string"},
            {"name": "observed", "type": "number"},
            {"name": "forecast", "type": "number"},
        ],
        "complete": True,
        "row_count": 3,
        "visualization": {
            "title": "Saved revenue",
            "type": "line",
            "x": "month",
            "y": ["observed", "forecast"],
            "measures": [
                {"field": "observed", "label": "Observed", "unit": "currency", "currency": "USD"},
                {"field": "forecast", "label": "Forecast", "unit": "currency", "currency": "USD"},
            ],
        },
        "provenance": [
            {
                "source": "bigquery",
                "executed_at": "2026-10-18T00:00:00Z",
                "sql": "SELECT 'saved only' AS evidence",
                "job_id": "captured-job",
            }
        ],
        "assumptions": ["Complete saved calendar."],
        "prediction": prediction,
    }
    rows = [
        {"month": "2026-09-01", "observed": 1234.56789, "forecast": None},
        {"month": "2026-10-01", "observed": None, "forecast": 1400.12345},
        {"month": "2026-11-01", "observed": None, "forecast": 1500.98765},
    ]
    document = {
        "title": "Revenue planning – saved evidence",
        "report_id": "report-1",
        "version": 2,
        "created_at": "2026-10-18T00:00:00+00:00",
        "style": style,
        "summary": "**Validated findings**\n\n- Saved evidence only.\n- No new inference.",
        "scope": "Revenue through September 2026.",
        "data_profile": "timeseries",
        "model": "saved-model",
        "mode_note": "Reviewed report",
        "claims": [
            {
                "label": "Saved revenue",
                "formatted": "USD 1,234.57",
                "calculation": "saved total",
                "artifact_id": "saved-sales",
            }
        ],
        "sections": [
            {
                "title": "Forecast evidence",
                "markdown": "## Interpretation\nSaved **forecast** & <unsafe> text.\n\n| Item | Value |\n| --- | --- |\n| Source | Frozen |",
                "artifact_ids": ["saved-sales"],
                "kind": "finding",
            }
        ]
        + [
            {
                "title": title,
                "markdown": "- Read the saved assumptions.",
                "artifact_ids": [],
                "kind": "finding",
            }
            for title in ["Assumptions", "Decision context", "Recommendations"]
        ],
        "definitions": ["Revenue after discounts."],
        "assumptions": ["Explicit future promotion."],
        "limitations": ["Synthetic data, no guarantees."],
        "skills_used": [],
    }
    return document, {"saved-sales": (artifact, rows)}


@pytest.mark.parametrize("style", ["business", "technical"])
def test_readable_exports_and_lossless_bundle(style):
    document, artifacts = example(style)
    captured = deepcopy((document, artifacts))
    files = _render(document, artifacts)
    assert (document, artifacts) == captured
    assert files["pdf"].startswith(b"%PDF")
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with zipfile.ZipFile(io.BytesIO(files["docx"])) as archive:
        xml = ET.fromstring(archive.read("word/document.xml"))
        text = " ".join(xml.itertext())
        for expected in [
            "Executive summary",
            "Saved verified highlights",
            "Forecast method and validation",
            "Saved future point estimates",
            "Conditional scenario assumptions",
            "Validated intervals unavailable",
            "Definitions",
            "USD 1,234.57",
            "<unsafe>",
        ]:
            assert expected in text
        assert "{'kind'" not in text
        assert xml.findall(".//w:tblHeader", ns)
        targets = {node.attrib["{" + ns["w"] + "}name"] for node in xml.findall(".//w:bookmarkStart", ns)}
        assert all(
            node.attrib.get("{" + ns["w"] + "}anchor") in targets
            for node in xml.findall(".//w:hyperlink", ns)
        )
        assert "PAGE" in archive.read("word/footer1.xml").decode()
        assert ("held-out folds" in text) == (style == "technical")
    with zipfile.ZipFile(io.BytesIO(files["data"])) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        item = manifest["datasets"][0]
        csv = archive.read(item["file"])
        assert "1234.56789" in csv.decode("utf-8-sig")
        assert "USD" not in csv.decode("utf-8-sig")
        assert hashlib.sha256(csv).hexdigest() == item["sha256"]
        assert item["prediction"] == artifacts["saved-sales"][0]["prediction"]
        assert json.loads(archive.read("report.json")) == document
        assert "USD" in archive.read("data_dictionary.csv").decode()
        assert "saved-sales.csv" in archive.read("README.md").decode()


def test_new_exports_are_repeatable_without_changing_old_file_contract():
    document, artifacts = example()
    first = _render(document, artifacts)
    second = _render(document, artifacts)
    assert first == second


def test_allocated_adjustments_do_not_become_independent_forecasts():
    document, artifacts = example()
    artifacts["saved-sales"][0]["prediction"].update(kind="adjusted_plan", status="allocated")
    files = _render(document, artifacts)
    with zipfile.ZipFile(io.BytesIO(files["docx"])) as archive:
        text = archive.read("word/document.xml").decode()
        assert "not statistical predictions" in text
        assert "not independently modeled or validated" in text
