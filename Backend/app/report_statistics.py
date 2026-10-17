"""Controlled deterministic statistics. No generated expressions, code, imports, or filesystem paths."""

import asyncio
import hashlib
import json
import math
import multiprocessing as mp
import os
import time
from decimal import Decimal, InvalidOperation

from app.errors import AppError
from app.report_models import ForecastSpec

HORIZONS = {"day": (28, 90), "week": (12, 26), "month": (3, 12)}


def factual_claims(artifact, rows):
    """Claims are computed on the full saved selection, never the chart preview."""
    from app.chart_presentation import date_value, metadata, next_date

    spec = metadata(artifact["visualization"], artifact["columns"], rows)
    measures = spec["measures"]
    claims = [
        {
            "id": "c_" + hashlib.sha256((artifact["id"] + "row_count").encode()).hexdigest()[:16],
            "artifact_id": artifact["id"],
            "label": "Number of saved result rows",
            "value": str(len(rows)),
            "formatted": f"{len(rows):,}",
            "calculation": "count(saved rows); not the source population",
            "unit": "count",
        }
    ]
    for measure in measures:
        field = measure["field"]
        values = []
        for row in rows:
            try:
                value = Decimal(str(row[field]))
                if value.is_finite():
                    values.append(value)
            except (KeyError, InvalidOperation, TypeError):
                pass
        if not values:
            continue
        operations = {"minimum": min(values), "maximum": max(values)}
        x = spec.get("x")
        pairs = []
        for row in rows:
            try:
                value = Decimal(str(row.get(field)))
                if value.is_finite():
                    pairs.append((row, value))
            except (InvalidOperation, TypeError):
                pass
        if x and pairs:
            leaders = sorted(
                {str(row.get(x, "Missing"))[:120] for row, value in pairs if value == max(values)}
            )
            claims.append(
                {
                    "id": "c_"
                    + hashlib.sha256((artifact["id"] + field + "peak_label").encode()).hexdigest()[:16],
                    "artifact_id": artifact["id"],
                    "label": f"{field}: dimension labels sharing the highest saved value",
                    "value": json.dumps(leaders),
                    "formatted": ", ".join(leaders[:3])
                    + (" (additional ties)" if len(leaders) > 3 else " (tied)" if len(leaders) > 1 else ""),
                    "calculation": f"labels at max({field}); no statistical-anomaly or causal claim",
                    "unit": "label",
                }
            )
        if (
            artifact["complete"]
            and not artifact.get("prediction")
            and spec.get("dimension_kind") == "temporal"
            and spec.get("granularity")
        ):
            ordered = sorted(
                [(row, value) for row, value in pairs if date_value(row.get(x))],
                key=lambda pair: date_value(pair[0][x]),
            )
            partials = set(spec.get("partial_periods", []))
            if len(ordered) >= 2:
                previous, current = ordered[-2:]
                if (
                    str(previous[0][x]) not in partials
                    and str(current[0][x]) not in partials
                    and next_date(date_value(previous[0][x]), spec["granularity"])
                    == date_value(current[0][x])
                ):
                    operations["latest"] = current[1]
                    operations["previous adjacent period"] = previous[1]
                    operations["latest minus previous adjacent period"] = current[1] - previous[1]
                    if previous[1] != 0:
                        delta = (current[1] - previous[1]) / abs(previous[1]) * 100
                        claims.append(
                            {
                                "id": "c_"
                                + hashlib.sha256(
                                    (artifact["id"] + field + "period_percent").encode()
                                ).hexdigest()[:16],
                                "artifact_id": artifact["id"],
                                "label": f"{field}: change from {previous[0][x]} to {current[0][x]}",
                                "value": str(delta),
                                "formatted": f"{delta:,.2f}%",
                                "calculation": "(latest - adjacent previous) / abs(previous) × 100; zero baseline withheld",
                                "unit": "percent",
                            }
                        )

        if artifact["complete"] and measure.get("additive") and len(values) == len(rows):
            operations["total"] = sum(values)
        # Grouped ratios/averages need their original denominators. A mean of
        # monthly AOVs or rates cannot stand in for the overall weighted metric.
        if len(values) == len(rows) and (
            measure.get("additive") or measure.get("unit") == "count" or len(rows) == 1
        ):
            operations["average"] = sum(values) / len(values)
        for operation, value in operations.items():
            if measure.get("unit") == "currency":
                formatted = f"{measure.get('currency', 'USD')} {value:,.2f}"
            elif measure.get("unit") == "percent":
                scaled = value * (100 if measure.get("percent_scale") == "fraction" else 1)
                formatted = (
                    f"{scaled:,.2f} percentage points"
                    if operation == "latest minus previous adjacent period"
                    else f"{scaled:,.2f}%"
                )
            else:
                formatted = f"{value:,.2f}".rstrip("0").rstrip(".")
            claims.append(
                {
                    "id": f"c_{hashlib.sha256((artifact['id'] + field + operation).encode()).hexdigest()[:16]}",
                    "artifact_id": artifact["id"],
                    "label": f"{measure.get('label') or field}: {operation} over saved rows",
                    "value": str(value),
                    "formatted": formatted,
                    "calculation": f"{operation}({field}); {len(values)} non-null saved observations",
                    "unit": measure.get("unit", "number"),
                }
            )
    return claims


