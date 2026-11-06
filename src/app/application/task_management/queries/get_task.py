from dataclasses import dataclass

from app.application.shared import NotFoundError
from app.application.task_management.dtos import TaskDTO
from app.application.task_management.ports import TaskReadModel
from app.domain.task_management.value_objects import TaskId


@dataclass(frozen=True, slots=True)
class GetTask:
    task_id: str


class GetTaskHandler:
    def __init__(self, read_model: TaskReadModel) -> None:
        self._read_model = read_model

    async def __call__(self, query: GetTask) -> TaskDTO:
        task_id = str(TaskId.from_string(query.task_id))
        task = await self._read_model.get(task_id)
        if task is None:
            raise NotFoundError("Tarefa", query.task_id)
        return task
