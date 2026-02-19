# =============================================================================
# DDD Enterprise Template - Dockerfile
# =============================================================================
# Multi-stage build otimizado para produção
#
# Stages:
# 1. builder: Instala dependências e exporta requirements
# 2. production: Imagem final mínima com apenas o necessário
#
# Uso:
#   docker build -t ddd-template .
#   docker run -p 8000:8000 ddd-template
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder
# -----------------------------------------------------------------------------
FROM python:3.12-slim as builder

WORKDIR /build

# Instala Poetry
ENV POETRY_HOME="/opt/poetry" \
    POETRY_VERSION="1.7.1" \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

# Copia arquivos de dependência
COPY pyproject.toml poetry.lock* ./

# Exporta requirements.txt (sem dev dependencies)
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --without dev

# -----------------------------------------------------------------------------
# Stage 2: Production
# -----------------------------------------------------------------------------
FROM python:3.12-slim as production

# Labels
LABEL maintainer="your-email@example.com" \
      version="0.1.0" \
      description="DDD Enterprise Template"

# Configurações de segurança e performance
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONFAULTHANDLER=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Cria usuário não-root
RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --shell /bin/bash --create-home appuser

WORKDIR /app

# Copia requirements do builder
COPY --from=builder /build/requirements.txt .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copia código fonte
COPY --chown=appuser:appgroup src/ ./src/

# Muda para usuário não-root
USER appuser

# Variáveis de ambiente padrão
ENV ENVIRONMENT=production \
    LOG_FORMAT=json \
    LOG_LEVEL=INFO \
    API_HOST=0.0.0.0 \
    API_PORT=8000

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Comando padrão: API
CMD ["python", "-m", "uvicorn", "app.interfaces.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