def _valid_domain(values, domain):
    if not all(math.isfinite(float(v)) for v in values):
        return False
    if domain == "nonnegative":
        return all(v >= 0 for v in values)
    if domain == "fraction":
        return all(0 <= v <= 1 for v in values)
    if domain == "percentage":
        return all(0 <= v <= 100 for v in values)
    return True


def prepare_series(rows, spec_dict):
    """Shared eligibility checks; no target imputation, clipping, or future leakage."""
    import numpy as np
    import pandas as pd

    spec = ForecastSpec.model_validate(spec_dict)
    horizon = spec.horizon or HORIZONS[spec.grain][0]
    if horizon > HORIZONS[spec.grain][1]:
        raise ValueError("Requested forecast horizon exceeds the supported grain limit.")
    frame = pd.DataFrame(rows)
    needed = [spec.date_column, spec.target, *spec.drivers]
    if any(c not in frame for c in needed):
        raise ValueError("Prediction fields must exist in the saved result.")
    if len(set(needed)) != len(needed):
        raise ValueError("The target, date, and driver fields must be distinct.")
    if frame[spec.date_column].duplicated().any():
        raise ValueError("Forecast requires one observation per date. Select a single series first.")
    frame[spec.date_column] = pd.to_datetime(frame[spec.date_column], errors="coerce")
    if frame[spec.date_column].isna().any():
        raise ValueError("Forecast dates contain missing or invalid values.")
    frame = frame.sort_values(spec.date_column)
    dates = pd.DatetimeIndex(frame[spec.date_column])
    freq = "D" if spec.grain == "day" else "7D" if spec.grain == "week" else "MS"
    if spec.grain == "month" and any(d.day != 1 for d in dates):
        raise ValueError("Monthly forecasts require calendar-month start dates.")
    expected = pd.date_range(dates[0], dates[-1], freq=freq)
    if not dates.equals(expected):
        raise ValueError(
            "Saved history has missing or irregular dates. Missing values are not treated as zero."
        )
    y = pd.to_numeric(frame[spec.target], errors="coerce").to_numpy(dtype=float)
    if not _valid_domain(y, spec.domain):
        raise ValueError("Training values violate the metric domain or contain missing values.")
    n = len(y)
    season = spec.season or {"day": 7, "week": 52, "month": 12}[spec.grain]
    min_train = max(12, 2 * season, horizon)
    if n - 3 * horizon < min_train:
        raise ValueError(
            "Insufficient complete history for three full-horizon backtests and two seasonal cycles. Use a shorter horizon or finer grain."
        )
    x = None
    if spec.drivers:
        x = frame[spec.drivers].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=float)
        if not np.isfinite(x).all():
            raise ValueError("Drivers contain missing or invalid values.")
        if any(np.std(x[:, i]) < 1e-8 for i in range(x.shape[1])):
            raise ValueError("Historical drivers do not vary enough to learn a scenario.")
        if any(abs(np.corrcoef(x[:, i], y)[0, 1]) > 0.9999 for i in range(x.shape[1])):
            raise ValueError("A driver is effectively identical to the target; possible target leakage.")
        if any(
            any(word in name.lower() for word in ("future", "target", "lead", "forecast"))
            for name in spec.drivers
        ):
            raise ValueError("Future/target-derived features are not approved historical drivers.")

    return {
        "spec": spec,
        "frame": frame,
        "dates": dates,
        "y": y,
        "x": x,
        "horizon": horizon,
        "season": season,
        "n": n,
    }


