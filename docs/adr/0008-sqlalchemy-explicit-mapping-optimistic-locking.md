# ADR 0008: SQLAlchemy com mapeamento explícito e concorrência otimista

## Status

Aceito

## Contexto

O domínio precisa de persistência real (PostgreSQL em produção) sem que
entidades herdem de classes do ORM ou carreguem anotações de coluna. Também é
preciso impedir que duas requisições concorrentes sobrescrevam uma à outra
(*lost update*).

## Decisão

- **SQLAlchemy 2 assíncrono**. PostgreSQL (asyncpg) em produção e no CI;
  SQLite (aiosqlite) como padrão local e nos testes rápidos.
- **Modelos ORM separados** (`infrastructure/database/models/`) e
  **mapeamento explícito** ORM ↔ domínio nos repositórios. O agregado é
  reconstituído pelo seu construtor, com Value Objects validados.
- Repositórios mantêm um **Identity Map** por Unit of Work e uma referência
  forte às linhas ORM carregadas. Antes do commit, `sync()` copia o estado de
  todos os agregados rastreados para as linhas: alterar um agregado basta, não
  existe `save()`.
- **Concorrência otimista** com `version_id_col`: todo UPDATE inclui
  `WHERE version = :lida`. Zero linhas afetadas vira
  `ConcurrencyConflictError` (HTTP 409).
- Esquema versionado com **Alembic**; `alembic check` no CI garante que os
  modelos e as migrações não divergem.

## Consequências

- O domínio continua puro e as regras de persistência ficam em um só lugar.
- Mapear à mão é código a mais por agregado, mas é explícito e fácil de testar.
- A referência forte às linhas é obrigatória: a Session do SQLAlchemy guarda
  objetos por referência fraca, e uma linha recarregada traria a versão de
  outra transação, anulando a checagem. O teste
  `test_concurrent_modification_is_detected` cobre esse caso.

## Alternativas consideradas

- **Mapeamento imperativo** (Cosmic Python): elegante, mas exige que entidades
  e Value Objects sejam instrumentáveis pelo ORM, o que conflita com
  dataclasses imutáveis com `slots`.
- **Entidades declarativas do ORM como modelo de domínio**: acopla o domínio ao
  SQLAlchemy.
