"""
Base class para Value Objects do domínio.

Um Value Object é um objeto imutável que é definido pelos seus atributos.
Dois value objects são iguais se todos os seus atributos são iguais.
"""

from abc import ABC
from typing import Any


class ValueObject(ABC):
    """
    Classe base para todos os Value Objects do domínio.

    Características de um Value Object:
    - Imutável (não pode ser alterado após criação)
    - Igualdade baseada em atributos
    - Sem identidade própria
    - Auto-validante (validação no construtor)

    Para criar um Value Object, herde desta classe e defina os atributos
    usando __slots__ para garantir imutabilidade e eficiência.

    Exemplo de uso:
        >>> class Email(ValueObject):
        ...     __slots__ = ("_value",)
        ...
        ...     def __init__(self, value: str) -> None:
        ...         if "@" not in value:
        ...             raise ValueError("Email inválido")
        ...         object.__setattr__(self, "_value", value)
        ...
        ...     @property
        ...     def value(self) -> str:
        ...         return self._value
    """

    __slots__ = ()

    def __setattr__(self, name: str, value: Any) -> None:
        """Impede modificação de atributos após criação."""
        if hasattr(self, name):
            raise AttributeError(f"Value Object é imutável. Não é possível alterar '{name}'.")
        object.__setattr__(self, name, value)

    def __delattr__(self, name: str) -> None:
        """Impede remoção de atributos."""
        raise AttributeError("Value Object é imutável. Não é possível remover atributos.")

    def __eq__(self, other: object) -> bool:
        """Value Objects são iguais se todos os atributos são iguais."""
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self._get_equality_components() == other._get_equality_components()

    def __hash__(self) -> int:
        """Hash baseado nos componentes de igualdade."""
        return hash(self._get_equality_components())

    def _get_equality_components(self) -> tuple[Any, ...]:
        """
        Retorna os componentes usados para comparação de igualdade.

        Sobrescreva este método se precisar de lógica customizada.
        Por padrão, usa todos os atributos definidos em __slots__.
        """
        components: list[Any] = []
        for cls in self.__class__.__mro__:
            if hasattr(cls, "__slots__"):
                for slot in cls.__slots__:
                    if slot.startswith("_"):
                        components.append(getattr(self, slot, None))
        return tuple(components)

    def __repr__(self) -> str:
        attrs = []
        for cls in self.__class__.__mro__:
            if hasattr(cls, "__slots__"):
                for slot in cls.__slots__:
                    if slot.startswith("_"):
                        attr_name = slot[1:]  # Remove underscore prefix
                        value = getattr(self, slot, None)
                        attrs.append(f"{attr_name}={value!r}")
        return f"{self.__class__.__name__}({', '.join(attrs)})"
