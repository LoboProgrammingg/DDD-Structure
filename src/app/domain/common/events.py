"""
Domain Events.

Domain Events representam algo que aconteceu no domínio.
São imutáveis e capturam o momento em que ocorreram.
"""

from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any
from uuid import uuid4


if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class DomainEvent(ABC):
    """
    Classe base para todos os eventos de domínio.

    Um evento de domínio:
    - É imutável (frozen=True)
    - Possui um ID único
    - Captura o momento em que ocorreu
    - Representa algo que JÁ aconteceu (passado)

    Exemplo de uso:
        >>> @dataclass(frozen=True)
        ... class UserRegistered(DomainEvent):
        ...     user_id: str
        ...     email: str
    """

    event_id: str = field(default_factory=lambda: str(uuid4()), kw_only=True)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc), kw_only=True)

    @property
    def event_type(self) -> str:
        """Retorna o tipo do evento (nome da classe)."""
        return self.__class__.__name__


class EventMixin:
    """
    Mixin para entidades que emitem eventos de domínio.

    Adiciona capacidade de acumular e limpar eventos.
    Use quando não quiser herdar de Entity mas precisar de eventos.
    """

    def __init__(self) -> None:
        self._domain_events: list[DomainEvent] = []

    @property
    def domain_events(self) -> list[DomainEvent]:
        """Retorna cópia dos eventos pendentes."""
        return self._domain_events.copy()

    def add_event(self, event: DomainEvent) -> None:
        """Adiciona um evento à lista de eventos pendentes."""
        self._domain_events.append(event)

    def clear_events(self) -> list[DomainEvent]:
        """Limpa e retorna os eventos pendentes."""
        events = self._domain_events.copy()
        self._domain_events.clear()
        return events


class EventDispatcher:
    """
    Dispatcher simples de eventos de domínio.

    Registra handlers e despacha eventos para eles.

    Exemplo de uso:
        >>> dispatcher = EventDispatcher()
        >>> dispatcher.register(UserRegistered, send_welcome_email)
        >>> dispatcher.dispatch(user_registered_event)
    """

    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[Any]] = {}

    def register(
        self,
        event_type: type[DomainEvent],
        handler: Any,
    ) -> None:
        """
        Registra um handler para um tipo de evento.

        Args:
            event_type: Tipo do evento
            handler: Callable que será chamado quando o evento ocorrer
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    def dispatch(self, event: DomainEvent) -> None:
        """
        Despacha um evento para todos os handlers registrados.

        Args:
            event: Evento a ser despachado
        """
        event_type = type(event)
        handlers = self._handlers.get(event_type, [])
        for handler in handlers:
            handler(event)

    def dispatch_all(self, events: list[DomainEvent]) -> None:
        """Despacha múltiplos eventos."""
        for event in events:
            self.dispatch(event)
