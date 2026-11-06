"""Entity: objeto definido por uma identidade que persiste ao longo do tempo."""


class Entity[TId]:
    """Duas entidades são iguais quando têm o mesmo tipo e a mesma identidade."""

    def __init__(self, entity_id: TId) -> None:
        self._id = entity_id

    @property
    def id(self) -> TId:
        return self._id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return NotImplemented
        return type(self) is type(other) and self._id == other._id

    def __hash__(self) -> int:
        return hash((type(self), self._id))

    def __repr__(self) -> str:
        return f"{type(self).__name__}(id={self._id!r})"
