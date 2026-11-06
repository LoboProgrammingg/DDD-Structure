from dataclasses import dataclass
from datetime import date, datetime

from app.domain.seedwork import ValueObject


@dataclass(frozen=True, slots=True)
class DueDate(ValueObject):
    value: date

    def is_before(self, moment: datetime) -> bool:
        return self.value < moment.date()

    def __str__(self) -> str:
        return self.value.isoformat()
