"""
Implementação in-memory do repositório de tarefas.

Armazena tarefas em memória usando um dicionário.
Útil para testes e desenvolvimento local.
"""

from app.domain.sample_context.entities.task import Task
from app.domain.sample_context.repositories.task_repository import TaskRepository
from app.domain.sample_context.value_objects import TaskId
from app.domain.sample_context.value_objects.task_status import StatusValue


class InMemoryTaskRepository(TaskRepository):
    """
    Implementação do TaskRepository que armazena em memória.

    Usa um dicionário para armazenar as tarefas.
    Os dados são perdidos quando a aplicação é encerrada.
    """

    def __init__(self) -> None:
        self._tasks: dict[str, Task] = {}

    def save(self, task: Task) -> None:
        """Salva ou atualiza uma tarefa."""
        self._tasks[task.id.value] = task

    def find_by_id(self, task_id: TaskId) -> Task | None:
        """Busca uma tarefa pelo ID."""
        return self._tasks.get(task_id.value)

    def find_all(self) -> list[Task]:
        """Retorna todas as tarefas."""
        return list(self._tasks.values())

    def find_pending(self) -> list[Task]:
        """Retorna tarefas pendentes ou em progresso."""
        return [
            task
            for task in self._tasks.values()
            if task.status.status in (StatusValue.PENDING, StatusValue.IN_PROGRESS)
        ]

    def find_completed(self) -> list[Task]:
        """Retorna tarefas concluídas."""
        return [
            task
            for task in self._tasks.values()
            if task.status.status == StatusValue.COMPLETED
        ]

    def delete(self, task_id: TaskId) -> bool:
        """Remove uma tarefa pelo ID."""
        if task_id.value in self._tasks:
            del self._tasks[task_id.value]
            return True
        return False

    def exists(self, task_id: TaskId) -> bool:
        """Verifica se uma tarefa existe."""
        return task_id.value in self._tasks

    def count(self) -> int:
        """Retorna o total de tarefas."""
        return len(self._tasks)

    def clear(self) -> None:
        """Remove todas as tarefas (útil para testes)."""
        self._tasks.clear()
