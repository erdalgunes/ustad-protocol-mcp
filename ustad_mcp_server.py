#!/usr/bin/env python3
"""
Ustad Protocol MCP Server - Minimal, Clean Implementation
Uses FastMCP with SSE protocol for containerized deployment.
Only two tools: ustad-think (sequential thinking) and ustad-search (Tavily).
"""

import logging
import os
from typing import Any

from fastmcp import FastMCP

from src.auth import create_auth_verifier
from src.exceptions import InvalidThoughtError, ThoughtValidationError
from src.intent_analyzer import analyze_intent
from src.rate_limiting import create_rate_limiter
from src.search_service import tavily_search

# Import our sequential thinking implementation and auth
from src.sequential_thinking import SequentialThinkingServer

# Configure logging for security and debugging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize OAuth 2.1 authentication (addresses CVE-2025-49596)
auth_verifier = create_auth_verifier()

# Initialize rate limiting for abuse prevention
rate_limiter = create_rate_limiter()

# Log security features status
if auth_verifier:
    logger.info("🔐 OAuth 2.1 authentication ENABLED - Server is secure")
else:
    logger.warning("⚠️  Authentication DISABLED - Development mode only")

if rate_limiter:
    logger.info("🚦 Rate limiting ENABLED - DoS protection active")
else:
    logger.warning("⚠️  Rate limiting DISABLED - Install slowapi for production")

# Initialize FastMCP server with optional authentication
mcp = FastMCP(
    name="ustad-protocol-mcp",
    auth=auth_verifier,  # None if auth not configured, enables development mode
)

# Add rate limiting middleware if available
if rate_limiter:
    try:
        mcp.add_middleware(rate_limiter)
        logger.info("Rate limiting middleware added successfully")
    except Exception as e:
        logger.exception("Failed to add rate limiting middleware")

# Initialize sequential thinking server (singleton pattern)
thinking_server = SequentialThinkingServer()


# Standalone function for processing thoughts (testable)
async def process_thought(
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
    Process a sequential thinking step with optional intent analysis.

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
    # Step 1: Analyze intent if OpenAI is configured (first thought only)
    intent_result = None
    if thought_number == 1:
        try:
            # Get context from previous thoughts if available
            context = None
            history = thinking_server.get_thought_history()
            if history:
                # Convert thought dicts to strings for context
                context_thoughts = [
                    str(t.get("thought", "")) if isinstance(t, dict) else str(t)
                    for t in history[-3:]
                ]
                context = "Previous thoughts: " + "; ".join(context_thoughts)

            # Analyze the intent
            intent_result = await analyze_intent(thought, context)

            # Log intent analysis for monitoring
            logger.info(
                "Intent analysis: needs_fact_check=%s, complexity=%s, steps_needed=%s",
                intent_result.get("needs_fact_check"),
                intent_result.get("complexity"),
                intent_result.get("reasoning_steps_needed"),
            )

            # Enforce minimum 10 thinking steps as per requirements
            min_steps = max(10, intent_result.get("reasoning_steps_needed", 10))
            if total_thoughts < min_steps:
                logger.info(
                    "Adjusting total_thoughts from %d to %d based on intent analysis",
                    total_thoughts,
                    min_steps,
                )
                total_thoughts = min_steps

        except Exception as e:
            # Log but don't fail on intent analysis errors
            logger.warning("Intent analysis failed (continuing without it): %s", e)

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

    try:
        # Process the thought
        result = thinking_server.process_thought(thought_data)

        # Add metadata about the thinking state
        result["thoughtHistoryLength"] = len(thinking_server.get_thought_history())
        result["branches"] = list(thinking_server.get_branches().keys())

        # Add intent analysis result if available
        if intent_result and intent_result.get("analysis_available"):
            result["intentAnalysis"] = {
                "needs_fact_check": intent_result.get("needs_fact_check", False),
                "complexity": intent_result.get("complexity", "medium"),
                "min_steps": max(10, intent_result.get("reasoning_steps_needed", 10)),
                "confidence": intent_result.get("confidence", 0.0),
            }

            # Emit SSE event for intent analysis (this will be part of the response)
            result["sse_event"] = {"type": "intent_analyzed", "data": result["intentAnalysis"]}

        return result
    except (InvalidThoughtError, ThoughtValidationError) as e:
        # Log validation errors for debugging
        logger.warning("Thought validation error: %s", e)
        # Return structured error response using our custom exception's to_dict method
        return e.to_dict()
    except Exception:
        # Log unexpected errors with full traceback
        logger.exception("Unexpected error in process_thought")
        # Return safe generic error
        return {"error": "Processing failed", "message": "Unable to process thought at this time"}


# Standalone function for Tavily search (testable)
async def search_tavily(
    query: str, max_results: int = 5, search_type: str = "general"
) -> dict[str, Any]:
    """
    Search using Tavily API for fact-checking and information retrieval.

    Args:
        query: Search query string
        max_results: Maximum number of results to return (default 5)
        search_type: Type of search - "general" or "news" (default "general")

    Returns:
        Dictionary with search results
    """
    # Delegate to the shared search service
    return await tavily_search(query, max_results, search_type)


# Standalone function for health check (testable)
async def get_health_status() -> dict[str, Any]:
    """
    Get server health status.

    Returns:
        Dictionary with server health status
    """
    return {
        "status": "healthy",
        "server": "ustad-protocol-mcp",
        "version": "0.1.0",
        "tools": ["ustad_think", "ustad_search"],
        "thinking_history_length": len(thinking_server.get_thought_history()),
        "tavily_configured": bool(os.getenv("TAVILY_API_KEY")),
    }


# MCP Tool Decorators (thin wrappers)
@mcp.tool()
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

    This is the MCP wrapper for the process_thought function.
    """
    return await process_thought(
        thought=thought,
        thought_number=thought_number,
        total_thoughts=total_thoughts,
        next_thought_needed=next_thought_needed,
        is_revision=is_revision,
        revises_thought=revises_thought,
        branch_from_thought=branch_from_thought,
        branch_id=branch_id,
        needs_more_thoughts=needs_more_thoughts,
    )


@mcp.tool()
async def ustad_search(
    query: str, max_results: int = 5, search_type: str = "general"
) -> dict[str, Any]:
    """
    Search tool using Tavily API.

    This is the MCP wrapper for the search_tavily function.
    """
    return await search_tavily(query=query, max_results=max_results, search_type=search_type)


@mcp.resource("health://server/status")
async def health_check() -> dict[str, Any]:
    """
    Health check endpoint for container orchestration.

    This is the MCP wrapper for the get_health_status function.
    """
    return await get_health_status()


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

    async def health_endpoint(request: Any) -> Any:  # Returns JSONResponse
        """Health check endpoint."""
        return JSONResponse(await get_health_status())

    # Create Starlette app for SSE
    sse_app = Starlette(
        routes=[
            Route("/sse", handle_sse, methods=["GET"]),
            Route("/health", health_endpoint, methods=["GET"]),
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
