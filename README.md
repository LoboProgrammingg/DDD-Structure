# 🏗️ DDD Python Template

> Template profissional para projetos Python usando **Domain-Driven Design** com **Clean Architecture** (Ports & Adapters / Hexagonal).

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 📑 Índice

- [Por que usar este template?](#-por-que-usar-este-template)
- [O que é DDD?](#-o-que-é-ddd-domain-driven-design)
- [Arquitetura](#-arquitetura)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Quick Start](#-quick-start)
- [Comandos Disponíveis](#-comandos-disponíveis)
- [O Sample Domain (Task)](#-o-sample-domain-task)
- [Guia: Como Evoluir o Template](#-guia-como-evoluir-o-template)
- [Padrões e Convenções](#-padrões-e-convenções)
- [Testes](#-testes)
- [Decisões de Arquitetura](#-decisões-de-arquitetura)
- [Contribuindo](#-contribuindo)

---

## 🎯 Por que usar este template?

### O problema que resolvemos

Muitos projetos Python começam simples, mas conforme crescem:
- A lógica de negócio fica espalhada por controllers, serviços e repositórios
- Testes se tornam difíceis porque tudo está acoplado a frameworks
- Mudanças simples exigem alterações em múltiplos arquivos
- Novos desenvolvedores demoram para entender onde cada coisa deve ficar

### A solução

Este template fornece uma **base sólida e escalável** com:

| Benefício | Como entregamos |
|-----------|-----------------|
| **Separação de responsabilidades** | Camadas bem definidas (domain, application, infrastructure, interfaces) |
| **Testabilidade** | Inversão de dependências com ports/adapters |
| **Flexibilidade** | Troque banco de dados, framework web ou qualquer infra sem tocar no domínio |
| **Consistência** | Padrões claros para entidades, value objects, use cases |
| **Produtividade** | Tooling configurado (lint, format, type-check, pre-commit) |

### Quando usar DDD?

✅ **Use quando:**
- O domínio é complexo e tem muitas regras de negócio
- O projeto vai crescer e ter múltiplos desenvolvedores
- Você precisa de testes confiáveis e isolados
- Pode haver mudanças de tecnologia (trocar banco, framework, etc.)

⚠️ **Considere alternativas quando:**
- É um CRUD simples sem regras de negócio
- É um script único ou protótipo rápido
- A equipe não tem familiaridade com os conceitos

---

## 📚 O que é DDD (Domain-Driven Design)?

**Domain-Driven Design** é uma abordagem de desenvolvimento que coloca o **domínio do negócio** no centro de todas as decisões de design.

### Conceitos fundamentais

#### 1. Ubiquitous Language (Linguagem Ubíqua)
Uma linguagem compartilhada entre desenvolvedores e especialistas de negócio. O código deve refletir os termos usados pelo negócio.

```python
# ❌ Ruim - termos técnicos
class DataProcessor:
    def process(self, record: dict) -> None: ...

# ✅ Bom - linguagem do domínio
class Task:
    def complete(self, completed_at: datetime) -> None: ...
```

#### 2. Bounded Context
Um limite claro que define onde um modelo específico se aplica. Diferentes contextos podem ter diferentes significados para o mesmo termo.

```
┌─────────────────┐    ┌─────────────────┐
│  Billing        │    │  Inventory      │
│  Context        │    │  Context        │
│                 │    │                 │
│  Product = item │    │  Product = SKU  │
│  com preço      │    │  com estoque    │
└─────────────────┘    └─────────────────┘
```

#### 3. Building Blocks

| Conceito | Descrição | Exemplo |
|----------|-----------|---------|
| **Entity** | Objeto com identidade única | `Task`, `User`, `Order` |
| **Value Object** | Objeto imutável definido por atributos | `Email`, `Money`, `TaskTitle` |
| **Aggregate** | Cluster de objetos tratados como uma unidade | `Order` com `OrderItems` |
| **Repository** | Abstração para persistência | `TaskRepository` |
| **Domain Service** | Lógica que não pertence a uma entidade | `PricingService` |
| **Domain Event** | Registro de algo que aconteceu | `TaskCompleted` |

---

## 🏛️ Arquitetura

Este template implementa **Clean Architecture** com **Ports & Adapters** (Hexagonal):

```
┌─────────────────────────────────────────────────────────────┐
│                        INTERFACES                           │
│              (CLI, API, Web Controllers)                    │
│         Adaptadores que conectam o mundo externo            │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      INFRASTRUCTURE                          │
│        (Repositories, Providers, External Services)         │
│         Implementações concretas de ports                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                       APPLICATION                            │
│              (Use Cases, Ports, DTOs)                       │
│         Orquestração e casos de uso                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                         DOMAIN                               │
│      (Entities, Value Objects, Domain Services)             │
│         Regras de negócio puras                             │
└─────────────────────────────────────────────────────────────┘
```

### A Regra de Dependência

> **As dependências sempre apontam para dentro (em direção ao domínio).**

- `domain` não importa nada de outras camadas
- `application` importa apenas de `domain`
- `infrastructure` implementa interfaces de `application`
- `interfaces` usa `application` e `infrastructure`

### Por que isso importa?

```python
# ✅ Use Case depende de uma INTERFACE (port)
class CreateTaskUseCase:
    def __init__(self, repository: TaskRepositoryPort):  # Interface
        self._repository = repository

# ✅ Infraestrutura IMPLEMENTA a interface
class InMemoryTaskRepository(TaskRepository):  # Implementação
    def save(self, task: Task) -> None: ...

# ✅ Podemos trocar a implementação sem mudar o use case!
class PostgresTaskRepository(TaskRepository):  # Outra implementação
    def save(self, task: Task) -> None: ...
```

---

## 📁 Estrutura do Projeto

```
ddd-python-template/
├── src/
│   └── app/
│       ├── domain/                    # 🧠 Camada de Domínio
│       │   ├── common/                # Building blocks compartilhados
│       │   │   ├── entity.py          # Classe base para entidades
│       │   │   ├── value_object.py    # Classe base para VOs
│       │   │   ├── events.py          # Domain events
│       │   │   ├── exceptions.py      # Exceções de domínio
│       │   │   ├── result.py          # Result pattern (Success/Failure)
│       │   │   └── validators.py      # Validadores reutilizáveis
│       │   │
│       │   └── sample_context/        # Bounded context de exemplo
│       │       ├── entities/          # Entidades do contexto
│       │       │   └── task.py
│       │       ├── value_objects/     # Value Objects
│       │       │   ├── task_id.py
│       │       │   ├── task_title.py
│       │       │   ├── task_description.py
│       │       │   ├── task_priority.py
│       │       │   └── task_status.py
│       │       ├── events/            # Domain events
│       │       │   └── task_events.py
│       │       ├── repositories/      # Interfaces de repositório
│       │       │   └── task_repository.py
│       │       └── services/          # Domain services (se necessário)
│       │
│       ├── application/               # 🎯 Camada de Aplicação
│       │   ├── common/                # Use case base, DTOs, errors
│       │   │   ├── use_case.py
│       │   │   ├── dto.py
│       │   │   └── errors.py
│       │   │
│       │   └── sample_context/
│       │       ├── use_cases/         # Casos de uso
│       │       │   ├── create_task.py
│       │       │   ├── complete_task.py
│       │       │   ├── rename_task.py
│       │       │   └── list_tasks.py
│       │       └── ports/             # Interfaces para infraestrutura
│       │           ├── repositories.py
│       │           ├── clock.py
│       │           └── id_generator.py
│       │
│       ├── infrastructure/            # 🔧 Camada de Infraestrutura
│       │   ├── persistence/
│       │   │   └── in_memory/         # Repositórios em memória
│       │   │       └── task_repository.py
│       │   ├── providers/             # Implementações de serviços
│       │   │   ├── system_clock.py
│       │   │   └── uuid_generator.py
│       │   └── messaging/             # (Futuro) Event publishers
│       │
│       └── interfaces/                # 🌐 Camada de Interfaces
│           ├── cli/                   # Interface de linha de comando
│           │   └── main.py
│           └── api/                   # (Futuro) REST API
│
├── tests/
│   ├── unit/                          # Testes unitários
│   │   ├── domain/
│   │   └── application/
│   ├── integration/                   # Testes de integração
│   └── conftest.py                    # Fixtures compartilhadas
│
├── pyproject.toml                     # Configuração do Poetry e tools
├── Makefile                           # Comandos de desenvolvimento
├── .pre-commit-config.yaml            # Hooks de pre-commit
├── .editorconfig                      # Configuração do editor
└── .gitignore
```

---

## 🚀 Quick Start

### Pré-requisitos

- Python 3.12+
- [Poetry](https://python-poetry.org/docs/#installation)

### Instalação

```bash
# Clone o repositório
git clone <repo-url> meu-projeto
cd meu-projeto

# Instale as dependências
make install

# Instale os hooks de pre-commit
make install-hooks

# Ou faça tudo de uma vez
make setup
```

### Executando a demonstração

```bash
# Execute a CLI de demonstração
poetry run task-cli demo

# Ou use o Makefile
make cli
```

### Executando testes

```bash
# Todos os testes com coverage
make test

# Apenas unitários
make test-unit

# Apenas integração
make test-integration
```

---

## 🛠️ Comandos Disponíveis

| Comando | Descrição |
|---------|-----------|
| `make install` | Instala dependências |
| `make setup` | Setup completo (install + hooks) |
| `make test` | Executa todos os testes com coverage |
| `make test-unit` | Executa apenas testes unitários |
| `make test-integration` | Executa apenas testes de integração |
| `make lint` | Executa linting com Ruff |
| `make lint-fix` | Corrige problemas de lint automaticamente |
| `make format` | Formata código com Black |
| `make typecheck` | Verifica tipos com MyPy |
| `make check` | Executa lint + format + typecheck + test |
| `make clean` | Remove arquivos temporários |
| `make cli` | Executa a CLI do sample domain |

---

## 📋 O Sample Domain (Task)

O template inclui um **bounded context de exemplo** chamado `sample_context` que implementa um sistema de gerenciamento de tarefas (ToDo).

### Entidade: Task

```python
from app.domain.sample_context.entities import Task
from app.domain.sample_context.value_objects import (
    TaskId, TaskTitle, TaskPriority
)

# Criar uma tarefa
task = Task.create(
    id=TaskId("task-001"),
    title=TaskTitle("Estudar DDD"),
    priority=TaskPriority.high(),
    created_at=datetime.now(timezone.utc),
)

# Completar a tarefa
task.complete(datetime.now(timezone.utc))

# Eventos são acumulados
events = task.clear_events()  # [TaskCreated, TaskCompleted]
```

### Value Objects

| Value Object | Regras |
|--------------|--------|
| `TaskId` | Não pode ser vazio |
| `TaskTitle` | Não vazio, máx 200 caracteres |
| `TaskDescription` | Opcional, máx 2000 caracteres |
| `TaskPriority` | low, medium, high, urgent |
| `TaskStatus` | pending, in_progress, completed, cancelled |

### Regras de Negócio

1. Tarefas completadas ou canceladas **não podem ser modificadas**
2. Apenas tarefas pendentes podem ser iniciadas
3. Apenas tarefas abertas podem ser completadas ou canceladas

### Use Cases Disponíveis

| Use Case | Descrição |
|----------|-----------|
| `CreateTaskUseCase` | Cria uma nova tarefa |
| `CompleteTaskUseCase` | Marca uma tarefa como concluída |
| `RenameTaskUseCase` | Altera o título de uma tarefa |
| `ListTasksUseCase` | Lista tarefas com filtros |

### CLI

```bash
# Criar tarefa
poetry run task-cli create "Minha tarefa" --priority high

# Listar tarefas
poetry run task-cli list
poetry run task-cli list --filter pending

# Completar tarefa
poetry run task-cli complete <task-id>

# Renomear tarefa
poetry run task-cli rename <task-id> "Novo título"

# Demo completa
poetry run task-cli demo
```

---

## 📖 Guia: Como Evoluir o Template

### 1. Adicionar um novo Bounded Context

```bash
# Criar estrutura
mkdir -p src/app/domain/billing/{entities,value_objects,events,repositories,services}
mkdir -p src/app/application/billing/{use_cases,ports}
mkdir -p src/app/infrastructure/persistence/in_memory
```

```python
# src/app/domain/billing/entities/invoice.py
from app.domain.common import Entity
from app.domain.billing.value_objects import InvoiceId

class Invoice(Entity[InvoiceId]):
    # Implementar a entidade
    pass
```

### 2. Criar uma nova Entidade

```python
# 1. Crie os Value Objects necessários
# src/app/domain/my_context/value_objects/user_id.py
from app.domain.common import ValueObject, Validator

class UserId(ValueObject):
    __slots__ = ("_value",)

    def __init__(self, value: str) -> None:
        validated = Validator.not_empty(value, "UserId")
        object.__setattr__(self, "_value", validated)

    @property
    def value(self) -> str:
        return self._value

# 2. Crie a Entidade
# src/app/domain/my_context/entities/user.py
from app.domain.common import Entity

class User(Entity[UserId]):
    def __init__(self, id: UserId, email: Email, name: UserName) -> None:
        super().__init__(id)
        self._email = email
        self._name = name

    @classmethod
    def create(cls, id: UserId, email: Email, name: UserName) -> "User":
        user = cls(id=id, email=email, name=name)
        user.add_event(UserCreated(user_id=id.value, email=email.value))
        return user
```

### 3. Criar um novo Use Case

```python
# src/app/application/my_context/use_cases/register_user.py
from dataclasses import dataclass
from app.application.common import UseCase

@dataclass(frozen=True)
class RegisterUserInput:
    email: str
    name: str

@dataclass(frozen=True)
class RegisterUserOutput:
    id: str
    email: str

class RegisterUserUseCase(UseCase[RegisterUserInput, RegisterUserOutput]):
    def __init__(
        self,
        repository: UserRepositoryPort,
        id_generator: IdGenerator,
    ) -> None:
        self._repository = repository
        self._id_generator = id_generator

    def execute(self, input: RegisterUserInput) -> RegisterUserOutput:
        # 1. Validar e criar value objects
        email = Email(input.email)
        name = UserName(input.name)

        # 2. Criar entidade
        user = User.create(
            id=UserId(self._id_generator.generate()),
            email=email,
            name=name,
        )

        # 3. Persistir
        self._repository.save(user)

        # 4. Retornar output
        return RegisterUserOutput(id=user.id.value, email=email.value)
```

### 4. Adicionar um novo Repository

```python
# 1. Interface no domínio
# src/app/domain/my_context/repositories/user_repository.py
from abc import ABC, abstractmethod

class UserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> None: ...

    @abstractmethod
    def find_by_id(self, user_id: UserId) -> User | None: ...

    @abstractmethod
    def find_by_email(self, email: Email) -> User | None: ...

# 2. Port na aplicação (re-export)
# src/app/application/my_context/ports/repositories.py
from app.domain.my_context.repositories import UserRepository
UserRepositoryPort = UserRepository

# 3. Implementação na infraestrutura
# src/app/infrastructure/persistence/in_memory/user_repository.py
class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self._users: dict[str, User] = {}

    def save(self, user: User) -> None:
        self._users[user.id.value] = user

    def find_by_id(self, user_id: UserId) -> User | None:
        return self._users.get(user_id.value)
```

### 5. Onde colocar validações?

| Tipo de Validação | Onde |
|-------------------|------|
| Formato de dados (email válido, etc.) | Value Object |
| Regras de negócio (não pode completar tarefa já completada) | Entity |
| Validação de input da API (campos obrigatórios) | Interface (Controller/CLI) |
| Regras que envolvem múltiplas entidades | Domain Service |

---

## 📏 Padrões e Convenções

### Conventional Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/) para mensagens de commit:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

**Tipos permitidos:**
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação
- `refactor`: Refatoração
- `perf`: Performance
- `test`: Testes
- `build`: Build system
- `ci`: CI/CD
- `chore`: Manutenção

**Exemplos:**
```bash
feat(domain): add Invoice entity
fix(task): prevent renaming completed tasks
docs: update README with new examples
test(use-cases): add tests for CreateTaskUseCase
```

### Branching

```
main
  └── feature/add-invoice-entity
  └── fix/task-completion-bug
  └── docs/update-readme
```

### Code Style

- **Line length**: 100 caracteres
- **Formatação**: Black
- **Imports**: Ordenados por Ruff (isort)
- **Type hints**: Obrigatórios (MyPy strict)
- **Docstrings**: Google style (onde necessário)

---

## 🧪 Testes

### Estrutura

```
tests/
├── unit/           # Testes isolados, sem I/O
│   ├── domain/     # Entidades, VOs, regras de negócio
│   └── application/ # Use cases com mocks
├── integration/    # Testes com implementações reais
└── conftest.py     # Fixtures compartilhadas
```

### Padrão AAA (Arrange-Act-Assert)

```python
@pytest.mark.unit
def test_complete_task(self) -> None:
    # Arrange - preparar dados
    task = Task.create(
        id=TaskId("task-001"),
        title=TaskTitle("Tarefa"),
        priority=TaskPriority.medium(),
        created_at=datetime.now(timezone.utc),
    )
    completed_at = datetime.now(timezone.utc)

    # Act - executar ação
    task.complete(completed_at)

    # Assert - verificar resultado
    assert task.is_completed
    assert task.completed_at == completed_at
```

### Fixtures para Testes

```python
# tests/conftest.py
@pytest.fixture
def fake_clock() -> FakeClock:
    """Clock com tempo controlável."""
    return FakeClock()

@pytest.fixture
def fake_id_generator() -> FakeIdGenerator:
    """Gerador de IDs previsíveis."""
    return FakeIdGenerator()
```

### Executando

```bash
# Com coverage
make test

# Apenas unitários
make test-unit

# Apenas integração
make test-integration

# Modo rápido (sem coverage)
make test-fast
```

---

## 🏛️ Decisões de Arquitetura

### ADR-001: Exceptions vs Result Pattern

**Decisão**: Este template fornece ambos os padrões. Escolha UM e use consistentemente.

**Exceptions** (abordagem deste template):
```python
# Domínio levanta exceções
class Task:
    def complete(self) -> None:
        if not self._status.is_open:
            raise BusinessRuleViolationException(...)
        # ...

# Use case captura se necessário
try:
    task.complete()
except BusinessRuleViolationException as e:
    # handle error
```

**Result Pattern** (alternativa):
```python
# Domínio retorna Result
class Task:
    def complete(self) -> Result[None, str]:
        if not self._status.is_open:
            return Failure("Tarefa já está fechada")
        # ...
        return Success(None)

# Use case verifica resultado
result = task.complete()
if result.is_failure:
    # handle error
```

### ADR-002: Localização de Domain Events

**Decisão**: Eventos são acumulados nas entidades e despachados pela camada de aplicação.

```python
# Entidade acumula eventos
class Task(Entity[TaskId]):
    def complete(self) -> None:
        # ... lógica
        self.add_event(TaskCompleted(task_id=self.id.value))

# Application despacha após persistir
class CompleteTaskUseCase:
    def execute(self, input: Input) -> Output:
        task.complete()
        self._repository.save(task)
        self._event_dispatcher.dispatch_all(task.clear_events())
```

### ADR-003: Ports na Application vs Domain

**Decisão**: Interfaces de repositório ficam no domínio, com alias na aplicação.

- **Domínio**: Define o contrato (`TaskRepository`)
- **Aplicação**: Re-exporta como port (`TaskRepositoryPort`)
- **Infraestrutura**: Implementa o contrato

---

## 🤝 Contribuindo

### Setup de desenvolvimento

```bash
# Clone e setup
git clone <repo>
cd ddd-python-template
make setup

# Crie uma branch
git checkout -b feature/minha-feature

# Faça suas alterações
# ...

# Verifique qualidade
make check

# Commit (pre-commit hooks irão rodar)
git commit -m "feat(domain): add new feature"
```

### Checklist antes do PR

- [ ] Testes passando (`make test`)
- [ ] Lint passando (`make lint`)
- [ ] Types passando (`make typecheck`)
- [ ] Formatação aplicada (`make format`)
- [ ] Documentação atualizada se necessário
- [ ] Commits seguem Conventional Commits

---

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

---

<div align="center">
  <strong>Feito com ❤️ para a comunidade Python</strong>
</div>
