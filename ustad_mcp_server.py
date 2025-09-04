#!/usr/bin/env python3
"""
Ustad Protocol MCP Server - Official MCP SDK Implementation
Uses official MCP Python SDK with SSE transport for containerized deployment.
Only two tools: ustad-think (sequential thinking) and ustad-search (Tavily).
"""

import json
import os
from typing import Any

import httpx
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from src.constants import CAPABILITIES_DATA, HEALTH_DATA
from src.sequential_thinking import SequentialThinkingServer

# Initialize MCP server
server = Server("ustad-protocol-mcp")

# Initialize sequential thinking server (singleton pattern)
thinking_server = SequentialThinkingServer()


@server.list_tools()  # type: ignore[misc]
async def list_tools() -> list[Tool]:  # type: ignore[no-any-unimported]
    """List available tools."""
    return [
        Tool(
            name="ustad_think",
            description="Sequential thinking tool for structured problem-solving.",
            inputSchema={
                "type": "object",
                "properties": {
                    "thought": {"type": "string", "description": "The thought content"},
                    "thought_number": {"type": "integer", "description": "Current thought number"},
                    "total_thoughts": {
                        "type": "integer",
                        "description": "Total number of thoughts planned",
                    },
                    "next_thought_needed": {
                        "type": "boolean",
                        "description": "Whether another thought is needed",
                    },
                    "is_revision": {
                        "type": "boolean",
                        "default": False,
                        "description": "Whether this is a revision",
                    },
                    "revises_thought": {
                        "type": "integer",
                        "description": "Which thought this revises",
                        "nullable": True,
                    },
                    "branch_from_thought": {
                        "type": "integer",
                        "description": "Which thought to branch from",
                        "nullable": True,
                    },
                    "branch_id": {
                        "type": "string",
                        "description": "Branch identifier",
                        "nullable": True,
                    },
                    "needs_more_thoughts": {
                        "type": "boolean",
                        "default": False,
                        "description": "Whether more thoughts are needed",
                    },
                },
                "required": ["thought", "thought_number", "total_thoughts", "next_thought_needed"],
            },
        ),
        Tool(
            name="ustad_search",
            description="Search tool using Tavily API for fact-checking and information retrieval.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query"},
                    "max_results": {
                        "type": "integer",
                        "default": 5,
                        "description": "Maximum number of results",
                    },
                    "search_type": {
                        "type": "string",
                        "default": "general",
                        "description": "Type of search",
                    },
                },
                "required": ["query"],
            },
        ),
    ]


