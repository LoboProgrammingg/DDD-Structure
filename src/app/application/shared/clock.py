from abc import ABC, abstractmethod
from datetime import datetime


class Clock(ABC):
    """Fonte de tempo injetável: casos de uso nunca chamam ``datetime.now()`` direto."""

    @abstractmethod
    def now(self) -> datetime: ...
