"""Barramento de eventos em processo.

Entrega cada evento, após o commit, a todos os handlers inscritos no seu tipo.
Uma falha em um handler é registrada e não afeta os demais nem a operação que
originou o evento (que já foi confirmada). A entrega é *at-most-once*: para
garantia *at-least-once* entre serviços, evolua para Transactional Outbox
(ver ADR-0007).
"""

import logging
from collections import defaultdict
from collections.abc import Awaitable, Callable, Sequence
from typing import Any

from app.application.shared import EventPublisher
from app.domain.seedwork import DomainEvent

logger = logging.getLogger(__name__)

type EventHandler[E: DomainEvent] = Callable[[E], Awaitable[None]]


class InProcessEventBus(EventPublisher):
    def __init__(self) -> None:
        self._handlers: defaultdict[type[DomainEvent], list[EventHandler[Any]]] = defaultdict(list)

    def subscribe[E: DomainEvent](self, event_type: type[E], handler: EventHandler[E]) -> None:
        self._handlers[event_type].append(handler)

    async def publish(self, events: Sequence[DomainEvent]) -> None:
        for event in events:
            logger.info("Domain event published", extra={"event": event.name})
            for handler in self._handlers[type(event)]:
                await self._deliver(event, handler)

    @staticmethod
    async def _deliver(event: DomainEvent, handler: EventHandler[Any]) -> None:
        try:
            await handler(event)
        except Exception:
            logger.exception(
                "Domain event handler failed",
                extra={"event": event.name, "event_id": str(event.event_id)},
            )
