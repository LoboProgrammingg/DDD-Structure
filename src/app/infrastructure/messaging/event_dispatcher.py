"""
Event Dispatcher para Domain Events.

Implementa o padrão Observer para despacho de eventos de domínio.
Permite desacoplamento entre quem emite eventos e quem os processa.

Por que usar Event Dispatcher?
- Desacoplamento: produtor não conhece consumidores
- Extensibilidade: adicione handlers sem modificar código existente
- Auditoria: ponto central para logging de eventos
- Preparado para evolução: fácil migrar para filas (RabbitMQ, Kafka)

Fluxo típico:
1. Use Case executa operação no domínio
2. Entidade acumula eventos
3. Use Case coleta eventos da entidade
4. Use Case envia eventos para o dispatcher
5. Dispatcher notifica todos os handlers registrados
"""

import asyncio
from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Callable
from typing import Any, Generic, TypeVar

from app.domain.common.events import DomainEvent
from app.infrastructure.logging import get_logger


logger = get_logger(__name__)

TEvent = TypeVar("TEvent", bound=DomainEvent)


class EventHandler(ABC, Generic[TEvent]):
    """
    Interface base para handlers de eventos.

    Implemente esta interface para criar handlers tipados.
    """

    @abstractmethod
    def handle(self, event: TEvent) -> None:
        """Processa o evento."""


# Tipo para handlers de função
EventHandlerFunc = Callable[[DomainEvent], None]
AsyncEventHandlerFunc = Callable[[DomainEvent], Any]


class EventDispatcher:
    """
    Dispatcher síncrono de eventos de domínio.

    Registra handlers e despacha eventos para todos os handlers
    registrados para aquele tipo de evento.

    Exemplo de uso:
        >>> dispatcher = EventDispatcher()
        >>> dispatcher.register(TaskCreated, log_task_created)
        >>> dispatcher.register(TaskCreated, notify_user)
        >>> dispatcher.dispatch(task_created_event)
    """

    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[EventHandlerFunc]] = defaultdict(list)
        self._global_handlers: list[EventHandlerFunc] = []

    def register(
        self,
        event_type: type[TEvent],
        handler: EventHandlerFunc | EventHandler[TEvent],
    ) -> None:
        """
        Registra um handler para um tipo específico de evento.

        Args:
            event_type: Tipo do evento
            handler: Função ou objeto handler
        """
        if isinstance(handler, EventHandler):
            self._handlers[event_type].append(handler.handle)
        else:
            self._handlers[event_type].append(handler)

        logger.info(
            f"Handler registrado para {event_type.__name__}",
            extra={"event_type": event_type.__name__},
        )

    def register_global(self, handler: EventHandlerFunc) -> None:
        """
        Registra um handler que recebe TODOS os eventos.

        Útil para logging, auditoria, métricas, etc.

        Args:
            handler: Função que processa qualquer evento
        """
        self._global_handlers.append(handler)
        logger.info("Handler global registrado")

    def unregister(
        self,
        event_type: type[TEvent],
        handler: EventHandlerFunc | EventHandler[TEvent],
    ) -> None:
        """
        Remove um handler registrado.

        Args:
            event_type: Tipo do evento
            handler: Handler a ser removido
        """
        handler_func = handler.handle if isinstance(handler, EventHandler) else handler
        if handler_func in self._handlers[event_type]:
            self._handlers[event_type].remove(handler_func)

    def dispatch(self, event: DomainEvent) -> None:
        """
        Despacha um evento para todos os handlers registrados.

        Args:
            event: Evento a ser despachado
        """
        event_type = type(event)

        logger.debug(
            f"Despachando evento {event_type.__name__}",
            extra={
                "event_type": event_type.__name__,
                "event_id": event.event_id,
            },
        )

        # Handlers globais primeiro
        for handler in self._global_handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(
                    f"Erro no handler global: {e}",
                    extra={"event_type": event_type.__name__, "error": str(e)},
                )

        # Handlers específicos
        for handler in self._handlers.get(event_type, []):
            try:
                handler(event)
            except Exception as e:
                logger.error(
                    f"Erro no handler de {event_type.__name__}: {e}",
                    extra={"event_type": event_type.__name__, "error": str(e)},
                )

    def dispatch_all(self, events: list[DomainEvent]) -> None:
        """
        Despacha múltiplos eventos em sequência.

        Args:
            events: Lista de eventos a serem despachados
        """
        for event in events:
            self.dispatch(event)

    def clear(self) -> None:
        """Remove todos os handlers registrados."""
        self._handlers.clear()
        self._global_handlers.clear()


class AsyncEventDispatcher:
    """
    Dispatcher assíncrono de eventos de domínio.

    Versão async do EventDispatcher para uso com FastAPI e outras
    aplicações assíncronas.

    Preparado para evolução futura:
    - Integração com message brokers (RabbitMQ, Kafka)
    - Retry policies
    - Dead letter queues
    """

    def __init__(self) -> None:
        self._handlers: dict[type[DomainEvent], list[AsyncEventHandlerFunc]] = defaultdict(list)
        self._global_handlers: list[AsyncEventHandlerFunc] = []

    def register(
        self,
        event_type: type[TEvent],
        handler: AsyncEventHandlerFunc,
    ) -> None:
        """Registra um handler async para um tipo específico de evento."""
        self._handlers[event_type].append(handler)
        logger.info(
            f"Handler async registrado para {event_type.__name__}",
            extra={"event_type": event_type.__name__},
        )

    def register_global(self, handler: AsyncEventHandlerFunc) -> None:
        """Registra um handler async global."""
        self._global_handlers.append(handler)

    async def dispatch(self, event: DomainEvent) -> None:
        """Despacha um evento de forma assíncrona."""
        event_type = type(event)

        logger.debug(
            f"Despachando evento async {event_type.__name__}",
            extra={"event_type": event_type.__name__, "event_id": event.event_id},
        )

        # Executa handlers globais
        for handler in self._global_handlers:
            try:
                result = handler(event)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.error(f"Erro no handler global async: {e}")

        # Executa handlers específicos
        for handler in self._handlers.get(event_type, []):
            try:
                result = handler(event)
                if asyncio.iscoroutine(result):
                    await result
            except Exception as e:
                logger.error(f"Erro no handler async: {e}")

    async def dispatch_all(self, events: list[DomainEvent]) -> None:
        """Despacha múltiplos eventos de forma assíncrona."""
        for event in events:
            await self.dispatch(event)

    def clear(self) -> None:
        """Remove todos os handlers."""
        self._handlers.clear()
        self._global_handlers.clear()
