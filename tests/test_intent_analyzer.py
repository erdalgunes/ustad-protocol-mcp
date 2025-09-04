"""Tests for the intent analysis module."""

import json
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.intent_analyzer import (
    CircuitBreaker,
    CircuitState,
    IntentAnalyzer,
    analyze_intent,
    get_intent_analyzer,
)


class TestCircuitBreaker:
    """Test the circuit breaker pattern implementation."""

    def test_initial_state(self):
        """Test initial state is CLOSED."""
        cb = CircuitBreaker()
        assert cb.state == CircuitState.CLOSED
        assert cb.can_execute() is True

    def test_failure_threshold(self):
        """Test circuit opens after threshold failures."""
        cb = CircuitBreaker(failure_threshold=3)

        # First two failures - still closed
        cb.call_failed()
        cb.call_failed()
        assert cb.state == CircuitState.CLOSED
        assert cb.can_execute() is True

        # Third failure - opens
        cb.call_failed()
        assert cb.state == CircuitState.OPEN
        assert cb.can_execute() is False

    def test_recovery_timeout(self):
        """Test circuit transitions to HALF_OPEN after timeout."""
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=1)

        # Open the circuit
        cb.call_failed()
        assert cb.state == CircuitState.OPEN
        assert cb.can_execute() is False

        # Mock time passing
        cb.last_failure_time = datetime.now() - timedelta(seconds=2)

        # Should transition to HALF_OPEN
        assert cb.can_execute() is True
        assert cb.state == CircuitState.HALF_OPEN

    def test_success_recovery(self):
        """Test circuit closes after successful calls in HALF_OPEN state."""
        cb = CircuitBreaker(success_threshold=2)

        # Set to HALF_OPEN state
        cb.state = CircuitState.HALF_OPEN

        # First success
        cb.call_succeeded()
        assert cb.state == CircuitState.HALF_OPEN

        # Second success - closes
        cb.call_succeeded()
        assert cb.state == CircuitState.CLOSED
        assert cb.success_count == 0


