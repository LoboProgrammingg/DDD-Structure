from dataclasses import dataclass

from app.application.task_management.commands._loading import load_task
from app.application.task_management.ports import TaskManagementUnitOfWorkFactory
from app.domain.task_management.services import WorkInProgressPolicy


@dataclass(frozen=True, slots=True)
class StartTask:
    task_id: str


class StartTaskHandler:
    def __init__(
        self,
        uow_factory: TaskManagementUnitOfWorkFactory,
        policy: WorkInProgressPolicy,
    ) -> None:
        self._uow_factory = uow_factory
        self._policy = policy

    async def __call__(self, command: StartTask) -> None:
        async with self._uow_factory() as uow:
            task = await load_task(uow, command.task_id)
            assignee_tasks = (
                await uow.tasks.list_by_assignee(task.assignee_id) if task.assignee_id else []
            )
            self._policy.start(task, assignee_tasks)
            await uow.commit()
