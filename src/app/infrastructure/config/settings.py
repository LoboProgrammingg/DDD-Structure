"""Configuração única, lida de variáveis de ambiente (ou ``.env``) e validada no startup."""

from enum import StrEnum
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogFormat(StrEnum):
    JSON = "json"
    CONSOLE = "console"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "DDD Structure"
    app_version: str = "1.0.0"
    environment: Environment = Environment.DEVELOPMENT

    log_level: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    log_format: LogFormat = LogFormat.CONSOLE

    cors_origins: list[str] = Field(
        default_factory=list,
        description="Origens liberadas no CORS. Vazio desliga o CORS; nunca use '*' em produção.",
    )

    database_url: str = "sqlite+aiosqlite:///./app.db"
    database_echo: bool = False

    work_in_progress_limit: int = Field(default=3, ge=1)


@lru_cache
def get_settings() -> Settings:
    return Settings()
