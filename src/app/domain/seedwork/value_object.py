"""Value Object: sem identidade, imutável e comparado pelos seus atributos.

Implemente subclasses como ``@dataclass(frozen=True, slots=True)`` e valide
as invariantes em ``__post_init__``: um Value Object inválido nunca existe.
"""


class ValueObject:
    __slots__ = ()
