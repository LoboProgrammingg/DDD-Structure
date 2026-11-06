from collections.abc import AsyncIterator, Callable

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.infrastructure.database import Base, create_engine, create_session_factory
from app.infrastructure.unit_of_work import SqlAlchemyTaskManagementUnitOfWork
from tests.fakes import RecordingPublisher


@pytest.fixture
async def engine(database_url: str) -> AsyncIterator[AsyncEngine]:
    engine = create_engine(database_url)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
def session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    return create_session_factory(engine)


@pytest.fixture
def task_uow(
    session_factory: async_sessionmaker[AsyncSession], publisher: RecordingPublisher
) -> Callable[[], SqlAlchemyTaskManagementUnitOfWork]:
    return lambda: SqlAlchemyTaskManagementUnitOfWork(session_factory, publisher)
