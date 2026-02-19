"""
Testes unitários para o Event Dispatcher.
"""

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from app.domain.common.events import DomainEvent
from app.infrastructure.messaging.event_dispatcher import EventDispatcher


class SampleEvent(DomainEvent):
    """Evento de exemplo para testes."""

    def __init__(self, data: str) -> None:
        super().__init__()
        self.data = data


class AnotherEvent(DomainEvent):
    """Outro evento de exemplo para testes."""

    def __init__(self, value: int) -> None:
        super().__init__()
        self.value = value


@pytest.mark.unit
class TestEventDispatcher:
    """Testes para EventDispatcher."""

    def test_should_dispatch_event_to_registered_handler(self) -> None:
        # Arrange
        dispatcher = EventDispatcher()
        handler = MagicMock()
        event = SampleEvent(data="test")

        dispatcher.register(SampleEvent, handler)

        # Act
        dispatcher.dispatch(event)

        # Assert
        handler.assert_called_once_with(event)

    def test_should_dispatch_to_multiple_handlers(self) -> None:
        # Arrange
        dispatcher = EventDispatcher()
        handler1 = MagicMock()
        handler2 = MagicMock()
        event = SampleEvent(data="test")

        dispatcher.register(SampleEvent, handler1)
        dispatcher.register(SampleEvent, handler2)

        # Act
        dispatcher.dispatch(event)

        # Assert
        handler1.assert_called_once_with(event)
        handler2.assert_called_once_with(event)

    def test_should_not_dispatch_to_unregistered_event_type(self) -> None:
        # Arrange
        dispatcher = EventDispatcher()
        handler = MagicMock()
        event = AnotherEvent(value=42)

        dispatcher.register(SampleEvent, handler)

        # Act
        dispatcher.dispatch(event)

        # Assert
        handler.assert_not_called()

    def test_should_dispatch_to_global_handlers(self) -> None:
        # Arrange
        dispatcher = EventDispatcher()
        global_handler = MagicMock()
        event = SampleEvent(data="test")

        dispatcher.register_global(global_handler)

        # Act
        dispatcher.dispatch(event)

        # Assert
        global_handler.assert_called_once_with(event)

    def test_should_dispatch_to_both_global_and_specific_handlers(self) -> None:
        # Arrange
        dispatcher = EventDispatcher()
        global_handler = MagicMock()
        specific_handler = MagicMock()
        event = SampleEvent(data="test")

        dispatcher.register_global(global_handler)
        dispatcher.register(SampleEvent, specific_handler)

        # Act
        dispatcher.dispatch(event)

        # Assert
        global_handler.assert_called_once_with(event)
        specific_handler.assert_called_once_with(event)

    def test_should_dispatch_all_events(self) -> None:
        # Arrange
        dispatcher = EventDispatcher()
        handler = MagicMock()
        events = [SampleEvent(data="1"), SampleEvent(data="2")]

        dispatcher.register(SampleEvent, handler)

        # Act
        dispatcher.dispatch_all(events)

        # Assert
        assert handler.call_count == 2

    def test_should_unregister_handler(self) -> None:
        # Arrange
        dispatcher = EventDispatcher()
        handler = MagicMock()
        event = SampleEvent(data="test")

        dispatcher.register(SampleEvent, handler)
        dispatcher.unregister(SampleEvent, handler)

        # Act
        dispatcher.dispatch(event)

        # Assert
        handler.assert_not_called()

    def test_should_clear_all_handlers(self) -> None:
        # Arrange
        dispatcher = EventDispatcher()
        handler = MagicMock()
        global_handler = MagicMock()
        event = SampleEvent(data="test")

        dispatcher.register(SampleEvent, handler)
        dispatcher.register_global(global_handler)
        dispatcher.clear()

        # Act
        dispatcher.dispatch(event)

        # Assert
        handler.assert_not_called()
        global_handler.assert_not_called()

    def test_should_handle_exception_in_handler_gracefully(self) -> None:
        # Arrange
        dispatcher = EventDispatcher()
        failing_handler = MagicMock(side_effect=Exception("Handler error"))
        working_handler = MagicMock()
        event = SampleEvent(data="test")

        dispatcher.register(SampleEvent, failing_handler)
        dispatcher.register(SampleEvent, working_handler)

        # Act - não deve levantar exceção
        dispatcher.dispatch(event)

        # Assert - segundo handler ainda deve ser chamado
        failing_handler.assert_called_once()
        working_handler.assert_called_once()
