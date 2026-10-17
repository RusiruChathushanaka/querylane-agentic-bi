"""Fixed managed TimesFM queries over immutable saved rows, never model SQL."""

import asyncio
import contextlib
import hashlib
import json
import math
import threading
import time
from datetime import datetime

from app.errors import AppError

MODEL = "TimesFM 3.0"
METHOD = "timesfm_3"
FATAL = {"cancelled", "report_stale_lease", "report_budget", "maintenance"}


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def policy(settings):
    return {
        "version": 1,
        "enabled": settings.report_timesfm_enabled and settings.report_timesfm_verified,
        "verified": settings.report_timesfm_verified,
        "model": MODEL,
        "preview": True,
        "targets": settings.report_timesfm_targets,
        "jobs": settings.report_timesfm_jobs,
        "job_seconds": settings.report_timesfm_job_seconds,
        "seconds": settings.report_timesfm_seconds,
        "input_tokens": settings.report_timesfm_input_tokens,
        "output_tokens": settings.report_timesfm_output_tokens,
        "pricing_reviewed": "2026-10-17",
        "pricing_note": "Bound bytes and model tokens separately; pricing changes from 2026-12-01.",
    }


def contexts(prepared):
    """No implicit truncation; all three folds share an explicit context policy."""
    n, h = prepared["n"], prepared["horizon"]
    if n > 2048:
        raise ValueError(
            "TimesFM comparison requires at most 2,048 saved observations; narrow the period explicitly."
        )
    if prepared["x"] is not None:
        # Explicitly use one common, complete context for all folds and final inference.
        # Any shorter scope is reported in provenance, never hidden as full-history inference.
        length = min(2048, ((n - 3 * h) // 32) * 32)
        if length < 64:
            raise ValueError(
                "TimesFM covariate forecasts need at least 64 complete training observations at the earliest fold. Statistical scenarios remain available; no history was padded."
            )
        return [length] * 4
    return [max(64, math.ceil(length / 32) * 32) for length in [n - 3 * h, n - 2 * h, n - h, n]]


def batches(prepared, *, final=False):
    import pandas as pd

    from app.report_statistics import driver_paths

    spec, dates, y, x, h, n = (prepared[k] for k in ("spec", "dates", "y", "x", "horizon", "n"))
    windows = contexts(prepared)
    future, alternative = driver_paths(prepared)
    origins = [n] if final else [n - 3 * h, n - 2 * h, n - h]
    groups = (
        [("baseline", n, future)]
        if final
        else [
            (f"fold_{i}", origin, x[origin : origin + h] if x is not None else None)
            for i, origin in enumerate(origins)
        ]
    )
    if final and alternative is not None:
        groups.append(("scenario", n, alternative))
    rows, expected, input_ranges = [], {}, {}
    for name, origin, future_x in groups:
        context = windows[-1] if final else windows[int(name.split("_")[-1])]
        start = max(0, origin - context)
        input_ranges[name] = {
            "start": dates[start].date().isoformat(),
            "end": dates[origin - 1].date().isoformat(),
            "observations": origin - start,
        }
        for i in range(start, origin):
            row = {"series": name, "stamp": dates[i].date().isoformat(), "value": float(y[i])}
            row.update({f"driver_{j}": float(x[i, j]) for j in range(len(spec.drivers))})
            rows.append(row)
        freq = "D" if spec.grain == "day" else "7D" if spec.grain == "week" else "MS"
        stamps = pd.date_range(dates[origin - 1], periods=h + 1, freq=freq)[1:]
        expected[name] = [v.date().isoformat() for v in stamps]
        if x is not None:
            for i, stamp in enumerate(stamps):
                row = {"series": name, "stamp": stamp.date().isoformat(), "value": None}
                row.update({f"driver_{j}": float(future_x[i, j]) for j in range(len(spec.drivers))})
                rows.append(row)
    context = windows[-1] if final else max(windows[:3])
    return {
        "rows": rows,
        "expected": expected,
        "context": context,
        "horizon": h,
        "drivers": len(spec.drivers),
        "history_lengths": origins,
        "input_ranges": input_ranges,
        "input_tokens": len(groups) * (context + (context + h) * len(spec.drivers)),
        "output_tokens": len(groups) * h,
        "phase": "final" if final else "backtest",
    }


def query(batch):
    """Only application-owned aliases/expressions; values enter one JSON parameter."""
    drivers = batch["drivers"]
    if drivers not in range(5) or not 1 <= batch["horizon"] <= 90 or not 64 <= batch["context"] <= 2048:
        raise ValueError("Invalid bounded TimesFM query configuration.")
    fields = [
        "JSON_VALUE(r, '$.series') AS series",
        "DATE(JSON_VALUE(r, '$.stamp')) AS stamp",
        "CAST(JSON_VALUE(r, '$.value') AS FLOAT64) AS value",
    ]
    fields += [f"CAST(JSON_VALUE(r, '$.driver_{i}') AS FLOAT64) AS driver_{i}" for i in range(drivers)]
    source = "SELECT " + ", ".join(fields) + " FROM UNNEST(JSON_QUERY_ARRAY(PARSE_JSON(@payload))) AS r"
    options = f"model => 'TimesFM 3.0', timestamp_col => 'stamp', id_cols => ['series'], horizon => {batch['horizon']}, context_window => {batch['context']}, confidence_level => 0.95, output_historical_time_series => TRUE"
    if drivers:
        names = ",".join(f"'driver_{i}'" for i in range(drivers))
        options += f", target_cols => ['value'], future_covariate_cols => [{names}]"
        selection = "series, stamp, value.value AS predicted, value.prediction_interval_lower_bound AS lower_bound, value.prediction_interval_upper_bound AS upper_bound, ai_forecast_status"
    else:
        options += ", data_col => 'value'"
        selection = "series, time_series_timestamp AS stamp, time_series_data AS predicted, prediction_interval_lower_bound AS lower_bound, prediction_interval_upper_bound AS upper_bound, ai_forecast_status"
    return f"SELECT {selection} FROM AI.FORECAST(({source}), {options}) WHERE time_series_type = 'forecast' ORDER BY series, stamp"


def parse_output(rows, batch):
    result = {name: [] for name in batch["expected"]}
    for row in rows:
        if row.get("ai_forecast_status"):
            raise AppError("TimesFM returned an unsuccessful series status.", 422, "timesfm_unavailable")
        name = row.get("series")
        if name not in result:
            raise AppError("TimesFM returned an unexpected series.", 422, "timesfm_invalid")
        stamp = row["stamp"]
        if isinstance(stamp, datetime):
            stamp = stamp.date()
        stamp = str(stamp)
        value = row.get("predicted")
        if value is None or not math.isfinite(float(value)):
            raise AppError("TimesFM returned a missing or nonfinite prediction.", 422, "timesfm_invalid")
        result[name].append(
            {
                "date": stamp,
                "value": float(value),
                "lower": float(row["lower_bound"])
                if row.get("lower_bound") is not None and math.isfinite(float(row["lower_bound"]))
                else None,
                "upper": float(row["upper_bound"])
                if row.get("upper_bound") is not None and math.isfinite(float(row["upper_bound"]))
                else None,
            }
        )
    for name, values in result.items():
        if [v["date"] for v in values] != batch["expected"][name]:
            raise AppError(
                "TimesFM output dates or row count do not match the requested horizon.",
                422,
                "timesfm_invalid",
            )
    return result


class TimesFM:
    def __init__(self, connectors, repository):
        self.connectors, self.repo = connectors, repository

    async def execute(self, run, lease, operation, batch):
        from google.cloud import bigquery

        await self.repo.guard(lease)
        admission = await self.repo.read_checkpoint(run["id"], f"timesfm_admission_{operation}")
        if not admission:
            raise AppError("TimesFM work was not admitted within the report budgets.", 422, "timesfm_budget")
        for field in ("input_tokens", "output_tokens"):
            if batch[field] > admission["reservation"]["timesfm_" + field]:
                raise AppError("TimesFM input exceeds its frozen reservation.", 422, "timesfm_budget")
        name = f"timesfm_job_{operation}_{batch['phase']}"
        sql, payload = query(batch), json.dumps(batch["rows"], sort_keys=True, allow_nan=False)
        identity = digest(
            {
                "sql": sql,
                "payload": payload,
                "model": MODEL,
                "location": self.connectors.settings.bigquery_location,
            }
        )
        saved = await self.repo.read_checkpoint(run["id"], name + "_result")
        if saved:
            if saved.get("identity") != identity:
                raise AppError("Saved TimesFM output belongs to different inputs.", 409, "timesfm_identity")
            if saved.get("error"):
                raise AppError(saved["error"], 422, "timesfm_unavailable")
            return saved
        job_id = f"abi_report_{run['id']}_tf_{identity[:24]}"
        active = await self.repo.guard(lease)
        prior = await self.repo.read_checkpoint(run["id"], name)
        seconds = (
            prior["seconds"]
            if prior
            else min(
                run["brief"]["forecast_policy"]["job_seconds"],
                run["brief"]["forecast_policy"]["seconds"] - active["budgets"].get("timesfm_seconds", 0),
            )
        )
        if seconds <= 0:
            raise AppError("TimesFM execution budget reached.", 422, "timesfm_budget")
        reservation = await self.repo.reserve_once(
            lease,
            name,
            {"timesfm_seconds": seconds},
            {"job_id": job_id, "identity": identity, "deadline": time.time() + seconds, "seconds": seconds},
        )
        if reservation["identity"] != identity:
            raise AppError("TimesFM recovered operation has different inputs.", 409, "timesfm_identity")
        seconds = reservation["seconds"]

        # A completed job may be recovered after its original inference deadline.
        # Allow a bounded read-only lookup; never restart expired inference.
        read_deadline = reservation["deadline"]
        if prior and read_deadline <= time.time():
            read_deadline = time.time() + 5

        def remaining():
            return max(0.01, read_deadline - time.time())

        cancel_flag = self.connectors.cancel_flags.setdefault(run["id"], threading.Event())
        operation_cancelled = threading.Event()

        def cancelled():
            return cancel_flag.is_set() or operation_cancelled.is_set()

        client, job = self.connectors.bq, None
        if client is None:
            raise AppError("Managed TimesFM requires the cloud BigQuery client.", 422, "timesfm_unavailable")
        config = bigquery.QueryJobConfig(
            query_parameters=[bigquery.ScalarQueryParameter("payload", "STRING", payload)],
            maximum_bytes_billed=self.connectors.settings.bigquery_max_bytes,
            job_timeout_ms=int(seconds * 1000),
            use_query_cache=False,
            labels={"application": "agentic-bi-demo", "purpose": "report-timesfm"},
        )

        def lookup_or_submit():
            from google.api_core.exceptions import Conflict, NotFound

            if cancelled():
                raise AppError("Cancellation requested.", 409, "cancelled")
            try:
                found = client.get_job(job_id, retry=None, timeout=min(10, remaining()))
            except NotFound:
                if time.time() >= reservation["deadline"]:
                    raise AppError("TimesFM inference deadline expired.", 422, "timesfm_timeout")
                dry_config = bigquery.QueryJobConfig(
                    dry_run=True, use_query_cache=False, query_parameters=config.query_parameters
                )
                estimate = client.query(sql, job_config=dry_config, retry=None, timeout=min(10, remaining()))
                if (estimate.total_bytes_processed or 0) > self.connectors.settings.bigquery_max_bytes:
                    raise AppError("TimesFM dry-run exceeds the query byte budget.", 422, "timesfm_budget")
                if cancelled():
                    raise AppError("Cancellation requested.", 409, "cancelled")
                try:
                    found = client.query(
                        sql,
                        job_id=job_id,
                        job_config=config,
                        retry=None,
                        job_retry=None,
                        timeout=min(10, remaining()),
                    )
                except Conflict:
                    found = client.get_job(job_id, retry=None, timeout=min(10, remaining()))
                except Exception as submission_error:
                    # Lost response: reconcile SAME identity; an unresolved transient result
                    # remains recoverable rather than being cached as a terminal failure.
                    try:
                        found = client.get_job(job_id, retry=None, timeout=min(10, remaining()))
                    except NotFound:
                        from google.api_core.exceptions import BadRequest, Forbidden, Unauthorized

                        if isinstance(submission_error, (BadRequest, Forbidden, Unauthorized)):
                            raise submission_error
                        raise AppError(
                            "TimesFM submission status is unresolved; recovery will reconcile the same job.",
                            503,
                            "timesfm_reconcile",
                        ) from submission_error
            actual = found.to_api_repr().get("configuration", {}).get("query", {})
            if (
                found.query != sql
                or actual.get("queryParameters") != config.to_api_repr()["query"]["queryParameters"]
            ):
                raise AppError(
                    "TimesFM job input identity does not match saved evidence.", 409, "timesfm_identity"
                )
            self.connectors.jobs.setdefault(run["id"], []).append(found)
            if cancelled():
                found.cancel()
                raise AppError("Cancellation requested.", 409, "cancelled")
            return found

        try:
            await self.repo.guard(lease)
            job = await asyncio.wait_for(asyncio.to_thread(lookup_or_submit), min(20, remaining()))
            while job.state != "DONE":
                await self.repo.guard(lease)
                if time.time() >= reservation["deadline"]:
                    raise TimeoutError
                await asyncio.sleep(min(0.5, remaining()))
                await asyncio.wait_for(
                    asyncio.to_thread(job.reload, retry=None, timeout=min(5, remaining())), remaining()
                )
            await self.repo.guard(lease)
            if job.error_result:
                raise AppError(
                    "Managed TimesFM inference failed; a statistical method may remain available.",
                    422,
                    "timesfm_unavailable",
                )
            iterator = await asyncio.wait_for(
                asyncio.to_thread(job.result, retry=None, timeout=remaining()), remaining()
            )

            def collect():
                values = []
                for row in iterator:
                    values.append(dict(row))
                    if len(values) > 3 * batch["horizon"]:
                        raise AppError("TimesFM returned too many observations.", 422, "timesfm_invalid")
                return values

            rows = await asyncio.wait_for(asyncio.to_thread(collect), remaining())
            output = parse_output(rows, batch)
            result = {
                "series": output,
                "job_id": job_id,
                "identity": identity,
                "model": MODEL,
                "context": batch["context"],
                "input_tokens_estimated": batch["input_tokens"],
                "output_tokens_estimated": batch["output_tokens"],
                "bytes_processed": int(job.total_bytes_processed or 0),
                "executed_at": datetime.now().astimezone().isoformat(),
            }
            result = await self.repo.checkpoint(lease, name + "_result", result)
            await self.repo.settle_forecast_seconds(
                lease, name, seconds, max(0, seconds - max(0, reservation["deadline"] - time.time()))
            )
            return result
        except BaseException as exc:
            operation_cancelled.set()
            if job is not None and job.state != "DONE":
                with contextlib.suppress(Exception):
                    await asyncio.to_thread(job.cancel, retry=None, timeout=5)
            if isinstance(exc, (asyncio.CancelledError, KeyboardInterrupt, SystemExit)):
                cancel_flag.set()
                raise
            if isinstance(exc, AppError) and exc.code in FATAL:
                cancel_flag.set()
                raise
            if isinstance(exc, AppError) and exc.code == "timesfm_reconcile":
                raise
            message = (
                exc.message
                if isinstance(exc, AppError)
                else "TimesFM inference was unavailable or timed out; saved statistical evidence was retained."
            )
            await self.repo.checkpoint(
                lease, name + "_result", {"error": message, "job_id": job_id, "identity": identity}
            )
            raise AppError(message, 422, "timesfm_unavailable") from exc
