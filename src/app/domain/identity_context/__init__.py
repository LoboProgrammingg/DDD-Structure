"""
Identity Context - Bounded Context para identidade e autenticação.

Este é um bounded context placeholder para demonstrar
como organizar múltiplos contextos no mesmo projeto.

Para implementar este contexto, crie:
- entities/: User, Role, Permission, etc.
- value_objects/: UserId, Email, Password, etc.
- events/: UserRegistered, UserActivated, etc.
- services/: AuthenticationService, etc.

Lembre-se:
- Cada contexto tem sua própria linguagem ubíqua
- Contextos se comunicam via eventos ou ACL (Anti-Corruption Layer)
- Não compartilhe entidades entre contextos
"""
