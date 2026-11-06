"""Aggregate Root: única porta de entrada de um agregado.

Regras aplicadas (Evans; Vernon, "Effective Aggregate Design"):

* o agregado é a fronteira de consistência transacional;
* objetos externos só referenciam a raiz, e outros agregados apenas por identidade;
* mudanças de estado registram Domain Events, publicados somente após o commit;
* ``version`` sustenta o controle de concorrência otimista feito pela persistência.
"""

from app.domain.seedwork.domain_event import DomainEvent
from app.domain.seedwork.entity import Entity


class AggregateRoot[TId](Entity[TId]):
    def __init__(self, entity_id: TId, version: int = 0) -> None:
        super().__init__(entity_id)
        self._version = version
        self._pending_events: list[DomainEvent] = []

    @property
    def version(self) -> int:
        return self._version

    def _record(self, event: DomainEvent) -> None:
        self._pending_events.append(event)

    def pull_events(self) -> list[DomainEvent]:
        """Entrega os eventos pendentes e esvazia a fila (cada evento sai uma única vez)."""
        events, self._pending_events = self._pending_events, []
        return events
