"""
Configurações centralizadas da aplicação.

Usa Pydantic Settings para:
- Carregar configurações de variáveis de ambiente
- Validar configurações automaticamente
- Fornecer valores padrão sensatos
- Suportar diferentes ambientes (dev/test/prod)

Por que configuração centralizada?
- Evita configurações espalhadas pelo código
- Facilita testes (basta injetar Settings diferente)
- Documenta todas as configurações em um lugar
- Valida configurações no startup (fail fast)
"""

from enum import Enum
from functools import lru_cache
from typing import Any

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(str, Enum):
    """Ambientes suportados pela aplicação."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Níveis de log suportados."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):
    """
    Configurações da aplicação.

    Todas as configurações podem ser sobrescritas via variáveis de ambiente.
    Exemplo: APP_NAME=MyApp, ENVIRONMENT=production
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ==========================================================================
    # Aplicação
    # ==========================================================================
    app_name: str = Field(
        default="DDD Enterprise Template",
        description="Nome da aplicação",
    )
    app_version: str = Field(
        default="0.1.0",
        description="Versão da aplicação",
    )
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        description="Ambiente de execução",
    )
    debug: bool = Field(
        default=False,
        description="Modo debug (mais logs, stack traces)",
    )

    # ==========================================================================
    # Logging
    # ==========================================================================
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        description="Nível de log",
    )
    log_format: str = Field(
        default="json",
        description="Formato do log: 'json' ou 'console'",
    )

    # ==========================================================================
    # API
    # ==========================================================================
    api_host: str = Field(
        default="0.0.0.0",
        description="Host para bind da API",
    )
    api_port: int = Field(
        default=8000,
        description="Porta da API",
    )
    api_prefix: str = Field(
        default="/api/v1",
        description="Prefixo das rotas da API",
    )
    cors_origins: list[str] = Field(
        default=["*"],
        description="Origens permitidas para CORS",
    )

    # ==========================================================================
    # Database (preparado para uso futuro)
    # ==========================================================================
    database_url: str = Field(
        default="sqlite:///./app.db",
        description="URL de conexão do banco de dados",
    )
    database_echo: bool = Field(
        default=False,
        description="Mostrar queries SQL no log",
    )

    # ==========================================================================
    # Propriedades computadas
    # ==========================================================================
    @property
    def is_development(self) -> bool:
        """Retorna True se estiver em ambiente de desenvolvimento."""
        return self.environment == Environment.DEVELOPMENT

    @property
    def is_testing(self) -> bool:
        """Retorna True se estiver em ambiente de teste."""
        return self.environment == Environment.TESTING

    @property
    def is_production(self) -> bool:
        """Retorna True se estiver em ambiente de produção."""
        return self.environment == Environment.PRODUCTION

    @property
    def use_json_logs(self) -> bool:
        """Retorna True se deve usar logs em formato JSON."""
        return self.log_format.lower() == "json" and not self.is_development

    @field_validator("log_format")
    @classmethod
    def validate_log_format(cls, v: str) -> str:
        """Valida o formato do log."""
        allowed = ("json", "console")
        if v.lower() not in allowed:
            raise ValueError(f"log_format deve ser um de: {allowed}")
        return v.lower()


@lru_cache
def get_settings() -> Settings:
    """
    Retorna instância singleton das configurações.

    Usa lru_cache para garantir que apenas uma instância seja criada.
    """
    return Settings()
