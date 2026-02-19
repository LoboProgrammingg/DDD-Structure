"""
Implementação do IdGenerator usando UUID.
"""

from uuid import uuid4

from app.application.sample_context.ports import IdGenerator


class UUIDGenerator(IdGenerator):
    """
    Implementação do IdGenerator que gera UUIDs.

    Usa UUID4 para gerar identificadores únicos.
    """

    def generate(self) -> str:
        """Gera um novo UUID."""
        return str(uuid4())
