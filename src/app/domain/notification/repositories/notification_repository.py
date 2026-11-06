from abc import ABC, abstractmethod

from app.domain.notification.aggregates import Notification
from app.domain.notification.value_objects import NotificationId


class NotificationRepository(ABC):
    @abstractmethod
    def next_identity(self) -> NotificationId: ...

    @abstractmethod
    async def add(self, notification: Notification) -> None: ...

    @abstractmethod
    async def get(self, notification_id: NotificationId) -> Notification | None: ...
