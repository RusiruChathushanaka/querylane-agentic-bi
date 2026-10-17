"""Application-owned candidate selection over a frozen saved series."""

import copy
import math

from app.errors import AppError
from app.report_statistics import _valid_domain, forecast, prepare_series
from app.timesfm import FATAL, METHOD, MODEL, TimesFM, batches, digest


def eligible(score, baseline):
    return (
        baseline["mae"] > 0
        and score["mae"] <= baseline["mae"] * 0.95
        and sum(a["mae"] < b["mae"] for a, b in zip(score["folds"], baseline["folds"])) >= 2
    )


def choose(scores):
    baseline = scores["seasonal_naive"]
    passing = [
        name for name, score in scores.items() if name == "seasonal_naive" or eligible(score, baseline)
    ]
    # Stable tie: statistical candidates precede managed inference.
    return min(passing, key=lambda name: (scores[name]["mae"], name == METHOD))


async def reserve_candidates(engine, run, lease, plan):
    saved = await engine.repo.read_checkpoint(run["id"], "timesfm_admissions")
    if saved is not None:
        return saved
    admitted = {}
    policy = run["brief"].get("forecast_policy", {})
    slots = max(0, engine.settings.report_query_limit - len(plan["tasks"]) * 2) // 2
    for index, spec in sorted(enumerate(plan["forecasts"]), key=lambda pair: pair[1].get("priority", 1)):
        reason = "TimesFM is disabled or its managed compatibility has not been verified."
        if policy.get("enabled") and spec.get("candidate_policy", "auto_compare") == "auto_compare":
            try:
                if slots <= 0:
                    raise AppError(
                        "Evidence collection leaves no complete TimesFM job pair within the report query budget.",
                        422,
                        "timesfm_budget",
                    )
                h = spec.get("horizon") or {"day": 28, "week": 12, "month": 3}[spec["grain"]]
                drivers = len(spec["drivers"])
                final_groups = 2 if spec.get("scenario_drivers") else 1
                amounts = {
                    "timesfm_targets": 1,
                    "timesfm_jobs": 2,
                    "queries": 2,
                    "scan_bytes": 2 * engine.settings.bigquery_max_bytes,
                    "fits": 3 + final_groups,
                    "timesfm_input_tokens": (3 + final_groups) * (2048 + (2048 + h) * drivers),
                    "timesfm_output_tokens": (3 + final_groups) * h,
                }
                await engine.repo.reserve_once(
                    lease, f"timesfm_admission_{index}", amounts, {"index": index, "reservation": amounts}
                )
                admitted[str(index)] = {"admitted": True}
                slots -= 1
                continue
            except AppError as exc:
                if exc.code in FATAL | {"timesfm_reconcile"}:
                    raise
                reason = exc.message
        elif spec.get("candidate_policy") == "statistical_only":
            reason = "The analysis plan selected statistical methods only: " + spec.get("rationale", "")
        admitted[str(index)] = {"admitted": False, "reason": reason}
    return await engine.repo.checkpoint(lease, "timesfm_admissions", admitted)


def score_remote(prepared, result):
    import numpy as np

    y, h, n, dates, domain = (*[prepared[k] for k in ("y", "horizon", "n", "dates")], prepared["spec"].domain)
    errors, folds = [], []
    for i, origin in enumerate([n - 3 * h, n - 2 * h, n - h]):
        values = [row["value"] for row in result["series"][f"fold_{i}"]]
        if not _valid_domain(values, domain):
            raise ValueError("TimesFM backtest violates the metric domain; values were not clipped.")
        residual = (y[origin : origin + h] - np.asarray(values)).tolist()
        errors.extend(residual)
        folds.append(
            {
                "train_end": dates[origin - 1].isoformat(),
                "test_start": dates[origin].isoformat(),
                "test_end": dates[origin + h - 1].isoformat(),
                "mae": sum(abs(v) for v in residual) / h,
            }
        )
    return {
        "mae": sum(abs(v) for v in errors) / len(errors),
        "rmse": math.sqrt(sum(v * v for v in errors) / len(errors)),
        "folds": folds,
        "errors": errors,
    }


