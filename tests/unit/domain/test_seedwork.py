from dataclasses import FrozenInstanceError, dataclass

import pytest

from app.domain.seedwork import AggregateRoot, DomainEvent, Entity, Specification, ValueObject


class Account(Entity[int]):
    pass


class Invoice(Entity[int]):
    pass


@dataclass(frozen=True, kw_only=True)
class SomethingHappened(DomainEvent):
    detail: str


class Order(AggregateRoot[int]):
    def place(self) -> None:
        self._record(SomethingHappened(detail="placed"))


@dataclass(frozen=True, slots=True)
class Money(ValueObject):
    amount: int
    currency: str


class IsEven(Specification[int]):
    def is_satisfied_by(self, candidate: int) -> bool:
        return candidate % 2 == 0


class IsPositive(Specification[int]):
    def is_satisfied_by(self, candidate: int) -> bool:
        return candidate > 0


class TestEntity:
    def test_entities_with_same_type_and_id_are_equal(self) -> None:
        assert Account(1) == Account(1)
        assert hash(Account(1)) == hash(Account(1))

    def test_entities_of_different_types_are_never_equal(self) -> None:
        assert Account(1) != Invoice(1)

    def test_entity_is_not_equal_to_other_objects(self) -> None:
        assert Account(1) != 1


class TestAggregateRoot:
    def test_pull_events_returns_recorded_events_once(self) -> None:
        order = Order(1)
        order.place()

        assert [event.detail for event in order.pull_events()] == ["placed"]  # type: ignore[attr-defined]
        assert order.pull_events() == []

    def test_version_starts_at_zero(self) -> None:
        assert Order(1).version == 0


class TestValueObject:
    def test_equality_is_structural(self) -> None:
        assert Money(10, "BRL") == Money(10, "BRL")
        assert Money(10, "BRL") != Money(10, "USD")

    def test_is_immutable(self) -> None:
        money = Money(10, "BRL")
        with pytest.raises(FrozenInstanceError):
            money.amount = 20  # type: ignore[misc]


class TestDomainEvent:
    def test_carries_identity_timestamp_and_name(self) -> None:
        event = SomethingHappened(detail="x")

        assert event.event_id != SomethingHappened(detail="x").event_id
        assert event.occurred_at.tzinfo is not None
        assert event.name == "SomethingHappened"


class TestSpecification:
    @pytest.mark.parametrize(
        ("candidate", "expected"), [(4, True), (3, False), (-2, False), (-3, False)]
    )
    def test_and(self, candidate: int, expected: bool) -> None:
        assert (IsEven() & IsPositive()).is_satisfied_by(candidate) is expected

    @pytest.mark.parametrize(("candidate", "expected"), [(4, True), (3, True), (-3, False)])
    def test_or(self, candidate: int, expected: bool) -> None:
        assert (IsEven() | IsPositive()).is_satisfied_by(candidate) is expected

    def test_not(self) -> None:
        assert (~IsEven()).is_satisfied_by(3)
        assert not (~IsEven()).is_satisfied_by(4)
