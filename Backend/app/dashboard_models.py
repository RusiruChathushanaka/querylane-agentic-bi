"""Typed, executable-free dashboard and saved-presentation contracts."""

from datetime import date
from typing import Literal

from pydantic import Field, field_validator

from app.models import StrictModel


class ChartViewState(StrictModel):
    version: Literal[1] = 1
    view: Literal["table", "kpi", "line", "area", "bar", "pie", "scatter"] = "table"
    start: date | None = None
    end: date | None = None
    primary: str | None = Field(default=None, max_length=128)
    visible_measures: list[str] = Field(default_factory=list, max_length=4)
    order: Literal["value_desc", "value_asc", "label", "original"] = "value_desc"
    top: Literal[5, 10, 20] = 10
    scatter_x: str | None = Field(default=None, max_length=128)
    scatter_y: str | None = Field(default=None, max_length=128)
    highlights: bool = True
    decimals: Literal[0, 1, 2] = 2

    @field_validator("visible_measures")
    @classmethod
    def distinct(cls, values):
        if len(values) != len(set(values)):
            raise ValueError("Choose distinct measures.")
        return values


class DashboardRequest(StrictModel):
    request_id: str = Field(min_length=8, max_length=100, pattern=r"^[A-Za-z0-9_-]+$")


class DashboardAction(DashboardRequest):
    expected_revision: int = Field(ge=1)


class DashboardCreate(DashboardRequest):
    name: str = Field(min_length=1, max_length=80)
    description: str = Field(default="", max_length=500)

    @field_validator("name", "description")
    @classmethod
    def trimmed(cls, value, info):
        if info.field_name == "name" and not value.strip():
            raise ValueError("Enter a dashboard name.")
        return value.strip()


class DashboardPatch(DashboardAction):
    name: str | None = Field(default=None, min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=500)

    @field_validator("name", "description")
    @classmethod
    def trimmed(cls, value, info):
        if value is not None and info.field_name == "name" and not value.strip():
            raise ValueError("Enter a dashboard name.")
        return value.strip() if value is not None else None


class DashboardPin(DashboardAction):
    artifact_id: str = Field(min_length=1, max_length=80, pattern=r"^[A-Za-z0-9_-]+$")
    view: ChartViewState
    title: str = Field(default="", max_length=160)


class DashboardItemPatch(DashboardAction):
    title: str | None = Field(default=None, max_length=160)
    note: str | None = Field(default=None, max_length=500)
    width: Literal["standard", "wide"] | None = None
    view: ChartViewState | None = None

    @field_validator("title", "note")
    @classmethod
    def trimmed(cls, value, info):
        if value is not None and info.field_name == "title" and not value.strip():
            raise ValueError("Enter a card title.")
        return value.strip() if value is not None else None


class DashboardLayout(DashboardAction):
    item_ids: list[str] = Field(max_length=20)
