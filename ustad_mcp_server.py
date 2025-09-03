#!/usr/bin/env python3
"""
Ustad Protocol MCP Server - Official MCP SDK Implementation
Uses official MCP Python SDK with SSE protocol for containerized deployment.
Only two tools: ustad-think (sequential thinking) and ustad-search (Tavily).
"""

import os
from typing import Any

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool
from starlette.requests import Request

from src.constants import CAPABILITIES_DATA, HEALTH_DATA
from src.sequential_thinking import SequentialThinkingServer

# Initialize MCP server
server = Server("ustad-protocol-mcp")

# Initialize sequential thinking server (singleton pattern)
thinking_server = SequentialThinkingServer()


@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="ustad_think",
            description="Sequential thinking tool for structured problem-solving",
            inputSchema={
                "type": "object",
                "properties": {
                    "thought": {"type": "string", "description": "Current thinking step"},
                    "thought_number": {
                        "type": "integer",
                        "description": "Current thought number (starting from 1)",
                    },
                    "total_thoughts": {
                        "type": "integer",
                        "description": "Estimated total thoughts needed",
                    },
                    "next_thought_needed": {
                        "type": "boolean",
                        "description": "Whether another thought is needed",
                    },
                    "is_revision": {
                        "type": "boolean",
                        "default": False,
                        "description": "Whether this revises a previous thought",
                    },
                    "revises_thought": {
                        "type": "integer",
                        "description": "Which thought number is being revised",
                    },
                    "branch_from_thought": {
                        "type": "integer",
                        "description": "Branching point thought number",
                    },
                    "branch_id": {
                        "type": "string",
                        "description": "Identifier for the current branch",
                    },
                    "needs_more_thoughts": {
                        "type": "boolean",
                        "default": False,
                        "description": "If more thoughts are needed than initially estimated",
                    },
                },
                "required": ["thought", "thought_number", "total_thoughts", "next_thought_needed"],
            },
        ),
        Tool(
            name="ustad_search",
            description="Search tool using Tavily API for fact-checking and information retrieval",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query string"},
                    "max_results": {
                        "type": "integer",
                        "default": 5,
                        "description": "Maximum number of results to return",
                    },
                    "search_type": {
                        "type": "string",
                        "default": "general",
                        "description": "Type of search - 'general' or 'news'",
                    },
                },
                "required": ["query"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: dict[str, Any]) -> list[dict[str, Any]]:
    """Handle tool calls."""
    if name == "ustad_think":
        return await handle_ustad_think(arguments)
    if name == "ustad_search":
        return await handle_ustad_search(arguments)
    raise ValueError(f"Unknown tool: {name}")


async def handle_ustad_think(arguments: dict[str, Any]) -> list[dict[str, Any]]:
    """Handle ustad_think tool call."""
    # Extract arguments
    thought = arguments["thought"]
    thought_number = arguments["thought_number"]
    total_thoughts = arguments["total_thoughts"]
    next_thought_needed = arguments["next_thought_needed"]
    is_revision = arguments.get("is_revision", False)
    revises_thought = arguments.get("revises_thought")
    branch_from_thought = arguments.get("branch_from_thought")
    branch_id = arguments.get("branch_id")
    needs_more_thoughts = arguments.get("needs_more_thoughts", False)

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

    return [{"type": "text", "text": str(result)}]


async def handle_ustad_search(arguments: dict[str, Any]) -> list[dict[str, Any]]:
    """Handle ustad_search tool call."""
    import httpx

    query = arguments["query"]
    max_results = arguments.get("max_results", 5)
    search_type = arguments.get("search_type", "general")

    # Get Tavily API key from environment
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        error_result = {
            "error": "Tavily API key not configured",
            "message": "Please set TAVILY_API_KEY environment variable",
        }
        return [{"type": "text", "text": str(error_result)}]

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
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
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

            return [{"type": "text", "text": str(result)}]

    except httpx.HTTPStatusError as e:
        error_result = {
            "error": "Search request failed",
            "status_code": e.response.status_code,
            "message": str(e),
        }
        return [{"type": "text", "text": str(error_result)}]
    except Exception as e:
        error_result = {"error": "Search error", "message": str(e)}
        return [{"type": "text", "text": str(error_result)}]


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
    import uvicorn
    from starlette.applications import Starlette
    from starlette.middleware.cors import CORSMiddleware
    from starlette.responses import JSONResponse
    from starlette.routing import Mount, Route

    async def health_check(request: Request) -> JSONResponse:
        """Health check endpoint."""
        return JSONResponse(get_health_data())

    async def capabilities_endpoint(request: Request) -> JSONResponse:
        """Capabilities endpoint for version and feature detection."""
        return JSONResponse(get_capabilities_data())

    # Create SSE transport
    sse_transport = SseServerTransport("/messages")

    # Create handler for SSE connection
    async def handle_sse(request: Request) -> None:
        """Handle SSE connections and run MCP server."""
        async with sse_transport.connect_sse(
            request.scope,
            request.receive,
            request._send,
        ) as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options(),
            )

    # Create Starlette app for SSE
    app = Starlette(
        routes=[
            Route("/health", health_check, methods=["GET"]),
            Route("/capabilities", capabilities_endpoint, methods=["GET"]),
            Route("/sse", handle_sse, methods=["GET"]),
            Mount("/messages/", sse_transport.handle_post_message),
        ]
    )

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allow all origins for development
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    # Run with uvicorn (container-friendly)
    port = int(os.getenv("PORT", "8000"))

    # Detect if running in container and set appropriate host
    is_container = os.path.exists("/.dockerenv") or os.getenv("DOCKER_CONTAINER") == "true"
    default_host = "0.0.0.0" if is_container else "127.0.0.1"  # nosec B104
    host = os.getenv("HOST", default_host)

    print("🚀 Ustad Protocol MCP Server (Official SDK + SSE)")
    print(f"📍 Running on {host}:{port}")
    print("🔧 Tools: ustad_think, ustad_search")
    print(f"🔑 Tavily API: {'✓ Configured' if os.getenv('TAVILY_API_KEY') else '✗ Not configured'}")

    uvicorn.run(app, host=host, port=port, log_level="info")
