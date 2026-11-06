"""Factory da aplicação FastAPI.

uvicorn app.interfaces.api:create_app --factory
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.bootstrap import Container, build_container
from app.infrastructure.config import LogFormat
from app.infrastructure.logging import configure_logging
from app.interfaces.api.error_handlers import register_error_handlers
from app.interfaces.api.middlewares import RequestIdMiddleware
from app.interfaces.api.v1.routes import health, tasks


def create_app(container: Container | None = None) -> FastAPI:
    container = container or build_container()
    settings = container.settings
    configure_logging(settings.log_level, json_format=settings.log_format is LogFormat.JSON)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        yield
        await container.dispose()

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="Referência de Domain-Driven Design com FastAPI e SQLAlchemy.",
        lifespan=lifespan,
    )
    app.state.container = container

    app.add_middleware(RequestIdMiddleware)
    if settings.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.cors_origins,
            allow_methods=["GET", "POST"],
            allow_headers=["Content-Type", "X-Request-ID"],
        )

    register_error_handlers(app)
    app.include_router(health.router)
    app.include_router(tasks.router, prefix="/api/v1")
    return app