def driver_paths(prepared):
    import numpy as np

    spec, x, horizon = prepared["spec"], prepared["x"], prepared["horizon"]
    if x is None:
        return None, None
    if not spec.future_drivers:
        raise ValueError("Future driver paths must be supplied explicitly before forecasting.")

    def path(values):
        if len(values) != horizon or any(set(v) != set(spec.drivers) for v in values):
            raise ValueError("Supply each approved driver for every future period.")
        values = np.array([[v[d] for d in spec.drivers] for v in values], dtype=float)
        if not np.isfinite(values).all() or np.any(values < x.min(axis=0)) or np.any(values > x.max(axis=0)):
            raise ValueError("Future drivers fall outside observed historical support.")
        scale = np.std(x, axis=0)
        nearest = np.min(np.mean(((values[:, None, :] - x[None, :, :]) / scale) ** 2, axis=2), axis=1)
        if np.any(nearest > 4):
            raise ValueError("Future driver combinations have insufficient joint historical support.")
        return values

    return path(spec.future_drivers), path(spec.scenario_drivers) if spec.scenario_drivers else None


def _forecast(rows, spec_dict, max_fits, max_seconds, baseline_only=False, comparison=False):
    import warnings

    import numpy as np
    import pandas as pd
    from sklearn.linear_model import Ridge
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from statsmodels.tsa.holtwinters import ExponentialSmoothing
    from statsmodels.tsa.statespace.sarimax import SARIMAX

    prepared = prepare_series(rows, spec_dict)
    spec, frame, dates, y, x, horizon, season, n = (
        prepared[k] for k in ("spec", "frame", "dates", "y", "x", "horizon", "season", "n")
    )
    started, fits = time.monotonic(), 0
    freq = "D" if spec.grain == "day" else "7D" if spec.grain == "week" else "MS"

    def fit_guard():
        nonlocal fits
        if fits >= max_fits or time.monotonic() - started >= max_seconds:
            raise ValueError("Prediction fitting budget reached.")
        fits += 1

    def baseline(train, h):
        return np.resize(train[-season:], h)

    def features(train_y, train_x, start, end, future_y=None):
        # During recursive evaluation future_y contains only predictions, never held-out targets.
        values = list(train_y) if future_y is None else future_y
        result = []
        for i in range(start, end):
            result.append(
                [
                    values[i - 1],
                    values[i - season],
                    math.sin(2 * math.pi * i / season),
                    math.cos(2 * math.pi * i / season),
                    *train_x[i],
                ]
            )
        return np.array(result)

    def predict(method, train, h, train_x=None, future_x=None):
        if method == "seasonal_naive":
            return baseline(train, h)
        fit_guard()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            if method == "ets":
                return np.asarray(
                    ExponentialSmoothing(
                        train,
                        trend="add",
                        damped_trend=True,
                        seasonal="add",
                        seasonal_periods=season,
                        initialization_method="estimated",
                    )
                    .fit(optimized=True)
                    .forecast(h)
                )
            if method == "sarimax":
                model = SARIMAX(
                    train, order=(1, 1, 0), seasonal_order=(1, 0, 0, season), enforce_stationarity=False
                ).fit(disp=False, maxiter=30)
                return np.asarray(model.get_forecast(steps=h).predicted_mean)
            if method == "driver_ridge":
                lag = max(1, season)
                training_features = features(train, train_x, lag, len(train))
                model = make_pipeline(StandardScaler(), Ridge(alpha=10.0))
                model.fit(training_features, train[lag:])
                path = list(train)
                all_x = np.vstack([train_x, future_x])
                for i in range(len(train), len(train) + h):
                    vector = features(train, all_x, i, i + 1, path)
                    path.append(float(model.predict(vector)[0]))
                return np.array(path[-h:])
        raise ValueError("Unsupported prediction method.")

    origins = [n - 3 * horizon, n - 2 * horizon, n - horizon]
    methods = (
        ["seasonal_naive"]
        if baseline_only
        else ["seasonal_naive", "ets"]
        + (["driver_ridge"] if x is not None else ["sarimax"] if season <= 52 else [])
    )
    scores, failures, fold_predictions = {}, [], {}
    for method in methods:
        errors, folds, predictions = [], [], []
        try:
            for origin in origins:
                predicted = predict(
                    method,
                    y[:origin],
                    horizon,
                    x[:origin] if x is not None else None,
                    x[origin : origin + horizon] if x is not None else None,
                )
                if not _valid_domain(predicted, spec.domain):
                    raise ValueError("Predictions violate the metric domain; values were not clipped.")
                residuals = y[origin : origin + horizon] - predicted
                errors.extend(residuals.tolist())
                predictions.extend(predicted.tolist())
                folds.append(
                    {
                        "train_end": dates[origin - 1].isoformat(),
                        "test_start": dates[origin].isoformat(),
                        "test_end": dates[origin + horizon - 1].isoformat(),
                        "mae": float(np.mean(np.abs(residuals))),
                    }
                )
            scores[method] = {
                "mae": float(np.mean(np.abs(errors))),
                "rmse": float(np.sqrt(np.mean(np.square(errors)))),
                "folds": folds,
                "errors": errors,
            }
            fold_predictions[method] = predictions
        except Exception as exc:
            failures.append(f"{method}: {str(exc)[:200]}")
    if "seasonal_naive" not in scores:
        raise ValueError("Even the baseline violates the metric domain.")
    chosen, base = "seasonal_naive", scores["seasonal_naive"]
    for method, score in scores.items():
        wins = sum(a["mae"] < b["mae"] for a, b in zip(score["folds"], base["folds"]))
        if (
            method != "seasonal_naive"
            and base["mae"] > 0
            and score["mae"] <= base["mae"] * 0.95
            and wins >= 2
            and score["mae"] < scores[chosen]["mae"]
        ):
            chosen = method
    limitations = [
        "Historical predictive associations are not causal effects or guaranteed future performance."
    ]
    if chosen == "seasonal_naive":
        limitations.append(
            "Candidate models did not pass the baseline improvement gate; seasonal-naive forecast retained."
        )
    if not comparison and scores[chosen]["mae"] > 0.5 * max(float(np.mean(np.abs(y))), 1e-9):
        raise ValueError(
            "The selected forecast has excessive held-out error relative to the metric scale; predictions were withheld."
        )
    future_x, scenario_x = driver_paths(prepared)
    predicted = predict(chosen, y, horizon, x, future_x)
    if not _valid_domain(predicted, spec.domain):
        raise ValueError("Final predictions violate the metric domain.")
    future_dates = pd.date_range(dates[-1], periods=horizon + 1, freq=freq)[1:]
    output = [
        {"date": d.date().isoformat(), "observed": float(v), "forecast": None, "scenario": None}
        for d, v in zip(dates, y)
    ]
    scenario = None
    if scenario_x is not None:
        if (
            "driver_ridge" not in scores
            or scores["driver_ridge"]["mae"] > base["mae"] * 0.95
            or sum(a["mae"] < b["mae"] for a, b in zip(scores["driver_ridge"]["folds"], base["folds"])) < 2
        ):
            limitations.append(
                "The learned driver model did not pass validation; scenario estimates were withheld."
            )
        else:
            # Scenario comparisons use the SAME fitted model and baseline driver path.
            scenario_baseline = predict("driver_ridge", y, horizon, x, future_x)
            scenario = predict("driver_ridge", y, horizon, x, scenario_x)
            if not _valid_domain(scenario, spec.domain) or not _valid_domain(scenario_baseline, spec.domain):
                scenario = None
                limitations.append("Scenario predictions violated the metric domain and were withheld.")
            else:
                if not comparison:
                    predicted = scenario_baseline
                    chosen = "driver_ridge"
    separate_scenario = None
    if comparison and scenario is not None:
        separate_scenario = {
            "method": "driver_ridge",
            "baseline": scenario_baseline.tolist(),
            "scenario": scenario.tolist(),
        }
        scenario = None
    for i, d in enumerate(future_dates):
        output.append(
            {
                "date": d.date().isoformat(),
                "observed": None,
                "forecast": float(predicted[i]),
                "scenario": float(scenario[i]) if scenario is not None else None,
            }
        )
    # Use an earlier fold to size residual intervals and later folds to check coverage.
    # No future observations enter calibration; uncertain/unsupported bands are omitted.
    interval = None
    residuals = np.array(scores[chosen]["errors"])
    calibration, validation = residuals[:horizon], residuals[horizon:]
    if len(calibration) >= 20 and len(validation) >= 40:
        width = float(np.quantile(np.abs(calibration), 0.95, method="higher"))
        coverage = float(np.mean(np.abs(validation) <= width))
        lower, upper = predicted - width, predicted + width
        if (
            coverage >= 0.85
            and width > 0
            and _valid_domain(lower, spec.domain)
            and _valid_domain(upper, spec.domain)
        ):
            interval = {
                "level": 0.95,
                "coverage": coverage,
                "method": "earlier-fold absolute residual quantile; later-fold coverage",
                "calibration_observations": len(calibration),
                "validation_observations": len(validation),
            }
            for i, row in enumerate(output[-horizon:]):
                row["interval_lower"], row["interval_upper"] = float(lower[i]), float(upper[i])
            limitations.append(
                "Prediction bands pool historical horizon residuals; their backtest coverage is not a guarantee of future coverage and excludes uncertainty in supplied future driver assumptions."
            )
    if interval is None:
        limitations.append(
            "Validated prediction intervals are unavailable for this bounded backtest; point predictions carry unquantified uncertainty."
        )
    return {
        "rows": output,
        **({"evaluation": scores, "scenario_candidate": separate_scenario} if comparison else {}),
        "method": chosen,
        "horizon": horizon,
        "grain": spec.grain,
        "season": season,
        "interval": interval,
        "specification": spec.model_dump(mode="json"),
        "libraries": {
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "statsmodels": __import__("statsmodels").__version__,
            "scikit-learn": __import__("sklearn").__version__,
        },
        "last_observed_period": dates[-1].date().isoformat(),
        "cutoff": (
            dates[-1]
            + (
                pd.offsets.MonthEnd(0)
                if spec.grain == "month"
                else pd.Timedelta(days=6)
                if spec.grain == "week"
                else pd.Timedelta(0)
            )
        )
        .date()
        .isoformat(),
        "target": spec.target,
        "drivers": spec.drivers,
        "scenario_name": spec.scenario_name if scenario is not None else None,
        "future_drivers": spec.future_drivers,
        "scenario_drivers": spec.scenario_drivers,
        "assumptions": spec.assumptions,
        "scores": {k: {f: v for f, v in s.items() if f != "errors"} for k, s in scores.items()},
        "limitations": limitations + failures,
        "fits": fits,
        "fit_seconds": time.monotonic() - started,
        "seed": 42,
        "data_hash": hashlib.sha256(json.dumps(rows, sort_keys=True).encode()).hexdigest(),
    }


