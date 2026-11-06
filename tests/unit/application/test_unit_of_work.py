import pytest

from app.domain.task_management.value_objects import TaskTitle
from tests.builders import a_task
from tests.fakes import FakeTaskUnitOfWork, InMemoryTaskRepository, RecordingPublisher


async def test_events_are_published_only_after_commit(publisher: RecordingPublisher) -> None:
    uow = FakeTaskUnitOfWork(InMemoryTaskRepository(), publisher)

    async with uow:
        task = a_task(title="Antes")
        await uow.tasks.add(task)
        task.rename(TaskTitle("Depois"))
        assert publisher.published == []
        await uow.commit()

    assert publisher.names() == ["TaskRenamed"]


async def test_leaving_without_commit_publishes_nothing(publisher: RecordingPublisher) -> None:
    uow = FakeTaskUnitOfWork(InMemoryTaskRepository(), publisher)

    async def fail_midway() -> None:
        async with uow:
            task = a_task()
            await uow.tasks.add(task)
            task.rename(TaskTitle("Nunca publicado"))
            raise RuntimeError

    with pytest.raises(RuntimeError):
        await fail_midway()

    assert not uow.committed
    assert publisher.published == []
