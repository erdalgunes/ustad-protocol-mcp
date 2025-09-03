#!/usr/bin/env python3
"""Improved MCP Server for Sequential Thinking - Better Client Compatibility.
Implements elicitation, structured outputs, and simplified tool interface.
Following YAGNI - only adding what improves compatibility.
"""

import asyncio
from typing import Any

from mcp import stdio_server
from mcp.server import Server
from pydantic import BaseModel, Field

from sequential_thinking import SequentialThinkingServer


# Structured output schemas (MCP 2025-06-18 requirement)
class ThoughtResponse(BaseModel):
    """Structured response for thought processing"""

    thought: str = Field(description="The processed thought")
    thought_number: int = Field(description="Current thought number", ge=1)
    total_thoughts: int = Field(description="Total thoughts expected", ge=1)
    next_needed: bool = Field(description="Whether more thinking is needed")
    history_length: int = Field(description="Number of thoughts in history")
    is_complete: bool = Field(description="Whether thinking is complete")


class SimpleThoughtRequest(BaseModel):
    """Simplified request for basic clients"""

    thought: str = Field(description="Your current thinking step")
    continue_thinking: bool = Field(default=True, description="Continue after this thought?")


class ElicitationResponse(BaseModel):
    """Response when client input needs clarification"""

    type: str = "elicitation"
    field: str = Field(description="Field that needs input")
    prompt: str = Field(description="Human-readable prompt")
    suggestions: list[str] | None = Field(default=None, description="Suggested values")


# Create the improved MCP server
app = Server("sequential-thinking-improved")

# Initialize the sequential thinking server
thinking_server = None
thought_counter = 0  # Auto-increment for simplified mode


@app.call_tool()
async def think_simple(thought: str, continue_thinking: bool = True) -> dict[str, Any]:
    """Simplified sequential thinking for basic clients.
    Only 2 parameters instead of 9!

    Args:
        thought: Your current thinking step
        continue_thinking: Whether to continue after this thought

    Returns:
        Structured response with thought processing result
    """
    global thinking_server, thought_counter

    if not thinking_server:
        thinking_server = SequentialThinkingServer()
        thought_counter = 0

    thought_counter += 1

    try:
        thought_data = {
            "thought": thought,
            "thoughtNumber": thought_counter,
            "totalThoughts": thought_counter + (5 if continue_thinking else 0),
            "nextThoughtNeeded": continue_thinking,
        }

        result = thinking_server.process_thought(thought_data)

        return ThoughtResponse(
            thought=result["thought"],
            thought_number=result["thoughtNumber"],
            total_thoughts=result["totalThoughts"],
            next_needed=result["nextThoughtNeeded"],
            history_length=len(thinking_server.get_thought_history()),
            is_complete=thinking_server.is_complete(),
        ).model_dump()

    except ValueError as e:
        # Provide elicitation instead of error
        if "empty" in str(e).lower():
            return ElicitationResponse(
                field="thought",
                prompt="Please provide a thought to process",
                suggestions=[
                    "Let me think about this problem...",
                    "First, I need to understand...",
                ],
            ).model_dump()
        raise


