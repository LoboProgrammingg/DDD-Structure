from dataclasses import dataclass
from typing import ClassVar

from app.domain.notification.exceptions import InvalidMessage
from app.domain.seedwork import ValueObject


@dataclass(frozen=True, slots=True)
class Message(ValueObject):
    MAX_LENGTH: ClassVar[int] = 500

    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise InvalidMessage("A mensagem não pode ser vazia.")
        if len(normalized) > self.MAX_LENGTH:
            raise InvalidMessage(f"A mensagem deve ter no máximo {self.MAX_LENGTH} caracteres.")
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value
