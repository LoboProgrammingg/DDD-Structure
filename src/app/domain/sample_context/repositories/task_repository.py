"""
Interface do repositório de tarefas.

Define o contrato para persistência de tarefas.
Esta é a interface (port) que será implementada na camada de infraestrutura.
"""

from abc import ABC, abstractmethod

from app.domain.sample_context.entities.task import Task
from app.domain.sample_context.value_objects.task_id import TaskId


class TaskRepository(ABC):
    """
    Interface para o repositório de tarefas.

    Define operações de persistência para a entidade Task.
    Implementações concretas ficam na camada de infraestrutura.
    """

    @abstractmethod
    def save(self, task: Task) -> None:
        """
        Persiste uma tarefa (cria ou atualiza).

        Args:
            task: Tarefa a ser salva
        """

    @abstractmethod
    def find_by_id(self, task_id: TaskId) -> Task | None:
        """
        Busca uma tarefa pelo ID.

        Args:
            task_id: ID da tarefa

        Returns:
            Task se encontrada, None caso contrário
        """

    @abstractmethod
    def find_all(self) -> list[Task]:
        """
        Retorna todas as tarefas.

        Returns:
            Lista de todas as tarefas
        """

    @abstractmethod
    def find_pending(self) -> list[Task]:
        """
        Retorna apenas tarefas pendentes.

        Returns:
            Lista de tarefas com status pending
        """

    @abstractmethod
    def find_completed(self) -> list[Task]:
        """
        Retorna apenas tarefas concluídas.

        Returns:
            Lista de tarefas com status completed
        """

    @abstractmethod
    def delete(self, task_id: TaskId) -> bool:
        """
        Remove uma tarefa pelo ID.

        Args:
            task_id: ID da tarefa a ser removida

        Returns:
            True se removida, False se não existia
        """

    @abstractmethod
    def exists(self, task_id: TaskId) -> bool:
        """
        Verifica se uma tarefa existe.

        Args:
            task_id: ID da tarefa

        Returns:
            True se existe, False caso contrário
        """

    @abstractmethod
    def count(self) -> int:
        """
        Retorna o total de tarefas.

        Returns:
            Número total de tarefas
        """
