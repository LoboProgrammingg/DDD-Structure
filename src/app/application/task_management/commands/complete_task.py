from dataclasses import dataclass

from app.application.shared import Clock
from app.application.task_management.commands._loading import load_task
from app.application.task_management.ports import TaskManagementUnitOfWorkFactory


@dataclass(frozen=True, slots=True)
class CompleteTask:
    task_id: str


class CompleteTaskHandler:
    def __init__(self, uow_factory: TaskManagementUnitOfWorkFactory, clock: Clock) -> None:
        self._uow_factory = uow_factory
        self._clock = clock

    async def __call__(self, command: CompleteTask) -> None:
        async with self._uow_factory() as uow:
            task = await load_task(uow, command.task_id)
            task.complete(self._clock.now())
            await uow.commit()
