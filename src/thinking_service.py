"""Thinking service for sequential chain-of-thought reasoning.

This module provides a thinking interface that integrates with
the sequential thinking server, following SOLID principles.
"""

from typing import Any

from .sequential_thinking import SequentialThinkingServer

# Singleton instance of the thinking server
_thinking_server = SequentialThinkingServer()


async def generate_thinking_steps(intent: str, min_steps: int = 10) -> list[str]:
    """Generate sequential thinking steps for analyzing an intent.

    Args:
        intent: The user's intent to analyze
        min_steps: Minimum number of thinking steps required

    Returns:
        List of thinking steps
    """
    thinking_steps: list[str] = []

    # Generate thinking steps using the sequential thinking server
    thought_data = {
        "thought": f"Analyzing user intent: {intent}",
        "thoughtNumber": 1,
        "totalThoughts": min_steps,
        "nextThoughtNeeded": True,
    }

    _ = _thinking_server.process_thought(thought_data)
    thinking_steps.append(str(thought_data["thought"]))

    # Continue generating steps
    step_prompts = [
        "Breaking down the request into components",
        "Identifying key entities and concepts",
        "Checking for factual claims that need verification",
        "Evaluating complexity of the request",
        "Determining information requirements",
        "Assessing need for external verification",
        "Identifying potential ambiguities",
        "Considering context and implications",
        "Planning execution approach",
        "Validating approach against requirements",
        "Finalizing intent analysis",
        "Checking for edge cases",
        "Ensuring comprehensive coverage",
        "Reviewing analysis completeness",
    ]

    for i, prompt in enumerate(step_prompts[: min_steps - 1], start=2):
        thought_data = {
            "thought": prompt,
            "thoughtNumber": i,
            "totalThoughts": min_steps,
            "nextThoughtNeeded": i < min_steps,
        }
        _ = _thinking_server.process_thought(thought_data)
        thinking_steps.append(prompt)

        if len(thinking_steps) >= min_steps:
            break

    return thinking_steps


def get_thinking_history() -> list[dict[str, Any]]:
    """Get the complete thinking history.

    Returns:
        List of all processed thoughts
    """
    return _thinking_server.get_thought_history()


def reset_thinking() -> None:
    """Reset the thinking server state."""
    global _thinking_server
    _thinking_server = SequentialThinkingServer()
