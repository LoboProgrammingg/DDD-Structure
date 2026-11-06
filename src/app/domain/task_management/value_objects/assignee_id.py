from dataclasses import dataclass
from typing import ClassVar

from app.domain.seedwork import ValueObject
from app.domain.task_management.exceptions import InvalidAssignee


@dataclass(frozen=True, slots=True)
class AssigneeId(ValueObject):
    """Identidade de um responsável que pertence a outro contexto (Identity).

    A tarefa guarda apenas o identificador, nunca o objeto (Vernon, regra 3):
    assim um único commit jamais altera dois agregados.
    """

    MAX_LENGTH: ClassVar[int] = 64

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise InvalidAssignee("O responsável deve ser informado.")
        if len(normalized) > self.MAX_LENGTH:
            raise InvalidAssignee(
                f"O identificador do responsável deve ter no máximo {self.MAX_LENGTH} caracteres."
            )
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value
