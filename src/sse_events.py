"""SSE guidance events for cognitive scaffolding transparency.

This module provides Server-Sent Events (SSE) functionality to emit
guidance events that help clients understand the server's cognitive process.
Following SOLID principles for clean, extensible architecture.
"""

import json
import uuid
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Protocol


class EventEmitter(Protocol):
    """Interface for event emission (Interface Segregation Principle)."""

    async def emit(self, event_data: str) -> None:
        """Emit an SSE event to connected clients."""
        ...


@dataclass
class BaseEvent(ABC):
    """Abstract base class for all SSE events (Dependency Inversion Principle).

    Provides common event structure and ensures all events follow the same format.
    """

    event_id: str
    event_type: str
    timestamp: str
    data: dict[str, Any]

    def __post_init__(self) -> None:
        """Initialize common fields after dataclass creation."""
        if not self.event_id:
            self.event_id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()

    @abstractmethod
    def validate_data(self) -> bool:
        """Validate event-specific data requirements."""

    def to_sse_format(self) -> str:
        """Convert event to SSE format string.

        Returns:
            SSE-formatted string ready for transmission
        """
        if not self.validate_data():
            raise ValueError(f"Invalid data for {self.event_type} event")

        event_dict = asdict(self)
        return f"id: {self.event_id}\nevent: {self.event_type}\ndata: {json.dumps(event_dict)}\n\n"


@dataclass
class IntentAnalyzedEvent(BaseEvent):
    """Event emitted when user intent has been analyzed (Single Responsibility)."""

    def __init__(
        self,
        intent: str,
        needs_fact_check: bool,
        thinking_steps_required: int = 10,
        event_id: str = "",
        timestamp: str = "",
    ):
        super().__init__(
            event_id=event_id,
            event_type="intent_analyzed",
            timestamp=timestamp,
            data={
                "intent": intent,
                "needs_fact_check": needs_fact_check,
                "thinking_steps_required": max(thinking_steps_required, 10),  # Enforce minimum
            },
        )

    def validate_data(self) -> bool:
        """Validate intent analysis data."""
        return (
            isinstance(self.data.get("intent"), str)
            and len(self.data["intent"].strip()) > 0
            and isinstance(self.data.get("needs_fact_check"), bool)
            and isinstance(self.data.get("thinking_steps_required"), int)
            and self.data["thinking_steps_required"] >= 10
        )


@dataclass
class FactCheckTriggeredEvent(BaseEvent):
    """Event emitted when fact-checking is triggered (Single Responsibility)."""

    def __init__(
        self,
        query: str,
        reason: str = "Preventing hallucination",
        event_id: str = "",
        timestamp: str = "",
    ):
        super().__init__(
            event_id=event_id,
            event_type="fact_check_triggered",
            timestamp=timestamp,
            data={"query": query, "reason": reason},
        )

    def validate_data(self) -> bool:
        """Validate fact-check trigger data."""
        return (
            isinstance(self.data.get("query"), str)
            and len(self.data["query"].strip()) > 0
            and isinstance(self.data.get("reason"), str)
            and len(self.data["reason"].strip()) > 0
        )


@dataclass
class ThinkingStepEvent(BaseEvent):
    """Event emitted for each thinking step (Single Responsibility)."""

    def __init__(
        self,
        step_number: int,
        total_steps: int,
        thought: str,
        event_id: str = "",
        timestamp: str = "",
    ):
        super().__init__(
            event_id=event_id,
            event_type="thinking_step",
            timestamp=timestamp,
            data={
                "step_number": step_number,
                "total_steps": max(total_steps, 10),  # Enforce minimum
                "thought": thought,
            },
        )

    def validate_data(self) -> bool:
        """Validate thinking step data."""
        return (
            isinstance(self.data.get("step_number"), int)
            and self.data["step_number"] >= 1
            and isinstance(self.data.get("total_steps"), int)
            and self.data["total_steps"] >= 10
            and self.data["step_number"] <= self.data["total_steps"]
            and isinstance(self.data.get("thought"), str)
            and len(self.data["thought"].strip()) > 0
        )


