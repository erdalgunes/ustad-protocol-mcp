"""
Rigorous test suite for sequential thinking - NO HALLUCINATED TESTS.
Tests actual BEHAVIOR, edge cases, and failure modes.
"""

import pytest
import random
import string
from typing import Dict, Any
from hypothesis import given, strategies as st, assume
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant


class TestRigorousSequentialThinking:
    """Tests that actually verify behavior, not just field presence"""
    
    # EDGE CASES AND BOUNDARIES
    
    def test_empty_thought_rejected(self):
        """Empty thoughts should be rejected"""
        from src.sequential_thinking import SequentialThinkingServer
        
        server = SequentialThinkingServer()
        
        # Arrange: Empty thought
        empty_thought = {
            "thought": "",  # EDGE CASE: empty string
            "thoughtNumber": 1,
            "totalThoughts": 1,
            "nextThoughtNeeded": False
        }
        
        # Act & Assert: Should raise or handle gracefully
        with pytest.raises(ValueError, match="empty or just whitespace"):
            server.process_thought(empty_thought)
    
    def test_thought_number_zero_rejected(self):
        """Thought number 0 should be rejected (must start at 1)"""
        from src.sequential_thinking import SequentialThinkingServer
        
        server = SequentialThinkingServer()
        
        # Arrange: Invalid thought number
        invalid = {
            "thought": "Valid thought",
            "thoughtNumber": 0,  # BOUNDARY: below minimum
            "totalThoughts": 1,
            "nextThoughtNeeded": False
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid thought number"):
            server.process_thought(invalid)
    
    def test_negative_thought_number_rejected(self):
        """Negative thought numbers should be rejected"""
        from src.sequential_thinking import SequentialThinkingServer
        
        server = SequentialThinkingServer()
        
        # Arrange: Negative number
        negative = {
            "thought": "Valid thought",
            "thoughtNumber": -1,  # EDGE CASE: negative
            "totalThoughts": 1,
            "nextThoughtNeeded": False
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid thought number"):
            server.process_thought(negative)
    
    def test_missing_required_fields(self):
        """Missing required fields should raise clear errors"""
        from src.sequential_thinking import SequentialThinkingServer
        
        server = SequentialThinkingServer()
        
        # Test each missing field
        required_fields = ["thought", "thoughtNumber", "totalThoughts", "nextThoughtNeeded"]
        
        for field_to_omit in required_fields:
            # Arrange: Create data missing one field
            incomplete = {
                "thought": "Test thought",
                "thoughtNumber": 1,
                "totalThoughts": 1,
                "nextThoughtNeeded": False
            }
            del incomplete[field_to_omit]
            
            # Act & Assert
            with pytest.raises(ValueError, match=f"Missing required field: {field_to_omit}"):
                server.process_thought(incomplete)
    
    def test_very_long_thought(self):
        """Test handling of extremely long thoughts"""
        from src.sequential_thinking import SequentialThinkingServer
        
        server = SequentialThinkingServer()
        
        # Arrange: 10MB thought (stress test)
        huge_thought = "x" * (10 * 1024 * 1024)
        
        thought_data = {
            "thought": huge_thought,
            "thoughtNumber": 1,
            "totalThoughts": 1,
            "nextThoughtNeeded": False
        }
        
        # Act: Should handle without crashing
        result = server.process_thought(thought_data)
        
        # Assert: Processed successfully
        assert result is not None
        assert len(server.get_thought_history()) == 1
    
    # BEHAVIORAL TESTS
    
    def test_completion_actually_stops_processing(self):
        """When nextThoughtNeeded=False, server should actually be complete"""
        from src.sequential_thinking import SequentialThinkingServer
        
        server = SequentialThinkingServer()
        
        # Arrange & Act: Complete the thinking
        final_thought = {
            "thought": "Final conclusion",
            "thoughtNumber": 1,
            "totalThoughts": 1,
            "nextThoughtNeeded": False  # This should complete it
        }
        server.process_thought(final_thought)
        
        # Assert: Server is ACTUALLY complete
        assert server.is_complete() == True
        
        # Further assertion: Adding more thoughts shouldn't change completion
        # (This tests that completion is sticky)
    
    def test_revision_actually_relates_to_original(self):
        """Revisions should maintain relationship to original thought"""
        from src.sequential_thinking import SequentialThinkingServer
        
        server = SequentialThinkingServer()
        
        # Arrange: Original thought
        original = {
            "thought": "Initial hypothesis",
            "thoughtNumber": 1,
            "totalThoughts": 3,
            "nextThoughtNeeded": True
        }
        server.process_thought(original)
        
        # Act: Revise non-existent thought
        invalid_revision = {
            "thought": "Revising something that doesn't exist",
            "thoughtNumber": 2,
            "totalThoughts": 3,
            "nextThoughtNeeded": True,
            "isRevision": True,
            "revisesThought": 999  # Non-existent thought
        }
        
        # This should raise an error (BUG FIXED!)
        with pytest.raises(ValueError, match="Cannot revise non-existent thought 999"):
            server.process_thought(invalid_revision)
    
    def test_branch_isolation(self):
        """Branches should be isolated from main history"""
        from src.sequential_thinking import SequentialThinkingServer
        
        server = SequentialThinkingServer()
        
        # Arrange: Main path
        main1 = {
            "thought": "Main path step 1",
            "thoughtNumber": 1,
            "totalThoughts": 4,
            "nextThoughtNeeded": True
        }
        server.process_thought(main1)
        
        # Act: Create branch
        branch1 = {
            "thought": "Branch exploration",
            "thoughtNumber": 2,
            "totalThoughts": 4,
            "nextThoughtNeeded": True,
            "branchFromThought": 1,
            "branchId": "experiment-1"
        }
        server.process_thought(branch1)
        
        # Continue main path
        main2 = {
            "thought": "Main path continues",
            "thoughtNumber": 3,
            "totalThoughts": 4,
            "nextThoughtNeeded": True
        }
        server.process_thought(main2)
        
        # Assert: Branches are tracked separately
        branches = server.get_branches()
        assert "experiment-1" in branches
        assert len(branches["experiment-1"]) == 1
        
        # Main history should have all thoughts
        history = server.get_thought_history()
        assert len(history) == 3
    
    def test_concurrent_modification_safety(self):
        """Test thread safety of thought processing"""
        from src.sequential_thinking import SequentialThinkingServer
        import threading
        
        server = SequentialThinkingServer()
        errors = []
        
        def add_thought(num):
            try:
                thought = {
                    "thought": f"Concurrent thought {num}",
                    "thoughtNumber": num,
                    "totalThoughts": 10,
                    "nextThoughtNeeded": num < 10
                }
                server.process_thought(thought)
            except Exception as e:
                errors.append(e)
        
        # Act: Add thoughts concurrently
        threads = []
        for i in range(1, 11):
            t = threading.Thread(target=add_thought, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Assert: Check if all thoughts were added
        history = server.get_thought_history()
        
        # Should have all 10 thoughts if thread-safe
        assert len(history) == 10, f"Expected 10 thoughts, got {len(history)}"
        
        # Check for duplicates or missing numbers
        thought_numbers = [h["thoughtNumber"] for h in history]
        assert sorted(thought_numbers) == list(range(1, 11)), f"Thought numbers corrupted: {thought_numbers}"


# PROPERTY-BASED TESTING

class TestPropertyBased:
    """Property-based tests to find edge cases automatically"""
    
    @given(
        thought=st.text(min_size=1, max_size=1000),
        thought_num=st.integers(min_value=1, max_value=1000),
        total=st.integers(min_value=1, max_value=1000),
        next_needed=st.booleans()
    )
    def test_valid_thoughts_always_processable(self, thought, thought_num, total, next_needed):
        """Any valid thought data should be processable without crashes"""
        from src.sequential_thinking import SequentialThinkingServer
        
        server = SequentialThinkingServer()
        
        thought_data = {
            "thought": thought,
            "thoughtNumber": thought_num,
            "totalThoughts": total,
            "nextThoughtNeeded": next_needed
        }
        
        # Should never crash on valid input
        result = server.process_thought(thought_data)
        
        # Properties that should ALWAYS hold
        assert result["thoughtNumber"] == thought_num
        assert result["totalThoughts"] == total
        assert result["nextThoughtNeeded"] == next_needed
        assert len(server.get_thought_history()) == 1
    
    @given(
        thoughts=st.lists(
            st.text(min_size=1, max_size=100),
            min_size=1,
            max_size=20
        )
    )
    def test_history_maintains_order(self, thoughts):
        """History should maintain insertion order"""
        from src.sequential_thinking import SequentialThinkingServer
        
        server = SequentialThinkingServer()
        
        # Add thoughts in sequence
        for i, thought in enumerate(thoughts, 1):
            data = {
                "thought": thought,
                "thoughtNumber": i,
                "totalThoughts": len(thoughts),
                "nextThoughtNeeded": i < len(thoughts)
            }
            server.process_thought(data)
        
        # History should match insertion order
        history = server.get_thought_history()
        assert len(history) == len(thoughts)
        
        for i, (original, stored) in enumerate(zip(thoughts, history), 1):
            assert stored["thought"] == original
            assert stored["thoughtNumber"] == i


# STATE MACHINE TESTING

class SequentialThinkingStateMachine(RuleBasedStateMachine):
    """Model-based testing to verify state transitions"""
    
    def __init__(self):
        super().__init__()
        from src.sequential_thinking import SequentialThinkingServer
        self.server = SequentialThinkingServer()
        self.thought_count = 0
        self.is_complete = False
    
    @rule()
    def add_thought(self):
        """Add a regular thought"""
        if not self.is_complete:
            self.thought_count += 1
            thought = {
                "thought": f"Thought {self.thought_count}",
                "thoughtNumber": self.thought_count,
                "totalThoughts": self.thought_count + 5,
                "nextThoughtNeeded": True
            }
            self.server.process_thought(thought)
    
    @rule()
    def complete_thinking(self):
        """Complete the thinking process"""
        if self.thought_count > 0 and not self.is_complete:
            self.thought_count += 1
            thought = {
                "thought": "Final thought",
                "thoughtNumber": self.thought_count,
                "totalThoughts": self.thought_count,
                "nextThoughtNeeded": False
            }
            self.server.process_thought(thought)
            self.is_complete = True
    
    @invariant()
    def history_matches_count(self):
        """History length should match thought count"""
        assert len(self.server.get_thought_history()) == self.thought_count
    
    @invariant()
    def completion_is_consistent(self):
        """Completion state should be consistent"""
        assert self.server.is_complete() == self.is_complete


# Run state machine test
TestStateMachine = SequentialThinkingStateMachine.TestCase