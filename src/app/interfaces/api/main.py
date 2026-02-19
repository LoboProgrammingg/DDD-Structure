"""
FastAPI Application - Interface REST API.

Esta é a camada de interface HTTP da aplicação.
Controllers apenas:
- Recebem requests
- Validam entrada (via Pydantic)
- Chamam use cases
- Retornam responses

NENHUMA lógica de negócio aqui. Tudo vai para os Use Cases.
"""

from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.application.common.errors import NotFoundError
from app.application.sample_context.use_cases.complete_task import CompleteTaskInput
from app.application.sample_context.use_cases.create_task import CreateTaskInput
from app.application.sample_context.use_cases.list_tasks import ListTasksInput, TaskFilter
from app.application.sample_context.use_cases.rename_task import RenameTaskInput
from app.bootstrap import get_container
from app.domain.common.exceptions import DomainException, ValidationException
from app.infrastructure.config import get_settings
from app.infrastructure.logging import get_logger


logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifecycle manager da aplicação."""
    logger.info("Iniciando API...")
    yield
    logger.info("Encerrando API...")


def create_app() -> FastAPI:
    """
    Factory function para criar a aplicação FastAPI.

    Separado para facilitar testes.
    """
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="API REST para o DDD Enterprise Template",
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
        lifespan=lifespan,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Inclui routers
    app.include_router(health_router, tags=["Health"])
    app.include_router(
        tasks_router,
        prefix=f"{settings.api_prefix}/tasks",
        tags=["Tasks"],
    )

    return app


# =============================================================================
# Health Check Router
# =============================================================================
from fastapi import APIRouter

health_router = APIRouter()


class HealthResponse(BaseModel):
    """Response do health check."""

    status: str = "ok"
    environment: str
    version: str


@health_router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Endpoint de health check."""
    return HealthResponse(
        status="ok",
        environment=settings.environment.value,
        version=settings.app_version,
    )


# =============================================================================
# Tasks Router
# =============================================================================
tasks_router = APIRouter()


# Request/Response Models (DTOs externos)
class CreateTaskRequest(BaseModel):
    """Request para criar uma tarefa."""

    title: str = Field(..., min_length=1, max_length=200)
    priority: str = Field(default="medium")
    description: str = Field(default="", max_length=2000)


class TaskResponse(BaseModel):
    """Response representando uma tarefa."""

    id: str
    title: str
    description: str
    priority: str
    status: str
    created_at: str
    completed_at: str | None = None


class TaskListResponse(BaseModel):
    """Response para listagem de tarefas."""

    tasks: list[TaskResponse]
    total: int


class RenameTaskRequest(BaseModel):
    """Request para renomear uma tarefa."""

    new_title: str = Field(..., min_length=1, max_length=200)


class MessageResponse(BaseModel):
    """Response genérica com mensagem."""

    message: str
    data: dict[str, Any] | None = None


# Endpoints
@tasks_router.post(
    "",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(request: CreateTaskRequest) -> TaskResponse:
    """Cria uma nova tarefa."""
    container = get_container()

    try:
        output = container.create_task_use_case.execute(
            CreateTaskInput(
                title=request.title,
                priority=request.priority,
                description=request.description,
            )
        )

        return TaskResponse(
            id=output.id,
            title=output.title,
            description=request.description,
            priority=output.priority,
            status=output.status,
            created_at=output.created_at,
        )

    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": e.message, "field": e.field},
        )
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "code": e.code},
        )


@tasks_router.get("", response_model=TaskListResponse)
async def list_tasks(
    filter_status: str = "all",
) -> TaskListResponse:
    """Lista todas as tarefas com filtro opcional."""
    container = get_container()

    try:
        task_filter = TaskFilter(filter_status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Filtro inválido. Use: all, pending, completed"},
        )

    output = container.list_tasks_use_case.execute(
        ListTasksInput(filter=task_filter)
    )

    return TaskListResponse(
        tasks=[
            TaskResponse(
                id=task.id,
                title=task.title,
                description=task.description,
                priority=task.priority,
                status=task.status,
                created_at=task.created_at,
                completed_at=task.completed_at,
            )
            for task in output.tasks
        ],
        total=output.total,
    )


@tasks_router.post("/{task_id}/complete", response_model=MessageResponse)
async def complete_task(task_id: str) -> MessageResponse:
    """Marca uma tarefa como concluída."""
    container = get_container()

    try:
        output = container.complete_task_use_case.execute(
            CompleteTaskInput(task_id=task_id)
        )

        return MessageResponse(
            message="Tarefa concluída com sucesso",
            data={
                "id": output.id,
                "title": output.title,
                "status": output.status,
                "completed_at": output.completed_at,
            },
        )

    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": e.message},
        )
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "code": e.code},
        )


@tasks_router.patch("/{task_id}/rename", response_model=MessageResponse)
async def rename_task(task_id: str, request: RenameTaskRequest) -> MessageResponse:
    """Renomeia uma tarefa."""
    container = get_container()

    try:
        output = container.rename_task_use_case.execute(
            RenameTaskInput(task_id=task_id, new_title=request.new_title)
        )

        return MessageResponse(
            message="Tarefa renomeada com sucesso",
            data={
                "id": output.id,
                "old_title": output.old_title,
                "new_title": output.new_title,
            },
        )

    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"message": e.message},
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"message": e.message, "field": e.field},
        )
    except DomainException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": e.message, "code": e.code},
        )


# Cria a aplicação
app = create_app()