@app.call_tool()
async def think_advanced(
    thought: str,
    thought_number: int | None = None,
    total_thoughts: int | None = None,
    next_thought_needed: bool | None = None,
    is_revision: bool = False,
    revises_thought: int | None = None,
) -> dict[str, Any]:
    """Advanced sequential thinking with full control.
    Provides elicitation for missing required fields.

    Args:
        thought: Your current thinking step
        thought_number: Current number in sequence (auto-generated if not provided)
        total_thoughts: Estimated total (defaults to 10)
        next_thought_needed: Continue thinking? (defaults to true)
        is_revision: Is this revising a previous thought?
        revises_thought: Which thought to revise

    Returns:
        Structured response or elicitation request
    """
    global thinking_server, thought_counter

    if not thinking_server:
        thinking_server = SequentialThinkingServer()
        thought_counter = 0

    # Elicitation for missing fields
    if not thought or not thought.strip():
        return ElicitationResponse(
            field="thought",
            prompt="What would you like to think about?",
            suggestions=[
                "Analyze this problem step by step",
                "Consider the implications",
                "Review my previous thinking",
            ],
        ).model_dump()

    # Auto-generate missing fields (YAGNI - sensible defaults)
    if thought_number is None:
        thought_counter += 1
        thought_number = thought_counter

    if total_thoughts is None:
        total_thoughts = thought_number + 5  # Assume 5 more thoughts

    if next_thought_needed is None:
        next_thought_needed = thought_number < total_thoughts

    # Validate revision
    if is_revision and revises_thought:
        history = thinking_server.get_thought_history()
        if not any(t["thoughtNumber"] == revises_thought for t in history):
            return ElicitationResponse(
                field="revises_thought",
                prompt=f"Thought {revises_thought} doesn't exist. Which thought would you like to revise?",
                suggestions=[str(t["thoughtNumber"]) for t in history[-3:]],  # Last 3 thoughts
            ).model_dump()

    try:
        thought_data = {
            "thought": thought,
            "thoughtNumber": thought_number,
            "totalThoughts": total_thoughts,
            "nextThoughtNeeded": next_thought_needed,
            "isRevision": is_revision,
            "revisesThought": revises_thought,
        }

        result = thinking_server.process_thought(thought_data)

        return ThoughtResponse(
            thought=result["thought"],
            thought_number=result["thoughtNumber"],
            total_thoughts=result["totalThoughts"],
            next_needed=result["nextThoughtNeeded"],
            history_length=len(thinking_server.get_thought_history()),
            is_complete=thinking_server.is_complete(),
        ).model_dump()

    except Exception as e:
        # Graceful error with suggestions
        return ElicitationResponse(
            field="thought",
            prompt=f"Something went wrong: {e!s}. Try rephrasing your thought.",
            suggestions=["Start with a simpler thought", "Break down the problem"],
        ).model_dump()


@app.call_tool()
async def get_summary() -> dict[str, Any]:
    """Get a summary of the current thinking session.

    Returns:
        Summary with statistics and final conclusion
    """
    global thinking_server

    if not thinking_server:
        return {
            "status": "no_session",
            "message": "No active thinking session. Start with think_simple() or think_advanced()",
        }

    summary = thinking_server.get_summary()
    history = thinking_server.get_thought_history()

    # Structured summary response
    return {
        "total_thoughts": summary["total_thoughts"],
        "branches_created": summary["branches_created"],
        "revisions_made": summary["revisions_made"],
        "is_complete": summary["is_complete"],
        "final_thought": summary.get("final_thought", "No conclusion yet"),
        "thinking_pattern": _analyze_pattern(history),
    }


def _analyze_pattern(history: list[dict]) -> str:
    """Analyze the thinking pattern (our unique value-add)"""
    if not history:
        return "No pattern yet"

    revisions = sum(1 for t in history if t.get("isRevision"))
    branches = len(set(t.get("branchId") for t in history if t.get("branchId")))

    if revisions > len(history) * 0.3:
        return "Iterative refinement pattern (high revision rate)"
    if branches > 1:
        return "Exploratory pattern (multiple branches)"
    if len(history) > 10:
        return "Deep analysis pattern (extended thinking)"
    return "Linear progression pattern"


@app.call_tool()
async def reset_session() -> dict[str, Any]:
    """Reset the thinking session."""
    global thinking_server, thought_counter

    if thinking_server:
        thinking_server.reset()
    thought_counter = 0

    return {"status": "success", "message": "Session reset. Ready for new thinking."}


# Health check endpoint (helps with client compatibility)
@app.call_tool()
async def health_check() -> dict[str, Any]:
    """Check server health and capabilities."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "protocol_version": "2025-06-18",
        "capabilities": {
            "elicitation": True,
            "structured_output": True,
            "simple_mode": True,
            "advanced_mode": True,
            "cognitive_scaffolding": True,  # Our unique feature
        },
    }


async def main():
    """Run the improved MCP server."""
    async with stdio_server() as streams:
        await app.run(
            *streams,
            initialization_options={
                "server_name": "Sequential Thinking (Improved)",
                "server_version": "1.0.0",
                "protocol_version": "2025-06-18",
                "capabilities": {"tools": {"elicitation": True, "structured_output": True}},
            },
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSequential thinking server stopped.")
    except Exception as e:
        print(f"Error: {e}")
        import sys

        sys.exit(1)
