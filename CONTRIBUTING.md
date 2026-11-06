# Contribuindo

Obrigado pelo interesse! Este guia resume como preparar o ambiente, os padrões
do projeto e o fluxo de Pull Request.

## Ambiente

```bash
make install    # dependências + hooks (pre-commit e commit-msg)
make migrate
make check      # lint, tipos, contratos de arquitetura e testes
```

Requisitos: Python 3.12+, Poetry 2.x e, opcionalmente, Docker.

## Onde cada coisa mora

Antes de escrever código, identifique a camada:

| Se a mudança é... | Ela vai em... |
|-------------------|---------------|
| Uma regra de negócio ou invariante | `domain/<contexto>/` (agregado, value object, domain service ou specification) |
| A orquestração de um caso de uso | `application/<contexto>/commands/` ou `queries/` |
| Persistência, mensageria ou integração externa | `infrastructure/` |
| Formato de entrada e saída (HTTP, CLI) | `interfaces/` |
| Montagem de dependências | `bootstrap/container.py` |

Regras que o CI verifica:

- O domínio importa apenas a biblioteca padrão.
- Domínio e aplicação não importam SQLAlchemy, FastAPI, Pydantic, Alembic nem Typer.
- Bounded contexts não se importam entre si; integração acontece por eventos e
  Anti-Corruption Layer.

## Padrões de código

- **Linguagem Ubíqua**: nomes de classes, métodos e eventos vêm do
  [glossário](docs/ubiquitous-language.md). Termo novo? Atualize o glossário no
  mesmo PR.
- **Value Objects** são `@dataclass(frozen=True, slots=True)` e validam no
  `__post_init__`.
- **Agregados** mudam de estado apenas por métodos com nome de negócio e
  registram Domain Events com `_record()`.
- **Erros** são exceções tipadas: `InvariantViolation` para valores impossíveis,
  `BusinessRuleViolation` para operações proibidas no estado atual.
- **Casos de uso** abrem uma Unit of Work, delegam ao domínio e fazem `commit()`.
  Nada de regra de negócio em handlers ou routers.
- Tipagem completa (`mypy --strict`), Ruff para lint e formatação.

## Testes

- Um teste por comportamento, nomeado pelo comportamento:
  `test_closed_task_rejects_changes`.
- Domínio: testes unitários sem nenhum dublê.
- Aplicação: fakes de `tests/fakes.py`.
- Persistência e API: banco real (SQLite local, PostgreSQL no CI via
  `TEST_DATABASE_URL`).
- Cobertura mínima: 90%.

## Commits

[Conventional Commits](https://www.conventionalcommits.org/pt-br/), validados
pelo hook `commit-msg`:

```text
feat(domain): add due date rescheduling to Task
fix(infrastructure): keep ORM rows referenced during the unit of work
docs(adr): record outbox adoption
```

Tipos: `feat`, `fix`, `refactor`, `perf`, `test`, `docs`, `build`, `ci`, `chore`.

## Pull Requests

1. Crie uma branch a partir de `main` (`feat/<assunto>`, `fix/<assunto>`).
2. Mudou o esquema? Gere a migração com `make migration m="..."` e revise.
3. Decisão arquitetural relevante? Registre um ADR em `docs/adr/`.
4. Rode `make check`.
5. Abra o PR preenchendo o template.

## Adicionando um bounded context

Siga o passo a passo do [README](README.md#adicionando-um-bounded-context).
