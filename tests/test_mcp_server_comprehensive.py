"""
Comprehensive MCP server test following best practices.
Tests actual behavior, error handling, and agent-friendly responses.
"""

from typing import Any

import pytest
from fastmcp import FastMCP

from src.sequential_thinking import SequentialThinkingServer


class TestMCPServerComprehensive:
    """Comprehensive tests for MCP server functionality"""

    @pytest.fixture
    async def mcp_app(self):
        """Create a test MCP application"""
        mcp = FastMCP("test-sequential-thinking")
        server = SequentialThinkingServer()

        @mcp.tool()
        async def sequentialthinking(
            thought: str,
            nextThoughtNeeded: bool,
            thoughtNumber: int,
            totalThoughts: int,
            isRevision: bool = False,
            revisesThought: int = None,
            branchFromThought: int = None,
            branchId: str = None,
            needsMoreThoughts: bool = False,
        ) -> dict[str, Any]:
            """Sequential thinking tool for structured problem-solving"""
            try:
                result = server.process_thought(
                    {
                        "thought": thought,
                        "thoughtNumber": thoughtNumber,
                        "totalThoughts": totalThoughts,
                        "nextThoughtNeeded": nextThoughtNeeded,
                        "isRevision": isRevision,
                        "revisesThought": revisesThought,
                        "branchFromThought": branchFromThought,
                        "branchId": branchId,
                        "needsMoreThoughts": needsMoreThoughts,
                    }
                )

                # Add helpful context for the agent
                result["branches"] = list(server.get_branches().keys())
                result["thoughtHistoryLength"] = len(server.get_thought_history())

                return result

            except ValueError as e:
                # Return agent-friendly error messages
                error_msg = str(e)
                if "empty" in error_msg:
                    return {
                        "error": "Thought cannot be empty. Please provide a meaningful thought.",
                        "suggestion": "Include your reasoning or analysis as the thought content.",
                    }
                if "Invalid thought number" in error_msg:
                    return {
                        "error": f"Invalid thought number. Must be >= 1, got {thoughtNumber}",
                        "suggestion": "Start with thoughtNumber: 1 for the first thought.",
                    }
                if "non-existent thought" in error_msg:
                    return {
                        "error": error_msg,
                        "suggestion": f"Available thoughts to revise: {[t['thoughtNumber'] for t in server.get_thought_history()]}",
                    }
                return {"error": error_msg}

        return mcp

    @pytest.mark.asyncio
    async def test_happy_path_sequential_reasoning(self, mcp_app):
        """Test basic sequential thinking flow"""
        # Simulate agent using the tool for problem-solving
        tools = mcp_app.get_tools()
        think_tool = next(t for t in tools if t.name == "sequentialthinking")

        # Step 1: Initial thought
        result1 = await think_tool.function(
            thought="Breaking down the problem into steps",
            thoughtNumber=1,
            totalThoughts=3,
            nextThoughtNeeded=True,
        )

        assert result1["thoughtNumber"] == 1
        assert result1["nextThoughtNeeded"] == True
        assert result1["thoughtHistoryLength"] == 1

        # Step 2: Continue reasoning
        result2 = await think_tool.function(
            thought="Analyzing the first component",
            thoughtNumber=2,
            totalThoughts=3,
            nextThoughtNeeded=True,
        )

        assert result2["thoughtNumber"] == 2
        assert result2["thoughtHistoryLength"] == 2

        # Step 3: Final conclusion
        result3 = await think_tool.function(
            thought="Synthesizing the solution",
            thoughtNumber=3,
            totalThoughts=3,
            nextThoughtNeeded=False,
        )

        assert result3["nextThoughtNeeded"] == False
        assert result3["thoughtHistoryLength"] == 3

    @pytest.mark.asyncio
    async def test_error_handling_with_helpful_messages(self, mcp_app):
        """Test that errors provide actionable guidance for agents"""
        tools = mcp_app.get_tools()
        think_tool = next(t for t in tools if t.name == "sequentialthinking")

        # Test empty thought
        result = await think_tool.function(
            thought="", thoughtNumber=1, totalThoughts=1, nextThoughtNeeded=False
        )

        assert "error" in result
        assert "suggestion" in result
        assert "meaningful thought" in result["suggestion"]

        # Test invalid thought number
        result = await think_tool.function(
            thought="Valid thought", thoughtNumber=0, totalThoughts=1, nextThoughtNeeded=False
        )

        assert "error" in result
        assert "suggestion" in result
        assert "Start with thoughtNumber: 1" in result["suggestion"]

    @pytest.mark.asyncio
    async def test_revision_workflow(self, mcp_app):
        """Test revising previous thoughts"""
        tools = mcp_app.get_tools()
        think_tool = next(t for t in tools if t.name == "sequentialthinking")

        # Add initial thought
        await think_tool.function(
            thought="Initial hypothesis", thoughtNumber=1, totalThoughts=2, nextThoughtNeeded=True
        )

        # Revise it
        result = await think_tool.function(
            thought="Actually, reconsidering the hypothesis",
            thoughtNumber=2,
            totalThoughts=2,
            nextThoughtNeeded=False,
            isRevision=True,
            revisesThought=1,
        )

        assert result["isRevision"] == True
        assert result["revisesThought"] == 1

        # Try to revise non-existent thought
        result = await think_tool.function(
            thought="Revising something invalid",
            thoughtNumber=3,
            totalThoughts=3,
            nextThoughtNeeded=False,
            isRevision=True,
            revisesThought=999,
        )

        assert "error" in result
        assert "suggestion" in result
        assert "Available thoughts to revise" in result["suggestion"]

    @pytest.mark.asyncio
    async def test_branching_exploration(self, mcp_app):
        """Test branching for exploring alternatives"""
        tools = mcp_app.get_tools()
        think_tool = next(t for t in tools if t.name == "sequentialthinking")

        # Main path
        await think_tool.function(
            thought="Main approach", thoughtNumber=1, totalThoughts=3, nextThoughtNeeded=True
        )

        # Branch to explore alternative
        result = await think_tool.function(
            thought="Alternative approach worth exploring",
            thoughtNumber=2,
            totalThoughts=3,
            nextThoughtNeeded=True,
            branchFromThought=1,
            branchId="alternative-1",
        )

        assert result["branchId"] == "alternative-1"
        assert "alternative-1" in result["branches"]

        # Continue main path
        result = await think_tool.function(
            thought="Continuing main approach",
            thoughtNumber=3,
            totalThoughts=3,
            nextThoughtNeeded=False,
        )

        assert result["thoughtHistoryLength"] == 3
        assert "alternative-1" in result["branches"]

    @pytest.mark.asyncio
    async def test_dynamic_thought_adjustment(self, mcp_app):
        """Test adjusting total thoughts as complexity emerges"""
        tools = mcp_app.get_tools()
        think_tool = next(t for t in tools if t.name == "sequentialthinking")

        # Start with estimated 2 thoughts
        await think_tool.function(
            thought="Starting analysis", thoughtNumber=1, totalThoughts=2, nextThoughtNeeded=True
        )

        # Realize we need more thoughts
        result = await think_tool.function(
            thought="This is more complex than expected",
            thoughtNumber=2,
            totalThoughts=5,  # Increased
            nextThoughtNeeded=True,
            needsMoreThoughts=True,
        )

        assert result["totalThoughts"] == 5
        assert result["needsMoreThoughts"] == True

    @pytest.mark.asyncio
    async def test_tool_description_clarity(self, mcp_app):
        """Test that tool description is clear for agents"""
        tools = mcp_app.get_tools()
        think_tool = next(t for t in tools if t.name == "sequentialthinking")

        # Check tool has clear description
        assert think_tool.description
        assert "problem-solving" in think_tool.description.lower()

        # Check parameters are documented
        params = think_tool.inputSchema.get("properties", {})
        assert "thought" in params
        assert "thoughtNumber" in params
        assert "nextThoughtNeeded" in params
