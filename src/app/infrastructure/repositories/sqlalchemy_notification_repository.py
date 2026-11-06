import uuid

from app.domain.notification.aggregates import Notification
from app.domain.notification.repositories import NotificationRepository
from app.domain.notification.value_objects import (
    Message,
    NotificationId,
    NotificationStatus,
    Recipient,
)
from app.infrastructure.database.models import NotificationModel
from app.infrastructure.repositories.sqlalchemy_repository import SqlAlchemyRepository


class SqlAlchemyNotificationRepository(
    SqlAlchemyRepository[Notification, NotificationModel], NotificationRepository
):
    model = NotificationModel

    def next_identity(self) -> NotificationId:
        return NotificationId(uuid.uuid4())

    async def add(self, notification: Notification) -> None:
        self._register(notification)

    async def get(self, notification_id: NotificationId) -> Notification | None:
        return await self._find(notification_id.value)

    def _primary_key(self, aggregate: Notification) -> uuid.UUID:
        return aggregate.id.value

    def _row_primary_key(self, row: NotificationModel) -> uuid.UUID:
        return row.id

    def _to_domain(self, row: NotificationModel) -> Notification:
        return Notification(
            NotificationId(row.id),
            recipient=Recipient(row.recipient),
            message=Message(row.message),
            status=NotificationStatus(row.status),
            created_at=row.created_at,
            sent_at=row.sent_at,
            failure_reason=row.failure_reason,
            version=row.version,
        )

    def _apply(self, aggregate: Notification, row: NotificationModel) -> None:
        row.recipient = aggregate.recipient.value
        row.message = aggregate.message.value
        row.status = aggregate.status.value
        row.created_at = aggregate.created_at
        row.sent_at = aggregate.sent_at
        row.failure_reason = aggregate.failure_reason
