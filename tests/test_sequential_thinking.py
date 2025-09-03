"""Comprehensive tests for sequential thinking module."""

import pytest
from src.sequential_thinking import SequentialThinkingServer, ThoughtData


class TestThoughtData:
    """Test ThoughtData dataclass."""

    def test_thought_data_creation(self) -> None:
        """Test creating a basic ThoughtData instance."""
        thought = ThoughtData(
            thought="Test thought",
            thought_number=1,
            total_thoughts=5,
            next_thought_needed=True,
        )
        assert thought.thought == "Test thought"
        assert thought.thought_number == 1
        assert thought.total_thoughts == 5
        assert thought.next_thought_needed is True
        assert thought.is_revision is False
        assert thought.revises_thought is None
        assert thought.branch_from_thought is None
        assert thought.branch_id is None
        assert thought.needs_more_thoughts is False

    def test_thought_data_with_revision(self) -> None:
        """Test creating a ThoughtData instance with revision."""
        thought = ThoughtData(
            thought="Revised thought",
            thought_number=3,
            total_thoughts=5,
            next_thought_needed=True,
            is_revision=True,
            revises_thought=2,
        )
        assert thought.is_revision is True
        assert thought.revises_thought == 2

    def test_thought_data_with_branch(self) -> None:
        """Test creating a ThoughtData instance with branching."""
        thought = ThoughtData(
            thought="Branched thought",
            thought_number=4,
            total_thoughts=6,
            next_thought_needed=True,
            branch_from_thought=2,
            branch_id="alternative-approach",
        )
        assert thought.branch_from_thought == 2
        assert thought.branch_id == "alternative-approach"


