"""TaskStatus - Status de uma tarefa."""

from enum import Enum

from app.domain.common.value_object import ValueObject
from app.domain.common.exceptions import ValidationException


class StatusValue(Enum):
    """Valores de status disponíveis."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskStatus(ValueObject):
    """
    Value Object que representa o status de uma tarefa.

    Estados possíveis: pending, in_progress, completed, cancelled
    """

    __slots__ = ("_status",)

    def __init__(self, status: StatusValue | str) -> None:
        """
        Cria um TaskStatus.

        Args:
            status: Status (StatusValue ou string)

        Raises:
            ValidationException: Se o status for inválido
        """
        if isinstance(status, str):
            try:
                status = StatusValue(status.lower())
            except ValueError:
                valid = [s.value for s in StatusValue]
                raise ValidationException(
                    f"Status inválido. Valores válidos: {valid}",
                    field="Status",
                )
        object.__setattr__(self, "_status", status)

    @property
    def status(self) -> StatusValue:
        """Retorna o valor do status."""
        return self._status

    @property
    def value(self) -> str:
        """Retorna o valor string do status."""
        return self._status.value

    @property
    def is_open(self) -> bool:
        """Retorna True se a tarefa ainda está aberta (não finalizada)."""
        return self._status in (StatusValue.PENDING, StatusValue.IN_PROGRESS)

    @property
    def is_completed(self) -> bool:
        """Retorna True se a tarefa foi concluída."""
        return self._status == StatusValue.COMPLETED

    @property
    def is_cancelled(self) -> bool:
        """Retorna True se a tarefa foi cancelada."""
        return self._status == StatusValue.CANCELLED

    def __str__(self) -> str:
        return self._status.value

    @classmethod
    def pending(cls) -> "TaskStatus":
        """Factory method para status pendente."""
        return cls(StatusValue.PENDING)

    @classmethod
    def in_progress(cls) -> "TaskStatus":
        """Factory method para status em progresso."""
        return cls(StatusValue.IN_PROGRESS)

    @classmethod
    def completed(cls) -> "TaskStatus":
        """Factory method para status concluído."""
        return cls(StatusValue.COMPLETED)

    @classmethod
    def cancelled(cls) -> "TaskStatus":
        """Factory method para status cancelado."""
        return cls(StatusValue.CANCELLED)
