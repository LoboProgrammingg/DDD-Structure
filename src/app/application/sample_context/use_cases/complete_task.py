"""
Use Case: Completar Tarefa.

Marca uma tarefa existente como concluída.
"""

from dataclasses import dataclass

from app.application.common.errors import NotFoundError
from app.application.common.use_case import UseCase
from app.application.sample_context.ports import Clock, TaskRepositoryPort
from app.domain.sample_context.value_objects import TaskId


@dataclass(frozen=True)
class CompleteTaskInput:
    """Dados de entrada para completar uma tarefa."""

    task_id: str


@dataclass(frozen=True)
class CompleteTaskOutput:
    """Dados de saída após completar uma tarefa."""

    id: str
    title: str
    status: str
    completed_at: str


class CompleteTaskUseCase(UseCase[CompleteTaskInput, CompleteTaskOutput]):
    """
    Use case para marcar uma tarefa como concluída.

    Busca a tarefa pelo ID e executa a operação de conclusão.
    """

    def __init__(
        self,
        repository: TaskRepositoryPort,
        clock: Clock,
    ) -> None:
        self._repository = repository
        self._clock = clock

    def execute(self, input: CompleteTaskInput) -> CompleteTaskOutput:
        """
        Executa a conclusão da tarefa.

        Args:
            input: ID da tarefa a ser concluída

        Returns:
            Output com os dados da tarefa concluída

        Raises:
            NotFoundError: Se a tarefa não existir
        """
        task_id = TaskId(input.task_id)
        task = self._repository.find_by_id(task_id)

        if task is None:
            raise NotFoundError("Task", input.task_id)

        completed_at = self._clock.now()
        task.complete(completed_at)

        self._repository.save(task)

        return CompleteTaskOutput(
            id=task.id.value,
            title=task.title.value,
            status=task.status.value,
            completed_at=completed_at.isoformat(),
        )
