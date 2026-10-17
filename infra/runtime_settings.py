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