class TestSequentialThinkingServer:
    """Test SequentialThinkingServer class."""

    def test_initialization(self) -> None:
        """Test server initialization."""
        server = SequentialThinkingServer()
        assert server.thought_history == []
        assert server.branches == {}
        assert server._is_complete is False
        assert server.is_complete() is False
        assert server.get_current_thought_number() == 0

    def test_process_basic_thought(self) -> None:
        """Test processing a basic thought."""
        server = SequentialThinkingServer()
        thought_data = {
            "thought": "First thought",
            "thoughtNumber": 1,
            "totalThoughts": 3,
            "nextThoughtNeeded": True,
        }
        result = server.process_thought(thought_data)

        assert result["thought"] == "First thought"
        assert result["thoughtNumber"] == 1
        assert result["totalThoughts"] == 3
        assert result["nextThoughtNeeded"] is True
        assert result["isRevision"] is False
        assert len(server.thought_history) == 1
        assert server.get_current_thought_number() == 1

    def test_process_multiple_thoughts(self) -> None:
        """Test processing multiple sequential thoughts."""
        server = SequentialThinkingServer()
        
        for i in range(1, 4):
            thought_data = {
                "thought": f"Thought {i}",
                "thoughtNumber": i,
                "totalThoughts": 3,
                "nextThoughtNeeded": i < 3,
            }
            server.process_thought(thought_data)

        assert len(server.thought_history) == 3
        assert server.is_complete() is True
        assert server.get_current_thought_number() == 3

    def test_process_thought_with_revision(self) -> None:
        """Test processing a thought that revises a previous thought."""
        server = SequentialThinkingServer()
        
        # Add initial thoughts
        server.process_thought({
            "thought": "Initial thought",
            "thoughtNumber": 1,
            "totalThoughts": 3,
            "nextThoughtNeeded": True,
        })
        
        server.process_thought({
            "thought": "Second thought",
            "thoughtNumber": 2,
            "totalThoughts": 3,
            "nextThoughtNeeded": True,
        })

        # Add revision
        result = server.process_thought({
            "thought": "Revised first thought",
            "thoughtNumber": 3,
            "totalThoughts": 4,
            "nextThoughtNeeded": True,
            "isRevision": True,
            "revisesThought": 1,
        })

        assert result["isRevision"] is True
        assert result["revisesThought"] == 1
        assert len(server.thought_history) == 3

    def test_process_thought_with_branching(self) -> None:
        """Test processing thoughts with branching."""
        server = SequentialThinkingServer()
        
        # Main branch
        server.process_thought({
            "thought": "Main thought 1",
            "thoughtNumber": 1,
            "totalThoughts": 3,
            "nextThoughtNeeded": True,
        })
        
        # Branch from thought 1
        server.process_thought({
            "thought": "Branch A thought",
            "thoughtNumber": 2,
            "totalThoughts": 4,
            "nextThoughtNeeded": True,
            "branchFromThought": 1,
            "branchId": "branch-a",
        })

        branches = server.get_branches()
        assert "branch-a" in branches
        assert len(branches["branch-a"]) == 1
        assert branches["branch-a"][0]["thought"] == "Branch A thought"

    def test_validation_missing_required_field(self) -> None:
        """Test validation for missing required fields."""
        server = SequentialThinkingServer()
        
        with pytest.raises(ValueError, match="Missing required field: thought"):
            server.process_thought({
                "thoughtNumber": 1,
                "totalThoughts": 3,
                "nextThoughtNeeded": True,
            })

    def test_validation_empty_thought(self) -> None:
        """Test validation for empty thought content."""
        server = SequentialThinkingServer()
        
        with pytest.raises(ValueError, match="Thought cannot be empty"):
            server.process_thought({
                "thought": "",
                "thoughtNumber": 1,
                "totalThoughts": 3,
                "nextThoughtNeeded": True,
            })

        with pytest.raises(ValueError, match="Thought cannot be empty"):
            server.process_thought({
                "thought": "   ",
                "thoughtNumber": 1,
                "totalThoughts": 3,
                "nextThoughtNeeded": True,
            })

    def test_validation_invalid_thought_number(self) -> None:
        """Test validation for invalid thought number."""
        server = SequentialThinkingServer()
        
        with pytest.raises(ValueError, match="Invalid thought number: 0"):
            server.process_thought({
                "thought": "Test",
                "thoughtNumber": 0,
                "totalThoughts": 3,
                "nextThoughtNeeded": True,
            })

        with pytest.raises(ValueError, match="Invalid thought number: -1"):
            server.process_thought({
                "thought": "Test",
                "thoughtNumber": -1,
                "totalThoughts": 3,
                "nextThoughtNeeded": True,
            })

    def test_validation_invalid_revision_target(self) -> None:
        """Test validation for revising non-existent thought."""
        server = SequentialThinkingServer()
        
        server.process_thought({
            "thought": "First thought",
            "thoughtNumber": 1,
            "totalThoughts": 3,
            "nextThoughtNeeded": True,
        })

        with pytest.raises(ValueError, match="Cannot revise non-existent thought 5"):
            server.process_thought({
                "thought": "Revision",
                "thoughtNumber": 2,
                "totalThoughts": 3,
                "nextThoughtNeeded": True,
                "isRevision": True,
                "revisesThought": 5,
            })

    def test_get_thought_history(self) -> None:
        """Test getting thought history."""
        server = SequentialThinkingServer()
        
        server.process_thought({
            "thought": "First",
            "thoughtNumber": 1,
            "totalThoughts": 2,
            "nextThoughtNeeded": True,
        })
        
        server.process_thought({
            "thought": "Second",
            "thoughtNumber": 2,
            "totalThoughts": 2,
            "nextThoughtNeeded": False,
        })

        history = server.get_thought_history()
        assert len(history) == 2
        assert history[0]["thought"] == "First"
        assert history[1]["thought"] == "Second"
        assert all(isinstance(item, dict) for item in history)

    def test_get_summary(self) -> None:
        """Test getting thinking process summary."""
        server = SequentialThinkingServer()
        
        # Empty summary
        summary = server.get_summary()
        assert summary["total_thoughts"] == 0
        assert summary["branches_created"] == 0
        assert summary["revisions_made"] == 0
        assert summary["is_complete"] is False

        # Add thoughts with revision and branch
        server.process_thought({
            "thought": "Initial",
            "thoughtNumber": 1,
            "totalThoughts": 3,
            "nextThoughtNeeded": True,
        })
        
        server.process_thought({
            "thought": "Revised",
            "thoughtNumber": 2,
            "totalThoughts": 3,
            "nextThoughtNeeded": True,
            "isRevision": True,
            "revisesThought": 1,
        })
        
        server.process_thought({
            "thought": "Branched",
            "thoughtNumber": 3,
            "totalThoughts": 3,
            "nextThoughtNeeded": False,
            "branchId": "alt",
        })

        summary = server.get_summary()
        assert summary["total_thoughts"] == 3
        assert summary["branches_created"] == 1
        assert summary["revisions_made"] == 1
        assert summary["is_complete"] is True
        assert summary["final_thought"] == "Branched"

    def test_reset(self) -> None:
        """Test resetting the server state."""
        server = SequentialThinkingServer()
        
        # Add some thoughts
        server.process_thought({
            "thought": "Test",
            "thoughtNumber": 1,
            "totalThoughts": 1,
            "nextThoughtNeeded": False,
        })

        assert len(server.thought_history) == 1
        assert server.is_complete() is True

        # Reset
        server.reset()
        
        assert len(server.thought_history) == 0
        assert server.is_complete() is False
        assert server.get_current_thought_number() == 0
        assert server.branches == {}

    def test_needs_more_thoughts(self) -> None:
        """Test handling needs_more_thoughts flag."""
        server = SequentialThinkingServer()
        
        result = server.process_thought({
            "thought": "Complex problem",
            "thoughtNumber": 3,
            "totalThoughts": 3,
            "nextThoughtNeeded": True,
            "needsMoreThoughts": True,
        })

        assert result["needsMoreThoughts"] is True
        assert result["nextThoughtNeeded"] is True

    def test_complete_thinking_flow(self) -> None:
        """Test a complete thinking flow with revision and branching."""
        server = SequentialThinkingServer()
        
        # Start thinking
        server.process_thought({
            "thought": "Analyze the problem",
            "thoughtNumber": 1,
            "totalThoughts": 5,
            "nextThoughtNeeded": True,
        })
        
        # Continue
        server.process_thought({
            "thought": "Consider approach A",
            "thoughtNumber": 2,
            "totalThoughts": 5,
            "nextThoughtNeeded": True,
        })
        
        # Branch to explore alternative
        server.process_thought({
            "thought": "Explore approach B",
            "thoughtNumber": 3,
            "totalThoughts": 6,
            "nextThoughtNeeded": True,
            "branchFromThought": 2,
            "branchId": "approach-b",
        })
        
        # Revise initial analysis
        server.process_thought({
            "thought": "Refined problem analysis",
            "thoughtNumber": 4,
            "totalThoughts": 6,
            "nextThoughtNeeded": True,
            "isRevision": True,
            "revisesThought": 1,
        })
        
        # Need more thoughts than expected
        server.process_thought({
            "thought": "Additional consideration",
            "thoughtNumber": 5,
            "totalThoughts": 6,
            "nextThoughtNeeded": True,
            "needsMoreThoughts": True,
        })
        
        # Final conclusion
        server.process_thought({
            "thought": "Final solution",
            "thoughtNumber": 6,
            "totalThoughts": 7,
            "nextThoughtNeeded": False,
        })

        # Verify final state
        assert server.is_complete() is True
        assert len(server.thought_history) == 6
        assert server.get_current_thought_number() == 6
        
        summary = server.get_summary()
        assert summary["total_thoughts"] == 6
        assert summary["branches_created"] == 1
        assert summary["revisions_made"] == 1
        assert summary["final_thought"] == "Final solution"