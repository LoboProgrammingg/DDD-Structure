from dataclasses import dataclass
from typing import ClassVar

from app.domain.seedwork import ValueObject
from app.domain.task_management.exceptions import InvalidTaskTitle


@dataclass(frozen=True, slots=True)
class TaskTitle(ValueObject):
    MAX_LENGTH: ClassVar[int] = 120

    value: str

    def __post_init__(self) -> None:
        normalized = " ".join(self.value.split())
        if not normalized:
            raise InvalidTaskTitle("O título da tarefa não pode ser vazio.")
        if len(normalized) > self.MAX_LENGTH:
            raise InvalidTaskTitle(
                f"O título da tarefa deve ter no máximo {self.MAX_LENGTH} caracteres."
            )
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value
