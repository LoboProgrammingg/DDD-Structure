import logging

from app.application.notification.ports import NotificationSender
from app.domain.notification.value_objects import Message, Recipient

logger = logging.getLogger(__name__)


class LoggingNotificationSender(NotificationSender):
    """Canal de desenvolvimento: registra o aviso no log em vez de enviá-lo.

    Em produção, troque por um adaptador de e-mail, push ou chat no composition root.
    """

    async def send(self, recipient: Recipient, message: Message) -> None:
        logger.info("Notification delivered", extra={"recipient": recipient.value})
