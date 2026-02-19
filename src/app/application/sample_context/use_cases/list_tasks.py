"""
Use Case: Listar Tarefas.

Lista todas as tarefas do sistema com filtros opcionais.
"""

from dataclasses import dataclass
from enum import Enum

from app.application.common.use_case import UseCase
from app.application.sample_context.ports import TaskRepositoryPort


class TaskFilter(Enum):
    """Filtros disponíveis para listagem."""

    ALL = "all"
    PENDING = "pending"
    COMPLETED = "completed"


@dataclass(frozen=True)
class ListTasksInput:
    """Dados de entrada para listar tarefas."""

    filter: TaskFilter = TaskFilter.ALL


@dataclass(frozen=True)
class TaskListItem:
    """Representação de uma tarefa na listagem."""

    id: str
    title: str
    description: str
    priority: str
    status: str
    created_at: str
    completed_at: str | None


@dataclass(frozen=True)
class ListTasksOutput:
    """Dados de saída da listagem de tarefas."""

    tasks: list[TaskListItem]
    total: int


class ListTasksUseCase(UseCase[ListTasksInput, ListTasksOutput]):
    """
    Use case para listar tarefas.

    Retorna lista de tarefas com filtro opcional.
    """

    def __init__(self, repository: TaskRepositoryPort) -> None:
        self._repository = repository

    def execute(self, input: ListTasksInput) -> ListTasksOutput:
        """
        Executa a listagem de tarefas.

        Args:
            input: Filtro a ser aplicado

        Returns:
            Output com lista de tarefas
        """
        match input.filter:
            case TaskFilter.PENDING:
                tasks = self._repository.find_pending()
            case TaskFilter.COMPLETED:
                tasks = self._repository.find_completed()
            case _:
                tasks = self._repository.find_all()

        items = [
            TaskListItem(
                id=task.id.value,
                title=task.title.value,
                description=task.description.value,
                priority=task.priority.value,
                status=task.status.value,
                created_at=task.created_at.isoformat(),
                completed_at=task.completed_at.isoformat() if task.completed_at else None,
            )
            for task in tasks
        ]

        return ListTasksOutput(
            tasks=items,
            total=len(items),
        )
