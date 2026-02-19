"""
Implementação do Clock usando o relógio do sistema.
"""

from datetime import UTC, datetime

from app.application.sample_context.ports import Clock


class SystemClock(Clock):
    """
    Implementação do Clock que usa o relógio do sistema.

    Retorna sempre datetime com timezone UTC.
    """

    def now(self) -> datetime:
        """Retorna a data/hora atual em UTC."""
        return datetime.now(UTC)
