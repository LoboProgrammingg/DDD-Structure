from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.bootstrap import Container
from app.infrastructure.config import Environment, Settings
from app.infrastructure.database import Base
from app.interfaces.api import create_app


@pytest.fixture
async def app(database_url: str) -> AsyncIterator[FastAPI]:
    settings = Settings(
        database_url=database_url, environment=Environment.TESTING, work_in_progress_limit=1
    )
    container = Container(settings)
    async with container.engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    yield create_app(container)
    async with container.engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
    await container.dispose()


@pytest.fixture
async def client(app: FastAPI) -> AsyncIterator[AsyncClient]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
