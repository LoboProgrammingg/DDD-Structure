"""Hierarquia de erros do domínio.

* ``InvariantViolation``: um valor nunca poderia existir (ex.: título vazio).
* ``BusinessRuleViolation``: a operação não é permitida no estado atual
  (ex.: concluir uma tarefa cancelada).
"""

from typing import ClassVar


class DomainError(Exception):
    code: ClassVar[str] = "domain_error"

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class InvariantViolation(DomainError):
    code: ClassVar[str] = "invariant_violation"


class BusinessRuleViolation(DomainError):
    code: ClassVar[str] = "business_rule_violation"
