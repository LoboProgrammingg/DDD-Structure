"""
Use Case: Criar Tarefa.

Cria uma nova tarefa no sistema.
"""

from dataclasses import dataclass

from app.application.common.use_case import UseCase
from app.application.sample_context.ports import Clock, IdGenerator, TaskRepositoryPort
from app.domain.sample_context.entities.task import Task
from app.domain.sample_context.value_objects import (
    TaskDescription,
    TaskId,
    TaskPriority,
    TaskTitle,
)


@dataclass(frozen=True)
class CreateTaskInput:
    """Dados de entrada para criar uma tarefa."""

    title: str
    priority: str = "medium"
    description: str = ""


@dataclass(frozen=True)
class CreateTaskOutput:
    """Dados de saída após criar uma tarefa."""

    id: str
    title: str
    priority: str
    status: str
    created_at: str


class CreateTaskUseCase(UseCase[CreateTaskInput, CreateTaskOutput]):
    """
    Use case para criar uma nova tarefa.

    Recebe dados de entrada, cria a entidade Task e persiste.
    """

    def __init__(
        self,
        repository: TaskRepositoryPort,
        clock: Clock,
        id_generator: IdGenerator,
    ) -> None:
        self._repository = repository
        self._clock = clock
        self._id_generator = id_generator

    def execute(self, input: CreateTaskInput) -> CreateTaskOutput:
        """
        Executa a criação da tarefa.

        Args:
            input: Dados da tarefa a ser criada

        Returns:
            Output com os dados da tarefa criada
        """
        task_id = TaskId(self._id_generator.generate())
        title = TaskTitle(input.title)
        priority = TaskPriority(input.priority)
        description = TaskDescription(input.description)
        created_at = self._clock.now()

        task = Task.create(
            id=task_id,
            title=title,
            priority=priority,
            created_at=created_at,
            description=description,
        )

        self._repository.save(task)

        return CreateTaskOutput(
            id=task.id.value,
            title=task.title.value,
            priority=task.priority.value,
            status=task.status.value,
            created_at=task.created_at.isoformat(),
        )
