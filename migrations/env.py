"""Ambiente do Alembic: usa a mesma configuração e os mesmos modelos da aplicação."""

import asyncio
from logging.config import fileConfig
from typing import Literal

from alembic import context
from alembic.autogenerate.api import AutogenContext
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from app.infrastructure.config import get_settings
from app.infrastructure.database import (
    Base,
    models,  # noqa: F401  (registra as tabelas)
)
from app.infrastructure.database.types import UTCDateTime

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata
database_url = get_settings().database_url


def render_item(type_: str, obj: object, _: AutogenContext) -> str | Literal[False]:
    """Tipos customizados viram o tipo nativo equivalente nas migrações."""
    if type_ == "type" and isinstance(obj, UTCDateTime):
        return "sa.DateTime(timezone=True)"
    return False


def run_migrations_offline() -> None:
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
        render_item=render_item,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,
        render_item=render_item,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    engine = create_async_engine(database_url)
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_async_migrations())
