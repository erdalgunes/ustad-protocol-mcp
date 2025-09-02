"""Tests for Batch of Thought engine."""

import pytest
from typing import List

from bot_mcp.bot_engine import (
    Thought,
    ThoughtBatch,
    BotEngine,
    ThoughtScorer,
)


class TestThought:
    """Test Thought data model."""

    def test_thought_creation(self):
        """Test creating a thought with content and metadata."""
        thought = Thought(
            content="e4 is the best opening move",
            confidence=0.85,
            reasoning="Controls center, develops pieces",
        )
        
        assert thought.content == "e4 is the best opening move"
        assert thought.confidence == 0.85
        assert thought.reasoning == "Controls center, develops pieces"
        assert thought.score is None  # Not scored yet

    def test_thought_with_score(self):
        """Test thought with evaluation score."""
        thought = Thought(
            content="Nf3 development",
            confidence=0.7,
            reasoning="Knights before bishops",
            score=0.65,
        )
        
        assert thought.score == 0.65


class TestThoughtBatch:
    """Test ThoughtBatch for managing multiple thoughts."""

    def test_batch_creation(self):
        """Test creating a batch of thoughts."""
        thoughts = [
            Thought(content=f"Move {i}", confidence=0.5 + i * 0.1)
            for i in range(3)
        ]
        
        batch = ThoughtBatch(thoughts=thoughts, context="Opening position")
        
        assert len(batch.thoughts) == 3
        assert batch.context == "Opening position"
        assert batch.best_thought is None  # Not evaluated yet

    def test_batch_with_best_thought(self):
        """Test batch after evaluation with best thought selected."""
        thoughts = [
            Thought(content="Move A", confidence=0.6, score=0.5),
            Thought(content="Move B", confidence=0.8, score=0.9),
            Thought(content="Move C", confidence=0.7, score=0.7),
        ]
        
        batch = ThoughtBatch(
            thoughts=thoughts,
            context="Midgame",
            best_thought=thoughts[1],  # Move B has highest score
        )
        
        assert batch.best_thought.content == "Move B"
        assert batch.best_thought.score == 0.9


class TestBotEngine:
    """Test the main Batch of Thought engine."""

    def test_engine_initialization(self):
        """Test creating BoT engine with parameters."""
        engine = BotEngine(
            batch_size=10,
            temperature=0.7,
            parallel=True,
        )
        
        assert engine.batch_size == 10
        assert engine.temperature == 0.7
        assert engine.parallel is True

    def test_generate_thoughts_basic(self):
        """Test generating a batch of thoughts."""
        engine = BotEngine(batch_size=5)
        
        batch = engine.generate_thoughts(
            prompt="What is the best chess opening?",
            context="Starting position",
        )
        
        assert isinstance(batch, ThoughtBatch)
        assert len(batch.thoughts) == 5
        assert batch.context == "Starting position"
        assert all(isinstance(t, Thought) for t in batch.thoughts)

    def test_generate_thoughts_with_diversity(self):
        """Test that generated thoughts are diverse."""
        engine = BotEngine(batch_size=10, temperature=0.9)
        
        batch = engine.generate_thoughts(
            prompt="Analyze position after 1.e4",
            context="After 1.e4",
        )
        
        # Check thoughts are unique
        contents = [t.content for t in batch.thoughts]
        assert len(contents) == len(set(contents)), "Thoughts should be diverse"
        
        # Check confidence varies
        confidences = [t.confidence for t in batch.thoughts]
        assert len(set(confidences)) > 1, "Confidence levels should vary"

    @pytest.mark.asyncio
    async def test_generate_thoughts_async(self):
        """Test async thought generation for parallel processing."""
        engine = BotEngine(batch_size=8, parallel=True)
        
        batch = await engine.generate_thoughts_async(
            prompt="Best response to 1.d4",
            context="Queen's pawn opening",
        )
        
        assert len(batch.thoughts) == 8
        assert batch.context == "Queen's pawn opening"


class TestThoughtScorer:
    """Test thought scoring and evaluation."""

    def test_scorer_initialization(self):
        """Test creating a thought scorer with criteria."""
        scorer = ThoughtScorer(
            criteria={
                "relevance": 0.4,
                "depth": 0.3,
                "creativity": 0.3,
            }
        )
        
        assert scorer.criteria["relevance"] == 0.4
        assert sum(scorer.criteria.values()) == 1.0

    def test_score_thought(self):
        """Test scoring individual thought."""
        scorer = ThoughtScorer()
        thought = Thought(
            content="Sacrifice bishop for attack",
            confidence=0.75,
            reasoning="Opens king position",
        )
        
        score = scorer.score_thought(thought, context="Attacking position")
        
        assert 0 <= score <= 1
        thought.score = score
        assert thought.score is not None

    def test_score_batch(self):
        """Test scoring entire batch and selecting best."""
        scorer = ThoughtScorer()
        thoughts = [
            Thought(content=f"Strategy {i}", confidence=0.5 + i * 0.15)
            for i in range(4)
        ]
        batch = ThoughtBatch(thoughts=thoughts, context="Endgame")
        
        scored_batch = scorer.score_batch(batch)
        
        assert all(t.score is not None for t in scored_batch.thoughts)
        assert scored_batch.best_thought is not None
        assert scored_batch.best_thought.score == max(
            t.score for t in scored_batch.thoughts
        )

    def test_custom_scoring_function(self):
        """Test using custom scoring function."""
        def chess_scorer(thought: Thought, context: str) -> float:
            # Favor aggressive moves
            if "attack" in thought.content.lower():
                return 0.9
            elif "defend" in thought.content.lower():
                return 0.6
            return 0.5
        
        scorer = ThoughtScorer(scoring_fn=chess_scorer)
        
        aggressive = Thought(content="Attack the king")
        defensive = Thought(content="Defend the position")
        
        assert scorer.score_thought(aggressive, "") > scorer.score_thought(defensive, "")