"""SSE transport integration for guidance events.

This module provides concrete implementations of the EventEmitter protocol
to integrate with MCP's SSE transport layer, enabling guidance events to be
sent through the actual SSE connection.
"""

import asyncio
import logging
from typing import Any
from weakref import WeakSet

from .sse_events import EventEmitter

# Set up logging for connection tracking
logger = logging.getLogger(__name__)


class SSEConnection:
    """Represents a single SSE connection with retry logic."""

    def __init__(self, connection_id: str, send_func: Any):
        """Initialize SSE connection.

        Args:
            connection_id: Unique identifier for this connection
            send_func: Function to send data through the connection
        """
        self.connection_id = connection_id
        self.send_func = send_func
        self.is_active = True
        self.retry_count = 0
        self.max_retries = 3

    async def send(self, data: str) -> bool:
        """Send data through this connection with retry logic.

        Args:
            data: SSE formatted data to send

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.is_active:
            return False

        for attempt in range(self.max_retries + 1):
            try:
                await self.send_func(data)
                self.retry_count = 0  # Reset on success
                return True
            except Exception as e:
                self.retry_count += 1
                logger.warning(
                    "SSE send failed for connection %s, attempt %d/%d: %s",
                    self.connection_id,
                    attempt + 1,
                    self.max_retries + 1,
                    e,
                )

                if attempt < self.max_retries:
                    # Exponential backoff
                    wait_time = 2**attempt
                    await asyncio.sleep(wait_time)
                else:
                    # Mark as inactive after max retries
                    self.is_active = False
                    logger.exception(
                        "SSE connection %s marked inactive after %d failed attempts",
                        self.connection_id,
                        self.max_retries + 1,
                    )

        return False

    def close(self) -> None:
        """Mark connection as inactive."""
        self.is_active = False


class GuidanceSSEEmitter(EventEmitter):
    """Concrete SSE emitter for guidance events with robust connection handling."""

    def __init__(self) -> None:
        """Initialize the SSE emitter."""
        self._connections: WeakSet[SSEConnection] = WeakSet()
        self._event_counter = 0

    def add_connection(self, connection_id: str, send_func: Any) -> SSEConnection:
        """Add a new SSE connection.

        Args:
            connection_id: Unique identifier for the connection
            send_func: Function to send data through the connection

        Returns:
            The created SSE connection object
        """
        connection = SSEConnection(connection_id, send_func)
        self._connections.add(connection)
        logger.info("Added SSE connection: %s", connection_id)
        return connection

    def remove_connection(self, connection: SSEConnection) -> None:
        """Remove an SSE connection.

        Args:
            connection: The connection to remove
        """
        connection.close()
        self._connections.discard(connection)
        logger.info("Removed SSE connection: %s", connection.connection_id)

    async def emit(self, event_data: str) -> None:
        """Emit SSE event to all active connections.

        Args:
            event_data: The SSE formatted event data
        """
        if not self._connections:
            # No connections, but don't break the flow (graceful degradation)
            return

        self._event_counter += 1

        # Add retry instruction to SSE event for client-side reconnection
        enhanced_data = f"retry: 3000\\n{event_data}"

        # Send to all active connections
        active_connections = [conn for conn in self._connections if conn.is_active]

        if not active_connections:
            logger.debug("No active SSE connections for guidance event")
            return

        # Send to all connections concurrently
        tasks = [conn.send(enhanced_data) for conn in active_connections]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Log results
        successful = sum(1 for result in results if result is True)
        failed = len(results) - successful

        if successful > 0:
            logger.debug("Guidance event sent to %d connections", successful)
        if failed > 0:
            logger.warning("Failed to send guidance event to %d connections", failed)

        # Clean up inactive connections
        inactive_connections = [conn for conn in self._connections if not conn.is_active]
        for conn in inactive_connections:
            self._connections.discard(conn)

    def get_connection_count(self) -> int:
        """Get the number of active connections."""
        return len([conn for conn in self._connections if conn.is_active])

    def get_total_events_sent(self) -> int:
        """Get the total number of events sent."""
        return self._event_counter


class MockSSEEmitter(EventEmitter):
    """Mock SSE emitter for testing and development."""

    def __init__(self, log_events: bool = True):
        """Initialize mock emitter.

        Args:
            log_events: Whether to log events to console
        """
        self.log_events = log_events
        self.sent_events: list[str] = []

    async def emit(self, event_data: str) -> None:
        """Mock emit that logs events instead of sending them."""
        self.sent_events.append(event_data)

        if self.log_events:
            logger.info("Mock SSE Event: %s...", event_data[:100])

    def clear_events(self) -> None:
        """Clear sent events history."""
        self.sent_events.clear()

    def get_event_count(self) -> int:
        """Get number of events sent."""
        return len(self.sent_events)


# Global emitter instance
_global_emitter: EventEmitter | None = None


def set_sse_emitter(emitter: EventEmitter) -> None:
    """Set the global SSE emitter for guidance events.

    Args:
        emitter: The SSE emitter to use globally
    """
    global _global_emitter
    _global_emitter = emitter

    # Configure the guidance event manager to use this emitter
    from .sse_events import set_global_emitter

    set_global_emitter(emitter)

    logger.info("Global SSE emitter set to: %s", type(emitter).__name__)


def get_sse_emitter() -> EventEmitter | None:
    """Get the current global SSE emitter."""
    return _global_emitter


def create_development_emitter() -> MockSSEEmitter:
    """Create a mock emitter for development and testing."""
    mock_emitter = MockSSEEmitter(log_events=True)
    set_sse_emitter(mock_emitter)
    return mock_emitter
