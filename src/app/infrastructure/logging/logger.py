"""
Logger estruturado configurável.

Suporta dois formatos:
- JSON: para produção, facilita ingestão por ferramentas de observabilidade
- Console: para desenvolvimento, legível por humanos

Por que logging estruturado?
- Logs JSON são facilmente parseados por ELK, Datadog, etc.
- Campos estruturados permitem queries e alertas precisos
- Contexto adicional (user_id, request_id) facilita debugging
- Consistência em toda a aplicação
"""

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any


class JsonFormatter(logging.Formatter):
    """
    Formatter que produz logs em formato JSON.

    Ideal para produção onde logs são ingeridos por ferramentas
    como Elasticsearch, Datadog, CloudWatch, etc.
    """

    def format(self, record: logging.LogRecord) -> str:
        log_data: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Adiciona exceção se presente
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Adiciona campos extras
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)

        return json.dumps(log_data, default=str, ensure_ascii=False)


class ConsoleFormatter(logging.Formatter):
    """
    Formatter colorido para console.

    Ideal para desenvolvimento onde a legibilidade é prioridade.
    """

    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"

    def format(self, record: logging.LogRecord) -> str:
        color = self.COLORS.get(record.levelname, self.RESET)

        # Formato: [TIMESTAMP] LEVEL | logger | message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level = f"{color}{record.levelname:8}{self.RESET}"

        formatted = f"[{timestamp}] {level} | {record.name} | {record.getMessage()}"

        # Adiciona exceção se presente
        if record.exc_info:
            formatted += f"\n{self.formatException(record.exc_info)}"

        return formatted


class StructuredLogger(logging.LoggerAdapter):
    """
    Logger adapter que adiciona contexto estruturado aos logs.

    Permite adicionar campos extras que serão incluídos em todos os logs.
    """

    def __init__(
        self,
        logger: logging.Logger,
        extra: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(logger, extra or {})

    def process(
        self,
        msg: str,
        kwargs: dict[str, Any],
    ) -> tuple[str, dict[str, Any]]:
        """Processa a mensagem adicionando campos extras."""
        extra = kwargs.get("extra", {})

        # Merge com campos do adapter
        merged_extra = {**self.extra, **extra}

        # Adiciona extra_fields para o JsonFormatter
        if merged_extra:
            kwargs["extra"] = {"extra_fields": merged_extra}

        return msg, kwargs

    def with_context(self, **context: Any) -> "StructuredLogger":
        """
        Cria novo logger com contexto adicional.

        Útil para adicionar request_id, user_id, etc.
        """
        new_extra = {**self.extra, **context}
        return StructuredLogger(self.logger, new_extra)


def setup_logging(
    level: str = "INFO",
    format_type: str = "console",
    app_name: str = "app",
) -> None:
    """
    Configura o logging da aplicação.

    Args:
        level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: Tipo de formato ('json' ou 'console')
        app_name: Nome da aplicação (usado como prefixo do logger)
    """
    # Remove handlers existentes
    root = logging.getLogger()
    for handler in root.handlers[:]:
        root.removeHandler(handler)

    # Configura handler
    handler = logging.StreamHandler(sys.stdout)

    if format_type.lower() == "json":
        handler.setFormatter(JsonFormatter())
    else:
        handler.setFormatter(ConsoleFormatter())

    # Configura root logger
    root.addHandler(handler)
    root.setLevel(getattr(logging, level.upper()))

    # Reduz verbosidade de loggers de terceiros
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(
    name: str,
    context: dict[str, Any] | None = None,
) -> StructuredLogger:
    """
    Obtém um logger estruturado.

    Args:
        name: Nome do logger (geralmente __name__)
        context: Contexto inicial opcional

    Returns:
        Logger estruturado
    """
    logger = logging.getLogger(name)
    return StructuredLogger(logger, context)
