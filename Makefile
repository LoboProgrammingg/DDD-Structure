.DEFAULT_GOAL := help
.PHONY: help install run migrate migration test test-unit test-integration cov lint format typecheck architecture check up down clean

help: ## Lista os comandos disponíveis
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: ## Instala dependências e hooks de pre-commit
	poetry install
	poetry run pre-commit install --hook-type pre-commit --hook-type commit-msg

run: ## Sobe a API em modo desenvolvimento (http://localhost:8000/docs)
	poetry run uvicorn app.interfaces.api:create_app --factory --reload

migrate: ## Aplica as migrações pendentes
	poetry run alembic upgrade head

migration: ## Gera uma migração a partir dos modelos: make migration m="descrição"
	poetry run alembic revision --autogenerate -m "$(m)"

test: ## Roda toda a suíte de testes
	poetry run pytest

test-unit: ## Roda só os testes unitários (domínio e aplicação)
	poetry run pytest tests/unit

test-integration: ## Roda integração e e2e (SQLite, ou PostgreSQL via TEST_DATABASE_URL)
	poetry run pytest tests/integration tests/e2e

cov: ## Testes com relatório de cobertura
	poetry run pytest --cov --cov-report=term --cov-report=html

lint: ## Ruff (lint + formatação)
	poetry run ruff check .
	poetry run ruff format --check .

format: ## Formata e corrige o que for automático
	poetry run ruff format .
	poetry run ruff check --fix .

typecheck: ## Mypy em modo strict
	poetry run mypy
	poetry run mypy tests

architecture: ## Verifica os contratos de arquitetura (import-linter)
	poetry run lint-imports

check: lint typecheck architecture test ## Tudo o que o CI verifica

up: ## Sobe PostgreSQL + API com Docker Compose
	docker compose up -d --build

down: ## Derruba o ambiente Docker Compose
	docker compose down

clean: ## Remove caches e artefatos locais
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage app.db
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
