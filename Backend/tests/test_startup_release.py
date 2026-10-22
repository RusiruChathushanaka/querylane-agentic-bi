"""Release policy tests are pure: no cloud configuration or data is changed."""
import importlib.util
from pathlib import Path

import pytest

spec = importlib.util.spec_from_file_location("startup_runtime", Path(__file__).parents[2] / "infra/runtime_settings.py")
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)


def test_api_service_minimum_and_existing_scaling_are_preserved():
    existing = {"metadata": {"annotations": {"run.googleapis.com/maxScale": "100"}}, "spec": {"template": {"metadata": {"annotations": {"autoscaling.knative.dev/maxScale": "2", "run.googleapis.com/startup-cpu-boost": "true", "run.googleapis.com/cpu-throttling": "false"}}}}}
    before = repr(existing)
    assert runtime.release_scaling("backend", existing) == ["--min", "1"]
    assert repr(existing) == before
    assert runtime.release_scaling("frontend", existing) == ["--min", "1"]
    assert runtime.release_scaling("worker", existing) == []
    existing["metadata"]["annotations"]["run.googleapis.com/minScale"] = "2"
    assert runtime.release_scaling("backend", existing) == ["--min", "2"]
    assert runtime.release_scaling("frontend", existing) == ["--min", "2"]


def test_foundation_remains_bounded_and_mixed_minima_require_review():
    assert runtime.release_scaling("backend", {}) == ["--max-instances", "2", "--min", "1"]
    assert runtime.release_scaling("frontend", {}) == ["--max-instances", "2", "--min", "1"]
    with pytest.raises(ValueError):
        runtime.release_scaling("frontend", {"spec": {"template": {"metadata": {"annotations": {"autoscaling.knative.dev/minScale": "1"}}}}})
    with pytest.raises(ValueError):
        runtime.release_scaling("backend", {"spec": {"template": {"metadata": {"annotations": {"autoscaling.knative.dev/minScale": "1"}}}}})


def test_dataset_and_verified_timesfm_settings_survive_release_preparation():
    existing = {"DATA_PROFILE": "timeseries", "SOURCE_ROW_LIMIT": "30000", "REPORT_TIMESFM_ENABLED": "true", "REPORT_TIMESFM_VERIFIED": "true"}
    result = runtime.preserve_analysis_settings({"DATA_PROFILE": "timeseries"}, existing)
    assert result["SOURCE_ROW_LIMIT"] == "30000"
    assert result["REPORT_TIMESFM_ENABLED"] == result["REPORT_TIMESFM_VERIFIED"] == "true"