class GuidanceEventManager:
    """Manager for emitting guidance events (Single Responsibility Principle).

    Handles the emission of cognitive scaffolding events to provide transparency
    into the server's thought process. Events are informational and non-blocking.
    """

    def __init__(self, emitter: EventEmitter | None = None):
        """Initialize event manager with optional emitter.

        Args:
            emitter: Event emitter implementation (Dependency Injection)
        """
        self._emitter = emitter
        self._enabled = emitter is not None

    def set_emitter(self, emitter: EventEmitter) -> None:
        """Set the event emitter (Dependency Injection)."""
        self._emitter = emitter
        self._enabled = True

    def disable(self) -> None:
        """Disable event emission (graceful degradation)."""
        self._enabled = False

    def enable(self) -> None:
        """Re-enable event emission if emitter is available."""
        self._enabled = self._emitter is not None

    async def emit_intent_analyzed(
        self, intent: str, needs_fact_check: bool, thinking_steps_required: int = 10
    ) -> None:
        """Emit intent analyzed event.

        Args:
            intent: The analyzed user intent
            needs_fact_check: Whether fact-checking is required
            thinking_steps_required: Number of thinking steps needed
        """
        if not self._enabled or not self._emitter:
            return

        try:
            event = IntentAnalyzedEvent(
                intent=intent,
                needs_fact_check=needs_fact_check,
                thinking_steps_required=thinking_steps_required,
            )
            await self._emitter.emit(event.to_sse_format())
        except Exception:
            # Events are informational only - don't break the flow
            # Silently fail to maintain non-blocking behavior
            return

    async def emit_fact_check_triggered(
        self, query: str, reason: str = "Preventing hallucination"
    ) -> None:
        """Emit fact-check triggered event.

        Args:
            query: The query being fact-checked
            reason: Reason for fact-checking
        """
        if not self._enabled or not self._emitter:
            return

        try:
            event = FactCheckTriggeredEvent(query=query, reason=reason)
            await self._emitter.emit(event.to_sse_format())
        except Exception:
            # Events are informational only - don't break the flow
            # Silently fail to maintain non-blocking behavior
            return

    async def emit_thinking_step(self, step_number: int, total_steps: int, thought: str) -> None:
        """Emit thinking step event.

        Args:
            step_number: Current step number (1-based)
            total_steps: Total number of steps
            thought: The current thought
        """
        if not self._enabled or not self._emitter:
            return

        try:
            event = ThinkingStepEvent(
                step_number=step_number, total_steps=total_steps, thought=thought
            )
            await self._emitter.emit(event.to_sse_format())
        except Exception:
            # Events are informational only - don't break the flow
            # Silently fail to maintain non-blocking behavior
            return


# Global instance for easy access (singleton pattern)
_guidance_manager = GuidanceEventManager()


def get_guidance_manager() -> GuidanceEventManager:
    """Get the global guidance event manager instance."""
    return _guidance_manager


def set_global_emitter(emitter: EventEmitter) -> None:
    """Set the global event emitter."""
    _guidance_manager.set_emitter(emitter)


# Convenience functions for direct event emission
async def emit_intent_analyzed(
    intent: str, needs_fact_check: bool, thinking_steps_required: int = 10
) -> None:
    """Convenience function to emit intent analyzed event."""
    await _guidance_manager.emit_intent_analyzed(intent, needs_fact_check, thinking_steps_required)


async def emit_fact_check_triggered(query: str, reason: str = "Preventing hallucination") -> None:
    """Convenience function to emit fact-check triggered event."""
    await _guidance_manager.emit_fact_check_triggered(query, reason)


async def emit_thinking_step(step_number: int, total_steps: int, thought: str) -> None:
    """Convenience function to emit thinking step event."""
    await _guidance_manager.emit_thinking_step(step_number, total_steps, thought)
