import uuid
from datetime import UTC, datetime

import pytest

from app.domain.notification.aggregates import Notification
from app.domain.notification.events import NotificationFailed, NotificationSent
from app.domain.notification.exceptions import (
    InvalidMessage,
    InvalidRecipient,
    NotificationAlreadyProcessed,
)
from app.domain.notification.value_objects import (
    Message,
    NotificationId,
    NotificationStatus,
    Recipient,
)

NOW = datetime(2026, 1, 15, 9, 0, tzinfo=UTC)


def a_notification() -> Notification:
    return Notification.create(
        NotificationId(uuid.uuid4()),
        recipient=Recipient("ana.souza"),
        message=Message("Você recebeu uma tarefa."),
        created_at=NOW,
    )


def test_new_notification_is_pending_and_silent() -> None:
    notification = a_notification()

    assert notification.status is NotificationStatus.PENDING
    assert notification.pull_events() == []


def test_mark_sent() -> None:
    notification = a_notification()

    notification.mark_sent(NOW)

    assert notification.status is NotificationStatus.SENT
    assert notification.sent_at == NOW
    assert isinstance(notification.pull_events()[0], NotificationSent)


def test_mark_failed_keeps_the_reason() -> None:
    notification = a_notification()

    notification.mark_failed("caixa cheia")

    assert notification.status is NotificationStatus.FAILED
    assert notification.failure_reason == "caixa cheia"
    assert isinstance(notification.pull_events()[0], NotificationFailed)


def test_cannot_be_processed_twice() -> None:
    notification = a_notification()
    notification.mark_sent(NOW)

    with pytest.raises(NotificationAlreadyProcessed):
        notification.mark_failed("tarde demais")


@pytest.mark.parametrize("raw", ["", "  "])
def test_recipient_is_required(raw: str) -> None:
    with pytest.raises(InvalidRecipient):
        Recipient(raw)


@pytest.mark.parametrize("raw", ["", "x" * 501])
def test_message_must_have_content_and_fit(raw: str) -> None:
    with pytest.raises(InvalidMessage):
        Message(raw)
