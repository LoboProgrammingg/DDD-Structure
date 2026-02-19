"""
Port para gerador de IDs.

Define a interface para geração de identificadores únicos.
Permite injetar um gerador previsível em testes.
"""

from abc import ABC, abstractmethod


class IdGenerator(ABC):
    """
    Interface para gerador de IDs únicos.

    Permite abstrair a geração de IDs,
    facilitando testes com IDs previsíveis.
    """

    @abstractmethod
    def generate(self) -> str:
        """
        Gera um novo ID único.

        Returns:
            String representando o ID único
        """
