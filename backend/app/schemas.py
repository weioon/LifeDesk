import re
from datetime import UTC, date, datetime
from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, StringConstraints, field_validator, model_validator

Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=200)]
Priority = Literal["low", "medium", "high"]


def date_only(value):
    if value is not None and not (
        type(value) is date or
        (isinstance(value, str) and re.fullmatch(r"\d{4}-\d{2}-\d{2}", value))
    ):
        raise ValueError("Use a calendar date in YYYY-MM-DD format")
    return value


DueDate = Annotated[date | None, BeforeValidator(date_only)]


class TaskCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Title
    description: str | None = None
    due_date: DueDate = None
    priority: Priority = "medium"


class TaskUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: Title | None = None
    description: str | None = None
    due_date: DueDate = None
    priority: Priority | None = None
    is_completed: bool | None = None

    @model_validator(mode="after")
    def reject_null_required_fields(self):
        for name in ("title", "priority", "is_completed"):
            if name in self.model_fields_set and getattr(self, name) is None:
                raise ValueError(f"{name} cannot be null")
        return self


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    due_date: date | None
    priority: Priority
    is_completed: bool
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @field_validator("completed_at", "created_at", "updated_at")
    @classmethod
    def add_utc_timezone(cls, value):
        return value.replace(tzinfo=UTC) if value is not None else None
