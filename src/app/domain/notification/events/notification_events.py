from dataclasses import dataclass

from app.domain.seedwork import DomainEvent


@dataclass(frozen=True, kw_only=True)
class NotificationSent(DomainEvent):
    notification_id: str
    recipient: str


@dataclass(frozen=True, kw_only=True)
class NotificationFailed(DomainEvent):
    notification_id: str
    recipient: str
    reason: str
