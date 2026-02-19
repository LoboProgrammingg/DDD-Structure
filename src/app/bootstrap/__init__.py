"""
Bootstrap e Composition Root da aplicação.

Este módulo é responsável por:
- Configurar a aplicação (logging, settings)
- Criar e conectar todas as dependências (DI container)
- Fornecer pontos de entrada para diferentes interfaces (CLI, API)

O que é Composition Root?
É o único lugar onde as dependências são criadas e conectadas.
Todos os use cases, repositories, providers, etc. são instanciados aqui.

Por que isso é importante?
- Centraliza a criação de dependências
- Facilita testes (basta trocar o container)
- Evita "new" espalhados pelo código
- Documenta todas as dependências em um lugar
- Permite trocar implementações facilmente
"""

from app.bootstrap.container import Container, create_container


__all__ = ["Container", "create_container"]
