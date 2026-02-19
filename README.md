# 🏗️ DDD Enterprise Template

> Template **Enterprise-Grade** para projetos Python usando **Domain-Driven Design** + **Clean Architecture** (Hexagonal/Ports & Adapters).

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📑 Índice

- [Por que Enterprise?](#-por-que-enterprise)
- [Arquitetura](#-arquitetura)
- [Quick Start](#-quick-start)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Conceitos Fundamentais](#-conceitos-fundamentais)
- [Como Usar](#-como-usar)
- [Guia de Evolução](#-guia-de-evolução)
- [Docker & CI](#-docker--ci)
- [Testes](#-testes)
- [ADRs](#-adrs)
- [Contribuindo](#-contribuindo)

---

## 🎯 Por que Enterprise?

Este não é mais um template básico. É uma **base sólida para aplicações de produção**:

| Feature | Descrição |
|---------|-----------|
| **Clean Architecture** | 4 camadas bem definidas com regras de dependência estritas |
| **Composition Root** | DI centralizada sem frameworks complexos |
| **Event Dispatcher** | Eventos de domínio com suporte a múltiplos handlers |
| **Configuração Centralizada** | Pydantic Settings com suporte a múltiplos ambientes |
| **Logging Estruturado** | JSON para produção, console colorido para dev |
| **API REST** | FastAPI isolado, controllers sem lógica de negócio |
| **CLI** | Interface de linha de comando com Typer |
| **Docker** | Multi-stage build, non-root user, healthcheck |
| **CI/CD** | GitHub Actions com lint, typecheck, test, coverage |
| **Múltiplos Bounded Contexts** | Estrutura preparada para crescer |

---

## 🏛️ Arquitetura

### Diagrama de Camadas

```
┌─────────────────────────────────────────────────────────────┐
│                      INTERFACES                             │
│              CLI (Typer) │ API (FastAPI)                   │
├─────────────────────────────────────────────────────────────┤
│                    INFRASTRUCTURE                           │
│   Repositories │ Providers │ Messaging │ Config │ Logging  │
├─────────────────────────────────────────────────────────────┤
│                     APPLICATION                             │
│           Use Cases │ Ports │ DTOs │ Errors                │
├─────────────────────────────────────────────────────────────┤
│                       DOMAIN                                │
│    Entities │ Value Objects │ Events │ Services │ Rules    │
└─────────────────────────────────────────────────────────────┘
```

### Regra de Dependência

**Dependências SEMPRE apontam para dentro (em direção ao Domain).**

```
Interfaces → Infrastructure → Application → Domain
                    ↓              ↓           ↓
                 implementa     usa/define    puro
```

- **Domain**: Zero dependências externas. Apenas Python puro.
- **Application**: Importa apenas Domain. Define Ports (interfaces).
- **Infrastructure**: Implementa Ports. Pode usar frameworks.
- **Interfaces**: Ponto de entrada. Usa Application e Bootstrap.

### Ports & Adapters (Hexagonal)

```
                    ┌─────────────────┐
    HTTP Request →  │   API Adapter   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │    Use Case     │ ← Application
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
┌────────▼────────┐ ┌────────▼────────┐ ┌────────▼────────┐
│ Repository Port │ │   Clock Port    │ │ ID Generator    │
│   (interface)   │ │   (interface)   │ │    Port         │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
┌────────▼────────┐ ┌────────▼────────┐ ┌────────▼────────┐
│  In-Memory Repo │ │  System Clock   │ │ UUID Generator  │
│   (adapter)     │ │   (adapter)     │ │   (adapter)     │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

---

## 🚀 Quick Start

### Pré-requisitos

- Python 3.12+
- [Poetry](https://python-poetry.org/docs/#installation)
- Docker (opcional)

### Instalação

```bash
# Clone o repositório
git clone <repo-url> meu-projeto
cd meu-projeto

# Instale dependências
make install

# Instale pre-commit hooks
make install-hooks

# Verifique que tudo funciona
make check
```

### Executando

```bash
# CLI Demo
make run-cli

# API
make run-api
# Acesse: http://localhost:8000/docs

# Com Docker
make docker-build
make docker-up
```

---

## 📁 Estrutura do Projeto

```
├── src/app/
│   ├── bootstrap/              # 🎯 Composition Root (DI)
│   │   └── container.py        # Cria e conecta todas as dependências
│   │
│   ├── domain/                 # 🧠 Regras de Negócio (PURO)
│   │   ├── common/             # Building blocks reutilizáveis
│   │   │   ├── entity.py       # Classe base Entity
│   │   │   ├── value_object.py # Classe base ValueObject
│   │   │   ├── events.py       # DomainEvent base
│   │   │   ├── exceptions.py   # Exceções de domínio
│   │   │   └── validators.py   # Validações comuns
│   │   ├── sample_context/     # Bounded Context de exemplo
│   │   ├── billing_context/    # Placeholder para faturamento
│   │   └── identity_context/   # Placeholder para identidade
│   │
│   ├── application/            # 🎯 Orquestração
│   │   ├── common/             # UseCase, DTO, Errors base
│   │   └── sample_context/
│   │       ├── ports/          # Interfaces (Repository, Clock, etc.)
│   │       └── use_cases/      # Casos de uso
│   │
│   ├── infrastructure/         # 🔧 Implementações
│   │   ├── config/             # Pydantic Settings
│   │   ├── logging/            # Logger estruturado
│   │   ├── messaging/          # Event Dispatcher
│   │   ├── persistence/        # Repositórios (in-memory, SQL, etc.)
│   │   └── providers/          # Clock, ID Generator, etc.
│   │
│   └── interfaces/             # 🌐 Pontos de Entrada
│       ├── api/                # FastAPI
│       └── cli/                # Typer CLI
│
├── tests/
│   ├── unit/                   # Testes isolados
│   └── integration/            # Testes com infra real
│
├── docs/adr/                   # Architecture Decision Records
│
├── Dockerfile                  # Multi-stage build
├── docker-compose.yml          # Ambiente local
├── .github/workflows/ci.yml    # CI Pipeline
├── Makefile                    # Comandos úteis
└── pyproject.toml              # Poetry + tooling config
```

---

## 📚 Conceitos Fundamentais

### O que é DDD?

**Domain-Driven Design** é uma abordagem que coloca o domínio de negócio no centro do desenvolvimento:

- **Ubiquitous Language**: Código fala a mesma língua do negócio
- **Bounded Contexts**: Limites claros entre subdomínios
- **Entities**: Objetos com identidade que persistem no tempo
- **Value Objects**: Objetos imutáveis definidos por seus atributos
- **Domain Events**: Fatos importantes que aconteceram no domínio
- **Aggregates**: Clusters de entidades com raiz bem definida

### O que é Clean Architecture?

Separação em camadas com **regra de dependência**:
- Camadas internas não conhecem camadas externas
- Dependências apontam para dentro
- Detalhes dependem de abstrações

### O que é Hexagonal (Ports & Adapters)?

- **Ports**: Interfaces que definem como a aplicação interage com o mundo externo
- **Adapters**: Implementações concretas dessas interfaces
- **Benefício**: Troque banco de dados sem modificar use cases

### Composition Root

É o **único lugar onde dependências são criadas e conectadas**:

```python
# bootstrap/container.py
@dataclass
class Container:
    settings: Settings

    @cached_property
    def task_repository(self) -> TaskRepository:
        return InMemoryTaskRepository()

    @cached_property
    def create_task_use_case(self) -> CreateTaskUseCase:
        return CreateTaskUseCase(
            repository=self.task_repository,
            clock=self.clock,
            id_generator=self.id_generator,
        )
```

**Por que isso importa?**
- Zero "new" espalhado pelo código
- Fácil substituir implementações para testes
- Documenta todas as dependências em um lugar

---

## 🔧 Como Usar

### Comandos Principais

```bash
# Desenvolvimento
make install        # Instala dependências
make run-api        # Inicia API (http://localhost:8000)
make run-cli        # Executa CLI demo

# Qualidade
make lint           # Verifica linting
make format         # Formata código
make typecheck      # Verifica tipos
make test           # Executa testes
make check          # Todos os checks

# Docker
make docker-build   # Build da imagem
make docker-up      # Inicia containers
make docker-down    # Para containers
make docker-logs    # Vê logs
```

### Usando a CLI

```bash
# Criar tarefa
poetry run task-cli create "Minha tarefa" --priority high

# Listar tarefas
poetry run task-cli list --filter pending

# Completar tarefa
poetry run task-cli complete <task-id>

# Renomear
poetry run task-cli rename <task-id> "Novo título"
```

### Usando a API

```bash
# Criar tarefa
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Minha tarefa", "priority": "high"}'

# Listar tarefas
curl http://localhost:8000/api/v1/tasks

# Completar tarefa
curl -X POST http://localhost:8000/api/v1/tasks/{id}/complete
```

---

## 📈 Guia de Evolução

### 1. Criar Novo Bounded Context

```bash
# Estrutura
mkdir -p src/app/domain/orders_context/{entities,value_objects,events,services}
mkdir -p src/app/application/orders_context/{use_cases,ports}
```

```python
# domain/orders_context/__init__.py
"""
Orders Context - Gerenciamento de Pedidos.
"""
```

### 2. Criar Nova Entidade

```python
# domain/orders_context/entities/order.py
from app.domain.common import Entity
from .value_objects import OrderId, OrderStatus

class Order(Entity[OrderId]):
    def __init__(self, id: OrderId, status: OrderStatus, ...):
        super().__init__(id)
        self._status = status
        self.add_event(OrderCreated(order_id=id.value))

    @classmethod
    def create(cls, ...) -> "Order":
        # Factory method com validações
        ...
```

### 3. Criar Novo Use Case

```python
# application/orders_context/use_cases/create_order.py
@dataclass(frozen=True)
class CreateOrderInput(DTO):
    customer_id: str
    items: list[dict]

@dataclass(frozen=True)
class CreateOrderOutput(DTO):
    order_id: str
    total: str

class CreateOrderUseCase(UseCase[CreateOrderInput, CreateOrderOutput]):
    def __init__(self, repository: OrderRepository, ...):
        self._repository = repository

    def execute(self, input: CreateOrderInput) -> CreateOrderOutput:
        # Orquestra criação do pedido
        ...
```

### 4. Adicionar ao Container

```python
# bootstrap/container.py
@cached_property
def order_repository(self) -> OrderRepository:
    return InMemoryOrderRepository()

@cached_property
def create_order_use_case(self) -> CreateOrderUseCase:
    return CreateOrderUseCase(
        repository=self.order_repository,
        ...
    )
```

### 5. Trocar Repositório por SQL

```python
# infrastructure/persistence/sqlalchemy/order_repository.py
class SQLAlchemyOrderRepository(OrderRepository):
    def __init__(self, session: Session):
        self._session = session

    def save(self, order: Order) -> None:
        # Implementação com SQLAlchemy
        ...
```

```python
# bootstrap/container.py
@cached_property
def order_repository(self) -> OrderRepository:
    if self.settings.is_testing:
        return InMemoryOrderRepository()
    return SQLAlchemyOrderRepository(self.db_session)
```

---

## 🐳 Docker & CI

### Docker

```bash
# Build
make docker-build

# Executar
make docker-up

# Logs
make docker-logs

# Parar
make docker-down
```

### CI Pipeline

O GitHub Actions executa em todo push/PR:

1. **Lint**: Ruff check
2. **Format**: Black check
3. **Typecheck**: MyPy
4. **Test**: Pytest com coverage
5. **Build**: Docker build

---

## 🧪 Testes

### Estrutura

```
tests/
├── unit/                    # Testes isolados, sem I/O
│   ├── domain/              # Entidades, VOs, regras
│   ├── application/         # Use cases com mocks
│   └── infrastructure/      # Dispatcher, container
└── integration/             # Fluxos completos
```

### Executando

```bash
make test              # Todos com coverage
make test-unit         # Apenas unitários
make test-integration  # Apenas integração
make test-fast         # Sem coverage (mais rápido)
```

### Exemplo de Teste

```python
@pytest.mark.unit
class TestCreateTaskUseCase:
    def test_should_create_task(self, container):
        # Arrange
        use_case = container.create_task_use_case

        # Act
        output = use_case.execute(
            CreateTaskInput(title="Test", priority="high")
        )

        # Assert
        assert output.title == "Test"
        assert output.priority == "high"
```

---

## 📋 ADRs

Architecture Decision Records documentam decisões importantes:

| ADR | Decisão |
|-----|---------|
| [0001](docs/adr/0001-clean-architecture-layers.md) | Clean Architecture com 4 camadas |
| [0002](docs/adr/0002-repositories-in-application-layer.md) | Repositories como Ports na Application |
| [0003](docs/adr/0003-event-dispatcher-design.md) | Design do Event Dispatcher |
| [0004](docs/adr/0004-composition-root.md) | Composition Root para DI |
| [0005](docs/adr/0005-config-strategy.md) | Configuração centralizada |

---

## 🤝 Contribuindo

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes sobre:

- Setup de desenvolvimento
- Padrões de código
- Processo de PR
- Convenções de commit

### Conventional Commits

```
feat(domain): add Invoice entity
fix(api): handle validation errors properly
docs: update README with API examples
test(use-cases): add billing tests
refactor(infra): extract base repository
```

---

## 📄 Licença

MIT - veja [LICENSE](LICENSE)