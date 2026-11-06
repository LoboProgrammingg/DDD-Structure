from dataclasses import dataclass

from app.application.notification.ports import (
    NotificationDeliveryError,
    NotificationSender,
    NotificationUnitOfWorkFactory,
)
from app.application.shared import Clock
from app.domain.notification.aggregates import Notification
from app.domain.notification.value_objects import Message, Recipient


@dataclass(frozen=True, slots=True)
class SendNotification:
    recipient: str
    message: str


class SendNotificationHandler:
    def __init__(
        self,
        uow_factory: NotificationUnitOfWorkFactory,
        sender: NotificationSender,
        clock: Clock,
    ) -> None:
        self._uow_factory = uow_factory
        self._sender = sender
        self._clock = clock

    async def __call__(self, command: SendNotification) -> str:
        async with self._uow_factory() as uow:
            notification = Notification.create(
                uow.notifications.next_identity(),
                recipient=Recipient(command.recipient),
                message=Message(command.message),
                created_at=self._clock.now(),
            )
            try:
                await self._sender.send(notification.recipient, notification.message)
            except NotificationDeliveryError as error:
                notification.mark_failed(str(error))
            else:
                notification.mark_sent(self._clock.now())
            await uow.notifications.add(notification)
            await uow.commit()
            return str(notification.id)