@server.call_tool()  # type: ignore[misc]
async def call_tool(name: str, arguments: dict[str, Any]) -> list[dict[str, Any]]:
    """Handle tool calls."""
    if name == "ustad_think":
        # Build thought data
        thought_data = {
            "thought": arguments["thought"],
            "thoughtNumber": arguments["thought_number"],
            "totalThoughts": arguments["total_thoughts"],
            "nextThoughtNeeded": arguments["next_thought_needed"],
        }

        # Add optional fields if provided
        if arguments.get("is_revision", False):
            thought_data["isRevision"] = arguments["is_revision"]
        if arguments.get("revises_thought") is not None:
            thought_data["revisesThought"] = arguments["revises_thought"]
        if arguments.get("branch_from_thought") is not None:
            thought_data["branchFromThought"] = arguments["branch_from_thought"]
        if arguments.get("branch_id") is not None:
            thought_data["branchId"] = arguments["branch_id"]
        if arguments.get("needs_more_thoughts", False):
            thought_data["needsMoreThoughts"] = arguments["needs_more_thoughts"]

        # Process the thought
        result = thinking_server.process_thought(thought_data)

        # Add metadata about the thinking state
        result["thoughtHistoryLength"] = len(thinking_server.get_thought_history())
        result["branches"] = list(thinking_server.get_branches().keys())

        return [{"type": "text", "text": json.dumps(result)}]

    if name == "ustad_search":
        # Get Tavily API key from environment
        api_key = os.getenv("TAVILY_API_KEY")
        print(f"DEBUG: API key present: {bool(api_key)}")
        print(f"DEBUG: API key length: {len(api_key) if api_key else 0}")
        print(f"DEBUG: API key starts with: {api_key[:10] if api_key else 'None'}...")
        print(f"DEBUG: All env vars: {list(os.environ.keys())}")
        print(f"DEBUG: DOCKER_CONTAINER env: {os.getenv('DOCKER_CONTAINER')}")

        if not api_key:
            error_result = {
                "error": "Tavily API key not configured",
                "message": "Please set TAVILY_API_KEY environment variable",
            }
            return [{"type": "text", "text": json.dumps(error_result)}]

        # Prepare the search request
        url = "https://api.tavily.com/search"
        headers = {"Content-Type": "application/json"}
        payload = {
            "api_key": api_key,
            "query": arguments["query"],
            "max_results": arguments.get("max_results", 5),
            "search_depth": "basic",
            "include_answer": True,
            "include_raw_content": False,
            "include_images": False,
        }

        # Add topic for news searches
        if arguments.get("search_type") == "news":
            payload["topic"] = "news"

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()

                data = response.json()

                # Format the response
                result = {
                    "query": arguments["query"],
                    "answer": data.get("answer", ""),
                    "results": [
                        {
                            "title": r.get("title", ""),
                            "url": r.get("url", ""),
                            "content": r.get("content", ""),
                            "score": r.get("score", 0),
                        }
                        for r in data.get("results", [])[: arguments.get("max_results", 5)]
                    ],
                    "result_count": len(data.get("results", [])),
                    "search_type": arguments.get("search_type", "general"),
                }

                return [{"type": "text", "text": json.dumps(result)}]

        except httpx.HTTPStatusError as e:
            print(f"DEBUG: HTTP Error - Status: {e.response.status_code}")
            print(f"DEBUG: Response text: {e.response.text}")
            print(f"DEBUG: Request payload was: {payload}")
            error_result = {
                "error": "Search request failed",
                "status_code": e.response.status_code,
                "message": str(e),
                "response_text": e.response.text[:200],
            }
            return [{"type": "text", "text": json.dumps(error_result)}]
        except Exception as e:
            error_result = {"error": "Search error", "message": str(e)}
            return [{"type": "text", "text": json.dumps(error_result)}]

    else:
        return [{"type": "text", "text": f"Unknown tool: {name}"}]


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


async def health_check(request: Any) -> JSONResponse:  # type: ignore[no-any-unimported]
    """Health check endpoint for deployment platforms like Render."""
    health_data = get_health_data()
    return JSONResponse(health_data)


def main() -> None:
    """Run the MCP server with SSE transport."""
    import uvicorn
    from mcp.server.models import InitializationOptions
    from mcp.types import ServerCapabilities, ToolsCapability
    from starlette.responses import Response

    print("🚀 Ustad Protocol MCP Server (Official SDK + SSE)")
    print("🔧 Tools: ustad_think, ustad_search")
    print(f"🔑 Tavily API: {'✓ Configured' if os.getenv('TAVILY_API_KEY') else '✗ Not configured'}")

    # Create SSE transport
    sse = SseServerTransport("/messages/")

    # SSE handler
    async def handle_sse(request: Any) -> Response:  # type: ignore[no-any-unimported]
        async with sse.connect_sse(request.scope, request.receive, request._send) as streams:
            await server.run(
                streams[0],
                streams[1],
                InitializationOptions(
                    server_name="ustad-protocol-mcp",
                    server_version="1.0.0",
                    capabilities=ServerCapabilities(tools=ToolsCapability()),
                ),
            )
        return Response()

    # Create routes
    routes = [
        Route("/sse", endpoint=handle_sse, methods=["GET"]),
        Mount("/messages/", app=sse.handle_post_message),
    ]

    # Add health check route
    async def health_check_inner(request: Any) -> JSONResponse:  # type: ignore[no-any-unimported]
        health_data = get_health_data()
        return JSONResponse(health_data)

    routes.append(Route("/health", endpoint=health_check_inner, methods=["GET"]))

    # Create and run Starlette app
    starlette_app = Starlette(routes=routes)

    port = int(os.getenv("PORT", "8080"))
    print(f"🌐 Starting SSE server on port {port}")
    uvicorn.run(starlette_app, host="0.0.0.0", port=port)  # nosec B104


if __name__ == "__main__":
    main()
