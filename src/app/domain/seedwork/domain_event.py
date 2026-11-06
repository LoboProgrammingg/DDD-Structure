"""Domain Event: fato relevante para o negócio que já aconteceu.

Nomes no passado (``TaskCompleted``), imutáveis e carregando apenas tipos
primitivos, para que possam atravessar fronteiras de contexto sem acoplamento.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


@dataclass(frozen=True, kw_only=True)
class DomainEvent:
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def name(self) -> str:
        return type(self).__name__
