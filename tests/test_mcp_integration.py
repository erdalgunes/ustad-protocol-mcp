"""
Integration tests for Sequential Thinking MCP Server.
Tests the full MCP server integration with the sequential thinking implementation.
"""

import pytest
import json
from unittest.mock import Mock, patch
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestMCPIntegration:
    """Test MCP server integration"""
    
    @pytest.mark.asyncio
    async def test_sequential_thinking_tool(self):
        """Test the main sequential_thinking tool"""
        # Import here to avoid import errors
        from sequential_thinking_mcp_server import sequential_thinking
        
        # Test basic thought processing
        result = await sequential_thinking(
            thought="Analyzing the problem",
            thought_number=1,
            total_thoughts=5,
            next_thought_needed=True
        )
        
        response = json.loads(result)
        assert "processed_thought" in response
        assert response["processed_thought"]["thoughtNumber"] == 1
        assert response["thought_history_length"] == 1
        assert response["is_complete"] == False
        
    @pytest.mark.asyncio
    async def test_thought_with_revision(self):
        """Test processing a revision thought"""
        from sequential_thinking_mcp_server import sequential_thinking, reset_thinking_session
        
        # Reset to ensure clean state
        await reset_thinking_session()
        
        # Add initial thought
        await sequential_thinking(
            thought="Initial analysis",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True
        )
        
        # Add revision
        result = await sequential_thinking(
            thought="Reconsidering initial analysis",
            thought_number=2,
            total_thoughts=3,
            next_thought_needed=True,
            is_revision=True,
            revises_thought=1
        )
        
        response = json.loads(result)
        assert response["processed_thought"]["isRevision"] == True
        assert response["processed_thought"]["revisesThought"] == 1
        assert response["thought_history_length"] == 2
        
    @pytest.mark.asyncio
    async def test_branching_functionality(self):
        """Test branching in thought process"""
        from sequential_thinking_mcp_server import sequential_thinking
        
        # Reset first
        from sequential_thinking_mcp_server import reset_thinking_session
        await reset_thinking_session()
        
        # Add initial thought
        await sequential_thinking(
            thought="Main path",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True
        )
        
        # Create branch
        result = await sequential_thinking(
            thought="Alternative approach",
            thought_number=2,
            total_thoughts=4,
            next_thought_needed=True,
            branch_from_thought=1,
            branch_id="alt-1"
        )
        
        response = json.loads(result)
        assert "alt-1" in response["branches"]
        assert response["processed_thought"]["branchId"] == "alt-1"
        
    @pytest.mark.asyncio
    async def test_thinking_summary(self):
        """Test getting thinking summary"""
        from sequential_thinking_mcp_server import sequential_thinking, get_thinking_summary, reset_thinking_session
        
        # Reset and add thoughts
        await reset_thinking_session()
        
        await sequential_thinking(
            thought="Step 1",
            thought_number=1,
            total_thoughts=2,
            next_thought_needed=True
        )
        
        await sequential_thinking(
            thought="Step 2 - Final",
            thought_number=2,
            total_thoughts=2,
            next_thought_needed=False
        )
        
        # Get summary
        result = await get_thinking_summary()
        summary = json.loads(result)
        
        assert summary["total_thoughts"] == 2
        assert summary["is_complete"] == True
        assert summary["last_thought"]["thoughtNumber"] == 2
        
    @pytest.mark.asyncio
    async def test_thought_history(self):
        """Test retrieving thought history"""
        from sequential_thinking_mcp_server import sequential_thinking, get_thought_history, reset_thinking_session
        
        # Reset and add multiple thoughts
        await reset_thinking_session()
        
        thoughts = [
            ("First thought", 1, 3, True),
            ("Second thought", 2, 3, True),
            ("Final thought", 3, 3, False)
        ]
        
        for thought, num, total, next_needed in thoughts:
            await sequential_thinking(
                thought=thought,
                thought_number=num,
                total_thoughts=total,
                next_thought_needed=next_needed
            )
        
        # Get history
        result = await get_thought_history()
        history_data = json.loads(result)
        
        assert history_data["total"] == 3
        assert len(history_data["history"]) == 3
        assert history_data["history"][0]["thought"] == "First thought"
        assert history_data["history"][2]["nextThoughtNeeded"] == False
        
    @pytest.mark.asyncio
    async def test_reset_session(self):
        """Test resetting the thinking session"""
        from sequential_thinking_mcp_server import sequential_thinking, reset_thinking_session, get_thinking_summary
        
        # Add a thought
        await sequential_thinking(
            thought="Some thought",
            thought_number=1,
            total_thoughts=1,
            next_thought_needed=False
        )
        
        # Reset
        reset_result = await reset_thinking_session()
        reset_data = json.loads(reset_result)
        assert reset_data["status"] == "reset"
        
        # Verify reset worked
        summary_result = await get_thinking_summary()
        summary = json.loads(summary_result)
        assert summary["total_thoughts"] == 0
        
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in MCP server"""
        from sequential_thinking_mcp_server import sequential_thinking
        
        # Test with missing required field
        result = await sequential_thinking(
            thought="Incomplete thought",
            thought_number=1,
            total_thoughts=5,
            next_thought_needed=None  # This will cause validation to fail
        )
        
        # Should handle the error gracefully
        response = json.loads(result)
        # The function should still process it (None becomes False in boolean context)
        assert "processed_thought" in response or "error" in response
        
    @pytest.mark.asyncio
    async def test_dynamic_total_adjustment(self):
        """Test adjusting total thoughts dynamically"""
        from sequential_thinking_mcp_server import sequential_thinking, reset_thinking_session
        
        await reset_thinking_session()
        
        # Start with 3 total
        await sequential_thinking(
            thought="Initial estimate",
            thought_number=1,
            total_thoughts=3,
            next_thought_needed=True
        )
        
        # Adjust to 6 total
        result = await sequential_thinking(
            thought="Need more analysis",
            thought_number=2,
            total_thoughts=6,
            next_thought_needed=True,
            needs_more_thoughts=True
        )
        
        response = json.loads(result)
        assert response["processed_thought"]["totalThoughts"] == 6
        assert response["processed_thought"]["needsMoreThoughts"] == True
        
    @pytest.mark.asyncio
    async def test_completion_detection(self):
        """Test that completion is properly detected"""
        from sequential_thinking_mcp_server import sequential_thinking, get_thinking_summary, reset_thinking_session
        
        await reset_thinking_session()
        
        # Add non-final thought
        await sequential_thinking(
            thought="Working on it",
            thought_number=1,
            total_thoughts=2,
            next_thought_needed=True
        )
        
        summary1 = json.loads(await get_thinking_summary())
        assert summary1["is_complete"] == False
        
        # Add final thought
        await sequential_thinking(
            thought="Conclusion reached",
            thought_number=2,
            total_thoughts=2,
            next_thought_needed=False
        )
        
        summary2 = json.loads(await get_thinking_summary())
        assert summary2["is_complete"] == True