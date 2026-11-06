"""DTOs: dados puros que cruzam a fronteira da aplicação, sem comportamento."""

from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True, slots=True)
class TaskDTO:
    id: str
    title: str
    description: str
    priority: str
    status: str
    assignee_id: str | None
    due_date: date | None
    created_at: datetime
    completed_at: datetime | None
    version: int


@dataclass(frozen=True, slots=True)
class TaskPageDTO:
    items: list[TaskDTO]
    total: int
    limit: int
    offset: int
