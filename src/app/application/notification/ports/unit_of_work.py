from abc import ABC
from collections.abc import Callable

from app.application.shared import UnitOfWork
from app.domain.notification.repositories import NotificationRepository


class NotificationUnitOfWork(UnitOfWork, ABC):
    notifications: NotificationRepository


type NotificationUnitOfWorkFactory = Callable[[], NotificationUnitOfWork]
