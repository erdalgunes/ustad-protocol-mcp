"""Tests for Ustad MCP Server.

Tests the standalone functions directly rather than the MCP-decorated versions.
This follows SOLID principles - we test the business logic separately from framework integration.
"""

import os
from unittest.mock import AsyncMock, Mock, patch

import httpx
import pytest

# Import the standalone functions we need to test
from ustad_mcp_server import (
    get_health_status,
    mcp,
    process_thought,
    search_tavily,
    thinking_server,
)


@pytest.mark.asyncio
class TestProcessThought:
    """Test process_thought function."""

    async def test_process_thought_basic(self) -> None:
        """Test basic thought processing."""
        thinking_server.reset()  # Clean state

        result = await process_thought(
            thought="Test thought",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
        )

        assert result["thought"] == "Test thought"
        assert result["thoughtNumber"] == 1
        assert result["totalThoughts"] == 3
        assert result["nextThoughtNeeded"] is True
        assert result["thoughtHistoryLength"] == 1
        assert result["branches"] == []

    async def test_process_thought_with_revision(self) -> None:
        """Test thought with revision."""
        thinking_server.reset()

        # First thought
        await process_thought(
            thought="Initial thought",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
        )

        # Revision
        result = await process_thought(
            thought="Revised thought",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=True,
            is_revision=True,
            revises_thought=1,
        )

        assert result["isRevision"] is True
        assert result["revisesThought"] == 1
        assert result["thoughtHistoryLength"] == 2

    async def test_process_thought_with_branching(self) -> None:
        """Test thought with branching."""
        thinking_server.reset()

        # Initial thought
        await process_thought(
            thought="Main branch",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
        )

        # Branch
        result = await process_thought(
            thought="Alternative approach",
            thought_number=2,
            total_thoughts=4,
            next_thought_needed=True,
            branch_from_thought=1,
            branch_id="alt-approach",
        )

        assert result["branchFromThought"] == 1
        assert result["branchId"] == "alt-approach"
        assert "alt-approach" in result["branches"]

    async def test_process_thought_completion(self) -> None:
        """Test marking thinking as complete."""
        thinking_server.reset()

        result = await process_thought(
            thought="Final thought",
            thought_number=1,
            total_thoughts=1,
            next_thought_needed=False,
        )

        assert result["nextThoughtNeeded"] is False
        assert thinking_server.is_complete() is True

    async def test_process_thought_needs_more(self) -> None:
        """Test when more thoughts are needed than initially estimated."""
        thinking_server.reset()

        result = await process_thought(
            thought="Complex problem",
            thought_number=5,
            total_thoughts=5,
            next_thought_needed=True,
            needs_more_thoughts=True,
        )

        assert result["needsMoreThoughts"] is True
        assert result["nextThoughtNeeded"] is True

    async def test_process_thought_validation_error(self) -> None:
        """Test validation errors are properly raised."""
        with pytest.raises(ValueError, match="Invalid thought number"):
            await process_thought(
                thought="Test",
                thought_number=0,  # Invalid
                total_thoughts=3,
                next_thought_needed=True,
            )


@pytest.mark.asyncio
class TestSearchTavily:
    """Test search_tavily function."""

    async def test_search_no_api_key(self) -> None:
        """Test search without API key configured."""
        with patch.dict(os.environ, {}, clear=True):
            result = await search_tavily("test query")

            assert "error" in result
            assert result["error"] == "Tavily API key not configured"
            assert "TAVILY_API_KEY" in result["message"]

    @patch("httpx.AsyncClient")
    async def test_search_success(self, mock_client_class: Mock) -> None:
        """Test successful search."""
        # Setup mock
        mock_response = Mock()
        mock_response.json.return_value = {
            "answer": "Test answer",
            "results": [
                {
                    "title": "Result 1",
                    "url": "https://example.com/1",
                    "content": "Content 1",
                    "score": 0.9,
                },
                {
                    "title": "Result 2",
                    "url": "https://example.com/2",
                    "content": "Content 2",
                    "score": 0.8,
                },
            ],
        }
        mock_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client

        with patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"}):
            result = await search_tavily("test query", max_results=2)

        assert result["query"] == "test query"
        assert result["answer"] == "Test answer"
        assert len(result["results"]) == 2
        assert result["results"][0]["title"] == "Result 1"
        assert result["result_count"] == 2
        assert result["search_type"] == "general"

    @patch("httpx.AsyncClient")
    async def test_search_news_type(self, mock_client_class: Mock) -> None:
        """Test search with news type."""
        mock_response = Mock()
        mock_response.json.return_value = {"answer": "", "results": []}
        mock_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client

        with patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"}):
            result = await search_tavily("news query", search_type="news")

        # Verify the API was called with news topic
        call_args = mock_client.post.call_args
        assert call_args[1]["json"]["topic"] == "news"
        assert result["search_type"] == "news"

    @patch("httpx.AsyncClient")
    async def test_search_http_error(self, mock_client_class: Mock) -> None:
        """Test search with HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 429
        error = httpx.HTTPStatusError("Too many requests", request=Mock(), response=mock_response)
        mock_response.raise_for_status.side_effect = error

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client

        with patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"}):
            result = await search_tavily("test query")

        assert "error" in result
        assert result["error"] == "Search request failed"
        assert result["status_code"] == 429

    @patch("httpx.AsyncClient")
    async def test_search_generic_error(self, mock_client_class: Mock) -> None:
        """Test search with generic error."""
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(side_effect=Exception("Network error"))
        mock_client_class.return_value.__aenter__.return_value = mock_client

        with patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"}):
            result = await search_tavily("test query")

        assert "error" in result
        assert result["error"] == "Search error"
        assert "Network error" in result["message"]

    @patch("httpx.AsyncClient")
    async def test_search_max_results(self, mock_client_class: Mock) -> None:
        """Test search respects max_results parameter."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "answer": "Answer",
            "results": [
                {"title": f"Result {i}", "url": f"https://example.com/{i}"} for i in range(10)
            ],
        }
        mock_response.raise_for_status = Mock()

        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client_class.return_value.__aenter__.return_value = mock_client

        with patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"}):
            result = await search_tavily("test", max_results=3)

        assert len(result["results"]) == 3
        assert result["result_count"] == 10  # Total available


