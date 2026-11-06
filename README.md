<div align="center">

# DDD Structure

**Referência de Domain-Driven Design em Python, do modelo à produção.**

Bounded contexts, agregados, eventos de domínio, Unit of Work, concorrência otimista
e uma arquitetura em camadas que o próprio CI impede de degradar.

[![CI](https://github.com/LoboProgrammingg/DDD-Structure/actions/workflows/ci.yml/badge.svg)](https://github.com/LoboProgrammingg/DDD-Structure/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-async-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![SQLAlchemy 2](https://img.shields.io/badge/SQLAlchemy-2.x-D71F00)](https://www.sqlalchemy.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![mypy: strict](https://img.shields.io/badge/mypy-strict-2A6DB2)](https://mypy-lang.org/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

</div>

---

## Sumário

- [Por que este repositório existe](#por-que-este-repositório-existe)
- [O domínio](#o-domínio)
- [Arquitetura](#arquitetura)
- [Padrões DDD e onde encontrá-los](#padrões-ddd-e-onde-encontrá-los)
- [Começando](#começando)
- [Usando a API](#usando-a-api)
- [Estrutura do projeto](#estrutura-do-projeto)
- [Qualidade](#qualidade)
- [Adicionando um bounded context](#adicionando-um-bounded-context)
- [Decisões de arquitetura](#decisões-de-arquitetura)
- [Referências](#referências)

## Por que este repositório existe

A maioria dos exemplos de DDD mostra classes `Entity` e `ValueObject` e para por
aí. Os problemas difíceis ficam de fora: quando publicar um evento, como impedir
que duas requisições sobrescrevam a mesma tarefa, como dois contextos conversam
sem se acoplar, como garantir que ninguém importe o ORM dentro do domínio daqui a
seis meses.

Este projeto resolve esses pontos com código executável, testado e documentado:

- **Domínio puro.** Nenhuma importação de framework na camada de domínio,
  verificada a cada commit.
- **Eventos publicados só depois do commit.** Nada de reagir a uma mudança que
  depois sofreu rollback.
- **Concorrência otimista.** Escritas concorrentes resultam em `409 Conflict`,
  nunca em *lost update*.
- **Dois bounded contexts reais** integrados por eventos e por uma
  Anti-Corruption Layer.
- **CQRS-lite.** Commands passam pelo agregado; queries leem projeções.
- **Problem Details (RFC 9457)** para todo erro de domínio e de aplicação.
- **132 testes, ~98% de cobertura**, rodando contra PostgreSQL no CI.

## O domínio

Gestão de tarefas com regras de negócio de verdade:

- uma tarefa encerrada (concluída ou cancelada) não pode mais ser alterada;
- o status muda apenas por transições permitidas;
- só tarefas com responsável podem ser iniciadas;
- cada responsável tem um limite de tarefas em andamento (WIP);
- o prazo não pode ser anterior à criação;
- ao receber uma tarefa, o responsável é notificado.

```mermaid
stateDiagram-v2
    [*] --> pending: criar
    pending --> in_progress: iniciar (exige responsável e respeita o WIP)
    pending --> completed: concluir
    pending --> cancelled: cancelar
    in_progress --> completed: concluir
    in_progress --> cancelled: cancelar
    completed --> [*]
    cancelled --> [*]
```

Os termos de negócio estão no glossário da
[Linguagem Ubíqua](docs/ubiquitous-language.md), e os contextos e suas relações
no [Context Map](docs/context-map.md):

| Bounded context | Tipo | Responsabilidade |
|-----------------|------|------------------|
| **Task Management** | Core Domain | Ciclo de vida das tarefas, prazos, limite de WIP |
| **Notification** | Generic Subdomain | Avisos às pessoas, independente da origem |

```mermaid
flowchart LR
    TM["Task Management<br/>(Core)"] -- "TaskAssigned<br/>(Published Language)" --> ACL{{"Anti-Corruption Layer"}}
    ACL -- "SendNotification" --> N["Notification<br/>(Generic)"]
```

## Arquitetura

A Layered Architecture de Eric Evans, com a regra de dependência apontando
sempre para o domínio:

```mermaid
flowchart TB
    I["<b>interfaces</b><br/>FastAPI · Typer"] --> B["<b>bootstrap</b><br/>Composition Root"]
    B --> INF["<b>infrastructure</b><br/>SQLAlchemy · Alembic · Event Bus · ACL"]
    INF --> APP["<b>application</b><br/>Commands · Queries · Unit of Work · Portas"]
    APP --> D["<b>domain</b><br/>Agregados · Value Objects · Eventos · Domain Services"]
```

Cada camada é organizada por bounded context. As regras são verificadas pelo
[import-linter](https://import-linter.readthedocs.io/) em cinco contratos: ordem das
camadas, domínio e aplicação livres de frameworks, e independência entre
contextos.

Como um comando atravessa o sistema:

```mermaid
sequenceDiagram
    autonumber
    participant API as Router (interfaces)
    participant H as StartTaskHandler (application)
    participant UoW as Unit of Work
    participant P as WorkInProgressPolicy (domain)
    participant T as Task (domain)
    participant DB as PostgreSQL
    participant Bus as Event Bus

    API->>H: StartTask(task_id)
    H->>UoW: abre transação
    H->>UoW: tasks.get(id), tasks.list_by_assignee(...)
    H->>P: start(task, tarefas_do_responsável)
    P->>T: start()
    T-->>T: valida e registra TaskStarted
    H->>UoW: commit()
    UoW->>DB: UPDATE ... WHERE version = n, depois COMMIT
    UoW->>Bus: publica TaskStarted
```

Mais detalhes em [docs/architecture.md](docs/architecture.md).

## Padrões DDD e onde encontrá-los

| Padrão | Arquivo |
|--------|---------|
| Entity | [`domain/seedwork/entity.py`](src/app/domain/seedwork/entity.py) |
| Aggregate Root | [`domain/seedwork/aggregate_root.py`](src/app/domain/seedwork/aggregate_root.py) · [`Task`](src/app/domain/task_management/aggregates/task.py) |
| Value Object | [`domain/task_management/value_objects/`](src/app/domain/task_management/value_objects) |
| Domain Event | [`domain/task_management/events/task_events.py`](src/app/domain/task_management/events/task_events.py) |
| Domain Service | [`WorkInProgressPolicy`](src/app/domain/task_management/services/work_in_progress_policy.py) |
| Specification | [`seedwork/specification.py`](src/app/domain/seedwork/specification.py) · [`task_specifications.py`](src/app/domain/task_management/specifications/task_specifications.py) |
| Factory | `Task.create`, `Notification.create` |
| Repository | [contrato no domínio](src/app/domain/task_management/repositories/task_repository.py) · [implementação SQLAlchemy](src/app/infrastructure/repositories/sqlalchemy_task_repository.py) |
| Unit of Work | [porta](src/app/application/shared/unit_of_work.py) · [implementação](src/app/infrastructure/unit_of_work.py) |
| Application Service | [`application/task_management/commands/`](src/app/application/task_management/commands) |
| Read Model (CQRS) | [`infrastructure/read_models/`](src/app/infrastructure/read_models) |
| Anti-Corruption Layer | [`TaskEventsTranslator`](src/app/infrastructure/notification/acl/task_events_translator.py) |
| Composition Root | [`bootstrap/container.py`](src/app/bootstrap/container.py) |

## Começando

### Pré-requisitos

- Python 3.12+
- [Poetry](https://python-poetry.org/) 2.x
- Docker (opcional, para PostgreSQL)

### Local (SQLite)

```bash
git clone https://github.com/LoboProgrammingg/DDD-Structure.git
cd DDD-Structure
cp .env.example .env

make install    # dependências + hooks de pre-commit
make migrate    # aplica as migrações
make run        # http://localhost:8000/docs
```

### Docker (PostgreSQL)

```bash
make up         # PostgreSQL + API; as migrações rodam na subida
make down
```

Todos os comandos: `make help`.

## Usando a API

A documentação interativa fica em `/docs`. Os endpoints são orientados a
comandos: cada verbo do negócio é uma ação explícita, mantendo a Linguagem
Ubíqua também no contrato HTTP.

| Método | Rota | Ação |
|--------|------|------|
| `POST` | `/api/v1/tasks` | Criar tarefa |
| `GET` | `/api/v1/tasks?status=&assignee_id=&limit=&offset=` | Listar |
| `GET` | `/api/v1/tasks/{id}` | Consultar |
| `POST` | `/api/v1/tasks/{id}/rename` | Renomear |
| `POST` | `/api/v1/tasks/{id}/reprioritize` | Repriorizar |
| `POST` | `/api/v1/tasks/{id}/assign` | Atribuir responsável |
| `POST` | `/api/v1/tasks/{id}/start` | Iniciar |
| `POST` | `/api/v1/tasks/{id}/complete` | Concluir |
| `POST` | `/api/v1/tasks/{id}/cancel` | Cancelar |
| `GET` | `/health/live` · `/health/ready` | Liveness e readiness (com checagem do banco) |

```bash
# Criar
curl -s -X POST localhost:8000/api/v1/tasks \
  -H 'Content-Type: application/json' \
  -d '{"title": "Desenhar o context map", "priority": "high", "due_date": "2026-12-01"}'

# Atribuir (dispara TaskAssigned, e o contexto Notification avisa o responsável)
curl -s -X POST localhost:8000/api/v1/tasks/<id>/assign \
  -H 'Content-Type: application/json' -d '{"assignee_id": "ana.souza"}'

# Iniciar e concluir
curl -s -X POST localhost:8000/api/v1/tasks/<id>/start
curl -s -X POST localhost:8000/api/v1/tasks/<id>/complete
```

Violação de regra de negócio:

```http
HTTP/1.1 409 Conflict
Content-Type: application/problem+json

{
  "type": "about:blank",
  "title": "Conflict",
  "status": 409,
  "detail": "A tarefa está 'completed' e não pode ser alterada.",
  "code": "task_is_closed",
  "instance": "/api/v1/tasks/3f1c.../rename"
}
```

| Erro | HTTP |
|------|------|
| Invariante violada (`InvalidTaskTitle`, `InvalidTaskId`...) | 422 |
| Regra de negócio violada (`TaskIsClosed`, `WorkInProgressLimitExceeded`...) | 409 |
| Recurso inexistente | 404 |
| Escrita concorrente detectada | 409 |

### CLI

Os mesmos casos de uso, por outro adaptador de entrada:

```bash
poetry run task-cli create "Revisar ADRs" --priority high
poetry run task-cli assign <id> ana.souza
poetry run task-cli start <id>
poetry run task-cli list --status in_progress
```

## Estrutura do projeto

```text
src/app/
├── domain/                     # Regras de negócio puras (só a biblioteca padrão)
│   ├── seedwork/               # Entity, AggregateRoot, ValueObject, DomainEvent, Specification
│   ├── task_management/        # Core Domain
│   │   ├── aggregates/         # Task (raiz do agregado)
│   │   ├── value_objects/      # TaskId, TaskTitle, TaskStatus, DueDate, AssigneeId...
│   │   ├── events/             # TaskCreated, TaskAssigned, TaskCompleted...
│   │   ├── exceptions/         # Erros tipados na Linguagem Ubíqua
│   │   ├── repositories/       # Contrato do repositório
│   │   ├── services/           # WorkInProgressPolicy
│   │   └── specifications/     # OpenTask, InProgressTask, OverdueTask, AssignedTo
│   └── notification/           # Generic Subdomain (mesma estrutura)
├── application/                # Casos de uso: orquestram, não decidem
│   ├── shared/                 # UnitOfWork, EventPublisher, Clock, erros de aplicação
│   ├── task_management/
│   │   ├── commands/           # Um arquivo por caso de uso: command + handler
│   │   ├── queries/            # GetTask, ListTasks
│   │   ├── ports/              # TaskManagementUnitOfWork, TaskReadModel
│   │   └── dtos.py
│   └── notification/
├── infrastructure/             # Implementações das portas
│   ├── config/                 # Pydantic Settings
│   ├── database/               # Engine, sessão, modelos ORM
│   ├── repositories/           # Repositórios SQLAlchemy (Identity Map + mapeamento explícito)
│   ├── unit_of_work.py         # Transação, concorrência otimista, publicação pós-commit
│   ├── read_models/            # Consultas SQL que devolvem DTOs
│   ├── messaging/              # Event bus em processo
│   ├── notification/           # Canal de entrega e Anti-Corruption Layer
│   ├── providers/              # SystemClock
│   └── logging/                # Logs estruturados (JSON / console)
├── bootstrap/                  # Composition Root
└── interfaces/                 # Adaptadores de entrada
    ├── api/                    # FastAPI: routers v1, schemas, Problem Details, request id
    └── cli/                    # Typer

tests/
├── unit/                       # domínio e aplicação, sem I/O
├── integration/                # SQLAlchemy real: mapeamento, rollback, concorrência, fluxo entre contextos
└── e2e/                        # contrato HTTP

docs/
├── architecture.md
├── context-map.md
├── ubiquitous-language.md
└── adr/                        # Architecture Decision Records
migrations/                     # Alembic
```

## Qualidade

```bash
make check      # lint + tipos + arquitetura + testes (o mesmo que o CI)
```

| Verificação | Ferramenta | Onde roda |
|-------------|------------|-----------|
| Lint e formatação | Ruff | pre-commit, CI |
| Tipos | mypy `--strict` (código e testes) | pre-commit, CI |
| Arquitetura | import-linter (5 contratos) | pre-commit, CI |
| Testes | pytest + pytest-asyncio, cobertura mínima de 90% | CI, contra PostgreSQL 17 |
| Migrações | `alembic upgrade`, `check` e `downgrade` | CI |
| Imagem | Docker multi-stage, usuário sem privilégios | CI |
| Commits | Conventional Commits | hook `commit-msg` |

Integração e e2e usam SQLite por padrão. Para rodar contra PostgreSQL:

```bash
docker compose up -d db
TEST_DATABASE_URL=postgresql+asyncpg://ddd:ddd@localhost:5432/ddd make test
```

## Adicionando um bounded context

1. Descreva os termos do novo contexto em `docs/ubiquitous-language.md` e sua
   relação com os demais em `docs/context-map.md`.
2. Crie o modelo em `src/app/domain/<contexto>/` (agregados, value objects,
   eventos, exceções, contrato de repositório). Só biblioteca padrão.
3. Crie os casos de uso em `src/app/application/<contexto>/` com a sua Unit of
   Work (`ports/unit_of_work.py`) e um arquivo por comando.
4. Implemente modelos ORM, repositório e Unit of Work em `src/app/infrastructure/`
   e gere a migração com `make migration m="..."`.
5. Integre com outros contextos por eventos. Se precisar consumir o modelo de
   outro contexto, traduza numa Anti-Corruption Layer na infraestrutura.
6. Registre o wiring em `bootstrap/container.py` e exponha em `interfaces/`.
7. Adicione o contexto aos contratos `independence` do import-linter no
   `pyproject.toml`.

## Decisões de arquitetura

Cada escolha relevante tem um ADR com contexto, alternativas e consequências.
Decisões revistas continuam no histórico, marcadas como substituídas.

| ADR | Decisão |
|-----|---------|
| [0001](docs/adr/0001-clean-architecture-layers.md) | Arquitetura em camadas com regra de dependência |
| [0004](docs/adr/0004-composition-root.md) | Composition Root explícito, sem framework de DI |
| [0005](docs/adr/0005-config-strategy.md) | Configuração centralizada com Pydantic Settings |
| [0006](docs/adr/0006-repository-contracts-in-domain.md) | Contratos de repositório no domínio |
| [0007](docs/adr/0007-unit-of-work-and-post-commit-events.md) | Unit of Work e publicação de eventos após o commit |
| [0008](docs/adr/0008-sqlalchemy-explicit-mapping-optimistic-locking.md) | SQLAlchemy com mapeamento explícito e concorrência otimista |
| [0009](docs/adr/0009-architecture-contracts-import-linter.md) | Contratos de arquitetura com import-linter |
| [0010](docs/adr/0010-cqrs-read-model.md) | Lado de leitura separado (CQRS-lite) |

Índice completo em [docs/adr](docs/adr/README.md).

## Referências

- Eric Evans, *Domain-Driven Design: Tackling Complexity in the Heart of Software* (2003)
- Vaughn Vernon, *Implementing Domain-Driven Design* (2013) e
  [*Effective Aggregate Design*](https://www.dddcommunity.org/library/vernon_2011/)
- Harry Percival e Bob Gregory, [*Architecture Patterns with Python*](https://www.cosmicpython.com/)
- Martin Fowler, [Unit of Work](https://martinfowler.com/eaaCatalog/unitOfWork.html) e
  [Specification](https://martinfowler.com/apsupp/spec.pdf)
- [RFC 9457: Problem Details for HTTP APIs](https://www.rfc-editor.org/rfc/rfc9457)

## Contribuindo

Veja o [guia de contribuição](CONTRIBUTING.md).

## Licença

[MIT](LICENSE) © Matheus Lobo Camara
