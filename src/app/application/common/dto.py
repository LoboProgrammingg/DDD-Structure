"""
Base class para DTOs (Data Transfer Objects).

DTOs são usados para transferir dados entre camadas.
São estruturas simples sem lógica de negócio.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class DTO:
    """
    Classe base para DTOs.

    Características:
    - Imutável (frozen=True)
    - Sem lógica de negócio
    - Usado para transferência de dados entre camadas

    Exemplo de uso:
        >>> @dataclass(frozen=True)
        ... class UserDTO(DTO):
        ...     id: str
        ...     email: str
        ...     name: str
    """

    pass
