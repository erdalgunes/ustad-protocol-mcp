"""Proper FastMCP Client integration tests following best practices.

This implements the correct testing approach using fastmcp.Client
for in-memory testing as recommended by FastMCP documentation.
"""

import os
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastmcp import Client

# Patch rate limiter before importing the server
with patch("src.rate_limiting.create_rate_limiter", return_value=None):
    from ustad_mcp_server import mcp


@pytest.mark.asyncio
class TestMcpIntegration:
    """Integration tests using proper FastMCP Client patterns."""

    async def test_ustad_think_through_mcp(self) -> None:
        """Test sequential thinking tool through MCP protocol."""
        async with Client(mcp) as client:
            # Test basic thinking
            result = await client.call_tool(
                "ustad_think",
                {
                    "thought": "Analyzing the problem",
                    "thought_number": 1,
                    "total_thoughts": 3,
                    "next_thought_needed": True,
                },
            )

            # Access the tool result data properly
            data = result.structured_content or result.data
            assert data["thought"] == "Analyzing the problem"
            assert data["thoughtNumber"] == 1
            assert data["nextThoughtNeeded"] is True
            assert "thoughtHistoryLength" in data

    async def test_ustad_search_through_mcp_no_key(self) -> None:
        """Test search tool through MCP protocol without API key."""
        with patch.dict(os.environ, {}, clear=True):
            async with Client(mcp) as client:
                result = await client.call_tool("ustad_search", {"query": "test query"})

                data = result.structured_content or result.data
                assert "error" in data
                assert "Tavily API key not configured" in data["error"]

    @patch("httpx.AsyncClient")
    async def test_ustad_search_through_mcp_success(self, mock_client_class: Mock) -> None:
        """Test successful search through MCP protocol."""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = {
            "answer": "Test answer from Tavily",
            "results": [
                {
                    "title": "Test Result",
                    "url": "https://example.com",
                    "content": "Test content",
                    "score": 0.95,
                }
            ],
        }
        mock_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client

        with patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"}):
            async with Client(mcp) as client:
                result = await client.call_tool(
                    "ustad_search", {"query": "Python best practices", "max_results": 1}
                )

                data = result.structured_content or result.data
                assert data["answer"] == "Test answer from Tavily"
                assert len(data["results"]) == 1
                assert data["results"][0]["title"] == "Test Result"

    async def test_health_resource_through_mcp(self) -> None:
        """Test health check resource through MCP protocol."""
        import json

        async with Client(mcp) as client:
            result = await client.read_resource("health://server/status")

            # Resources return list of TextResourceContents objects
            assert isinstance(result, list)
            assert len(result) > 0
            resource_content = result[0]

            # Parse the JSON text content
            data = json.loads(resource_content.text)

            assert data["status"] == "healthy"
            assert data["server"] == "ustad-protocol-mcp"
            assert "tools" in data
            assert "ustad_think" in data["tools"]
            assert "ustad_search" in data["tools"]

    async def test_complete_thinking_flow_through_mcp(self) -> None:
        """Test complete sequential thinking flow through MCP protocol."""
        async with Client(mcp) as client:
            # Step 1: Initial thought
            result1 = await client.call_tool(
                "ustad_think",
                {
                    "thought": "I need to research best practices",
                    "thought_number": 1,
                    "total_thoughts": 3,
                    "next_thought_needed": True,
                },
            )

            data1 = result1.structured_content or result1.data
            assert data1["thoughtHistoryLength"] >= 1

            # Step 2: Revision
            result2 = await client.call_tool(
                "ustad_think",
                {
                    "thought": "Let me refine my approach",
                    "thought_number": 2,
                    "total_thoughts": 3,
                    "next_thought_needed": True,
                    "is_revision": True,
                    "revises_thought": 1,
                },
            )

            data2 = result2.structured_content or result2.data
            assert data2["isRevision"] is True
            assert data2["revisesThought"] == 1

            # Step 3: Final conclusion
            result3 = await client.call_tool(
                "ustad_think",
                {
                    "thought": "Final solution based on research",
                    "thought_number": 3,
                    "total_thoughts": 3,
                    "next_thought_needed": False,
                },
            )

            data3 = result3.structured_content or result3.data
            assert data3["nextThoughtNeeded"] is False
            assert data3["thoughtHistoryLength"] >= 3

    async def test_branching_through_mcp(self) -> None:
        """Test branching functionality through MCP protocol."""
        async with Client(mcp) as client:
            # Main branch
            await client.call_tool(
                "ustad_think",
                {
                    "thought": "Main approach",
                    "thought_number": 1,
                    "total_thoughts": 3,
                    "next_thought_needed": True,
                },
            )

            # Create branch
            result = await client.call_tool(
                "ustad_think",
                {
                    "thought": "Alternative approach",
                    "thought_number": 2,
                    "total_thoughts": 4,
                    "next_thought_needed": True,
                    "branch_from_thought": 1,
                    "branch_id": "alternative",
                },
            )

            data = result.structured_content or result.data
            assert data["branchId"] == "alternative"
            assert "alternative" in data["branches"]

    async def test_error_handling_invalid_thought_number(self) -> None:
        """Test error handling for invalid thought number."""
        async with Client(mcp) as client:
            result = await client.call_tool(
                "ustad_think",
                {
                    "thought": "Invalid thought",
                    "thought_number": 0,  # Invalid: should be >= 1
                    "total_thoughts": 3,
                    "next_thought_needed": True,
                },
            )

            data = result.structured_content or result.data
            assert "error" in data
            assert "invalid" in data["error"].lower() or "thought" in data["error"].lower()

    async def test_error_handling_missing_required_field(self) -> None:
        """Test error handling for missing required fields."""
        from fastmcp.exceptions import ToolError

        async with Client(mcp) as client:
            with pytest.raises(ToolError) as exc_info:
                await client.call_tool(
                    "ustad_think",
                    {
                        "thought": "Missing fields",
                        # Missing thought_number and total_thoughts
                        "next_thought_needed": True,
                    },
                )

            # Verify the error message mentions required fields
            assert "required" in str(exc_info.value).lower()

    async def test_search_with_different_search_types(self) -> None:
        """Test search with different search types."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = Mock()
            mock_response.json.return_value = {
                "answer": "News results",
                "results": [
                    {"title": "News", "url": "https://example.com", "content": "News content"}
                ],
            }
            mock_response.raise_for_status = Mock()

            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            with patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"}):
                async with Client(mcp) as client:
                    # Test news search type
                    result = await client.call_tool(
                        "ustad_search",
                        {"query": "latest news", "search_type": "news", "max_results": 1},
                    )

                    data = result.structured_content or result.data
                    assert "results" in data

                    # Verify the API was called with news endpoint
                    mock_client.post.assert_called()
                    call_args = mock_client.post.call_args
                    assert "news" in str(call_args)

    async def test_concurrent_thinking_sessions(self) -> None:
        """Test handling of concurrent thinking sessions."""
        async with Client(mcp) as client:
            # Start first thinking session
            result1 = await client.call_tool(
                "ustad_think",
                {
                    "thought": "First session",
                    "thought_number": 1,
                    "total_thoughts": 2,
                    "next_thought_needed": True,
                },
            )

            # Start second thinking session (should reset)
            result2 = await client.call_tool(
                "ustad_think",
                {
                    "thought": "Second session",
                    "thought_number": 1,
                    "total_thoughts": 3,
                    "next_thought_needed": True,
                },
            )

            data1 = result1.structured_content or result1.data
            data2 = result2.structured_content or result2.data

            # Both should succeed
            assert data1["thoughtNumber"] == 1
            assert data2["thoughtNumber"] == 1
            # History should accumulate
            assert data2["thoughtHistoryLength"] > data1["thoughtHistoryLength"]

    async def test_search_empty_query(self) -> None:
        """Test search with empty query."""
        with patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"}):
            async with Client(mcp) as client:
                result = await client.call_tool("ustad_search", {"query": "", "max_results": 1})

                data = result.structured_content or result.data
                # Should handle empty query gracefully
                assert "error" in data or "results" in data

    async def test_max_results_boundary(self) -> None:
        """Test search with boundary values for max_results."""
        with patch("httpx.AsyncClient") as mock_client_class:
            mock_response = Mock()
            mock_response.json.return_value = {
                "answer": "Test",
                "results": [
                    {
                        "title": f"Result {i}",
                        "url": f"https://example{i}.com",
                        "content": f"Content {i}",
                    }
                    for i in range(10)
                ],
            }
            mock_response.raise_for_status = Mock()

            mock_client = AsyncMock()
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_client_class.return_value.__aenter__.return_value = mock_client

            with patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"}):
                async with Client(mcp) as client:
                    # Test with max value
                    result = await client.call_tool(
                        "ustad_search", {"query": "test", "max_results": 10}
                    )

                    data = result.structured_content or result.data
                    assert len(data["results"]) <= 10
