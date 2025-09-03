#!/usr/bin/env python3
"""
Ustad Protocol MCP Server - Minimal, Clean Implementation
Uses FastMCP with SSE protocol for containerized deployment.
Only two tools: ustad-think (sequential thinking) and ustad-search (Tavily).
"""

import os
from typing import Any

from fastmcp import FastMCP

# Import our implementations
from src.search_service import tavily_search
from src.sequential_thinking import SequentialThinkingServer

# Initialize FastMCP server
mcp = FastMCP(
    name="ustad-protocol-mcp",
    description="Minimal MCP server with sequential thinking and search capabilities",
)

# Initialize sequential thinking server (singleton pattern)
thinking_server = SequentialThinkingServer()


@mcp.tool()  # type: ignore[misc]
async def ustad_think(
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
    """
    Sequential thinking tool for structured problem-solving.

    Args:
        thought: Current thinking step
        thought_number: Current thought number (starting from 1)
        total_thoughts: Estimated total thoughts needed
        next_thought_needed: Whether another thought is needed
        is_revision: Whether this revises a previous thought
        revises_thought: Which thought number is being revised
        branch_from_thought: Branching point thought number
        branch_id: Identifier for the current branch
        needs_more_thoughts: If more thoughts are needed than initially estimated

    Returns:
        Dictionary with thought processing results and state
    """
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
async def ustad_search(
    query: str, max_results: int = 5, search_type: str = "general"
) -> dict[str, Any]:
    """
    Search tool using Tavily API for fact-checking and information retrieval.

    Args:
        query: Search query string
        max_results: Maximum number of results to return (default 5)
        search_type: Type of search - "general" or "news" (default "general")

    Returns:
        Dictionary with search results
    """
    # Delegate to the shared search service
    return await tavily_search(query, max_results, search_type)


@mcp.resource("health")  # type: ignore[misc]
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint for container orchestration.

    Returns:
        Dictionary with server health status
    """
    return {
        "status": "healthy",
        "server": "ustad-protocol-mcp",
        "version": "1.0.0",
        "tools": ["ustad_think", "ustad_search"],
        "thinking_history_length": len(thinking_server.get_thought_history()),
        "tavily_configured": bool(os.getenv("TAVILY_API_KEY")),
    }


if __name__ == "__main__":
    # For containerized deployment with SSE
    import uvicorn
    from fastapi import FastAPI
    from mcp.server.sse import SseServerTransport
    from starlette.applications import Starlette
    from starlette.responses import JSONResponse
    from starlette.routing import Mount, Route

    # Create SSE transport
    transport = SseServerTransport("/messages/")

    async def handle_sse(request: Any) -> None:
        """Handle SSE connections for MCP."""
        async with transport.connect_sse(request.scope, request.receive, request._send) as (
            in_stream,
            out_stream,
        ):
            await mcp._mcp_server.run(
                in_stream, out_stream, mcp._mcp_server.create_initialization_options()
            )

    async def health_check(request: Any) -> Any:  # Returns JSONResponse
        """Health check endpoint."""
        return JSONResponse({"status": "healthy", "server": "ustad-protocol", "version": "1.0.0"})

    # Create Starlette app for SSE
    sse_app = Starlette(
        routes=[
            Route("/sse", handle_sse, methods=["GET"]),
            Route("/health", health_check, methods=["GET"]),
            Mount("/messages/", app=transport.handle_post_message),
        ]
    )

    # Create FastAPI wrapper
    app = FastAPI(title="Ustad Protocol MCP Server")
    app.mount("/", sse_app)

    # Run with uvicorn (container-friendly)
    port = int(os.getenv("PORT", "8000"))

    # Detect if running in container and set appropriate host
    # In containers, we must bind to 0.0.0.0 to be accessible
    # In development, we bind to localhost for security
    is_container = os.path.exists("/.dockerenv") or os.getenv("DOCKER_CONTAINER") == "true"
    default_host = "0.0.0.0" if is_container else "127.0.0.1"  # nosec B104 - Conditional binding only in containers
    host = os.getenv("HOST", default_host)

    print("🚀 Ustad Protocol MCP Server (SSE)")
    print(f"📍 Running on {host}:{port}")
    print("🔧 Tools: ustad_think, ustad_search")
    print(f"🔑 Tavily API: {'✓ Configured' if os.getenv('TAVILY_API_KEY') else '✗ Not configured'}")

    uvicorn.run(app, host=host, port=port, log_level="info")
