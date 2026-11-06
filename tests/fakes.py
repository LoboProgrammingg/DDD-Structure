"""Dublês de teste para as portas da aplicação.

Ficam fora de ``src/``: são detalhes de teste, não adaptadores de produção.
"""

import uuid
from collections.abc import Sequence
from datetime import UTC, datetime, timedelta

from app.application.notification.ports import (
    NotificationDeliveryError,
    NotificationSender,
    NotificationUnitOfWork,
)
from app.application.shared import Clock, EventPublisher
from app.application.task_management.ports import TaskManagementUnitOfWork
from app.domain.notification.aggregates import Notification
from app.domain.notification.repositories import NotificationRepository
from app.domain.notification.value_objects import Message, NotificationId, Recipient
from app.domain.seedwork import AggregateRoot, DomainEvent
from app.domain.task_management.aggregates import Task
from app.domain.task_management.repositories import TaskRepository
from app.domain.task_management.value_objects import AssigneeId, TaskId


class FixedClock(Clock):
    def __init__(self, now: datetime = datetime(2026, 1, 15, 9, 0, tzinfo=UTC)) -> None:
        self._now = now

    def now(self) -> datetime:
        return self._now

    def advance(self, delta: timedelta) -> None:
        self._now += delta


class RecordingPublisher(EventPublisher):
    def __init__(self) -> None:
        self.published: list[DomainEvent] = []

    async def publish(self, events: Sequence[DomainEvent]) -> None:
        self.published.extend(events)

    def names(self) -> list[str]:
        return [event.name for event in self.published]


class InMemoryTaskRepository(TaskRepository):
    def __init__(self) -> None:
        self.items: dict[TaskId, Task] = {}

    def next_identity(self) -> TaskId:
        return TaskId(uuid.uuid4())

    async def add(self, task: Task) -> None:
        self.items[task.id] = task

    async def get(self, task_id: TaskId) -> Task | None:
        return self.items.get(task_id)

    async def list_by_assignee(self, assignee_id: AssigneeId) -> list[Task]:
        return [task for task in self.items.values() if task.assignee_id == assignee_id]


class InMemoryNotificationRepository(NotificationRepository):
    def __init__(self) -> None:
        self.items: dict[NotificationId, Notification] = {}

    def next_identity(self) -> NotificationId:
        return NotificationId(uuid.uuid4())

    async def add(self, notification: Notification) -> None:
        self.items[notification.id] = notification

    async def get(self, notification_id: NotificationId) -> Notification | None:
        return self.items.get(notification_id)


def _drain(aggregates: Sequence[AggregateRoot[object]]) -> list[DomainEvent]:
    return [event for aggregate in aggregates for event in aggregate.pull_events()]


class FakeTaskUnitOfWork(TaskManagementUnitOfWork):
    def __init__(self, tasks: InMemoryTaskRepository, publisher: EventPublisher) -> None:
        super().__init__(publisher)
        self.tasks = tasks
        self.committed = False

    async def rollback(self) -> None:
        pass

    async def _commit(self) -> None:
        self.committed = True

    def _collect_events(self) -> list[DomainEvent]:
        assert isinstance(self.tasks, InMemoryTaskRepository)
        return _drain(list(self.tasks.items.values()))


class FakeNotificationUnitOfWork(NotificationUnitOfWork):
    def __init__(
        self, notifications: InMemoryNotificationRepository, publisher: EventPublisher
    ) -> None:
        super().__init__(publisher)
        self.notifications = notifications
        self.committed = False

    async def rollback(self) -> None:
        pass

    async def _commit(self) -> None:
        self.committed = True

    def _collect_events(self) -> list[DomainEvent]:
        assert isinstance(self.notifications, InMemoryNotificationRepository)
        return _drain(list(self.notifications.items.values()))


class RecordingNotificationSender(NotificationSender):
    def __init__(self, *, fail_with: str | None = None) -> None:
        self.sent: list[tuple[str, str]] = []
        self._fail_with = fail_with

    async def send(self, recipient: Recipient, message: Message) -> None:
        if self._fail_with is not None:
            raise NotificationDeliveryError(self._fail_with)
        self.sent.append((recipient.value, message.value))
