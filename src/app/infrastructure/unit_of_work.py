"""Unit of Work sobre SQLAlchemy.

Uma sessão por Unit of Work. O conflito de versão detectado pelo
``version_id_col`` (UPDATE ... WHERE version = :lida) vira
``ConcurrencyConflictError``, um erro que a aplicação sabe tratar.
"""

from abc import abstractmethod
from collections.abc import Sequence
from types import TracebackType
from typing import Any, Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm.exc import StaleDataError

from app.application.notification.ports import NotificationUnitOfWork
from app.application.shared import ConcurrencyConflictError, EventPublisher, UnitOfWork
from app.application.task_management.ports import TaskManagementUnitOfWork
from app.domain.seedwork import DomainEvent
from app.infrastructure.repositories import (
    SqlAlchemyNotificationRepository,
    SqlAlchemyRepository,
    SqlAlchemyTaskRepository,
)

type SessionFactory = async_sessionmaker[AsyncSession]


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: SessionFactory, publisher: EventPublisher) -> None:
        super().__init__(publisher)
        self._session_factory = session_factory

    async def __aenter__(self) -> Self:
        self._session = self._session_factory()
        self._bind_repositories(self._session)
        return await super().__aenter__()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        try:
            await super().__aexit__(exc_type, exc, traceback)
        finally:
            await self._session.close()

    async def rollback(self) -> None:
        await self._session.rollback()

    async def _commit(self) -> None:
        try:
            for repository in self._repositories():
                repository.sync()
            await self._session.commit()
        except StaleDataError as error:
            await self._session.rollback()
            raise ConcurrencyConflictError from error

    def _collect_events(self) -> list[DomainEvent]:
        return [event for repository in self._repositories() for event in repository.pull_events()]

    @abstractmethod
    def _bind_repositories(self, session: AsyncSession) -> None: ...

    @abstractmethod
    def _repositories(self) -> Sequence[SqlAlchemyRepository[Any, Any]]: ...


class SqlAlchemyTaskManagementUnitOfWork(SqlAlchemyUnitOfWork, TaskManagementUnitOfWork):
    def _bind_repositories(self, session: AsyncSession) -> None:
        self._task_repository = SqlAlchemyTaskRepository(session)
        self.tasks = self._task_repository

    def _repositories(self) -> Sequence[SqlAlchemyRepository[Any, Any]]:
        return (self._task_repository,)


class SqlAlchemyNotificationUnitOfWork(SqlAlchemyUnitOfWork, NotificationUnitOfWork):
    def _bind_repositories(self, session: AsyncSession) -> None:
        self._notification_repository = SqlAlchemyNotificationRepository(session)
        self.notifications = self._notification_repository

    def _repositories(self) -> Sequence[SqlAlchemyRepository[Any, Any]]:
        return (self._notification_repository,)
