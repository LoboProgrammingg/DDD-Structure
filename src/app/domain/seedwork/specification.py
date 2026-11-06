"""Specification (Evans, cap. 9): regra de negócio nomeada, testável e combinável.

overdue = OpenTask() & ~AssignedTo(assignee)
overdue.is_satisfied_by(task)
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


class Specification[T](ABC):
    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool: ...

    def __and__(self, other: "Specification[T]") -> "Specification[T]":
        return _AndSpecification(self, other)

    def __or__(self, other: "Specification[T]") -> "Specification[T]":
        return _OrSpecification(self, other)

    def __invert__(self) -> "Specification[T]":
        return _NotSpecification(self)


@dataclass(frozen=True)
class _AndSpecification[T](Specification[T]):
    left: Specification[T]
    right: Specification[T]

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(candidate)


@dataclass(frozen=True)
class _OrSpecification[T](Specification[T]):
    left: Specification[T]
    right: Specification[T]

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.left.is_satisfied_by(candidate) or self.right.is_satisfied_by(candidate)


@dataclass(frozen=True)
class _NotSpecification[T](Specification[T]):
    spec: Specification[T]

    def is_satisfied_by(self, candidate: T) -> bool:
        return not self.spec.is_satisfied_by(candidate)
