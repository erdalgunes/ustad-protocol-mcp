"""
Test suite for sequential thinking implementation.
Following TDD principles - write tests first.
"""

import pytest
from typing import Dict, List, Optional


class TestSequentialThinking:
    """Test sequential thinking functionality"""
    
    def test_create_thought(self):
        """Test creating a basic thought"""
        from src.sequential_thinking import SequentialThinkingServer
        
        server = SequentialThinkingServer()
        
        thought_data = {
            "thought": "Analyzing the problem step by step",
            "thoughtNumber": 1,
            "totalThoughts": 5,
            "nextThoughtNeeded": True
        }
        
        result = server.process_thought(thought_data)
        
        assert result is not None
        assert "thoughtNumber" in result
        assert result["thoughtNumber"] == 1
        assert result["totalThoughts"] == 5
        assert result["nextThoughtNeeded"] == True
        
    def test_thought_history(self):
        """Test that thoughts are stored in history"""
        from src.sequential_thinking import SequentialThinkingServer
        
        server = SequentialThinkingServer()
        
        # Add first thought
        thought1 = {
            "thought": "First step of analysis",
            "thoughtNumber": 1,
            "totalThoughts": 3,
            "nextThoughtNeeded": True
        }
        server.process_thought(thought1)
        
        # Add second thought
        thought2 = {
            "thought": "Second step of analysis",
            "thoughtNumber": 2,
            "totalThoughts": 3,
            "nextThoughtNeeded": True
        }
        server.process_thought(thought2)
        
        # Check history
        history = server.get_thought_history()
        assert len(history) == 2
        assert history[0]["thoughtNumber"] == 1
        assert history[1]["thoughtNumber"] == 2
        
    def test_revision_thought(self):
        """Test revising a previous thought"""
        from src.sequential_thinking import SequentialThinkingServer
        
        server = SequentialThinkingServer()
        
        # Add initial thought
        thought1 = {
            "thought": "Initial analysis",
            "thoughtNumber": 1,
            "totalThoughts": 3,
            "nextThoughtNeeded": True
        }
        server.process_thought(thought1)
        
        # Revise the thought
        revision = {
            "thought": "Actually, reconsidering the first step",
            "thoughtNumber": 2,
            "totalThoughts": 3,
            "isRevision": True,
            "revisesThought": 1,
            "nextThoughtNeeded": True
        }
        result = server.process_thought(revision)
        
        assert result["isRevision"] == True
        assert result["revisesThought"] == 1
        
    def test_branching_thoughts(self):
        """Test branching from a thought"""
        from src.sequential_thinking import SequentialThinkingServer
        
        server = SequentialThinkingServer()
        
        # Add initial thoughts
        thought1 = {
            "thought": "Main path analysis",
            "thoughtNumber": 1,
            "totalThoughts": 3,
            "nextThoughtNeeded": True
        }
        server.process_thought(thought1)
        
        # Branch from thought 1
        branch = {
            "thought": "Alternative approach",
            "thoughtNumber": 2,
            "totalThoughts": 4,
            "branchFromThought": 1,
            "branchId": "alt-1",
            "nextThoughtNeeded": True
        }
        result = server.process_thought(branch)
        
        assert result["branchFromThought"] == 1
        assert result["branchId"] == "alt-1"
        
        # Check branches are tracked
        branches = server.get_branches()
        assert "alt-1" in branches
        
    def test_dynamic_total_adjustment(self):
        """Test adjusting total thoughts dynamically"""
        from src.sequential_thinking import SequentialThinkingServer
        
        server = SequentialThinkingServer()
        
        # Start with 3 thoughts
        thought1 = {
            "thought": "Starting analysis",
            "thoughtNumber": 1,
            "totalThoughts": 3,
            "nextThoughtNeeded": True
        }
        server.process_thought(thought1)
        
        # Realize we need more thoughts
        thought2 = {
            "thought": "This is more complex, need more steps",
            "thoughtNumber": 2,
            "totalThoughts": 6,  # Increased from 3
            "needsMoreThoughts": True,
            "nextThoughtNeeded": True
        }
        result = server.process_thought(thought2)
        
        assert result["totalThoughts"] == 6
        assert result["needsMoreThoughts"] == True
        
    def test_completion_detection(self):
        """Test detecting when thinking is complete"""
        from src.sequential_thinking import SequentialThinkingServer
        
        server = SequentialThinkingServer()
        
        # Add thoughts
        for i in range(1, 3):
            thought = {
                "thought": f"Step {i} of analysis",
                "thoughtNumber": i,
                "totalThoughts": 3,
                "nextThoughtNeeded": True
            }
            server.process_thought(thought)
        
        # Final thought
        final_thought = {
            "thought": "Final conclusion reached",
            "thoughtNumber": 3,
            "totalThoughts": 3,
            "nextThoughtNeeded": False  # No more thoughts needed
        }
        result = server.process_thought(final_thought)
        
        assert result["nextThoughtNeeded"] == False
        assert server.is_complete() == True
        
    def test_validation_errors(self):
        """Test validation of invalid thought data"""
        from src.sequential_thinking import SequentialThinkingServer
        
        server = SequentialThinkingServer()
        
        # Missing required fields
        invalid_thought = {
            "thought": "Missing fields"
            # Missing thoughtNumber, totalThoughts, nextThoughtNeeded
        }
        
        with pytest.raises(ValueError, match="Missing required field"):
            server.process_thought(invalid_thought)
        
        # Invalid thought number
        invalid_number = {
            "thought": "Invalid number",
            "thoughtNumber": 0,  # Should be >= 1
            "totalThoughts": 3,
            "nextThoughtNeeded": True
        }
        
        with pytest.raises(ValueError, match="Invalid thought number"):
            server.process_thought(invalid_number)