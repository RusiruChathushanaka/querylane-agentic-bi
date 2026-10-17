"""Bounded contracts shared by the report harness, API, renderer, and numerical tools."""

import json
import math
from typing import Literal

from pydantic import Field, field_validator, model_validator

from app.models import StrictModel

ReportStyle = Literal["business", "technical"]
ReportStatus = Literal["queued", "running", "waiting_input", "complete", "failed", "cancelled"]


class ReportCreate(StrictModel):
    question: str = Field(min_length=1, max_length=4000)
    idempotency_key: str = Field(min_length=8, max_length=100, pattern=r"^[A-Za-z0-9_-]+$")
    model: str | None = Field(default=None, max_length=100)
    style: ReportStyle = "business"

    @field_validator("question")
    @classmethod
    def meaningful(cls, value):
        if not value.strip():
            raise ValueError("Enter a report question.")
        return value.strip()


class ReportRevisionCreate(ReportCreate):
    expected_revision: int = Field(ge=1)
    base_version: int = Field(ge=1)
    mode: Literal["presentation", "reanalyze"] = "reanalyze"


class ReportMutation(StrictModel):
    expected_revision: int = Field(ge=1)


class ReportPatch(ReportMutation):
    name: str = Field(min_length=1, max_length=120)

    @field_validator("name")
    @classmethod
    def meaningful(cls, value):
        if not value.strip():
            raise ValueError("Enter a report name.")
        return value.strip()


class ForecastInputs(StrictModel):
    baseline: list[dict[str, float]] = Field(min_length=1, max_length=90)
    scenario: list[dict[str, float]] = Field(default_factory=list, max_length=90)

    @model_validator(mode="after")
    def bounded_values(self):
        for row in self.baseline + self.scenario:
            if not 1 <= len(row) <= 4 or any(
                len(key) > 128 or not math.isfinite(value) for key, value in row.items()
            ):
                raise ValueError("Provide finite values for at most four drivers per period.")
        return self


class ReportClarification(StrictModel):
    answer: str = Field(min_length=1, max_length=4000)
    expected_revision: int = Field(ge=1)
    forecast_inputs: dict[str, ForecastInputs] = Field(default_factory=dict, max_length=6)

    @model_validator(mode="after")
    def bounded_inputs(self):
        if any(not key or len(key) > 128 for key in self.forecast_inputs):
            raise ValueError("Forecast target names must match a result column.")
        if len(json.dumps(self.forecast_inputs, default=lambda v: v.model_dump()).encode()) > 24000:
            raise ValueError("Future assumptions are too large. Request fewer series or periods.")
        return self

    @field_validator("answer")
    @classmethod
    def meaningful(cls, value):
        if not value.strip():
            raise ValueError("Enter an answer.")
        return value.strip()


class AnalysisTask(StrictModel):
    id: str = Field(max_length=64, pattern=r"^[a-z][a-z0-9_]{0,63}$")
    question: str = Field(min_length=1, max_length=1800)
    purpose: str = Field(min_length=1, max_length=600)


class ForecastSpec(StrictModel):
    candidate_policy: Literal["auto_compare", "statistical_only"] = "auto_compare"
    rationale: str = Field(
        default="Compare eligible candidates against chronological backtests.", max_length=600
    )
    priority: int = Field(default=1, ge=1, le=6)
    task_id: str = Field(max_length=64)
    date_column: str = Field(min_length=1, max_length=128)
    target: str = Field(min_length=1, max_length=128)
    grain: Literal["day", "week", "month"] = "month"
    horizon: int | None = Field(default=None, ge=1, le=90)
    season: int | None = Field(default=None, ge=2, le=366)
    domain: Literal["nonnegative", "signed", "fraction", "percentage"] = "nonnegative"
    drivers: list[str] = Field(default_factory=list, max_length=4)
    future_drivers: list[dict[str, float]] = Field(default_factory=list, max_length=90)
    scenario_drivers: list[dict[str, float]] = Field(default_factory=list, max_length=90)
    scenario_name: str | None = Field(default=None, max_length=100)
    assumptions: list[str] = Field(default_factory=list, max_length=8)


class ReportPlan(StrictModel):
    title: str = Field(min_length=1, max_length=120)
    scope: str = Field(min_length=1, max_length=1500)
    tasks: list[AnalysisTask] = Field(default_factory=list, max_length=5)
    definitions: list[str] = Field(default_factory=list, max_length=10)
    assumptions: list[str] = Field(default_factory=list, max_length=10)
    forecasts: list[ForecastSpec] = Field(default_factory=list, max_length=6)
    clarification: str | None = Field(default=None, max_length=1200)

    @model_validator(mode="after")
    def references(self):
        ids = [t.id for t in self.tasks]
        if len(ids) != len(set(ids)):
            raise ValueError("Analysis task IDs must be unique.")
        if any(f.task_id not in ids for f in self.forecasts):
            raise ValueError("Forecasts must reference an analysis task.")
        return self


class EvidenceClaim(StrictModel):
    id: str
    artifact_id: str
    label: str
    value: str
    formatted: str
    calculation: str
    unit: str = "number"


class ReportSection(StrictModel):
    id: str = Field(max_length=40, pattern=r"^[a-z][a-z0-9_-]{0,39}$")
    title: str = Field(min_length=1, max_length=120)
    markdown: str = Field(max_length=12000)
    claim_ids: list[str] = Field(default_factory=list, max_length=40)
    artifact_ids: list[str] = Field(default_factory=list, max_length=8)
    kind: Literal["finding", "recommendation", "methodology", "limitation"] = "finding"


class ReportDraft(StrictModel):
    summary: str = Field(max_length=4000)
    sections: list[ReportSection] = Field(min_length=1, max_length=12)


class ReviewResult(StrictModel):
    approved: bool
    issues: list[str] = Field(default_factory=list, max_length=10)


class ResearchRequest(StrictModel):
    topic: Literal[
        "retail seasonality",
        "retail forecasting methods",
        "retail inventory planning",
        "retail promotion measurement",
    ]
    model: str | None = Field(default=None, max_length=100)
