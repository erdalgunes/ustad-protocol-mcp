#!/usr/bin/env python3
"""
Ustad Protocol MCP Server - FastMCP 2.x Implementation
Uses FastMCP with SSE transport for containerized deployment.
Only two tools: ustad-think (sequential thinking) and ustad-search (Tavily).
"""

import os
from typing import Any

import httpx
from fastmcp import FastMCP

from src.constants import CAPABILITIES_DATA, HEALTH_DATA
from src.sequential_thinking import SequentialThinkingServer

# Initialize FastMCP server
mcp = FastMCP("Ustad Protocol MCP Server")

# Initialize sequential thinking server (singleton pattern)
thinking_server = SequentialThinkingServer()


@mcp.tool()  # type: ignore[misc]
def ustad_think(
    thought: str,
    thought_number: int,
    total_thoughts: int,
    next_thought_needed: bool,
    is_revision: bool = False,
    revises_thought: int | None = None,
    branch_from_thought: int | None = None,
    branch_id: str | None = None,
    needs_more_thoughts: bool = False,
) -> dict[str, Any]:
    """Sequential thinking tool for structured problem-solving."""
    # Build thought data
    thought_data = {
        "thought": thought,
        "thoughtNumber": thought_number,
        "totalThoughts": total_thoughts,
        "nextThoughtNeeded": next_thought_needed,
    }

    # Add optional fields if provided
    if is_revision:
        thought_data["isRevision"] = is_revision
    if revises_thought is not None:
        thought_data["revisesThought"] = revises_thought
    if branch_from_thought is not None:
        thought_data["branchFromThought"] = branch_from_thought
    if branch_id is not None:
        thought_data["branchId"] = branch_id
    if needs_more_thoughts:
        thought_data["needsMoreThoughts"] = needs_more_thoughts

    # Process the thought
    result = thinking_server.process_thought(thought_data)

    # Add metadata about the thinking state
    result["thoughtHistoryLength"] = len(thinking_server.get_thought_history())
    result["branches"] = list(thinking_server.get_branches().keys())

    return result


@mcp.tool()  # type: ignore[misc]
def ustad_search(
    query: str,
    max_results: int = 5,
    search_type: str = "general",
) -> dict[str, Any]:
    """Search tool using Tavily API for fact-checking and information retrieval."""
    # Get Tavily API key from environment
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        return {
            "error": "Tavily API key not configured",
            "message": "Please set TAVILY_API_KEY environment variable",
        }

    # Prepare the search request
    url = "https://api.tavily.com/search"
    headers = {"Content-Type": "application/json"}
    payload = {
        "api_key": api_key,
        "query": query,
        "max_results": max_results,
        "search_depth": "basic",
        "include_answer": True,
        "include_raw_content": False,
        "include_images": False,
    }

    # Add topic for news searches
    if search_type == "news":
        payload["topic"] = "news"

    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.post(url, json=payload, headers=headers)
            response.raise_for_status()

            data = response.json()

            # Format the response
            result = {
                "query": query,
                "answer": data.get("answer", ""),
                "results": [
                    {
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "content": r.get("content", ""),
                        "score": r.get("score", 0),
                    }
                    for r in data.get("results", [])[:max_results]
                ],
                "result_count": len(data.get("results", [])),
                "search_type": search_type,
            }

            return result

    except httpx.HTTPStatusError as e:
        return {
            "error": "Search request failed",
            "status_code": e.response.status_code,
            "message": str(e),
        }
    except Exception as e:
        return {"error": "Search error", "message": str(e)}


def get_health_data() -> dict[str, Any]:
    """Get current health status data."""
    health_data = HEALTH_DATA.copy()
    health_data.update(
        {
            "thinking_history_length": len(thinking_server.get_thought_history()),
            "tavily_configured": bool(os.getenv("TAVILY_API_KEY")),
        }
    )
    return health_data


def get_capabilities_data() -> dict[str, Any]:
    """Get server capabilities data."""
    return CAPABILITIES_DATA.copy()


if __name__ == "__main__":
    # For containerized deployment with SSE
    port = int(os.getenv("PORT", "8000"))

    # Detect if running in container and set appropriate host
    is_container = os.path.exists("/.dockerenv") or os.getenv("DOCKER_CONTAINER") == "true"
    default_host = "0.0.0.0" if is_container else "127.0.0.1"  # nosec B104
    host = os.getenv("HOST", default_host)

    print("🚀 Ustad Protocol MCP Server (FastMCP 2.x + SSE)")
    print(f"📍 Running on {host}:{port}")
    print("🔧 Tools: ustad_think, ustad_search")
    print(f"🔑 Tavily API: {'✓ Configured' if os.getenv('TAVILY_API_KEY') else '✗ Not configured'}")

    # Run with SSE transport
    mcp.run(transport="sse", host=host, port=port)
