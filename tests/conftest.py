import os
from pathlib import Path

import pytest

from tests.fakes import FixedClock, RecordingPublisher


@pytest.fixture
def clock() -> FixedClock:
    return FixedClock()


@pytest.fixture
def publisher() -> RecordingPublisher:
    return RecordingPublisher()


@pytest.fixture
def database_url(tmp_path: Path) -> str:
    """SQLite isolado por teste; defina TEST_DATABASE_URL para rodar contra PostgreSQL."""
    return os.environ.get("TEST_DATABASE_URL") or f"sqlite+aiosqlite:///{tmp_path / 'test.db'}"
