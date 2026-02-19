"""
Port para serviço de clock (data/hora).

Define a interface para obter a data/hora atual.
Permite injetar um clock falso em testes.
"""

from abc import ABC, abstractmethod
from datetime import datetime


class Clock(ABC):
    """
    Interface para serviço de clock.

    Permite abstrair a obtenção de data/hora,
    facilitando testes com datas fixas.
    """

    @abstractmethod
    def now(self) -> datetime:
        """
        Retorna a data/hora atual.

        Returns:
            Datetime atual (com timezone)
        """
