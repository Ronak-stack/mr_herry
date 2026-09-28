from pydantic import BaseModel, ConfigDict, Field
from datetime import date, time
from typing import Literal


class TodoCreate(BaseModel):
    title: str
    description: str | None = None
    due_date: date | None = None
    due_time: time | None = None


class TodoSearchFilters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    due_date: date | None = None
    status: Literal["pending", "completed", "cancelled"] | None = None
    sort_by: Literal["created_at", "due_date", "updated_at"] | None = None
    sort_order: Literal["asc", "desc"] | None = None
    limit: int | None = Field(
    default=None,
    ge=1,
    le=50
)


class TodoUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    description: str | None = None
    due_date: date | None = None
    due_time: time | None = None


class TodoTarget(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    due_date: date | None = None
    status: Literal["pending", "completed", "cancelled"] | None = None


class TodoUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target: TodoTarget
    changes: TodoUpdate
    
class TodoCandidateScore(BaseModel):
    model_config = ConfigDict(extra="forbid")

    todo_id: int
    score: float = Field(ge=0.0, le=1.0)
    
class TodoMatchResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: Literal["MATCHED", "AMBIGUOUS", "NO_MATCH"]
    todo_id: int | None = None
    candidates: list[TodoCandidateScore]
    reason: str
    
class TodoDeleteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target: TodoTarget