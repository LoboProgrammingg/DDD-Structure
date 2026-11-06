from app.application.shared import NotFoundError
from app.application.task_management.ports import TaskManagementUnitOfWork
from app.domain.task_management.aggregates import Task
from app.domain.task_management.value_objects import TaskId


async def load_task(uow: TaskManagementUnitOfWork, raw_task_id: str) -> Task:
    task = await uow.tasks.get(TaskId.from_string(raw_task_id))
    if task is None:
        raise NotFoundError("Tarefa", raw_task_id)
    return task
