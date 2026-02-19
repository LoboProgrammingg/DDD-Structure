"""TaskTitle - Título de uma tarefa."""

from app.domain.common.validators import Validator
from app.domain.common.value_object import ValueObject


class TaskTitle(ValueObject):
    """
    Value Object que representa o título de uma tarefa.

    Regras:
    - Não pode ser vazio
    - Máximo de 200 caracteres
    - Espaços extras são removidos (trim)
    """

    __slots__ = ("_value",)

    MAX_LENGTH = 200

    def __init__(self, value: str) -> None:
        """
        Cria um TaskTitle.

        Args:
            value: Título da tarefa

        Raises:
            ValidationException: Se violar as regras de validação
        """
        validated = Validator.not_empty(value, "Título")
        validated = Validator.max_length(validated, self.MAX_LENGTH, "Título")
        object.__setattr__(self, "_value", validated)

    @property
    def value(self) -> str:
        """Retorna o título."""
        return self._value

    def __str__(self) -> str:
        return self._value
