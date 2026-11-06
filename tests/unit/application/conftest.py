import pytest

from app.application.task_management.ports import TaskManagementUnitOfWorkFactory
from tests.fakes import FakeTaskUnitOfWork, InMemoryTaskRepository, RecordingPublisher


@pytest.fixture
def tasks() -> InMemoryTaskRepository:
    return InMemoryTaskRepository()


@pytest.fixture
def uow_factory(
    tasks: InMemoryTaskRepository, publisher: RecordingPublisher
) -> TaskManagementUnitOfWorkFactory:
    return lambda: FakeTaskUnitOfWork(tasks, publisher)
