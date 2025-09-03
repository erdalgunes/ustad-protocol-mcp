"""OpenAI analyzer module for intent analysis using GPT-3.5."""

import asyncio
import json
import logging
import os
from typing import Any

from openai import APIError, AsyncOpenAI, RateLimitError

logger = logging.getLogger(__name__)

# Initialize OpenAI client if API key is available
api_key = os.getenv("OPENAI_API_KEY")
client: AsyncOpenAI | None = AsyncOpenAI(api_key=api_key) if api_key else None  # type: ignore[no-any-unimported]

# Model configuration
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-3.5-turbo")

# Retry configuration
MAX_RETRIES = 3
BASE_WAIT_TIME = 1  # seconds


async def analyze_intent(text: str) -> dict[str, Any]:
    """
    Analyze user intent and detect if fact-checking is needed.

    Args:
        text: The user input text to analyze

    Returns:
        Dictionary containing:
        - intent: "question"|"task"|"clarification"
        - needs_fact_check: bool indicating if fact verification needed
        - complexity: "simple"|"moderate"|"complex"
        - reasoning_steps_needed: int (minimum 10)
    """
    # Fallback response for when API is unavailable
    fallback_response = {
        "intent": "task",
        "needs_fact_check": True,  # Conservative: assume fact-checking needed
        "complexity": "moderate",
        "reasoning_steps_needed": 10,
    }

    # Check if client is available
    if not client:
        logger.info("OpenAI client not initialized (no API key), using fallback")
        return fallback_response

    # Prepare the prompt for intent analysis
    prompt = f"""Analyze the following text and determine:
1. The intent (question, task, or clarification)
2. Whether it needs fact-checking (true if it contains factual claims or questions)
3. The complexity level (simple, moderate, or complex)
4. The minimum reasoning steps needed (at least 10)

Text: "{text}"

Respond in JSON format:
{{
    "intent": "question|task|clarification",
    "needs_fact_check": true|false,
    "complexity": "simple|moderate|complex",
    "reasoning_steps_needed": <number>
}}"""

    # Retry logic with exponential backoff
    for attempt in range(MAX_RETRIES):
        try:
            response = await client.chat.completions.create(
                model=GPT_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an intent analyzer. Analyze text and return structured JSON responses.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=150,
            )

            # Parse the response
            content = response.choices[0].message.content
            result = json.loads(content)

            # Ensure minimum reasoning steps
            if result.get("reasoning_steps_needed", 0) < 10:
                result["reasoning_steps_needed"] = 10

            # Validate response structure
            required_keys = {"intent", "needs_fact_check", "complexity", "reasoning_steps_needed"}
            if not all(key in result for key in required_keys):
                logger.warning("Invalid response structure: %s", result)
                return fallback_response

            # Validate values
            if result["intent"] not in ["question", "task", "clarification"]:
                result["intent"] = "task"
            if result["complexity"] not in ["simple", "moderate", "complex"]:
                result["complexity"] = "moderate"

            return result  # type: ignore[no-any-return]

        except RateLimitError as e:
            wait_time = BASE_WAIT_TIME * (2**attempt)
            logger.warning(
                "Rate limit hit, attempt %d/%d. Waiting %ds",
                attempt + 1,
                MAX_RETRIES,
                wait_time,
            )

            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(wait_time)
            else:
                logger.exception("Max retries exceeded for rate limit")
                return fallback_response

        except (APIError, json.JSONDecodeError, Exception) as e:
            logger.exception("Error analyzing intent")
            return fallback_response

    return fallback_response
