import uuid
from datetime import UTC, datetime

import pytest

from app.application.shared import NotFoundError
from app.application.task_management.dtos import TaskDTO, TaskPageDTO
from app.application.task_management.ports import TaskReadModel
from app.application.task_management.queries import (
    GetTask,
    GetTaskHandler,
    ListTasks,
    ListTasksHandler,
)
from app.domain.task_management.exceptions import InvalidTaskId
from app.domain.task_management.value_objects import TaskStatus

TASK = TaskDTO(
    id=str(uuid.uuid4()),
    title="Ler o blue book",
    description="",
    priority="low",
    status="pending",
    assignee_id=None,
    due_date=None,
    created_at=datetime(2026, 1, 15, tzinfo=UTC),
    completed_at=None,
    version=1,
)


class StubReadModel(TaskReadModel):
    def __init__(self) -> None:
        self.list_calls: list[dict[str, object]] = []

    async def get(self, task_id: str) -> TaskDTO | None:
        return TASK if task_id == TASK.id else None

    async def list(
        self, *, status: TaskStatus | None, assignee_id: str | None, limit: int, offset: int
    ) -> TaskPageDTO:
        self.list_calls.append(
            {"status": status, "assignee_id": assignee_id, "limit": limit, "offset": offset}
        )
        return TaskPageDTO(items=[TASK], total=1, limit=limit, offset=offset)


async def test_get_task_returns_the_projection() -> None:
    assert await GetTaskHandler(StubReadModel())(GetTask(TASK.id)) == TASK


async def test_get_task_raises_not_found() -> None:
    with pytest.raises(NotFoundError):
        await GetTaskHandler(StubReadModel())(GetTask(str(uuid.uuid4())))


async def test_get_task_validates_the_identifier() -> None:
    with pytest.raises(InvalidTaskId):
        await GetTaskHandler(StubReadModel())(GetTask("abc"))


async def test_list_tasks_forwards_filters() -> None:
    read_model = StubReadModel()

    page = await ListTasksHandler(read_model)(
        ListTasks(status=TaskStatus.PENDING, assignee_id="ana", limit=10, offset=20)
    )

    assert page.total == 1
    assert read_model.list_calls == [
        {"status": TaskStatus.PENDING, "assignee_id": "ana", "limit": 10, "offset": 20}
    ]
