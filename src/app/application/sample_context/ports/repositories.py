"""
Port para repositório de tarefas.

Este é o LOCAL CORRETO para interfaces de repositório em Clean Architecture.
Repositories são PORTS da camada de aplicação - não pertencem ao domínio.

O domínio define ENTIDADES e REGRAS DE NEGÓCIO.
A aplicação define PORTS (interfaces) para serviços externos.
A infraestrutura IMPLEMENTA esses ports.

Regra de dependência:
    Domain ← Application ← Infrastructure
    (setas indicam direção das dependências)
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from app.domain.sample_context.entities.task import Task
    from app.domain.sample_context.value_objects.task_id import TaskId


class TaskRepository(ABC):
    """
    Interface (Port) para o repositório de tarefas.

    Define operações de persistência para a entidade Task.
    Implementações concretas (Adapters) ficam na camada de infraestrutura.

    Por que esta interface está na Application e não no Domain?
    - O domínio não deve conhecer conceitos de persistência
    - Repositories são portas de saída (driven ports) da aplicação
    - Isso permite que o domínio seja 100% puro e focado em regras de negócio
    """

    @abstractmethod
    def save(self, task: "Task") -> None:
        """
        Persiste uma tarefa (cria ou atualiza).

        Args:
            task: Tarefa a ser salva
        """

    @abstractmethod
    def find_by_id(self, task_id: "TaskId") -> "Task | None":
        """
        Busca uma tarefa pelo ID.

        Args:
            task_id: ID da tarefa

        Returns:
            Task se encontrada, None caso contrário
        """

    @abstractmethod
    def find_all(self) -> "list[Task]":
        """
        Retorna todas as tarefas.

        Returns:
            Lista de todas as tarefas
        """

    @abstractmethod
    def find_pending(self) -> "list[Task]":
        """
        Retorna apenas tarefas pendentes ou em progresso.

        Returns:
            Lista de tarefas abertas
        """

    @abstractmethod
    def find_completed(self) -> "list[Task]":
        """
        Retorna apenas tarefas concluídas.

        Returns:
            Lista de tarefas com status completed
        """

    @abstractmethod
    def delete(self, task_id: "TaskId") -> bool:
        """
        Remove uma tarefa pelo ID.

        Args:
            task_id: ID da tarefa a ser removida

        Returns:
            True se removida, False se não existia
        """

    @abstractmethod
    def exists(self, task_id: "TaskId") -> bool:
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


# Alias para compatibilidade e clareza
TaskRepositoryPort = TaskRepository

__all__ = ["TaskRepository", "TaskRepositoryPort"]
