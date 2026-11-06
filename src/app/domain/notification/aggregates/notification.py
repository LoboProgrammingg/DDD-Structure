from datetime import datetime

from app.domain.notification.events import NotificationFailed, NotificationSent
from app.domain.notification.exceptions import NotificationAlreadyProcessed
from app.domain.notification.value_objects import (
    Message,
    NotificationId,
    NotificationStatus,
    Recipient,
)
from app.domain.seedwork import AggregateRoot


class Notification(AggregateRoot[NotificationId]):
    """Aviso a um destinatário. Só pode ser processado (enviado ou falho) uma vez."""

    def __init__(
        self,
        notification_id: NotificationId,
        *,
        recipient: Recipient,
        message: Message,
        status: NotificationStatus,
        created_at: datetime,
        sent_at: datetime | None = None,
        failure_reason: str | None = None,
        version: int = 0,
    ) -> None:
        super().__init__(notification_id, version)
        self._recipient = recipient
        self._message = message
        self._status = status
        self._created_at = created_at
        self._sent_at = sent_at
        self._failure_reason = failure_reason

    @classmethod
    def create(
        cls,
        notification_id: NotificationId,
        *,
        recipient: Recipient,
        message: Message,
        created_at: datetime,
    ) -> "Notification":
        return cls(
            notification_id,
            recipient=recipient,
            message=message,
            status=NotificationStatus.PENDING,
            created_at=created_at,
        )

    @property
    def recipient(self) -> Recipient:
        return self._recipient

    @property
    def message(self) -> Message:
        return self._message

    @property
    def status(self) -> NotificationStatus:
        return self._status

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def sent_at(self) -> datetime | None:
        return self._sent_at

    @property
    def failure_reason(self) -> str | None:
        return self._failure_reason

    def mark_sent(self, at: datetime) -> None:
        self._ensure_pending()
        self._status = NotificationStatus.SENT
        self._sent_at = at
        self._record(NotificationSent(notification_id=str(self.id), recipient=str(self._recipient)))

    def mark_failed(self, reason: str) -> None:
        self._ensure_pending()
        self._status = NotificationStatus.FAILED
        self._failure_reason = reason
        self._record(
            NotificationFailed(
                notification_id=str(self.id), recipient=str(self._recipient), reason=reason
            )
        )

    def _ensure_pending(self) -> None:
        if self._status is not NotificationStatus.PENDING:
            raise NotificationAlreadyProcessed(
                f"A notificação já foi processada (status: '{self._status}')."
            )
