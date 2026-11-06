from abc import ABC, abstractmethod

from app.domain.notification.value_objects import Message, Recipient


class NotificationDeliveryError(Exception):
    """O canal de entrega (e-mail, push, chat...) recusou ou não respondeu."""


class NotificationSender(ABC):
    @abstractmethod
    async def send(self, recipient: Recipient, message: Message) -> None:
        """Entrega a mensagem. Levanta ``NotificationDeliveryError`` em caso de falha."""
