"""Search service for fact-checking and information retrieval using Tavily API.

This module provides a reusable search interface that can be used by both
the MCP server and the workflow orchestrator, following SOLID principles.
"""

import os
from typing import Any

import httpx


async def tavily_search(
    query: str, max_results: int = 5, search_type: str = "general"
) -> dict[str, Any]:
    """Search using Tavily API for fact-checking and information retrieval.

    Args:
        query: Search query string
        max_results: Maximum number of results to return (default 5)
        search_type: Type of search - "general" or "news" (default "general")

    Returns:
        Dictionary with search results or error information
    """
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
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()

            data = response.json()

            # Format the response
            return {
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

    except httpx.HTTPStatusError as e:
        return {
            "error": "Search request failed",
            "status_code": e.response.status_code,
            "message": str(e),
        }
    except Exception as e:
        return {"error": "Search error", "message": str(e)}
