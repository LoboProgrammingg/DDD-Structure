"""
Configurações e fixtures compartilhadas para testes.

Este arquivo é carregado automaticamente pelo pytest e contém
fixtures que podem ser usadas em todos os testes.
"""

from datetime import UTC, datetime

import pytest

from app.application.sample_context.ports import Clock, IdGenerator


class FakeClock(Clock):
    """Clock falso para testes que permite controlar o tempo."""

    def __init__(self, fixed_time: datetime | None = None) -> None:
        self._time = fixed_time or datetime(2024, 1, 15, 10, 30, 0, tzinfo=UTC)

    def now(self) -> datetime:
        return self._time

    def set_time(self, time: datetime) -> None:
        self._time = time


class FakeIdGenerator(IdGenerator):
    """Gerador de IDs falso para testes que permite IDs previsíveis."""

    def __init__(self, prefix: str = "test") -> None:
        self._counter = 0
        self._prefix = prefix

    def generate(self) -> str:
        self._counter += 1
        return f"{self._prefix}-{self._counter:04d}"

    def reset(self) -> None:
        self._counter = 0


@pytest.fixture
def fake_clock() -> FakeClock:
    """Fixture que fornece um clock falso para testes."""
    return FakeClock()


@pytest.fixture
def fake_id_generator() -> FakeIdGenerator:
    """Fixture que fornece um gerador de IDs falso para testes."""
    return FakeIdGenerator()
