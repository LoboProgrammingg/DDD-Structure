"""TaskId - Identificador único de uma tarefa."""

from app.domain.common.value_object import ValueObject
from app.domain.common.validators import Validator


class TaskId(ValueObject):
    """
    Value Object que representa o identificador único de uma tarefa.

    Imutável e auto-validante.
    """

    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        """
        Cria um TaskId.

        Args:
            value: String não vazia representando o ID

        Raises:
            ValidationException: Se o valor for vazio
        """
        validated = Validator.not_empty(value, "TaskId")
        object.__setattr__(self, "_value", validated)

    @property
    def value(self) -> str:
        """Retorna o valor do ID."""
        return self._value

    def __str__(self) -> str:
        return self._value
