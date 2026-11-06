"""Contrato do repositório de Task.

O repositório pertence ao domínio (Evans): ele oferece a ilusão de uma coleção
em memória de agregados, falando a Linguagem Ubíqua. A implementação concreta
fica na infraestrutura; o domínio não conhece banco, ORM nem transação.
"""

from abc import ABC, abstractmethod

from app.domain.task_management.aggregates import Task
from app.domain.task_management.value_objects import AssigneeId, TaskId


class TaskRepository(ABC):
    @abstractmethod
    def next_identity(self) -> TaskId: ...

    @abstractmethod
    async def add(self, task: Task) -> None: ...

    @abstractmethod
    async def get(self, task_id: TaskId) -> Task | None: ...

    @abstractmethod
    async def list_by_assignee(self, assignee_id: AssigneeId) -> list[Task]: ...
