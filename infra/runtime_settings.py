"""Pure release configuration preservation; no cloud access or implicit feature enablement."""

PLANNING_KEYS = {"PLANNING_ENABLED", "FORECAST_PLAN_FIT_LIMIT"}


def preserve_analysis_settings(values, existing):
    values.update(
        {
            key: value
            for key, value in existing.items()
            if key.startswith("REPORT_")
            or key == "REPORTS_ENABLED"
            or key in PLANNING_KEYS
        }
    )
    # First compatible release must explicitly enable public planning admission.
    values.setdefault("PLANNING_ENABLED", "false")
    values.setdefault("FORECAST_PLAN_FIT_LIMIT", "128")
    if existing.get("DATA_PROFILE") == values.get("DATA_PROFILE") and existing.get(
        "SOURCE_ROW_LIMIT"
    ):
        values["SOURCE_ROW_LIMIT"] = existing["SOURCE_ROW_LIMIT"]
    return values


def release_scaling(service, existing):
    """Prepare the approved warm frontend/API policy; preserve existing ceilings and other services."""
    flags = [] if existing else ["--max-instances", "2"]
    if service in {"backend", "frontend"}:
        annotations = existing.get("metadata", {}).get("annotations", {})
        revision = existing.get("spec", {}).get("template", {}).get("metadata", {}).get("annotations", {})
        if int(revision.get("autoscaling.knative.dev/minScale", "0")) > 0:
            raise ValueError("Resolve revision-level minimum instances before applying the service-level warm-service policy.")
        flags += ["--min", str(max(1, int(annotations.get("run.googleapis.com/minScale", "0"))))]
    return flags
