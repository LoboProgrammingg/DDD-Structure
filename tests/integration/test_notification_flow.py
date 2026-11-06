"""Fluxo entre bounded contexts: TaskAssigned → ACL → SendNotification."""

from collections.abc import AsyncIterator

import pytest
from sqlalchemy import select

from app.application.task_management.commands import AssignTask, CreateTask
from app.application.task_management.queries import GetTask
from app.bootstrap import Container
from app.infrastructure.config import Settings
from app.infrastructure.database import Base
from app.infrastructure.database.models import NotificationModel
from tests.fakes import RecordingNotificationSender


async def _container(database_url: str, sender: RecordingNotificationSender) -> Container:
    container = Container(Settings(database_url=database_url), notification_sender=sender)
    async with container.engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    return container


async def _dispose(container: Container) -> None:
    async with container.engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await container.dispose()


@pytest.fixture
def sender() -> RecordingNotificationSender:
    return RecordingNotificationSender()


@pytest.fixture
async def container(
    database_url: str, sender: RecordingNotificationSender
) -> AsyncIterator[Container]:
    container = await _container(database_url, sender)
    yield container
    await _dispose(container)


async def test_assigning_a_task_notifies_the_assignee(
    container: Container, sender: RecordingNotificationSender
) -> None:
    task_id = await container.create_task(CreateTask(title="Revisar context map"))

    await container.assign_task(AssignTask(task_id=task_id, assignee_id="ana.souza"))

    assert sender.sent == [
        ("ana.souza", 'Você é o novo responsável pela tarefa "Revisar context map".')
    ]
    async with container.session_factory() as session:
        [stored] = (await session.scalars(select(NotificationModel))).all()
    assert (stored.recipient, stored.status) == ("ana.souza", "sent")


async def test_failed_delivery_is_stored_and_does_not_undo_the_assignment(
    database_url: str,
) -> None:
    container = await _container(database_url, RecordingNotificationSender(fail_with="offline"))
    try:
        task_id = await container.create_task(CreateTask(title="Integração resiliente"))

        await container.assign_task(AssignTask(task_id=task_id, assignee_id="ana"))

        task = await container.get_task(GetTask(task_id))
        assert task.assignee_id == "ana"
        async with container.session_factory() as session:
            [stored] = (await session.scalars(select(NotificationModel))).all()
        assert (stored.status, stored.failure_reason) == ("failed", "offline")
    finally:
        await _dispose(container)
