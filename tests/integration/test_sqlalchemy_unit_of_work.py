from collections.abc import Callable

import pytest

from app.application.shared import ConcurrencyConflictError
from app.domain.task_management.value_objects import TaskTitle
from app.infrastructure.unit_of_work import SqlAlchemyTaskManagementUnitOfWork
from tests.builders import a_task
from tests.fakes import RecordingPublisher

type UowFactory = Callable[[], SqlAlchemyTaskManagementUnitOfWork]


async def test_uncommitted_work_is_rolled_back(
    task_uow: UowFactory, publisher: RecordingPublisher
) -> None:
    task = a_task()
    async with task_uow() as uow:
        await uow.tasks.add(task)
        task.rename(TaskTitle("Nunca salva"))

    async with task_uow() as uow:
        assert await uow.tasks.get(task.id) is None
    assert publisher.published == []


async def test_events_are_published_after_a_successful_commit(
    task_uow: UowFactory, publisher: RecordingPublisher
) -> None:
    task = a_task()
    async with task_uow() as uow:
        await uow.tasks.add(task)
        task.rename(TaskTitle("Publicada"))
        await uow.commit()

    assert publisher.names() == ["TaskRenamed"]


async def test_concurrent_modification_is_detected(
    task_uow: UowFactory, publisher: RecordingPublisher
) -> None:
    task = a_task()
    async with task_uow() as uow:
        await uow.tasks.add(task)
        await uow.commit()

    async with task_uow() as first, task_uow() as second:
        mine = await first.tasks.get(task.id)
        theirs = await second.tasks.get(task.id)
        assert mine is not None
        assert theirs is not None

        mine.rename(TaskTitle("Primeira escrita"))
        await first.commit()

        theirs.rename(TaskTitle("Escrita concorrente"))
        with pytest.raises(ConcurrencyConflictError):
            await second.commit()

    assert publisher.names() == ["TaskRenamed"]
    async with task_uow() as uow:
        stored = await uow.tasks.get(task.id)
        assert stored is not None
        assert stored.title == TaskTitle("Primeira escrita")
