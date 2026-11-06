# ADR 0001: Arquitetura em camadas com regra de dependência

## Status

Aceito

## Contexto

Evans propõe isolar o domínio em uma **Layered Architecture**: a lógica de
negócio não pode se misturar com interface, banco de dados ou frameworks.
Sem essa separação, regras ficam espalhadas por controllers e consultas SQL e
o modelo deixa de expressar o negócio.

## Decisão

Quatro camadas conceituais, mais o composition root:

| Camada | Responsabilidade | Pode depender de |
|--------|------------------|------------------|
| `interfaces` | HTTP (FastAPI) e CLI (Typer): traduz entrada e saída | todas abaixo |
| `bootstrap` | Composition root: monta as implementações concretas | infrastructure, application, domain |
| `infrastructure` | Persistência, mensageria, configuração, adaptadores externos | application, domain |
| `application` | Casos de uso: orquestra, controla transação, não decide regra | domain |
| `domain` | Modelo: agregados, value objects, eventos, serviços de domínio | nada (só a biblioteca padrão) |

Dentro de cada camada, o código é organizado por **bounded context**
(`task_management`, `notification`).

## Consequências

- O domínio é testável sem banco, sem HTTP e sem mocks de framework.
- Trocar FastAPI, SQLAlchemy ou o banco não toca no domínio.
- A regra é verificada automaticamente (ADR 0009), não depende de disciplina.
- Há mais arquivos do que em um CRUD simples; o custo compensa quando o
  domínio tem regras de verdade.

## Alternativas consideradas

- **Organização por tipo técnico** (`models/`, `services/`, `routers/`): mistura
  contextos e esconde a fronteira do domínio.
- **Módulos verticais por contexto** (`task_management/{domain,application,...}`):
  igualmente válido; escolhemos camadas no topo para deixar a regra de
  dependência visível na árvore de diretórios.
