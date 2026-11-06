from dataclasses import dataclass

from app.application.task_management.dtos import TaskPageDTO
from app.application.task_management.ports import TaskReadModel
from app.domain.task_management.value_objects import TaskStatus


@dataclass(frozen=True, slots=True)
class ListTasks:
    status: TaskStatus | None = None
    assignee_id: str | None = None
    limit: int = 50
    offset: int = 0


class ListTasksHandler:
    def __init__(self, read_model: TaskReadModel) -> None:
        self._read_model = read_model

    async def __call__(self, query: ListTasks) -> TaskPageDTO:
        return await self._read_model.list(
            status=query.status,
            assignee_id=query.assignee_id,
            limit=query.limit,
            offset=query.offset,
        )
