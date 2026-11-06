from dataclasses import dataclass
from uuid import UUID

from app.domain.seedwork import ValueObject
from app.domain.task_management.exceptions import InvalidTaskId


@dataclass(frozen=True, slots=True)
class TaskId(ValueObject):
    """Identidade tipada: impede passar o id de outro agregado no lugar de uma Task."""

    value: UUID

    @classmethod
    def from_string(cls, raw: str) -> "TaskId":
        try:
            return cls(UUID(raw))
        except (ValueError, AttributeError, TypeError):
            raise InvalidTaskId(f"'{raw}' não é um identificador de tarefa válido.") from None

    def __str__(self) -> str:
        return str(self.value)
