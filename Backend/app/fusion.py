"""A typed plan compiler; no model-supplied SQL or Python reaches DuckDB."""

import asyncio
import multiprocessing as mp
import queue
import re
from typing import Any

import pyarrow as pa

from app.errors import AppError
from app.models import FusionPlan, QueryResult


def _identifier(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", value):
        raise ValueError("Invalid fusion identifier")
    return '"' + value + '"'


def _worker(channel, left_bytes: bytes, right_bytes: bytes, plan_dict: dict, max_rows: int):
    try:
        import duckdb

        plan = FusionPlan.model_validate(plan_dict)
        left = pa.ipc.open_stream(left_bytes).read_all()
        right = pa.ipc.open_stream(right_bytes).read_all()
        if left.nbytes + right.nbytes > 16_777_216:
            raise ValueError("Fusion input exceeds 16 MiB.")
        names = {"left": left.column_names, "right": right.column_names}
        for projection in plan.projections:
            if projection.column not in names[projection.side]:
                raise ValueError("Projection references an unavailable column.")
        if len({p.alias for p in plan.projections}) != len(plan.projections):
            raise ValueError("Fusion aliases must be unique.")
        for key in plan.keys:
            if key.left not in names["left"] or key.right not in names["right"]:
                raise ValueError("Join references an unavailable key.")
            ltype, rtype = left.schema.field(key.left).type, right.schema.field(key.right).type
            if ltype != rtype and not (pa.types.is_integer(ltype) and pa.types.is_integer(rtype)):
                raise ValueError("Join key types differ; normalize them in source queries explicitly.")
        config = {
            "enable_external_access": False,
            "python_enable_replacements": False,
            "autoinstall_known_extensions": False,
            "autoload_known_extensions": False,
            "allow_unsigned_extensions": False,
            "allow_community_extensions": False,
            "memory_limit": "256MB",
            "threads": 1,
            "max_temp_directory_size": "0B",
            "temp_directory": "",
        }
        with duckdb.connect(":memory:", config=config) as connection:
            connection.register("source_left", left)
            connection.register("source_right", right)
            connection.execute("SET lock_configuration = true")
            left_keys = ",".join(_identifier(k.left) for k in plan.keys)
            right_keys = ",".join(_identifier(k.right) for k in plan.keys)
            left_not_null = " AND ".join(f"{_identifier(k.left)} IS NOT NULL" for k in plan.keys)
            right_not_null = " AND ".join(f"{_identifier(k.right)} IS NOT NULL" for k in plan.keys)
            ld = connection.execute(
                f"SELECT count(*) FROM (SELECT {left_keys} FROM source_left WHERE {left_not_null} GROUP BY {left_keys} HAVING count(*) > 1)"
            ).fetchone()[0]
            rd = connection.execute(
                f"SELECT count(*) FROM (SELECT {right_keys} FROM source_right WHERE {right_not_null} GROUP BY {right_keys} HAVING count(*) > 1)"
            ).fetchone()[0]
            actual = (
                "many-to-many"
                if ld and rd
                else "many-to-one"
                if ld
                else "one-to-many"
                if rd
                else "one-to-one"
            )
            if actual == "many-to-many" or actual != plan.expected_cardinality:
                raise ValueError(
                    f"Observed {actual}, expected {plan.expected_cardinality}. Aggregate or choose different keys."
                )
            condition = " AND ".join(f"l.{_identifier(k.left)} = r.{_identifier(k.right)}" for k in plan.keys)
            expressions = []
            groups = []
            for p in plan.projections:
                expression = f"{'l' if p.side == 'left' else 'r'}.{_identifier(p.column)}"
                if p.aggregate:
                    expression = f"{p.aggregate.upper()}({expression})"
                else:
                    groups.append(expression)
                expressions.append(f"{expression} AS {_identifier(p.alias)}")
            projection = ", ".join(expressions)
            count = connection.execute(
                f"SELECT count(*) FROM source_left l {plan.join_type.upper()} JOIN source_right r ON {condition}"
            ).fetchone()[0]
            if count > max_rows:
                raise ValueError("Joined result exceeds the row budget.")
            group_sql = (
                " GROUP BY " + ", ".join(groups)
                if groups and any(p.aggregate for p in plan.projections)
                else ""
            )
            compiled = f"SELECT {projection} FROM source_left l {plan.join_type.upper()} JOIN source_right r ON {condition}{group_sql}"
            derived = []
            aliases = {p.alias for p in plan.projections}
            for calculation in plan.calculations:
                if (
                    calculation.left not in aliases
                    or calculation.right not in aliases
                    or calculation.alias in aliases
                ):
                    raise ValueError("Calculation references invalid or duplicate projected columns.")
                a, b = _identifier(calculation.left), _identifier(calculation.right)
                expression = f"{a} - {b}" if calculation.operation == "subtract" else f"{a} / NULLIF({b}, 0)"
                if calculation.operation == "attainment_percent":
                    expression = f"100.0 * {expression}"
                derived.append(f"{expression} AS {_identifier(calculation.alias)}")
            if derived:
                compiled = f"SELECT *, {', '.join(derived)} FROM ({compiled}) AS projected"
            result = connection.execute(f"{compiled} LIMIT {max_rows + 1}")
            columns = [{"name": c[0], "type": str(c[1])} for c in result.description]
            rows = [dict(zip([c["name"] for c in columns], row)) for row in result.fetchall()]
            unmatched_left = connection.execute(
                f"SELECT count(*) FROM source_left l WHERE NOT EXISTS (SELECT 1 FROM source_right r WHERE {condition})"
            ).fetchone()[0]
            unmatched_right = connection.execute(
                f"SELECT count(*) FROM source_right r WHERE NOT EXISTS (SELECT 1 FROM source_left l WHERE {condition})"
            ).fetchone()[0]
            matched_left = len(left) - unmatched_left
            diagnostics = {
                "cardinality": actual,
                "left_rows": len(left),
                "right_rows": len(right),
                "joined_rows": count,
                "unmatched_left": unmatched_left,
                "unmatched_right": unmatched_right,
                "left_key_coverage": round(matched_left / len(left), 4) if len(left) else 0,
                "relationship": plan.relationship,
                "confidence": plan.confidence,
                "keys": [k.model_dump() for k in plan.keys],
                "null_semantics": "Null keys do not match",
                "normalization": "Only explicit source-query transformations",
                "snapshot": "Sources were queried independently; no shared transactional snapshot.",
            }
        channel.put({"rows": rows, "columns": columns, "diagnostics": diagnostics})
    except Exception as exc:
        channel.put({"error": str(exc)})


def _arrow_bytes(result: QueryResult) -> bytes:
    table = pa.Table.from_pylist(result.rows)
    if not result.rows:
        raise AppError(
            "A source returned no rows; there is no cross-source relationship to combine.",
            code="empty_fusion",
        )
    sink = pa.BufferOutputStream()
    with pa.ipc.new_stream(sink, table.schema) as writer:
        writer.write_table(table)
    return sink.getvalue().to_pybytes()


async def fuse(
    left: QueryResult, right: QueryResult, plan: FusionPlan, timeout: int = 10, max_rows: int = 50_000
) -> dict[str, Any]:
    if not left.complete or not right.complete:
        raise AppError(
            "Cannot join incomplete inputs. Narrow filters or aggregate at each source.",
            code="incomplete_fusion",
        )
    left_bytes, right_bytes = _arrow_bytes(left), _arrow_bytes(right)
    if len(left_bytes) + len(right_bytes) > 16_777_216:
        raise AppError("Combined source data exceeds 16 MiB.", code="result_too_large")
    context = mp.get_context("spawn")
    channel = context.Queue(maxsize=1)
    process = context.Process(
        target=_worker, args=(channel, left_bytes, right_bytes, plan.model_dump(), max_rows), daemon=True
    )
    process.start()
    try:

        def receive():
            try:
                return channel.get(timeout=timeout)
            except queue.Empty:
                return {"error": "Fusion timed out. Narrow the analysis."}

        result = await asyncio.to_thread(receive)
        if "error" in result:
            raise AppError(result["error"], code="fusion_rejected")
        return result
    finally:
        if process.is_alive():
            process.terminate()
        await asyncio.to_thread(process.join, 2)
        channel.close()