def _entry(pipe, rows, spec, fits, seconds, comparison=False):
    os.environ["OMP_NUM_THREADS"] = "1"
    os.environ["OPENBLAS_NUM_THREADS"] = "1"
    try:
        # Publish a validated baseline before fitting candidates, so an expensive candidate
        # cannot discard supported baseline evidence when the child process hits its deadline.
        try:
            baseline = _forecast(rows, spec, fits, seconds, baseline_only=True, comparison=comparison)
            pipe.send({"baseline": baseline})
        except ValueError:
            pass  # A poor baseline must not prevent a better candidate from being validated.
        pipe.send({"result": _forecast(rows, spec, fits, seconds, comparison=comparison)})
    except Exception as exc:
        pipe.send({"error": str(exc)[:600]})
    finally:
        pipe.close()


async def forecast(rows, spec, *, max_fits=12, max_seconds=30, comparison=False):
    context = mp.get_context("spawn")
    parent, child = context.Pipe(duplex=False)
    process = context.Process(
        target=_entry,
        args=(child, rows, spec.model_dump(mode="json"), max_fits, max_seconds, comparison),
        daemon=True,
    )
    process.start()
    child.close()
    started = time.monotonic()
    baseline = None

    def supported_fallback(reason):
        if baseline is None:
            raise AppError(reason, 422, "prediction_unavailable")
        baseline["limitations"].append(reason + " A validated seasonal-naive baseline was retained.")
        baseline["fits"], baseline["fit_seconds"] = max_fits, max_seconds
        return baseline

    try:
        while True:
            if parent.poll():
                try:
                    message = parent.recv()
                except EOFError:
                    return supported_fallback(
                        "Prediction worker stopped before candidate results were saved."
                    )
                if "baseline" in message:
                    baseline = message["baseline"]
                elif "result" in message:
                    return message["result"]
                else:
                    return supported_fallback(message["error"])
            elif not process.is_alive():
                return supported_fallback("Prediction worker stopped unexpectedly.")
            if time.monotonic() - started > max_seconds:
                return supported_fallback("Prediction fitting deadline reached.")
            await asyncio.sleep(0.05)
    finally:
        if process.is_alive():
            process.terminate()
        await asyncio.to_thread(process.join, 2)
        if process.is_alive():
            process.kill()
            await asyncio.to_thread(process.join, 2)
        parent.close()
