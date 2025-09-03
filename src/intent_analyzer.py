"""Intent analysis module for ustad_think with OpenAI integration."""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states."""

    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failures detected, blocking calls
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """Circuit breaker pattern implementation for OpenAI calls."""

    def __init__(
        self, failure_threshold: int = 3, recovery_timeout: int = 60, success_threshold: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: datetime | None = None

    def call_succeeded(self) -> None:
        """Record a successful call."""
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.success_count = 0
                logger.info("Circuit breaker closed - service recovered")

    def call_failed(self) -> None:
        """Record a failed call."""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        self.success_count = 0

        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning("Circuit breaker opened after %d failures", self.failure_count)

    def can_execute(self) -> bool:
        """Check if we can execute a call."""
        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            if self.last_failure_time:
                time_since_failure = datetime.now() - self.last_failure_time
                if time_since_failure > timedelta(seconds=self.recovery_timeout):
                    self.state = CircuitState.HALF_OPEN
                    logger.info("Circuit breaker half-open - testing recovery")
                    return True
            return False

        # HALF_OPEN state
        return True


class IntentAnalyzer:
    """Analyzes user intent using OpenAI GPT-3.5."""

    def __init__(self) -> None:
        self.client = None
        self.circuit_breaker = CircuitBreaker()
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize OpenAI client if API key is available."""
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            try:
                from openai import AsyncOpenAI

                self.client = AsyncOpenAI(api_key=api_key)
                logger.info("OpenAI client initialized successfully")
            except ImportError:
                logger.warning("OpenAI library not installed")
                self.client = None
            except Exception as e:
                logger.exception("Failed to initialize OpenAI client")
                self.client = None
        else:
            logger.info("OpenAI API key not configured - intent analysis disabled")

    async def analyze_intent(
        self, thought: str, context: str | None = None, retry_count: int = 3
    ) -> dict[str, Any]:
        """
        Analyze the intent of a thought using OpenAI.

        Args:
            thought: The thought to analyze
            context: Optional context for the analysis
            retry_count: Number of retries for transient failures

        Returns:
            Dict containing intent analysis results
        """
        # Default response when OpenAI unavailable
        default_response = {
            "needs_fact_check": False,
            "complexity": "medium",
            "reasoning_steps_needed": 10,
            "confidence": 0.0,
            "analysis_available": False,
        }

        # Check if we can make the call
        if not self.client or not self.circuit_breaker.can_execute():
            logger.debug("OpenAI unavailable or circuit breaker open")
            return default_response

        # Build the prompt
        prompt = self._build_prompt(thought, context)

        # Try to call OpenAI with retries
        for attempt in range(retry_count):
            try:
                response = await self._call_openai(prompt)
                self.circuit_breaker.call_succeeded()
                return self._parse_response(response)

            except Exception as e:
                logger.warning(
                    "OpenAI call failed (attempt %d/%d): %s", attempt + 1, retry_count, e
                )

                if attempt < retry_count - 1:
                    # Exponential backoff
                    await asyncio.sleep(2**attempt)
                else:
                    self.circuit_breaker.call_failed()

        # All retries failed
        return default_response

    def _build_prompt(self, thought: str, context: str | None) -> str:
        """Build the prompt for OpenAI."""
        base_prompt = f"""Analyze the following thought and determine:
1. Whether it needs fact-checking (true/false)
2. The complexity level (simple/medium/complex)
3. Minimum reasoning steps needed (number 1-20)

Thought: {thought}"""

        if context:
            base_prompt += f"\n\nContext: {context}"

        base_prompt += """

Respond in JSON format:
{
    "needs_fact_check": boolean,
    "complexity": "simple|medium|complex",
    "reasoning_steps_needed": number,
    "confidence": float (0-1),
    "rationale": "brief explanation"
}"""

        return base_prompt

    async def _call_openai(self, prompt: str) -> str:
        """Make the actual OpenAI API call."""
        if not self.client:
            raise RuntimeError("OpenAI client not initialized")

        response = await self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are an intent analysis assistant. Respond only with valid JSON.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=200,
        )

        return str(response.choices[0].message.content)

    def _parse_response(self, response: str) -> dict[str, Any]:
        """Parse the OpenAI response."""
        import json

        try:
            parsed = json.loads(response)

            # Ensure minimum 10 steps as per requirements
            if parsed.get("reasoning_steps_needed", 0) < 10:
                parsed["reasoning_steps_needed"] = 10

            parsed["analysis_available"] = True
            parsed.setdefault("confidence", 0.8)

            return parsed  # type: ignore[no-any-return]

        except json.JSONDecodeError as e:
            logger.exception("Failed to parse OpenAI response")
            return {
                "needs_fact_check": True,  # Conservative default
                "complexity": "complex",
                "reasoning_steps_needed": 10,
                "confidence": 0.5,
                "analysis_available": True,
                "parse_error": str(e),
            }


# Global instance for easy access
_analyzer: IntentAnalyzer | None = None


def get_intent_analyzer() -> IntentAnalyzer:
    """Get or create the global intent analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = IntentAnalyzer()
    return _analyzer


async def analyze_intent(thought: str, context: str | None = None) -> dict[str, Any]:
    """
    Convenience function to analyze intent.

    This is the main entry point for the ustad_think integration.
    """
    analyzer = get_intent_analyzer()
    return await analyzer.analyze_intent(thought, context)
