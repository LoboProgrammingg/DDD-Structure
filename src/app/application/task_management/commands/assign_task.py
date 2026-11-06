from dataclasses import dataclass

from app.application.task_management.commands._loading import load_task
from app.application.task_management.ports import TaskManagementUnitOfWorkFactory
from app.domain.task_management.value_objects import AssigneeId


@dataclass(frozen=True, slots=True)
class AssignTask:
    task_id: str
    assignee_id: str


class AssignTaskHandler:
    def __init__(self, uow_factory: TaskManagementUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    async def __call__(self, command: AssignTask) -> None:
        async with self._uow_factory() as uow:
            task = await load_task(uow, command.task_id)
            task.assign_to(AssigneeId(command.assignee_id))
            await uow.commit()
