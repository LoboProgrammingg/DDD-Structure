"""Builders: criam agregados válidos e deixam o teste declarar só o que importa."""

import uuid
from datetime import UTC, date, datetime

from app.domain.task_management.aggregates import Task
from app.domain.task_management.value_objects import (
    AssigneeId,
    DueDate,
    TaskId,
    TaskPriority,
    TaskTitle,
)

CREATED_AT = datetime(2026, 1, 15, 9, 0, tzinfo=UTC)


def a_task(
    *,
    title: str = "Mapear o contexto de faturamento",
    priority: TaskPriority = TaskPriority.MEDIUM,
    due_date: date | None = None,
    assignee: str | None = None,
    created_at: datetime = CREATED_AT,
) -> Task:
    task = Task.create(
        TaskId(uuid.uuid4()),
        title=TaskTitle(title),
        priority=priority,
        created_at=created_at,
        due_date=DueDate(due_date) if due_date else None,
    )
    if assignee is not None:
        task.assign_to(AssigneeId(assignee))
    task.pull_events()
    return task


def a_started_task(assignee: str = "ana.souza") -> Task:
    task = a_task(assignee=assignee)
    task.start()
    task.pull_events()
    return task
