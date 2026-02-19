"""TaskPriority - Prioridade de uma tarefa."""

from enum import Enum

from app.domain.common.exceptions import ValidationException
from app.domain.common.value_object import ValueObject


class PriorityLevel(Enum):
    """Níveis de prioridade disponíveis."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskPriority(ValueObject):
    """
    Value Object que representa a prioridade de uma tarefa.

    Valores válidos: low, medium, high, urgent
    """

    __slots__ = ("_level",)

    def __init__(self, level: PriorityLevel | str) -> None:
        """
        Cria uma TaskPriority.

        Args:
            level: Nível de prioridade (PriorityLevel ou string)

        Raises:
            ValidationException: Se o nível for inválido
        """
        if isinstance(level, str):
            try:
                level = PriorityLevel(level.lower())
            except ValueError:
                valid = [p.value for p in PriorityLevel]
                raise ValidationException(
                    f"Prioridade inválida. Valores válidos: {valid}",
                    field="Prioridade",
                ) from None
        object.__setattr__(self, "_level", level)

    @property
    def level(self) -> PriorityLevel:
        """Retorna o nível de prioridade."""
        return self._level

    @property
    def value(self) -> str:
        """Retorna o valor string da prioridade."""
        return self._level.value

    @property
    def is_high_priority(self) -> bool:
        """Retorna True se for alta prioridade ou urgente."""
        return self._level in (PriorityLevel.HIGH, PriorityLevel.URGENT)

    def __str__(self) -> str:
        return self._level.value

    @classmethod
    def low(cls) -> "TaskPriority":
        """Factory method para prioridade baixa."""
        return cls(PriorityLevel.LOW)

    @classmethod
    def medium(cls) -> "TaskPriority":
        """Factory method para prioridade média."""
        return cls(PriorityLevel.MEDIUM)

    @classmethod
    def high(cls) -> "TaskPriority":
        """Factory method para prioridade alta."""
        return cls(PriorityLevel.HIGH)

    @classmethod
    def urgent(cls) -> "TaskPriority":
        """Factory method para prioridade urgente."""
        return cls(PriorityLevel.URGENT)