@pytest.mark.asyncio
class TestHealthStatus:
    """Test get_health_status function."""

    async def test_health_status_with_api_key(self) -> None:
        """Test health status when API key is configured."""
        thinking_server.reset()

        with patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"}):
            result = await get_health_status()

        assert result["status"] == "healthy"
        assert result["server"] == "ustad-protocol-mcp"
        assert result["version"] == "1.0.0"
        assert "ustad_think" in result["tools"]
        assert "ustad_search" in result["tools"]
        assert result["thinking_history_length"] == 0
        assert result["tavily_configured"] is True

    async def test_health_status_without_api_key(self) -> None:
        """Test health status when API key is not configured."""
        with patch.dict(os.environ, {}, clear=True):
            result = await get_health_status()

        assert result["status"] == "healthy"
        assert result["tavily_configured"] is False

    async def test_health_status_with_history(self) -> None:
        """Test health status reflects thought history."""
        thinking_server.reset()

        # Add some thoughts
        await process_thought(
            thought="Test 1",
            thought_number=1,
            total_thoughts=2,
            next_thought_needed=True,
        )
        await process_thought(
            thought="Test 2",
            thought_number=2,
            total_thoughts=2,
            next_thought_needed=False,
        )

        result = await get_health_status()
        assert result["thinking_history_length"] == 2


class TestServerConfiguration:
    """Test server configuration and setup."""

    def test_mcp_server_initialization(self) -> None:
        """Test that MCP server is properly initialized."""
        assert mcp is not None
        assert mcp.name == "ustad-protocol-mcp"

    def test_thinking_server_singleton(self) -> None:
        """Test that thinking server is a singleton."""
        from src.sequential_thinking import SequentialThinkingServer

        assert thinking_server is not None
        assert isinstance(thinking_server, SequentialThinkingServer)

    @patch.dict(os.environ, {"DOCKER_CONTAINER": "true", "PORT": "9000"})
    def test_container_detection(self) -> None:
        """Test container environment detection."""
        is_container = os.path.exists("/.dockerenv") or os.getenv("DOCKER_CONTAINER") == "true"
        assert is_container is True

        port = int(os.getenv("PORT", "8000"))
        assert port == 9000

    @patch.dict(os.environ, {}, clear=True)
    def test_default_host_selection(self) -> None:
        """Test default host selection based on environment."""
        is_container = os.path.exists("/.dockerenv") or os.getenv("DOCKER_CONTAINER") == "true"
        default_host = "0.0.0.0" if is_container else "127.0.0.1"
        host = os.getenv("HOST", default_host)

        # In non-container environment, should use localhost
        assert host == "127.0.0.1"


class TestIntegration:
    """Integration tests for the complete flow."""

    @pytest.mark.asyncio
    async def test_complete_thinking_flow(self) -> None:
        """Test a complete thinking and search flow."""
        thinking_server.reset()

        # Start with a thought
        result1 = await process_thought(
            thought="I need to search for information",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True,
        )
        assert result1["thoughtHistoryLength"] == 1

        # Search (mocked)
        with patch.dict(os.environ, {"TAVILY_API_KEY": "test-key"}):
            with patch("httpx.AsyncClient") as mock_client_class:
                mock_response = Mock()
                mock_response.json.return_value = {
                    "answer": "Found information",
                    "results": [{"title": "Info", "url": "http://example.com"}],
                }
                mock_response.raise_for_status = Mock()

                mock_client = AsyncMock()
                mock_client.post = AsyncMock(return_value=mock_response)
                mock_client_class.return_value.__aenter__.return_value = mock_client

                search_result = await search_tavily("test query")
                assert search_result["answer"] == "Found information"

        # Continue thinking
        result2 = await process_thought(
            thought="Based on search results, I conclude",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=True,
        )
        assert result2["thoughtHistoryLength"] == 2

        # Final thought
        result3 = await process_thought(
            thought="Final conclusion",
            thought_number=3,
            total_thoughts=3,
            next_thought_needed=False,
        )
        assert result3["thoughtHistoryLength"] == 3
        assert thinking_server.is_complete() is True

        # Check health
        health = await get_health_status()
        assert health["thinking_history_length"] == 3
