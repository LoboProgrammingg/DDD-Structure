import uuid
from datetime import date

import pytest

from app.application.shared import NotFoundError
from app.application.task_management.commands import (
    AssignTask,
    AssignTaskHandler,
    CancelTask,
    CancelTaskHandler,
    CompleteTask,
    CompleteTaskHandler,
    CreateTask,
    CreateTaskHandler,
    RenameTask,
    RenameTaskHandler,
    ReprioritizeTask,
    ReprioritizeTaskHandler,
    StartTask,
    StartTaskHandler,
)
from app.application.task_management.ports import TaskManagementUnitOfWorkFactory
from app.domain.task_management.exceptions import (
    InvalidTaskId,
    InvalidTaskPriority,
    WorkInProgressLimitExceeded,
)
from app.domain.task_management.services import WorkInProgressPolicy
from app.domain.task_management.value_objects import TaskId, TaskPriority, TaskStatus
from tests.builders import a_started_task, a_task
from tests.fakes import FixedClock, InMemoryTaskRepository, RecordingPublisher


async def test_create_task_persists_and_publishes(
    uow_factory: TaskManagementUnitOfWorkFactory,
    tasks: InMemoryTaskRepository,
    clock: FixedClock,
    publisher: RecordingPublisher,
) -> None:
    handler = CreateTaskHandler(uow_factory, clock)

    task_id = await handler(
        CreateTask(title="Desenhar o context map", priority="high", due_date=date(2026, 2, 1))
    )

    task = tasks.items[TaskId.from_string(task_id)]
    assert task.priority is TaskPriority.HIGH
    assert task.created_at == clock.now()
    assert publisher.names() == ["TaskCreated"]


async def test_create_task_rejects_unknown_priority(
    uow_factory: TaskManagementUnitOfWorkFactory, clock: FixedClock
) -> None:
    with pytest.raises(InvalidTaskPriority):
        await CreateTaskHandler(uow_factory, clock)(CreateTask(title="x", priority="max"))


async def test_rename(
    uow_factory: TaskManagementUnitOfWorkFactory, tasks: InMemoryTaskRepository
) -> None:
    task = a_task()
    await tasks.add(task)

    await RenameTaskHandler(uow_factory)(RenameTask(task_id=str(task.id), title="Novo título"))

    assert task.title.value == "Novo título"


async def test_reprioritize(
    uow_factory: TaskManagementUnitOfWorkFactory, tasks: InMemoryTaskRepository
) -> None:
    task = a_task()
    await tasks.add(task)

    await ReprioritizeTaskHandler(uow_factory)(
        ReprioritizeTask(task_id=str(task.id), priority="urgent")
    )

    assert task.priority is TaskPriority.URGENT


async def test_assign_publishes_task_assigned(
    uow_factory: TaskManagementUnitOfWorkFactory,
    tasks: InMemoryTaskRepository,
    publisher: RecordingPublisher,
) -> None:
    task = a_task()
    await tasks.add(task)

    await AssignTaskHandler(uow_factory)(AssignTask(task_id=str(task.id), assignee_id="ana"))

    assert publisher.names() == ["TaskAssigned"]


async def test_start_applies_work_in_progress_policy(
    uow_factory: TaskManagementUnitOfWorkFactory, tasks: InMemoryTaskRepository
) -> None:
    await tasks.add(a_started_task("ana"))
    task = a_task(assignee="ana")
    await tasks.add(task)
    handler = StartTaskHandler(uow_factory, WorkInProgressPolicy(limit=1))

    with pytest.raises(WorkInProgressLimitExceeded):
        await handler(StartTask(task_id=str(task.id)))

    assert task.status is TaskStatus.PENDING


async def test_start(
    uow_factory: TaskManagementUnitOfWorkFactory, tasks: InMemoryTaskRepository
) -> None:
    task = a_task(assignee="ana")
    await tasks.add(task)

    await StartTaskHandler(uow_factory, WorkInProgressPolicy())(StartTask(task_id=str(task.id)))

    assert task.status is TaskStatus.IN_PROGRESS


async def test_complete_uses_the_clock(
    uow_factory: TaskManagementUnitOfWorkFactory,
    tasks: InMemoryTaskRepository,
    clock: FixedClock,
) -> None:
    task = a_task()
    await tasks.add(task)

    await CompleteTaskHandler(uow_factory, clock)(CompleteTask(task_id=str(task.id)))

    assert task.completed_at == clock.now()


async def test_cancel(
    uow_factory: TaskManagementUnitOfWorkFactory, tasks: InMemoryTaskRepository
) -> None:
    task = a_task()
    await tasks.add(task)

    await CancelTaskHandler(uow_factory)(CancelTask(task_id=str(task.id)))

    assert task.status is TaskStatus.CANCELLED


async def test_missing_task_raises_not_found(
    uow_factory: TaskManagementUnitOfWorkFactory,
) -> None:
    with pytest.raises(NotFoundError):
        await CancelTaskHandler(uow_factory)(CancelTask(task_id=str(uuid.uuid4())))


async def test_malformed_id_is_an_invariant_violation(
    uow_factory: TaskManagementUnitOfWorkFactory,
) -> None:
    with pytest.raises(InvalidTaskId):
        await CancelTaskHandler(uow_factory)(CancelTask(task_id="42"))
