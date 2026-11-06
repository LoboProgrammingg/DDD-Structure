from dataclasses import dataclass

from app.application.task_management.commands._loading import load_task
from app.application.task_management.ports import TaskManagementUnitOfWorkFactory
from app.domain.task_management.value_objects import TaskPriority


@dataclass(frozen=True, slots=True)
class ReprioritizeTask:
    task_id: str
    priority: str


class ReprioritizeTaskHandler:
    def __init__(self, uow_factory: TaskManagementUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    async def __call__(self, command: ReprioritizeTask) -> None:
        async with self._uow_factory() as uow:
            task = await load_task(uow, command.task_id)
            task.reprioritize(TaskPriority.parse(command.priority))
            await uow.commit()
