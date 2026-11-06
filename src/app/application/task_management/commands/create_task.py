from dataclasses import dataclass
from datetime import date

from app.application.shared import Clock
from app.application.task_management.ports import TaskManagementUnitOfWorkFactory
from app.domain.task_management.aggregates import Task
from app.domain.task_management.value_objects import (
    DueDate,
    TaskDescription,
    TaskPriority,
    TaskTitle,
)


@dataclass(frozen=True, slots=True)
class CreateTask:
    title: str
    priority: str = TaskPriority.MEDIUM.value
    description: str = ""
    due_date: date | None = None


class CreateTaskHandler:
    def __init__(self, uow_factory: TaskManagementUnitOfWorkFactory, clock: Clock) -> None:
        self._uow_factory = uow_factory
        self._clock = clock

    async def __call__(self, command: CreateTask) -> str:
        async with self._uow_factory() as uow:
            task = Task.create(
                uow.tasks.next_identity(),
                title=TaskTitle(command.title),
                priority=TaskPriority.parse(command.priority),
                description=TaskDescription(command.description),
                due_date=DueDate(command.due_date) if command.due_date else None,
                created_at=self._clock.now(),
            )
            await uow.tasks.add(task)
            await uow.commit()
            return str(task.id)
