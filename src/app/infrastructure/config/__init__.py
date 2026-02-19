"""
Configuração centralizada da aplicação.

Este módulo gerencia todas as configurações da aplicação usando Pydantic Settings.
"""

from app.infrastructure.config.settings import Settings, get_settings


__all__ = ["Settings", "get_settings"]
