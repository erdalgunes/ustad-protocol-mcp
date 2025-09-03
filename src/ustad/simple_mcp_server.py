#!/usr/bin/env python3
"""Simple MCP Server for Perfect Collaborative Batch of Thought."""

import asyncio
import json

from mcp import stdio_server
from mcp.server import Server

from .perfect_collaborative_bot import PerfectCollaborativeBatchOfThought

# Create the MCP server
app = Server("ustad")

# Initialize the BoT system
bot = None


@app.call_tool()
async def ustad_think(problem: str, context: str = "", num_thoughts: int = 8) -> str:
    """Multi-round collaborative dialogue where 8 AI perspectives debate,
    challenge each other, and reach consensus through structured discussion.

    Args:
        problem: The problem or question to analyze collaboratively
        context: Additional context, constraints, or requirements
        num_thoughts: Number of perspectives (max 8 for optimal dialogue)

    Returns:
        JSON string with collaborative analysis results
    """
    global bot
    if not bot:
        bot = PerfectCollaborativeBatchOfThought()

    try:
        result = await bot.think(problem, context)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e), "problem": problem})


async def main():
    """Run the MCP server."""
    async with stdio_server() as streams:
        await app.run(*streams, initialization_options={})


if __name__ == "__main__":
    asyncio.run(main())
