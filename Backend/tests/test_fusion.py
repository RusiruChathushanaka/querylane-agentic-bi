from decimal import Decimal

import pytest

from app.errors import AppError
from app.fusion import fuse
from app.models import Calculation, FusionPlan, JoinKey, Projection, QueryResult


def result(source, rows, complete=True):
    return QueryResult(
        source=source,
        sql="SELECT approved",
        columns=[],
        rows=rows,
        row_count=len(rows),
        complete=complete,
        elapsed_ms=1,
        executed_at="2026-01-01T00:00:00Z",
    )


def plan(cardinality="one-to-one"):
    return FusionPlan(
        keys=[JoinKey(left="key", right="key")],
        projections=[
            Projection(side="left", column="key", alias="key"),
            Projection(side="left", column="revenue", alias="revenue"),
            Projection(side="right", column="target", alias="target"),
        ],
        relationship="Inferred test key",
        expected_cardinality=cardinality,
    )


async def test_join_nulls_unmatched_and_exact_decimal():
    left = result(
        "bigquery",
        [
            {"key": "A", "revenue": Decimal("0.10")},
            {"key": "B", "revenue": Decimal("0.20")},
            {"key": None, "revenue": Decimal("0.30")},
        ],
    )
    right = result(
        "postgres", [{"key": "A", "target": Decimal("0.30")}, {"key": None, "target": Decimal("0.40")}]
    )
    output = await fuse(left, right, plan())
    assert len(output["rows"]) == 3
    assert output["rows"][0]["revenue"] == Decimal("0.10")
    assert sum(row["target"] is None for row in output["rows"]) == 2
    assert output["diagnostics"]["unmatched_left"] == 2
    assert output["diagnostics"]["unmatched_right"] == 1


async def test_fanout_rejected():
    left = result("bigquery", [{"key": "A", "revenue": 1}, {"key": "A", "revenue": 2}])
    right = result("postgres", [{"key": "A", "target": 3}, {"key": "A", "target": 4}])
    with pytest.raises(AppError, match="many-to-many"):
        await fuse(left, right, plan())


async def test_incomplete_inputs_rejected_before_execution():
    with pytest.raises(AppError) as exc:
        await fuse(result("bigquery", [{"key": "A"}], False), result("postgres", [{"key": "A"}]), plan())
    assert exc.value.code == "incomplete_fusion"


async def test_unsafe_identifier_rejected_by_contract():
    with pytest.raises(ValueError):
        Projection(side="left", column="read_csv('/etc/passwd')", alias="stolen")


async def test_projection_validation_and_result_cap():
    left = result("bigquery", [{"key": "A", "revenue": 1}, {"key": "B", "revenue": 2}])
    right = result("postgres", [{"key": "A", "target": 2}, {"key": "B", "target": 3}])
    with pytest.raises(AppError, match="row budget"):
        await fuse(left, right, plan(), max_rows=1)


async def test_zero_denominator_returns_null():
    selected = plan()
    selected.calculations = [
        Calculation(left="revenue", right="target", operation="attainment_percent", alias="attainment")
    ]
    output = await fuse(
        result("bigquery", [{"key": "A", "revenue": 2}]),
        result("postgres", [{"key": "A", "target": 0}]),
        selected,
    )
    assert output["rows"][0]["attainment"] is None
