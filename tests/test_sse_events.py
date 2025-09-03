"""Integration tests for SSE guidance events functionality.

This module tests the complete SSE events system including event creation,
emission, transport integration, and error handling scenarios.
"""

import asyncio
import json
from unittest.mock import AsyncMock, patch

import pytest

from src.sse_events import (
    FactCheckTriggeredEvent,
    GuidanceEventManager,
    IntentAnalyzedEvent,
    ThinkingStepEvent,
    emit_fact_check_triggered,
    emit_intent_analyzed,
    emit_thinking_step,
    get_guidance_manager,
)
from src.sse_transport import (
    GuidanceSSEEmitter,
    MockSSEEmitter,
    SSEConnection,
    create_development_emitter,
    set_sse_emitter,
)


class TestSSEEventSchema:
    """Test SSE event schema and validation."""

    def test_intent_analyzed_event_creation(self):
        """Test IntentAnalyzedEvent creation and validation."""
        event = IntentAnalyzedEvent(
            intent="test user query", needs_fact_check=True, thinking_steps_required=15
        )

        assert event.event_type == "intent_analyzed"
        assert event.data["intent"] == "test user query"
        assert event.data["needs_fact_check"] is True
        assert event.data["thinking_steps_required"] == 15
        assert event.validate_data()

    def test_intent_analyzed_event_minimum_steps_enforcement(self):
        """Test that minimum 10 steps are enforced."""
        event = IntentAnalyzedEvent(
            intent="test query",
            needs_fact_check=False,
            thinking_steps_required=5,  # Below minimum
        )

        # Should be enforced to minimum 10
        assert event.data["thinking_steps_required"] == 10
        assert event.validate_data()

    def test_fact_check_triggered_event_creation(self):
        """Test FactCheckTriggeredEvent creation and validation."""
        event = FactCheckTriggeredEvent(
            query="what is the capital of France", reason="Verifying factual information"
        )

        assert event.event_type == "fact_check_triggered"
        assert event.data["query"] == "what is the capital of France"
        assert event.data["reason"] == "Verifying factual information"
        assert event.validate_data()

    def test_thinking_step_event_creation(self):
        """Test ThinkingStepEvent creation and validation."""
        event = ThinkingStepEvent(
            step_number=5, total_steps=12, thought="Analyzing the problem structure"
        )

        assert event.event_type == "thinking_step"
        assert event.data["step_number"] == 5
        assert event.data["total_steps"] == 12
        assert event.data["thought"] == "Analyzing the problem structure"
        assert event.validate_data()

    def test_thinking_step_event_minimum_total_steps(self):
        """Test minimum total steps enforcement."""
        event = ThinkingStepEvent(
            step_number=1,
            total_steps=8,  # Below minimum
            thought="test thought",
        )

        # Should be enforced to minimum 10
        assert event.data["total_steps"] == 10
        assert event.validate_data()

    def test_event_sse_format_conversion(self):
        """Test SSE format conversion."""
        event = IntentAnalyzedEvent(
            intent="test intent", needs_fact_check=True, thinking_steps_required=10
        )

        sse_format = event.to_sse_format()

        # Should contain SSE format elements
        assert "id: " in sse_format
        assert "event: intent_analyzed" in sse_format
        assert "data: " in sse_format
        assert sse_format.endswith("\n\n")

        # Data should be valid JSON
        data_line = next(line for line in sse_format.split("\n") if line.startswith("data: "))
        data_json = data_line[6:]  # Remove "data: " prefix
        parsed_data = json.loads(data_json)

        assert parsed_data["event_type"] == "intent_analyzed"
        assert parsed_data["data"]["intent"] == "test intent"

    def test_event_validation_failures(self):
        """Test event validation for invalid data."""
        # Empty intent should fail
        event = IntentAnalyzedEvent("", needs_fact_check=False)
        assert not event.validate_data()

        # Invalid step numbers should fail
        event = ThinkingStepEvent(0, 10, "test")  # step_number < 1
        assert not event.validate_data()

        event = ThinkingStepEvent(15, 10, "test")  # step_number > total_steps
        assert not event.validate_data()