class TestIntentAnalyzer:
    """Test the IntentAnalyzer class."""

    @pytest.fixture
    def mock_openai_client(self):
        """Create a mock OpenAI client."""
        with patch("openai.AsyncOpenAI") as mock:
            yield mock

    @pytest.fixture
    def analyzer_no_key(self, monkeypatch):
        """Create analyzer without API key."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        return IntentAnalyzer()

    @pytest.fixture
    def analyzer_with_key(self, monkeypatch, mock_openai_client):
        """Create analyzer with mocked API key."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        return IntentAnalyzer()

    def test_initialization_without_key(self, analyzer_no_key):
        """Test initialization without API key."""
        assert analyzer_no_key.client is None
        assert analyzer_no_key.circuit_breaker.state == CircuitState.CLOSED

    def test_initialization_with_key(self, monkeypatch, mock_openai_client):
        """Test initialization with API key."""
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        analyzer = IntentAnalyzer()
        assert analyzer.client is not None
        mock_openai_client.assert_called_once_with(api_key="test-key")

    @pytest.mark.asyncio
    async def test_analyze_intent_no_client(self, analyzer_no_key):
        """Test analyze_intent returns default when no client."""
        result = await analyzer_no_key.analyze_intent("test thought")

        assert result["analysis_available"] is False
        assert result["needs_fact_check"] is False
        assert result["complexity"] == "medium"
        assert result["reasoning_steps_needed"] == 10
        assert result["confidence"] == 0.0

    @pytest.mark.asyncio
    async def test_analyze_intent_success(self, analyzer_with_key):
        """Test successful intent analysis."""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(
            {
                "needs_fact_check": True,
                "complexity": "complex",
                "reasoning_steps_needed": 15,
                "confidence": 0.9,
                "rationale": "Complex technical topic",
            }
        )

        analyzer_with_key.client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await analyzer_with_key.analyze_intent("Complex technical question")

        assert result["analysis_available"] is True
        assert result["needs_fact_check"] is True
        assert result["complexity"] == "complex"
        assert result["reasoning_steps_needed"] == 15
        assert result["confidence"] == 0.9

    @pytest.mark.asyncio
    async def test_analyze_intent_minimum_steps(self, analyzer_with_key):
        """Test that minimum 10 steps are enforced."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(
            {
                "needs_fact_check": False,
                "complexity": "simple",
                "reasoning_steps_needed": 3,  # Less than 10
                "confidence": 0.8,
            }
        )

        analyzer_with_key.client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await analyzer_with_key.analyze_intent("Simple question")

        assert result["reasoning_steps_needed"] == 10  # Enforced minimum

    @pytest.mark.asyncio
    async def test_analyze_intent_parse_error(self, analyzer_with_key):
        """Test handling of JSON parse errors."""
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Not valid JSON"

        analyzer_with_key.client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await analyzer_with_key.analyze_intent("Test thought")

        assert result["analysis_available"] is True
        assert result["needs_fact_check"] is True  # Conservative default
        assert result["complexity"] == "complex"
        assert "parse_error" in result

    @pytest.mark.asyncio
    async def test_analyze_intent_retry_logic(self, analyzer_with_key):
        """Test retry logic with exponential backoff."""
        # Mock to fail twice, then succeed
        call_count = 0

        async def mock_create(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise RuntimeError("API error")

            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = json.dumps(
                {
                    "needs_fact_check": False,
                    "complexity": "medium",
                    "reasoning_steps_needed": 10,
                    "confidence": 0.7,
                }
            )
            return mock_response

        analyzer_with_key.client.chat.completions.create = mock_create

        # Use shorter retry count for testing
        result = await analyzer_with_key.analyze_intent("Test", retry_count=3)

        assert call_count == 3
        assert result["analysis_available"] is True

    @pytest.mark.asyncio
    async def test_analyze_intent_circuit_breaker_open(self, analyzer_with_key):
        """Test that open circuit breaker prevents calls."""
        analyzer_with_key.circuit_breaker.state = CircuitState.OPEN
        analyzer_with_key.circuit_breaker.last_failure_time = datetime.now()

        result = await analyzer_with_key.analyze_intent("Test thought")

        # Should return default without calling OpenAI
        assert result["analysis_available"] is False
        assert analyzer_with_key.client.chat.completions.create.called is False

    def test_build_prompt(self, analyzer_with_key):
        """Test prompt building."""
        prompt = analyzer_with_key._build_prompt("Test thought", None)
        assert "Test thought" in prompt
        assert "JSON format" in prompt

        prompt_with_context = analyzer_with_key._build_prompt("Test", "Previous context")
        assert "Previous context" in prompt_with_context


class TestGlobalFunctions:
    """Test module-level functions."""

    def test_get_intent_analyzer_singleton(self):
        """Test that get_intent_analyzer returns singleton."""
        analyzer1 = get_intent_analyzer()
        analyzer2 = get_intent_analyzer()
        assert analyzer1 is analyzer2

    @pytest.mark.asyncio
    async def test_analyze_intent_convenience(self, monkeypatch):
        """Test the convenience analyze_intent function."""
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        # Reset global analyzer to ensure fresh instance without key
        import src.intent_analyzer

        src.intent_analyzer._analyzer = None

        result = await analyze_intent("Test thought")

        assert result["analysis_available"] is False
        assert result["reasoning_steps_needed"] == 10


@pytest.mark.asyncio
async def test_integration_with_context(monkeypatch):
    """Test full integration with context."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    with patch("openai.AsyncOpenAI") as mock_client_class:
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps(
            {
                "needs_fact_check": True,
                "complexity": "complex",
                "reasoning_steps_needed": 12,
                "confidence": 0.85,
            }
        )

        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        # Reset global analyzer
        import src.intent_analyzer

        src.intent_analyzer._analyzer = None

        result = await analyze_intent(
            "How does quantum computing work?",
            context="Previous thoughts: Understanding computing basics",
        )

        assert result["needs_fact_check"] is True
        assert result["complexity"] == "complex"
        assert result["reasoning_steps_needed"] == 12
