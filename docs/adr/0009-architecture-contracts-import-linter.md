# ADR 0009: Contratos de arquitetura verificados pelo import-linter

## Status

Aceito

## Contexto

Regras de arquitetura documentadas e não verificadas se degradam: basta um
import "temporário" do SQLAlchemy no domínio para a fronteira deixar de existir.

## Decisão

[import-linter](https://import-linter.readthedocs.io/) roda no pre-commit e no CI
com cinco contratos em `pyproject.toml`:

1. **Camadas**: `interfaces > bootstrap > infrastructure > application > domain`.
2. **Domínio livre de frameworks**: proibido importar SQLAlchemy, FastAPI,
   Starlette, Pydantic, Alembic ou Typer.
3. **Aplicação livre de frameworks**: mesma regra.
4. **Contextos do domínio independentes**: `task_management` e `notification`
   não se importam.
5. **Contextos da aplicação independentes**: idem.

A integração entre contextos acontece na infraestrutura, por uma
Anti-Corruption Layer (ver `docs/context-map.md`).

## Consequências

- Violação de arquitetura quebra o build, com a cadeia de imports no relatório.
- Um novo bounded context precisa ser adicionado aos contratos de independência.
