import logging
from dataclasses import dataclass

import pytest

from app.domain.seedwork import DomainEvent
from app.infrastructure.messaging import InProcessEventBus


@dataclass(frozen=True, kw_only=True)
class Paid(DomainEvent):
    amount: int


@dataclass(frozen=True, kw_only=True)
class Refunded(DomainEvent):
    amount: int


async def test_delivers_each_event_to_its_subscribers_only() -> None:
    bus = InProcessEventBus()
    received: list[str] = []

    async def on_paid(event: Paid) -> None:
        received.append(f"paid:{event.amount}")

    async def audit(event: Paid) -> None:
        received.append("audit")

    bus.subscribe(Paid, on_paid)
    bus.subscribe(Paid, audit)

    await bus.publish([Paid(amount=10), Refunded(amount=5)])

    assert received == ["paid:10", "audit"]


async def test_failing_handler_does_not_stop_the_others(
    caplog: pytest.LogCaptureFixture,
) -> None:
    bus = InProcessEventBus()
    received: list[int] = []

    async def broken(_: Paid) -> None:
        raise RuntimeError("boom")

    async def healthy(event: Paid) -> None:
        received.append(event.amount)

    bus.subscribe(Paid, broken)
    bus.subscribe(Paid, healthy)

    with caplog.at_level(logging.ERROR):
        await bus.publish([Paid(amount=7)])

    assert received == [7]
    assert "Domain event handler failed" in caplog.text
