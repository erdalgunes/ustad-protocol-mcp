"""Tests for OpenAI analyzer module with intent analysis."""

import json
import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from openai import APIError, RateLimitError

from src.openai_analyzer import analyze_intent


@pytest.mark.asyncio
async def test_analyze_intent_returns_correct_structure():
    """Test that analyze_intent returns the expected dictionary structure."""
    with patch("src.openai_analyzer.client") as mock_client:
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='{"intent": "question", "needs_fact_check": true, "complexity": "moderate", "reasoning_steps_needed": 10}'
                )
            )
        ]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await analyze_intent("What is the capital of France?")

        assert "intent" in result
        assert "needs_fact_check" in result
        assert "complexity" in result
        assert "reasoning_steps_needed" in result
        assert result["intent"] in ["question", "task", "clarification"]
        assert isinstance(result["needs_fact_check"], bool)
        assert result["complexity"] in ["simple", "moderate", "complex"]
        assert result["reasoning_steps_needed"] >= 10


@pytest.mark.asyncio
async def test_analyze_intent_handles_missing_api_key():
    """Test graceful fallback when API key is missing."""
    with patch.dict(os.environ, {}, clear=True):
        with patch("src.openai_analyzer.client", None):
            result = await analyze_intent("Test query without API key")

            assert result["intent"] == "task"
            assert result["needs_fact_check"] is True
            assert result["complexity"] == "moderate"
            assert result["reasoning_steps_needed"] == 10


@pytest.mark.asyncio
async def test_analyze_intent_retry_on_rate_limit():
    """Test exponential backoff retry logic on rate limit errors."""
    with patch("src.openai_analyzer.client") as mock_client:
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='{"intent": "task", "needs_fact_check": false, "complexity": "simple", "reasoning_steps_needed": 10}'
                )
            )
        ]

        # First two calls fail with rate limit, third succeeds
        mock_client.chat.completions.create = AsyncMock(
            side_effect=[
                RateLimitError(
                    message="Rate limit exceeded", response=MagicMock(status_code=429), body={}
                ),
                RateLimitError(
                    message="Rate limit exceeded", response=MagicMock(status_code=429), body={}
                ),
                mock_response,
            ]
        )

        with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
            result = await analyze_intent("Build a simple calculator")

            # Verify retry logic was called
            assert mock_sleep.call_count == 2
            assert mock_client.chat.completions.create.call_count == 3

            # Verify result is correct
            assert result["intent"] == "task"
            assert result["needs_fact_check"] is False


@pytest.mark.asyncio
async def test_analyze_intent_max_retries_exceeded():
    """Test fallback when max retries are exceeded."""
    with patch("src.openai_analyzer.client") as mock_client:
        # All calls fail with rate limit
        mock_client.chat.completions.create = AsyncMock(
            side_effect=RateLimitError(
                message="Rate limit exceeded", response=MagicMock(status_code=429), body={}
            )
        )

        with patch("asyncio.sleep", new_callable=AsyncMock):
            result = await analyze_intent("Test query")

            # Should return fallback result
            assert result["intent"] == "task"
            assert result["needs_fact_check"] is True
            assert result["complexity"] == "moderate"
            assert result["reasoning_steps_needed"] == 10


@pytest.mark.asyncio
async def test_analyze_intent_detects_fact_checking_needed():
    """Test that factual questions are properly identified."""
    test_cases = [
        ("What year was Python created?", True),
        ("Is the Earth flat?", True),
        ("Write a function to sort a list", False),
        ("How many planets are in our solar system?", True),
        ("Create a todo app", False),
    ]

    with patch("src.openai_analyzer.client") as mock_client:
        for query, should_check in test_cases:
            mock_response = MagicMock()
            response_data = {
                "intent": "question" if should_check else "task",
                "needs_fact_check": should_check,
                "complexity": "simple",
                "reasoning_steps_needed": 10,
            }
            mock_response.choices = [
                MagicMock(message=MagicMock(content=json.dumps(response_data)))
            ]
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

            result = await analyze_intent(query)
            assert result["needs_fact_check"] == should_check


@pytest.mark.asyncio
async def test_analyze_intent_handles_api_errors():
    """Test handling of general API errors."""
    with patch("src.openai_analyzer.client") as mock_client:
        mock_client.chat.completions.create = AsyncMock(
            side_effect=APIError(message="Service unavailable", request=MagicMock(), body={})
        )

        result = await analyze_intent("Test query with API error")

        # Should return fallback result
        assert result["intent"] == "task"
        assert result["needs_fact_check"] is True
        assert result["complexity"] == "moderate"
        assert result["reasoning_steps_needed"] == 10


@pytest.mark.asyncio
async def test_analyze_intent_complexity_assessment():
    """Test that complexity is properly assessed based on query."""
    with patch("src.openai_analyzer.client") as mock_client:
        complexity_map = {
            "What is 2+2?": "simple",
            "Explain quantum computing": "complex",
            "Write a Python function": "moderate",
        }

        for query, expected_complexity in complexity_map.items():
            mock_response = MagicMock()
            mock_response.choices = [
                MagicMock(
                    message=MagicMock(
                        content=f'{{"intent": "question", "needs_fact_check": true, "complexity": "{expected_complexity}", "reasoning_steps_needed": {"15" if expected_complexity == "complex" else "10"}}}'
                    )
                )
            ]
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

            result = await analyze_intent(query)
            assert result["complexity"] == expected_complexity


@pytest.mark.asyncio
async def test_analyze_intent_minimum_reasoning_steps():
    """Test that reasoning_steps_needed is always at least 10."""
    with patch("src.openai_analyzer.client") as mock_client:
        mock_response = MagicMock()
        mock_response.choices = [
            MagicMock(
                message=MagicMock(
                    content='{"intent": "question", "needs_fact_check": false, "complexity": "simple", "reasoning_steps_needed": 5}'
                )
            )
        ]
        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        result = await analyze_intent("Simple query")

        # Should enforce minimum of 10 steps
        assert result["reasoning_steps_needed"] >= 10
