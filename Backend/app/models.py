from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ConversationCreate(StrictModel):
    title: str = Field(default="New exploration", min_length=1, max_length=100)
    source: Literal["all", "bigquery", "postgres"] = "all"


class TurnCreate(StrictModel):
    question: str = Field(min_length=1, max_length=4000)
    idempotency_key: str = Field(min_length=8, max_length=100, pattern=r"^[a-zA-Z0-9_-]+$")
    model: str | None = Field(default=None, min_length=1, max_length=100)

    @field_validator("question")
    @classmethod
    def meaningful_question(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Enter a question.")
        return value.strip()


class SourceQuery(StrictModel):
    source: Literal["bigquery", "postgres"]
    sql: str = Field(min_length=1, max_length=12_000)
    purpose: str = Field(max_length=1000)


class JoinKey(StrictModel):
    left: str = Field(pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
    right: str = Field(pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")


class Projection(StrictModel):
    side: Literal["left", "right"]
    column: str = Field(pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
    alias: str = Field(pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
    aggregate: Literal["sum", "avg", "min", "max", "count"] | None = None


class Calculation(StrictModel):
    left: str = Field(pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
    right: str = Field(pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")
    operation: Literal["subtract", "divide", "attainment_percent"]
    alias: str = Field(pattern=r"^[A-Za-z_][A-Za-z0-9_]*$")


class FusionPlan(StrictModel):
    keys: list[JoinKey] = Field(min_length=1, max_length=4)
    join_type: Literal["inner", "left", "full"] = "left"
    projections: list[Projection] = Field(min_length=1, max_length=20)
    calculations: list[Calculation] = Field(default_factory=list, max_length=4)
    relationship: str = Field(min_length=1, max_length=1500)
    confidence: Literal["declared", "inferred-high", "inferred-low"] = "inferred-low"
    expected_cardinality: Literal["one-to-one", "one-to-many", "many-to-one"] = "one-to-one"


class VisualizationSpec(StrictModel):
    type: Literal["bar", "line", "area", "pie", "scatter", "table", "kpi"] = "table"
    title: str = Field(max_length=160)
    x: str | None = None
    y: list[str] = Field(default_factory=list, max_length=4)
    format: Literal["number", "currency", "percent"] = "number"


class AnalysisPlan(StrictModel):
    title: str = Field(max_length=120)
    queries: list[SourceQuery] = Field(default_factory=list, max_length=2)
    fusion: FusionPlan | None = None
    visualization: VisualizationSpec
    assumptions: list[str] = Field(default_factory=list, max_length=10)
    clarification: str | None = Field(default=None, max_length=1000)


class Answer(StrictModel):
    explanation: str = Field(max_length=12_000)
    followups: list[str] = Field(default_factory=list, max_length=3)


class QueryResult(BaseModel):
    source: str
    sql: str
    columns: list[dict[str, str]]
    rows: list[dict[str, Any]]
    row_count: int
    complete: bool
    executed_at: str
    elapsed_ms: int
    job_id: str | None = None
    bytes_processed: int | None = None


class ResultArtifact(BaseModel):
    id: str
    conversation_id: str
    title: str
    columns: list[dict[str, str]]
    row_count: int
    preview_count: int
    complete: bool
    visualization: VisualizationSpec
    provenance: list[dict[str, Any]]
    assumptions: list[str]
    join_diagnostics: dict[str, Any] | None = None
    created_at: str
