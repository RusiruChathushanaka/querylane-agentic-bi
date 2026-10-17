"""Closed contracts for dashboard proposals and coherent forecast planning."""

from datetime import date
from typing import Literal

from pydantic import Field, model_validator

from app.dashboard_models import ChartViewState
from app.metrics import MetricRef
from app.models import StrictModel


class PlanningCreate(StrictModel):
    objective: str = Field(min_length=3, max_length=4000)
    request_id: str = Field(min_length=8, max_length=100, pattern=r"^[A-Za-z0-9_-]+$")
    source: Literal["all", "bigquery", "postgres"] = "all"
    model: str | None = Field(default=None, max_length=100)
    skill_ids: list[str] = Field(default_factory=list, max_length=3)
    start: date | None = None
    end: date | None = None
    audience: str = Field(default="Business", max_length=200)
    dashboard_id: str | None = Field(default=None, pattern=r"^[a-f0-9]{32}$")
    expected_revision: int | None = Field(default=None, ge=1)
    reuse_saved: bool = True
    metric: MetricRef | None = None
    hierarchy: Literal["both", "geography", "products"] = "both"
    horizon: int = Field(default=3, ge=1, le=6)
    focus: str = Field(default="", max_length=100)
    base_plan_id: str | None = Field(default=None, pattern=r"^[a-f0-9]{32}$")

    @model_validator(mode="after")
    def bounds(self):
        if not self.objective.strip() or (self.start and self.end and self.start > self.end):
            raise ValueError("Enter an objective and valid date range.")
        return self


class DashboardQuestion(StrictModel):
    id: str = Field(pattern=r"^[a-z0-9_]{1,32}$")
    question: str = Field(min_length=3, max_length=1500)
    purpose: str = Field(max_length=600)
    title: str = Field(min_length=1, max_length=160)
    saved_artifact_id: str | None = Field(default=None, pattern=r"^[a-f0-9]{32}$")


class DashboardCardEdit(StrictModel):
    artifact_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    title: str | None = Field(default=None, min_length=1, max_length=160)
    note: str | None = Field(default=None, max_length=500)
    width: Literal["standard", "wide"] | None = None


class DashboardBlueprint(StrictModel):
    title: str = Field(min_length=1, max_length=80)
    description: str = Field(max_length=500)
    questions: list[DashboardQuestion] = Field(default_factory=list, max_length=8)
    clarification: str | None = Field(default=None, max_length=1000)
    retained_artifact_ids: list[str] | None = Field(default=None, max_length=20)
    existing_card_edits: list[DashboardCardEdit] = Field(default_factory=list, max_length=20)

    @model_validator(mode="after")
    def distinct_questions(self):
        if len({q.id for q in self.questions}) != len(self.questions):
            raise ValueError("Dashboard question IDs must be unique.")
        return self


class ProposedCard(StrictModel):
    artifact_id: str = Field(pattern=r"^[a-f0-9]{32}$")
    title: str = Field(min_length=1, max_length=160)
    note: str = Field(default="", max_length=500)
    width: Literal["standard", "wide"] = "standard"
    view: ChartViewState
    reused: bool = False


class ProposalWrite(StrictModel):
    expected_revision: int = Field(ge=1)
    request_id: str = Field(min_length=8, max_length=100)
    name: str = Field(min_length=1, max_length=80)
    description: str = Field(default="", max_length=500)
    cards: list[ProposedCard] = Field(max_length=20)
    rebase: bool = False


class PlanningAction(StrictModel):
    expected_revision: int = Field(ge=1)
    request_id: str = Field(min_length=8, max_length=100)
    name: str | None = Field(default=None, min_length=1, max_length=100)


class PlanAdjustment(PlanningAction):
    base_version: int = Field(ge=1)
    node_id: str = Field(max_length=100)
    operation: Literal["set", "percent"]
    value: float = Field(allow_inf_nan=False)
    reason: str = Field(min_length=3, max_length=1000)


class PlanningClarification(PlanningAction):
    answer: str = Field(min_length=1, max_length=4000)
