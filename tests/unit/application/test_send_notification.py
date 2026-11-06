from app.application.notification.commands import SendNotification, SendNotificationHandler
from app.domain.notification.value_objects import NotificationStatus
from tests.fakes import (
    FakeNotificationUnitOfWork,
    FixedClock,
    InMemoryNotificationRepository,
    RecordingNotificationSender,
    RecordingPublisher,
)


async def test_delivered_notification_is_marked_sent(
    clock: FixedClock, publisher: RecordingPublisher
) -> None:
    notifications = InMemoryNotificationRepository()
    sender = RecordingNotificationSender()
    handler = SendNotificationHandler(
        lambda: FakeNotificationUnitOfWork(notifications, publisher), sender, clock
    )

    await handler(SendNotification(recipient="ana", message="Olá"))

    [notification] = notifications.items.values()
    assert notification.status is NotificationStatus.SENT
    assert sender.sent == [("ana", "Olá")]
    assert publisher.names() == ["NotificationSent"]


async def test_delivery_failure_is_recorded_not_raised(
    clock: FixedClock, publisher: RecordingPublisher
) -> None:
    notifications = InMemoryNotificationRepository()
    handler = SendNotificationHandler(
        lambda: FakeNotificationUnitOfWork(notifications, publisher),
        RecordingNotificationSender(fail_with="SMTP indisponível"),
        clock,
    )

    await handler(SendNotification(recipient="ana", message="Olá"))

    [notification] = notifications.items.values()
    assert notification.status is NotificationStatus.FAILED
    assert notification.failure_reason == "SMTP indisponível"
    assert publisher.names() == ["NotificationFailed"]
