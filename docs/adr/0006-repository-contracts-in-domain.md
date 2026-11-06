# ADR 0006: Contratos de repositório no domínio

## Status

Aceito. Substitui o [ADR 0002](0002-repositories-in-application-layer.md).

## Contexto

O ADR 0002 colocou as interfaces de repositório na camada de aplicação,
tratando-as como portas de persistência. Isso contraria Evans: o
**Repository** é um bloco de construção do domínio, que oferece a ilusão de uma
coleção em memória de agregados e fala a Linguagem Ubíqua
(`list_by_assignee`, `next_identity`). O domínio não conhece *como* algo é
persistido, mas sabe *que* agregados podem ser recuperados.

## Decisão

- Cada agregado tem um contrato de repositório em
  `domain/<contexto>/repositories/`, como ABC, só com tipos do domínio.
- Somente raízes de agregado têm repositório.
- A implementação concreta fica em `infrastructure/repositories/`.
- Repositórios não fazem commit: a transação é da Unit of Work (ADR 0007).
- `next_identity()` fica no repositório (Vernon): a identidade existe antes da
  persistência, sem depender de autoincremento do banco.

## Consequências

- Serviços de domínio e especificações podem trabalhar com o contrato.
- O domínio continua sem nenhuma importação de infraestrutura (verificado no
  ADR 0009).
