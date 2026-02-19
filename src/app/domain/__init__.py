"""
Camada de Domínio (Domain Layer).

Esta é a camada mais interna da arquitetura e contém:
- Entidades: objetos com identidade única
- Value Objects: objetos imutáveis definidos por seus atributos
- Domain Services: lógica que não pertence a uma entidade específica
- Domain Events: eventos que representam algo que aconteceu no domínio
- Repository Interfaces: contratos para persistência (apenas interfaces aqui)

REGRAS IMPORTANTES:
1. Esta camada NÃO pode depender de nenhuma outra camada
2. Nenhum import de frameworks ou bibliotecas de infraestrutura
3. Toda lógica de negócio deve residir aqui
4. Entidades e VOs devem ser sempre válidos (validação no construtor)
"""
