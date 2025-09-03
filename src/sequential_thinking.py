"""Sequential Thinking MCP Server - Pythonic implementation
Following YAGNI and SOLID principles
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class ThoughtData:
    """Data class for a single thought in the sequence"""

    thought: str
    thought_number: int
    total_thoughts: int
    next_thought_needed: bool
    is_revision: bool = False
    revises_thought: int | None = None
    branch_from_thought: int | None = None
    branch_id: str | None = None
    needs_more_thoughts: bool = False


class SequentialThinkingServer:
    """Sequential thinking server for structured problem-solving.
    Implements chain-of-thought reasoning with revision and branching capabilities.
    """

    def __init__(self) -> None:
        """Initialize the sequential thinking server"""
        self.thought_history: list[ThoughtData] = []
        self.branches: dict[str, list[ThoughtData]] = {}
        self._is_complete = False

    def process_thought(self, thought_data: dict[str, Any]) -> dict[str, Any]:
        """Process a thought and add it to the history.

        Args:
            thought_data: Dictionary containing thought information

        Returns:
            Processed thought data with validation

        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate required fields
        required_fields = ["thought", "thoughtNumber", "totalThoughts", "nextThoughtNeeded"]
        for field in required_fields:
            if field not in thought_data:
                raise ValueError(f"Missing required field: {field}")

        # Validate thought content (FIX BUG #1: Empty thoughts)
        thought_text = thought_data.get("thought", "")
        if not thought_text or not thought_text.strip():
            raise ValueError("Thought cannot be empty or just whitespace")

        # Validate thought number
        thought_number = thought_data["thoughtNumber"]
        if thought_number < 1:
            raise ValueError(f"Invalid thought number: {thought_number}, must be >= 1")

        # Validate revision target exists (FIX BUG #2: Invalid revisions)
        if thought_data.get("isRevision") and thought_data.get("revisesThought"):
            target = thought_data["revisesThought"]
            if not any(t.thought_number == target for t in self.thought_history):
                raise ValueError(f"Cannot revise non-existent thought {target}")

        # Create ThoughtData object
        thought = ThoughtData(
            thought=thought_data["thought"],
            thought_number=thought_number,
            total_thoughts=thought_data["totalThoughts"],
            next_thought_needed=thought_data["nextThoughtNeeded"],
            is_revision=thought_data.get("isRevision", False),
            revises_thought=thought_data.get("revisesThought"),
            branch_from_thought=thought_data.get("branchFromThought"),
            branch_id=thought_data.get("branchId"),
            needs_more_thoughts=thought_data.get("needsMoreThoughts", False),
        )

        # Add to history
        self.thought_history.append(thought)

        # Handle branching
        if thought.branch_id:
            if thought.branch_id not in self.branches:
                self.branches[thought.branch_id] = []
            self.branches[thought.branch_id].append(thought)

        # Check if complete
        if not thought.next_thought_needed:
            self._is_complete = True

        # Return processed data (using original field names for compatibility)
        return {
            "thought": thought.thought,
            "thoughtNumber": thought.thought_number,
            "totalThoughts": thought.total_thoughts,
            "nextThoughtNeeded": thought.next_thought_needed,
            "isRevision": thought.is_revision,
            "revisesThought": thought.revises_thought,
            "branchFromThought": thought.branch_from_thought,
            "branchId": thought.branch_id,
            "needsMoreThoughts": thought.needs_more_thoughts,
        }

    def get_thought_history(self) -> list[dict[str, Any]]:
        """Get the complete thought history.

        Returns:
            List of thought data dictionaries
        """
        return [
            {
                "thought": t.thought,
                "thoughtNumber": t.thought_number,
                "totalThoughts": t.total_thoughts,
                "nextThoughtNeeded": t.next_thought_needed,
                "isRevision": t.is_revision,
                "revisesThought": t.revises_thought,
                "branchFromThought": t.branch_from_thought,
                "branchId": t.branch_id,
                "needsMoreThoughts": t.needs_more_thoughts,
            }
            for t in self.thought_history
        ]

    def get_branches(self) -> dict[str, list[dict[str, Any]]]:
        """Get all branches in the thinking process.

        Returns:
            Dictionary mapping branch IDs to lists of thoughts
        """
        return {
            branch_id: [
                {
                    "thought": t.thought,
                    "thoughtNumber": t.thought_number,
                    "totalThoughts": t.total_thoughts,
                    "nextThoughtNeeded": t.next_thought_needed,
                }
                for t in thoughts
            ]
            for branch_id, thoughts in self.branches.items()
        }

    def is_complete(self) -> bool:
        """Check if the thinking process is complete.

        Returns:
            True if complete, False otherwise
        """
        return self._is_complete

    def reset(self) -> None:
        """Reset the server to initial state"""
        self.thought_history.clear()
        self.branches.clear()
        self._is_complete = False

    def get_current_thought_number(self) -> int:
        """Get the current thought number.

        Returns:
            Current thought number or 0 if no thoughts yet
        """
        if not self.thought_history:
            return 0
        return self.thought_history[-1].thought_number

    def get_summary(self) -> dict[str, Any]:
        """Get a summary of the thinking process.

        Returns:
            Summary including stats and key insights
        """
        if not self.thought_history:
            return {
                "total_thoughts": 0,
                "branches_created": 0,
                "revisions_made": 0,
                "is_complete": False,
            }

        revisions = sum(1 for t in self.thought_history if t.is_revision)
        branches_created = len(self.branches)

        return {
            "total_thoughts": len(self.thought_history),
            "branches_created": branches_created,
            "revisions_made": revisions,
            "is_complete": self._is_complete,
            "final_thought": self.thought_history[-1].thought if self.thought_history else None,
        }
