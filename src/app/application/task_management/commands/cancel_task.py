from dataclasses import dataclass

from app.application.task_management.commands._loading import load_task
from app.application.task_management.ports import TaskManagementUnitOfWorkFactory


@dataclass(frozen=True, slots=True)
class CancelTask:
    task_id: str


class CancelTaskHandler:
    def __init__(self, uow_factory: TaskManagementUnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    async def __call__(self, command: CancelTask) -> None:
        async with self._uow_factory() as uow:
            task = await load_task(uow, command.task_id)
            task.cancel()
            await uow.commit()
