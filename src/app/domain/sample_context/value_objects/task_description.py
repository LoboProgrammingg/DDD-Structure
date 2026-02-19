"""TaskDescription - Descrição de uma tarefa."""

from app.domain.common.validators import Validator
from app.domain.common.value_object import ValueObject


class TaskDescription(ValueObject):
    """
    Value Object que representa a descrição de uma tarefa.

    Regras:
    - Pode ser vazia (opcional)
    - Máximo de 2000 caracteres
    """

    __slots__ = ("_value",)

    MAX_LENGTH = 2000

    def __init__(self, value: str = "") -> None:
        """
        Cria uma TaskDescription.

        Args:
            value: Descrição da tarefa (pode ser vazia)

        Raises:
            ValidationException: Se exceder o tamanho máximo
        """
        stripped = value.strip()
        if stripped:
            Validator.max_length(stripped, self.MAX_LENGTH, "Descrição")
        object.__setattr__(self, "_value", stripped)

    @property
    def value(self) -> str:
        """Retorna a descrição."""
        return self._value

    @property
    def is_empty(self) -> bool:
        """Retorna True se a descrição estiver vazia."""
        return not self._value

    def __str__(self) -> str:
        return self._value

    @classmethod
    def empty(cls) -> "TaskDescription":
        """Factory method para criar descrição vazia."""
        return cls("")
