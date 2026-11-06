from typing import ClassVar

from app.domain.seedwork import BusinessRuleViolation, InvariantViolation


class InvalidRecipient(InvariantViolation):
    code: ClassVar[str] = "invalid_recipient"


class InvalidMessage(InvariantViolation):
    code: ClassVar[str] = "invalid_message"


class NotificationAlreadyProcessed(BusinessRuleViolation):
    code: ClassVar[str] = "notification_already_processed"
