"""Lado de leitura (CQRS-lite).

Consultas não precisam reconstituir agregados nem respeitar suas fronteiras:
leem projeções otimizadas e devolvem DTOs prontos para a interface.
"""

from abc import ABC, abstractmethod

from app.application.task_management.dtos import TaskDTO, TaskPageDTO
from app.domain.task_management.value_objects import TaskStatus


class TaskReadModel(ABC):
    @abstractmethod
    async def get(self, task_id: str) -> TaskDTO | None: ...

    @abstractmethod
    async def list(
        self,
        *,
        status: TaskStatus | None,
        assignee_id: str | None,
        limit: int,
        offset: int,
    ) -> TaskPageDTO: ...
