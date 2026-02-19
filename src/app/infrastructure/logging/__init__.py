"""
Logging estruturado para aplicações enterprise.

Fornece logging configurável com suporte a:
- Formato JSON para produção (facilita parsing por ferramentas como ELK)
- Formato console para desenvolvimento (legível por humanos)
- Contexto estruturado (correlation IDs, request IDs, etc.)
"""

from app.infrastructure.logging.logger import get_logger, setup_logging


__all__ = ["get_logger", "setup_logging"]
