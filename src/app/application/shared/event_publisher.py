from abc import ABC, abstractmethod
from collections.abc import Sequence

from app.domain.seedwork import DomainEvent


class EventPublisher(ABC):
    """Porta de saída para entregar Domain Events aos interessados."""

    @abstractmethod
    async def publish(self, events: Sequence[DomainEvent]) -> None: ...
