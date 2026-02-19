"""
Base class para Entidades do domínio.

Uma Entidade é um objeto que possui identidade única e um ciclo de vida.
Duas entidades são iguais se possuem o mesmo ID, independente de seus atributos.
"""

from abc import ABC
from typing import TYPE_CHECKING, Any, Generic, TypeVar


if TYPE_CHECKING:
    from app.domain.common.events import DomainEvent


TId = TypeVar("TId")


class Entity(ABC, Generic[TId]):
    """
    Classe base para todas as entidades do domínio.

    Uma entidade possui:
    - Identidade única (id)
    - Igualdade baseada em identidade, não em atributos
    - Capacidade de acumular eventos de domínio

    Exemplo de uso:
        >>> class User(Entity[UserId]):
        ...     def __init__(self, id: UserId, name: str) -> None:
        ...         super().__init__(id)
        ...         self._name = name
    """

    __slots__ = ("_id", "_events")

    def __init__(self, id: TId) -> None:
        """
        Inicializa a entidade com um ID único.

        Args:
            id: Identificador único da entidade
        """
        self._id = id
        self._events: list[DomainEvent] = []

    @property
    def id(self) -> TId:
        """Retorna o identificador único da entidade."""
        return self._id

    @property
    def domain_events(self) -> list["DomainEvent"]:
        """Retorna lista de eventos de domínio pendentes."""
        return self._events.copy()

    def add_event(self, event: "DomainEvent") -> None:
        """
        Adiciona um evento de domínio à entidade.

        Args:
            event: Evento de domínio a ser adicionado
        """
        self._events.append(event)

    def clear_events(self) -> list["DomainEvent"]:
        """
        Limpa e retorna todos os eventos pendentes.

        Returns:
            Lista de eventos que foram removidos
        """
        events = self._events.copy()
        self._events.clear()
        return events

    def __eq__(self, other: object) -> bool:
        """Entidades são iguais se possuem o mesmo ID."""
        if not isinstance(other, Entity):
            return NotImplemented
        return self._id == other._id

    def __hash__(self) -> int:
        """Hash baseado no ID da entidade."""
        return hash(self._id)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self._id!r})"
