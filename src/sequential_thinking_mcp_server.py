#!/usr/bin/env python3
"""
MCP Server for Sequential Thinking - Pythonic implementation.
Provides structured problem-solving through sequential thought processing.
"""

import asyncio
import json
import sys
from typing import Any, Dict, Optional

from mcp.server import Server
from mcp import stdio_server
from sequential_thinking import SequentialThinkingServer


# Create the MCP server
app = Server("sequential-thinking")

# Initialize the sequential thinking server
thinking_server = None


@app.call_tool()
async def sequential_thinking(
    thought: str,
    thought_number: int,
    total_thoughts: int,
    next_thought_needed: bool,
    is_revision: bool = False,
    revises_thought: Optional[int] = None,
    branch_from_thought: Optional[int] = None,
    branch_id: Optional[str] = None,
    needs_more_thoughts: bool = False
) -> str:
    """
    Process a sequential thought for structured problem-solving.
    
    This tool helps analyze problems through a flexible thinking process that can adapt and evolve.
    Each thought can build on, question, or revise previous insights as understanding deepens.
    
    Args:
        thought: Your current thinking step
        thought_number: Current number in sequence (starts at 1)
        total_thoughts: Current estimate of thoughts needed (can be adjusted)
        next_thought_needed: True if more thinking needed
        is_revision: Whether this revises previous thinking
        revises_thought: Which thought number is being reconsidered
        branch_from_thought: Branching point thought number
        branch_id: Identifier for the current branch
        needs_more_thoughts: If more thoughts are needed than originally estimated
    
    Returns:
        JSON string with processed thought data and current state
    """
    global thinking_server
    if not thinking_server:
        thinking_server = SequentialThinkingServer()
    
    try:
        thought_data = {
            "thought": thought,
            "thoughtNumber": thought_number,
            "totalThoughts": total_thoughts,
            "nextThoughtNeeded": next_thought_needed,
            "isRevision": is_revision,
            "revisesThought": revises_thought,
            "branchFromThought": branch_from_thought,
            "branchId": branch_id,
            "needsMoreThoughts": needs_more_thoughts
        }
        
        result = thinking_server.process_thought(thought_data)
        
        # Add additional context
        response = {
            "processed_thought": result,
            "thought_history_length": len(thinking_server.get_thought_history()),
            "branches": list(thinking_server.get_branches().keys()),
            "is_complete": thinking_server.is_complete()
        }
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": str(e),
            "thought": thought,
            "thought_number": thought_number
        })


@app.call_tool()
async def get_thinking_summary() -> str:
    """
    Get a summary of the current thinking process.
    
    Returns:
        JSON string with summary statistics and insights
    """
    global thinking_server
    if not thinking_server:
        return json.dumps({"error": "No thinking session active"})
    
    try:
        summary = thinking_server.get_summary()
        history = thinking_server.get_thought_history()
        branches = thinking_server.get_branches()
        
        response = {
            "summary": summary,
            "total_thoughts": len(history),
            "branches_created": len(branches),
            "is_complete": thinking_server.is_complete(),
            "last_thought": history[-1] if history else None
        }
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e)})


@app.call_tool()
async def reset_thinking_session() -> str:
    """
    Reset the thinking session to start fresh.
    
    Returns:
        JSON confirmation of reset
    """
    global thinking_server
    if thinking_server:
        thinking_server.reset()
        return json.dumps({"status": "reset", "message": "Thinking session reset successfully"})
    else:
        return json.dumps({"status": "no_session", "message": "No active session to reset"})


@app.call_tool()
async def get_thought_history() -> str:
    """
    Get the complete history of thoughts in the current session.
    
    Returns:
        JSON array of all thoughts processed
    """
    global thinking_server
    if not thinking_server:
        return json.dumps({"error": "No thinking session active"})
    
    try:
        history = thinking_server.get_thought_history()
        return json.dumps({"history": history, "total": len(history)}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})


async def main():
    """Run the MCP server."""
    async with stdio_server() as streams:
        await app.run(*streams, initialization_options={})


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSequential thinking server stopped.", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)