"""
Providers de serviços de infraestrutura.

Implementações de serviços utilitários como:
- Clock: provedor de data/hora
- ID Generator: gerador de identificadores únicos
"""

from app.infrastructure.providers.system_clock import SystemClock
from app.infrastructure.providers.uuid_generator import UUIDGenerator


__all__ = [
    "SystemClock",
    "UUIDGenerator",
]