class TestGuidanceEventManager:
    """Test guidance event manager functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_emitter = AsyncMock()
        self.manager = GuidanceEventManager(self.mock_emitter)

    @pytest.mark.asyncio
    async def test_emit_intent_analyzed(self):
        """Test intent analyzed event emission."""
        await self.manager.emit_intent_analyzed(
            intent="test query", needs_fact_check=True, thinking_steps_required=15
        )

        self.mock_emitter.emit.assert_called_once()
        call_args = self.mock_emitter.emit.call_args[0][0]

        assert "event: intent_analyzed" in call_args
        assert "test query" in call_args

    @pytest.mark.asyncio
    async def test_emit_fact_check_triggered(self):
        """Test fact check triggered event emission."""
        await self.manager.emit_fact_check_triggered(
            query="test search query", reason="Testing fact verification"
        )

        self.mock_emitter.emit.assert_called_once()
        call_args = self.mock_emitter.emit.call_args[0][0]

        assert "event: fact_check_triggered" in call_args
        assert "test search query" in call_args

    @pytest.mark.asyncio
    async def test_emit_thinking_step(self):
        """Test thinking step event emission."""
        await self.manager.emit_thinking_step(
            step_number=3, total_steps=10, thought="Analyzing the problem"
        )

        self.mock_emitter.emit.assert_called_once()
        call_args = self.mock_emitter.emit.call_args[0][0]

        assert "event: thinking_step" in call_args
        assert "Analyzing the problem" in call_args

    @pytest.mark.asyncio
    async def test_graceful_degradation_no_emitter(self):
        """Test graceful degradation when no emitter is set."""
        manager = GuidanceEventManager(None)

        # Should not raise exceptions
        await manager.emit_intent_analyzed("test", needs_fact_check=False)
        await manager.emit_fact_check_triggered("test")
        await manager.emit_thinking_step(1, 10, "test")

    @pytest.mark.asyncio
    async def test_graceful_degradation_emitter_exception(self):
        """Test graceful degradation when emitter raises exceptions."""
        failing_emitter = AsyncMock()
        failing_emitter.emit.side_effect = Exception("Network error")

        manager = GuidanceEventManager(failing_emitter)

        # Should not raise exceptions (events are informational only)
        await manager.emit_intent_analyzed("test", needs_fact_check=False)
        await manager.emit_fact_check_triggered("test")
        await manager.emit_thinking_step(1, 10, "test")

    def test_manager_disable_enable(self):
        """Test manager disable/enable functionality."""
        assert self.manager._enabled

        self.manager.disable()
        assert not self.manager._enabled

        self.manager.enable()
        assert self.manager._enabled


class TestSSETransport:
    """Test SSE transport integration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.emitter = GuidanceSSEEmitter()

    @pytest.mark.asyncio
    async def test_sse_connection_successful_send(self):
        """Test successful SSE connection send."""
        mock_send = AsyncMock()
        connection = SSEConnection("test-conn-1", mock_send)

        result = await connection.send("test data")

        assert result is True
        assert connection.is_active
        assert connection.retry_count == 0
        mock_send.assert_called_once_with("test data")

    @pytest.mark.asyncio
    async def test_sse_connection_retry_logic(self):
        """Test SSE connection retry logic with failures."""
        mock_send = AsyncMock()
        mock_send.side_effect = [
            Exception("Network error"),
            Exception("Still failing"),
            None,  # Success on third try
        ]

        connection = SSEConnection("test-conn-1", mock_send)

        with patch("asyncio.sleep", new=AsyncMock()):  # Speed up test
            result = await connection.send("test data")

        assert result is True
        assert connection.is_active
        assert connection.retry_count == 0  # Reset after success
        assert mock_send.call_count == 3

    @pytest.mark.asyncio
    async def test_sse_connection_max_retries_exceeded(self):
        """Test SSE connection when max retries are exceeded."""
        mock_send = AsyncMock()
        mock_send.side_effect = Exception("Persistent network error")

        connection = SSEConnection("test-conn-1", mock_send)
        connection.max_retries = 2  # Lower for faster test

        with patch("asyncio.sleep", new=AsyncMock()):  # Speed up test
            result = await connection.send("test data")

        assert result is False
        assert not connection.is_active
        assert mock_send.call_count == 3  # Initial + 2 retries

    @pytest.mark.asyncio
    async def test_guidance_emitter_multiple_connections(self):
        """Test guidance emitter with multiple connections."""
        mock_send1 = AsyncMock()
        mock_send2 = AsyncMock()

        conn1 = self.emitter.add_connection("conn1", mock_send1)
        conn2 = self.emitter.add_connection("conn2", mock_send2)

        await self.emitter.emit("test event data")

        # Both connections should receive the event
        mock_send1.assert_called_once()
        mock_send2.assert_called_once()

        # Both should get the same enhanced data with retry instruction
        call_data1 = mock_send1.call_args[0][0]
        call_data2 = mock_send2.call_args[0][0]

        assert call_data1 == call_data2
        assert "retry: 3000" in call_data1
        assert "test event data" in call_data1

    @pytest.mark.asyncio
    async def test_guidance_emitter_connection_cleanup(self):
        """Test automatic cleanup of inactive connections."""
        # Create a failing connection
        mock_send = AsyncMock()
        mock_send.side_effect = Exception("Connection failed")

        connection = self.emitter.add_connection("failing-conn", mock_send)
        connection.max_retries = 1  # Fail quickly

        initial_count = len(self.emitter._connections)

        with patch("asyncio.sleep", new=AsyncMock()):
            await self.emitter.emit("test data")

        # Connection should be marked inactive and cleaned up
        assert not connection.is_active

    def test_mock_sse_emitter(self):
        """Test mock SSE emitter for testing."""
        mock_emitter = MockSSEEmitter(log_events=False)

        # Test async emit
        asyncio.run(mock_emitter.emit("test event 1"))
        asyncio.run(mock_emitter.emit("test event 2"))

        assert mock_emitter.get_event_count() == 2
        assert len(mock_emitter.sent_events) == 2
        assert mock_emitter.sent_events[0] == "test event 1"
        assert mock_emitter.sent_events[1] == "test event 2"

        mock_emitter.clear_events()
        assert mock_emitter.get_event_count() == 0

    def test_development_emitter_setup(self):
        """Test development emitter creation and setup."""
        mock_emitter = create_development_emitter()

        assert isinstance(mock_emitter, MockSSEEmitter)
        assert mock_emitter.log_events is True

        # Should be set as global emitter
        manager = get_guidance_manager()
        assert manager._emitter is mock_emitter


