from dataclasses import dataclass
from typing import ClassVar

from app.domain.seedwork import ValueObject
from app.domain.task_management.exceptions import InvalidTaskDescription


@dataclass(frozen=True, slots=True)
class TaskDescription(ValueObject):
    MAX_LENGTH: ClassVar[int] = 2000

    value: str = ""

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if len(normalized) > self.MAX_LENGTH:
            raise InvalidTaskDescription(
                f"A descrição deve ter no máximo {self.MAX_LENGTH} caracteres."
            )
        object.__setattr__(self, "value", normalized)

    @property
    def is_empty(self) -> bool:
        return not self.value

    def __str__(self) -> str:
        return self.value
