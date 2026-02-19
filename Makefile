# ============================================================================
# DDD Enterprise Template - Makefile
# ============================================================================
# Comandos para desenvolvimento, testes, build e deploy
#
# Uso:
#   make install      - Instala dependências com Poetry
#   make test         - Executa todos os testes
#   make lint         - Executa linting com Ruff
#   make format       - Formata código com Black e Ruff
#   make typecheck    - Verifica tipos com MyPy
#   make check        - Executa todos os checks
#   make run-api      - Inicia API FastAPI
#   make run-cli      - Executa CLI demo
#   make docker-build - Build da imagem Docker
#   make docker-up    - Inicia containers
# ============================================================================

.PHONY: install test test-unit test-integration lint format typecheck check clean pre-commit help
.PHONY: run-api run-cli docker-build docker-up docker-down docker-logs

# Cores para output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# ============================================================================
# Instalação
# ============================================================================

install: ## Instala todas as dependências com Poetry
	@echo "$(BLUE)📦 Instalando dependências...$(NC)"
	poetry install
	@echo "$(GREEN)✓ Dependências instaladas!$(NC)"

install-hooks: ## Instala pre-commit hooks
	@echo "$(BLUE)🪝 Instalando pre-commit hooks...$(NC)"
	poetry run pre-commit install
	poetry run pre-commit install --hook-type commit-msg
	@echo "$(GREEN)✓ Hooks instalados!$(NC)"

setup: install install-hooks ## Setup completo do projeto
	@echo "$(GREEN)✓ Setup completo!$(NC)"

# ============================================================================
# Testes
# ============================================================================

test: ## Executa todos os testes com coverage
	@echo "$(BLUE)🧪 Executando testes...$(NC)"
	poetry run pytest --cov --cov-report=term-missing
	@echo "$(GREEN)✓ Testes concluídos!$(NC)"

test-unit: ## Executa apenas testes unitários
	@echo "$(BLUE)🧪 Executando testes unitários...$(NC)"
	poetry run pytest -m unit -v
	@echo "$(GREEN)✓ Testes unitários concluídos!$(NC)"

test-integration: ## Executa apenas testes de integração
	@echo "$(BLUE)🧪 Executando testes de integração...$(NC)"
	poetry run pytest -m integration -v
	@echo "$(GREEN)✓ Testes de integração concluídos!$(NC)"

test-fast: ## Executa testes sem coverage (mais rápido)
	@echo "$(BLUE)🧪 Executando testes (fast mode)...$(NC)"
	poetry run pytest -x -q
	@echo "$(GREEN)✓ Testes concluídos!$(NC)"

# ============================================================================
# Qualidade de Código
# ============================================================================

lint: ## Executa linting com Ruff
	@echo "$(BLUE)🔍 Executando linting...$(NC)"
	poetry run ruff check src/ tests/
	@echo "$(GREEN)✓ Linting concluído!$(NC)"

lint-fix: ## Executa linting e corrige problemas automaticamente
	@echo "$(BLUE)🔧 Corrigindo problemas de lint...$(NC)"
	poetry run ruff check src/ tests/ --fix
	@echo "$(GREEN)✓ Correções aplicadas!$(NC)"

format: ## Formata código com Black e Ruff
	@echo "$(BLUE)✨ Formatando código...$(NC)"
	poetry run black src/ tests/
	poetry run ruff check src/ tests/ --fix --select I
	@echo "$(GREEN)✓ Código formatado!$(NC)"

format-check: ## Verifica formatação sem alterar arquivos
	@echo "$(BLUE)🔍 Verificando formatação...$(NC)"
	poetry run black src/ tests/ --check
	@echo "$(GREEN)✓ Formatação OK!$(NC)"

typecheck: ## Executa verificação de tipos com MyPy
	@echo "$(BLUE)🔬 Verificando tipos...$(NC)"
	poetry run mypy src/
	@echo "$(GREEN)✓ Type check concluído!$(NC)"

# ============================================================================
# Checks Combinados
# ============================================================================

check: lint format-check typecheck test ## Executa todos os checks
	@echo "$(GREEN)✓ Todos os checks passaram!$(NC)"

check-fast: lint format-check typecheck ## Checks rápidos (sem testes)
	@echo "$(GREEN)✓ Checks rápidos concluídos!$(NC)"

pre-commit: ## Executa pre-commit em todos os arquivos
	@echo "$(BLUE)🪝 Executando pre-commit...$(NC)"
	poetry run pre-commit run --all-files
	@echo "$(GREEN)✓ Pre-commit concluído!$(NC)"

# ============================================================================
# Executar Aplicação
# ============================================================================

run-api: ## Inicia API FastAPI em modo desenvolvimento
	@echo "$(BLUE)🚀 Iniciando API...$(NC)"
	poetry run uvicorn app.interfaces.api.main:app --reload --host 0.0.0.0 --port 8000

run-cli: ## Executa demonstração da CLI
	@echo "$(BLUE)🚀 Executando CLI demo...$(NC)"
	poetry run task-cli demo

cli: ## Executa a CLI interativa
	poetry run task-cli

cli-help: ## Mostra ajuda da CLI
	poetry run task-cli --help

# ============================================================================
# Docker
# ============================================================================

docker-build: ## Build da imagem Docker
	@echo "$(BLUE)🐳 Building Docker image...$(NC)"
	docker build -t ddd-template:latest .
	@echo "$(GREEN)✓ Build concluído!$(NC)"

docker-up: ## Inicia containers com docker-compose
	@echo "$(BLUE)🐳 Iniciando containers...$(NC)"
	docker-compose up -d
	@echo "$(GREEN)✓ Containers iniciados!$(NC)"

docker-down: ## Para containers
	@echo "$(YELLOW)🐳 Parando containers...$(NC)"
	docker-compose down
	@echo "$(GREEN)✓ Containers parados!$(NC)"

docker-logs: ## Mostra logs dos containers
	docker-compose logs -f

docker-shell: ## Acessa shell do container API
	docker-compose exec api /bin/bash

# ============================================================================
# Limpeza
# ============================================================================

clean: ## Remove arquivos temporários e caches
	@echo "$(YELLOW)🧹 Limpando arquivos temporários...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name ".coverage" -delete 2>/dev/null || true
	rm -rf htmlcov/ dist/ build/ .coverage coverage.xml
	@echo "$(GREEN)✓ Limpeza concluída!$(NC)"

# ============================================================================
# Ajuda
# ============================================================================

help: ## Mostra esta mensagem de ajuda
	@echo "$(BLUE)DDD Python Template - Comandos disponíveis:$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""

# Default target
.DEFAULT_GOAL := help