def intervals(result, score, predicted, domain):
    import numpy as np

    h = result["horizon"]
    calibration, validation = np.asarray(score["errors"][:h]), np.asarray(score["errors"][h:])
    result["interval"] = None
    if len(calibration) < 20 or len(validation) < 40:
        return
    width = float(np.quantile(np.abs(calibration), 0.95, method="higher"))
    coverage = float(np.mean(np.abs(validation) <= width))
    lower, upper = np.asarray(predicted) - width, np.asarray(predicted) + width
    if coverage >= 0.85 and width > 0 and _valid_domain(lower, domain) and _valid_domain(upper, domain):
        result["interval"] = {
            "level": 0.95,
            "coverage": coverage,
            "method": "earlier-fold residual quantile; later-fold coverage",
        }
        for row, lo, hi in zip(result["rows"][-h:], lower, upper):
            row.update(interval_lower=float(lo), interval_upper=float(hi))


async def compare(engine, run, lease, index, rows, spec):
    await engine.repo.guard(lease)
    key = f"forecast_comparison_{index}"
    existing = await engine.repo.read_checkpoint(run["id"], key)
    if existing is not None:
        if existing.get("unavailable"):
            raise AppError(existing["unavailable"], 422, "prediction_unavailable")
        return existing
    try:
        prepared = prepare_series(rows, spec.model_dump(mode="json"))
    except ValueError as exc:
        raise AppError(str(exc), 422, "prediction_unavailable") from exc
    local_key = f"forecast_local_{index}"
    local = await engine.repo.read_checkpoint(run["id"], local_key)
    if local is None:
        active = await engine.repo.guard(lease)
        fits = min(12, engine.settings.report_fit_limit - active["budgets"]["fits"])
        seconds = min(30, engine.settings.report_fit_seconds - active["budgets"]["fit_seconds"])
        if fits < 1 or seconds < 1:
            raise AppError("Statistical forecast budget reached.", 422, "prediction_unavailable")
        await engine.repo.reserve_once(
            lease,
            local_key + f"_reservation_{lease['generation']}",
            {"fits": fits, "fit_seconds": seconds},
            {},
        )
        local = await forecast(rows, spec, max_fits=fits, max_seconds=seconds, comparison=True)
        local = await engine.repo.checkpoint(lease, local_key, local)
    scores = copy.deepcopy(local.pop("evaluation", {}))
    if "seasonal_naive" not in scores:
        raise AppError("No validated comparison baseline is available.", 422, "prediction_unavailable")
    scenario_candidate = local.pop("scenario_candidate", None)
    admissions = await engine.repo.read_checkpoint(run["id"], "timesfm_admissions") or {}
    admission = admissions.get(
        str(index), {"admitted": False, "reason": "TimesFM was not reserved for this target."}
    )
    diagnostic = {
        "provider": "bigquery",
        "model": MODEL,
        "preview": True,
        "status": "skipped",
        "reason": admission.get("reason"),
        "jobs": [],
        "input_hash": digest(rows),
        "selection_policy_version": 1,
    }
    remote, final_batch = None, None
    if admission["admitted"]:
        try:
            backtest, final_batch = batches(prepared), batches(prepared, final=True)

            def manifest(batch):
                return {
                    **{k: v for k, v in batch.items() if k != "rows"},
                    "payload_hash": digest(batch["rows"]),
                }

            capture = {
                "input_hash": digest(rows),
                "specification": spec.model_dump(mode="json"),
                "backtest": manifest(backtest),
                "final": manifest(final_batch),
                "policy": run["brief"]["forecast_policy"],
            }
            capture_key = f"timesfm_capture_{index}"
            captured = await engine.repo.checkpoint(lease, capture_key, capture)
            if digest(captured) != digest(capture):
                raise AppError(
                    "Frozen forecasting evidence differs from the recovered operation.",
                    409,
                    "timesfm_identity",
                )
            await engine.stage(lease, "Comparing forecasting methods")
            provider = TimesFM(engine.connectors, engine.repo)
            remote = await provider.execute(run, lease, str(index), backtest)
            scores[METHOD] = score_remote(prepared, remote)
            diagnostic.update(
                status="evaluated",
                reason="Chronological comparison completed.",
                jobs=[{k: v for k, v in remote.items() if k != "series"}],
                context=backtest["context"],
                history_lengths=backtest["history_lengths"],
                input_ranges=backtest["input_ranges"],
                scope_note="Driver comparisons use the explicitly recorded complete context at each cutoff; all saved history remains in source evidence.",
                native_backtest_intervals=remote["series"],
            )
        except (AppError, ValueError) as exc:
            if isinstance(exc, AppError) and exc.code in FATAL | {"timesfm_reconcile"}:
                raise
            diagnostic.update(
                status="unavailable", reason=exc.message if isinstance(exc, AppError) else str(exc)
            )
    chosen = choose(scores)
    driver_methods = [
        name
        for name in ("driver_ridge", METHOD)
        if name in scores and spec.drivers and eligible(scores[name], scores["seasonal_naive"])
    ]
    scenario_method = (
        min(driver_methods, key=lambda name: (scores[name]["mae"], name == METHOD))
        if driver_methods and spec.scenario_drivers
        else None
    )
    final = None
    if METHOD in {chosen, scenario_method}:
        try:
            final = await TimesFM(engine.connectors, engine.repo).execute(run, lease, str(index), final_batch)
            for values in final["series"].values():
                if not _valid_domain([r["value"] for r in values], spec.domain):
                    raise ValueError(
                        "TimesFM final predictions violate the metric domain; values were not clipped."
                    )
            diagnostic["jobs"].append({k: v for k, v in final.items() if k != "series"})
            diagnostic["native_final_intervals"] = final["series"]
        except (AppError, ValueError) as exc:
            if isinstance(exc, AppError) and exc.code in FATAL | {"timesfm_reconcile"}:
                raise
            diagnostic.update(
                status="unavailable", reason=exc.message if isinstance(exc, AppError) else str(exc)
            )
            scores.pop(METHOD, None)
            chosen = choose(scores)
            scenario_method = "driver_ridge" if scenario_candidate else None
    scale = max(float(abs(prepared["y"]).mean()), 1e-9)
    if scores[chosen]["mae"] > 0.5 * scale:
        reason = "All selected forecasts have excessive held-out error; predictions were withheld."
        await engine.repo.checkpoint(lease, key, {"unavailable": reason, "timesfm": diagnostic})
        raise AppError(reason, 422, "prediction_unavailable")
    result = copy.deepcopy(local)
    result.update(
        kind="forecast",
        scenario_name=None,
        scenario_drivers=[],
        comparison=diagnostic,
        selection_reason=f"{chosen} had the lowest passing chronological MAE; ties favor statistical methods.",
        scores={name: {k: v for k, v in score.items() if k != "errors"} for name, score in scores.items()},
    )
    # Scenario evidence never silently replaces the winning ordinary forecast.
    for row in result["rows"]:
        row["scenario"] = None
    if chosen == METHOD:
        result["limitations"] = [
            item
            for item in result["limitations"]
            if not item.startswith("Candidate models did not pass the baseline improvement gate")
        ]
        result.update(method=METHOD, provider="bigquery", model=MODEL, preview=True, interval=None)
        predicted = [v["value"] for v in final["series"]["baseline"]]
        for row, value in zip(result["rows"][-result["horizon"] :], predicted):
            row["forecast"] = value
            row.pop("interval_lower", None)
            row.pop("interval_upper", None)
        intervals(result, scores[METHOD], predicted, spec.domain)
    additional = []
    if scenario_method and scores[scenario_method]["mae"] <= 0.5 * scale:
        if scenario_method == METHOD and final:
            baseline = [v["value"] for v in final["series"]["baseline"]]
            alternative = [v["value"] for v in final["series"]["scenario"]]
        elif scenario_candidate:
            baseline, alternative = scenario_candidate["baseline"], scenario_candidate["scenario"]
        else:
            baseline = alternative = None
        if baseline is not None:
            scenario = copy.deepcopy(result)
            scenario.update(
                kind="scenario",
                method=scenario_method,
                scenario_name=spec.scenario_name or "Alternative driver path",
                scenario_drivers=spec.scenario_drivers,
                interval=None,
                provider="bigquery" if scenario_method == METHOD else "statistical",
                model=MODEL if scenario_method == METHOD else None,
                selection_reason="Best validated driver-capable method; baseline and alternative share its history and configuration.",
            )
            for row in scenario["rows"]:
                row.pop("interval_lower", None)
                row.pop("interval_upper", None)
            for row, base, alt in zip(scenario["rows"][-scenario["horizon"] :], baseline, alternative):
                row.update(forecast=base, scenario=alt)
            additional.append(scenario)
    elif spec.scenario_drivers:
        result["limitations"].append(
            "No supported driver-capable candidate passed scenario validation; descriptive analysis and supported forecasts remain available."
        )
    if diagnostic["status"] in {"unavailable", "skipped"}:
        result["limitations"].append("TimesFM: " + (diagnostic.get("reason") or "Unavailable."))
    elif chosen != METHOD:
        diagnostic["reason"] = (
            "A statistical method had lower passing MAE or TimesFM did not pass baseline promotion."
        )
    if result["interval"]:
        result["limitations"] = [
            v for v in result["limitations"] if "Validated prediction intervals are unavailable" not in v
        ]
    result["additional_predictions"] = additional
    return await engine.repo.checkpoint(lease, key, result)
