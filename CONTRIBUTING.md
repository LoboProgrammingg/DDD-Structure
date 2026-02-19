# Contribuindo para o DDD Python Template

Obrigado por considerar contribuir! Este documento explica como contribuir de forma efetiva.

## 📋 Índice

- [Código de Conduta](#código-de-conduta)
- [Como posso contribuir?](#como-posso-contribuir)
- [Setup de Desenvolvimento](#setup-de-desenvolvimento)
- [Padrões de Código](#padrões-de-código)
- [Processo de Pull Request](#processo-de-pull-request)
- [Convenções de Commit](#convenções-de-commit)
- [Estrutura de Branches](#estrutura-de-branches)

---

## Código de Conduta

Este projeto segue um código de conduta baseado em respeito mútuo. Esperamos que todos os contribuidores:

- Sejam respeitosos e construtivos em suas comunicações
- Aceitem feedback construtivo com graciosidade
- Foquem no que é melhor para a comunidade e o projeto

---

## Como posso contribuir?

### 🐛 Reportando Bugs

Antes de criar um issue:
1. Verifique se já não existe um issue similar
2. Use a versão mais recente do projeto

Ao criar o issue, inclua:
- Descrição clara do problema
- Passos para reproduzir
- Comportamento esperado vs atual
- Versão do Python e sistema operacional

### 💡 Sugerindo Melhorias

Abra um issue descrevendo:
- O problema ou limitação atual
- Sua proposta de solução
- Impacto esperado

### 🔧 Contribuindo com Código

1. Procure issues marcados como `good first issue` ou `help wanted`
2. Comente no issue que você vai trabalhar nele
3. Siga o processo de Pull Request abaixo

---

## Setup de Desenvolvimento

### Pré-requisitos

- Python 3.12+
- [Poetry](https://python-poetry.org/docs/#installation)
- Git

### Instalação

```bash
# Clone o repositório
git clone <repo-url>
cd ddd-python-template

# Instale dependências
make install

# Instale pre-commit hooks
make install-hooks

# Verifique que tudo funciona
make check
```

### Comandos úteis

```bash
make test          # Executa testes
make lint          # Verifica linting
make format        # Formata código
make typecheck     # Verifica tipos
make check         # Executa tudo
```

---

## Padrões de Código

### Estilo

- **Formatador**: Black (line-length: 100)
- **Linter**: Ruff
- **Type Checker**: MyPy (strict)

### Boas práticas

```python
# ✅ Bom - Type hints explícitos
def create_task(title: str, priority: str) -> Task:
    ...

# ❌ Evitar - Sem type hints
def create_task(title, priority):
    ...
```

```python
# ✅ Bom - Docstrings para funções públicas
def calculate_total(items: list[Item]) -> Money:
    """
    Calcula o total de uma lista de items.

    Args:
        items: Lista de items a serem somados

    Returns:
        Valor total como Money
    """
    ...
```

### Testes

- Use o padrão AAA (Arrange-Act-Assert)
- Marque testes com `@pytest.mark.unit` ou `@pytest.mark.integration`
- Use fixtures do `conftest.py`

```python
@pytest.mark.unit
def test_should_complete_task(self) -> None:
    # Arrange
    task = create_sample_task()

    # Act
    task.complete(datetime.now(timezone.utc))

    # Assert
    assert task.is_completed
```

---

## Processo de Pull Request

### 1. Prepare sua branch

```bash
# Atualize main
git checkout main
git pull origin main

# Crie sua branch
git checkout -b feature/minha-feature
```

### 2. Faça suas alterações

- Commits pequenos e focados
- Siga as convenções de commit
- Adicione testes para novas funcionalidades

### 3. Verifique qualidade

```bash
make check
```

### 4. Abra o PR

- Título descritivo seguindo Conventional Commits
- Descrição explicando o que foi feito e por quê
- Referencie issues relacionados

### 5. Review

- Responda aos comentários
- Faça ajustes se necessário
- Mantenha a branch atualizada com main

---

## Convenções de Commit

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

### Tipos

| Tipo | Descrição |
|------|-----------|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `docs` | Documentação |
| `style` | Formatação (não afeta código) |
| `refactor` | Refatoração |
| `perf` | Melhoria de performance |
| `test` | Adição/correção de testes |
| `build` | Alterações no build |
| `ci` | CI/CD |
| `chore` | Manutenção geral |

### Exemplos

```bash
feat(domain): add Invoice entity with line items
fix(task): prevent modification of completed tasks
docs: add examples for creating new bounded context
test(use-cases): add integration tests for billing
refactor(infra): extract repository base class
```

---

## Estrutura de Branches

```
main                    # Branch principal, sempre estável
├── feature/*           # Novas funcionalidades
├── fix/*               # Correções de bugs
├── docs/*              # Documentação
└── refactor/*          # Refatorações
```

### Nomes de branch

```bash
# ✅ Bom
feature/add-invoice-entity
fix/task-completion-validation
docs/update-contributing-guide

# ❌ Evitar
my-branch
feature1
test
```

---

## Adicionando um novo Bounded Context

Se você está adicionando um novo bounded context:

1. Crie a estrutura de diretórios:
```bash
mkdir -p src/app/domain/my_context/{entities,value_objects,events,repositories,services}
mkdir -p src/app/application/my_context/{use_cases,ports}
```

2. Crie os `__init__.py` com exports adequados

3. Adicione testes em:
```bash
mkdir -p tests/unit/domain/my_context
mkdir -p tests/unit/application/my_context
mkdir -p tests/integration/my_context
```

4. Atualize a documentação se necessário

---

## Dúvidas?

Abra um issue com a tag `question` ou entre em contato com os mantenedores.

**Obrigado por contribuir! 🎉**
