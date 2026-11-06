from datetime import UTC, datetime

from app.application.shared import Clock


class SystemClock(Clock):
    def now(self) -> datetime:
        return datetime.now(UTC)