class TestIntegrationScenarios:
    """Test complete integration scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_emitter = MockSSEEmitter(log_events=False)
        set_sse_emitter(self.mock_emitter)

    @pytest.mark.asyncio
    async def test_complete_thinking_workflow(self):
        """Test complete thinking workflow with all event types."""
        # Simulate a complete thinking process
        intent = "What are the main causes of climate change?"

        # 1. Intent analysis
        await emit_intent_analyzed(intent, needs_fact_check=True, thinking_steps_required=12)

        # 2. Fact checking
        await emit_fact_check_triggered("climate change causes", "Verifying scientific facts")

        # 3. Thinking steps
        for step in range(1, 13):
            await emit_thinking_step(step, 12, f"Thinking step {step}: analyzing aspect {step}")

        # Verify all events were captured
        events = self.mock_emitter.sent_events
        assert len(events) == 14  # 1 intent + 1 fact check + 12 thinking steps

        # Verify event types (be more precise with matching)
        intent_events = [e for e in events if "event: intent_analyzed" in e]
        fact_check_events = [e for e in events if "event: fact_check_triggered" in e]
        thinking_events = [e for e in events if "event: thinking_step" in e]

        assert len(intent_events) == 1
        assert len(fact_check_events) == 1
        assert len(thinking_events) == 12

        # Verify content
        assert intent in intent_events[0]
        assert "climate change causes" in fact_check_events[0]
        assert all(f"Thinking step {i}" in thinking_events[i - 1] for i in range(1, 13))

    @pytest.mark.asyncio
    async def test_concurrent_event_emission(self):
        """Test concurrent event emission doesn't cause issues."""
        # Emit multiple events concurrently
        tasks = []

        # Create mixed event types
        for i in range(5):
            tasks.append(emit_intent_analyzed(f"intent {i}", i % 2 == 0))
            tasks.append(emit_fact_check_triggered(f"query {i}"))
            tasks.append(emit_thinking_step(i + 1, 10, f"thought {i}"))

        await asyncio.gather(*tasks)

        # Should have 15 events total (5 of each type)
        events = self.mock_emitter.sent_events
        assert len(events) == 15

        # Count event types (be more precise with matching)
        intent_count = sum(1 for e in events if "event: intent_analyzed" in e)
        fact_count = sum(1 for e in events if "event: fact_check_triggered" in e)
        thinking_count = sum(1 for e in events if "event: thinking_step" in e)

        assert intent_count == 5
        assert fact_count == 5
        assert thinking_count == 5

    @pytest.mark.asyncio
    async def test_error_resilience(self):
        """Test system resilience to various error conditions."""
        # Test with failing emitter
        failing_emitter = AsyncMock()
        failing_emitter.emit.side_effect = Exception("Simulated failure")
        set_sse_emitter(failing_emitter)

        # These should not raise exceptions
        await emit_intent_analyzed("test", needs_fact_check=False)
        await emit_fact_check_triggered("test")
        await emit_thinking_step(1, 10, "test")

        # Test with no emitter
        set_sse_emitter(None)

        # These should also not raise exceptions
        await emit_intent_analyzed("test", needs_fact_check=False)
        await emit_fact_check_triggered("test")
        await emit_thinking_step(1, 10, "test")

    def teardown_method(self):
        """Clean up after tests."""
        # Reset global state
        self.mock_emitter.clear_events()
