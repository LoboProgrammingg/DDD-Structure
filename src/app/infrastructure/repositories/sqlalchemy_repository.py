"""Base dos repositórios SQLAlchemy com mapeamento explícito ORM ↔ domínio.

* Identity Map: dentro de uma Unit of Work, cada agregado existe uma única vez.
* ``sync``: antes do commit, copia o estado de todos os agregados rastreados
  para as linhas ORM. Assim o repositório se comporta como uma coleção:
  quem altera um agregado não precisa chamar ``save``.
* ``pull_events``: entrega à Unit of Work os eventos dos agregados rastreados.

As linhas ORM carregadas ficam referenciadas aqui. A Session do SQLAlchemy só
guarda referências fracas; sem isso, a linha poderia ser recarregada já com a
versão de outra transação e o controle de concorrência otimista não detectaria
a escrita concorrente (lost update).
"""

import uuid
from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.seedwork import AggregateRoot, DomainEvent
from app.infrastructure.database.base import Base


class SqlAlchemyRepository[TAggregate: AggregateRoot[object], TModel: Base](ABC):
    model: type[TModel]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._identity_map: dict[uuid.UUID, TAggregate] = {}
        self._rows: dict[uuid.UUID, TModel] = {}

    def sync(self) -> None:
        for primary_key, aggregate in self._identity_map.items():
            row = self._rows.get(primary_key)
            if row is None:
                row = self.model(id=primary_key)
                self._session.add(row)
                self._rows[primary_key] = row
            self._apply(aggregate, row)

    def pull_events(self) -> list[DomainEvent]:
        return [
            event for aggregate in self._identity_map.values() for event in aggregate.pull_events()
        ]

    def _register(self, aggregate: TAggregate) -> None:
        self._identity_map[self._primary_key(aggregate)] = aggregate

    async def _find(self, primary_key: uuid.UUID) -> TAggregate | None:
        if primary_key in self._identity_map:
            return self._identity_map[primary_key]
        row = await self._session.get(self.model, primary_key)
        return None if row is None else self._track(row)

    def _track(self, row: TModel) -> TAggregate:
        primary_key = self._row_primary_key(row)
        if primary_key not in self._identity_map:
            self._identity_map[primary_key] = self._to_domain(row)
            self._rows[primary_key] = row
        return self._identity_map[primary_key]

    @abstractmethod
    def _primary_key(self, aggregate: TAggregate) -> uuid.UUID: ...

    @abstractmethod
    def _row_primary_key(self, row: TModel) -> uuid.UUID: ...

    @abstractmethod
    def _to_domain(self, row: TModel) -> TAggregate: ...

    @abstractmethod
    def _apply(self, aggregate: TAggregate, row: TModel) -> None: ...
