from dataclasses import dataclass
from uuid import UUID

from app.domain.seedwork import ValueObject


@dataclass(frozen=True, slots=True)
class NotificationId(ValueObject):
    value: UUID

    def __str__(self) -> str:
        return str(self.value)
