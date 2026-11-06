from dataclasses import dataclass

from app.domain.notification.exceptions import InvalidRecipient
from app.domain.seedwork import ValueObject


@dataclass(frozen=True, slots=True)
class Recipient(ValueObject):
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if not normalized:
            raise InvalidRecipient("O destinatário deve ser informado.")
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value
