"""Unit of Work: fronteira transacional de um caso de uso.

    async with uow_factory() as uow:
        task = await uow.tasks.get(task_id)
        task.complete(clock.now())
        await uow.commit()

``commit`` grava todos os agregados alterados de forma atômica e, só depois
do commit bem-sucedido, publica os Domain Events registrados por eles.
Sair do bloco sem ``commit`` (ou com exceção) desfaz tudo e descarta os eventos.
"""

from abc import ABC, abstractmethod
from types import TracebackType
from typing import Self

from app.application.shared.event_publisher import EventPublisher
from app.domain.seedwork import DomainEvent


class UnitOfWork(ABC):
    def __init__(self, publisher: EventPublisher) -> None:
        self._publisher = publisher

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.rollback()

    async def commit(self) -> None:
        await self._commit()
        await self._publisher.publish(self._collect_events())

    @abstractmethod
    async def rollback(self) -> None: ...

    @abstractmethod
    async def _commit(self) -> None: ...

    @abstractmethod
    def _collect_events(self) -> list[DomainEvent]: ...
