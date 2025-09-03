"""Batch of Thought engine for parallel thought generation and evaluation."""

import asyncio
import random
from collections.abc import Callable
from dataclasses import dataclass


@dataclass
class Thought:
    """Single thought in a batch."""

    content: str
    confidence: float = 0.5
    reasoning: str = ""
    score: float | None = None


@dataclass
class ThoughtBatch:
    """Collection of thoughts generated for a prompt."""

    thoughts: list[Thought]
    context: str
    best_thought: Thought | None = None


class BotEngine:
    """Main engine for Batch of Thought generation."""

    def __init__(
        self,
        batch_size: int = 10,
        temperature: float = 0.7,
        parallel: bool = True,
    ):
        """Initialize BoT engine.

        Args:
            batch_size: Number of thoughts to generate per batch
            temperature: Diversity of thought generation (0-1)
            parallel: Whether to generate thoughts in parallel
        """
        self.batch_size = batch_size
        self.temperature = temperature
        self.parallel = parallel

    def generate_thoughts(
        self,
        prompt: str,
        context: str = "",
    ) -> ThoughtBatch:
        """Generate batch of diverse thoughts.

        Args:
            prompt: Input prompt for thought generation
            context: Additional context for generation

        Returns:
            ThoughtBatch with generated thoughts
        """
        thoughts = []

        for i in range(self.batch_size):
            # Simulate diverse thought generation
            thought = self._generate_single_thought(prompt, context, i)
            thoughts.append(thought)

        return ThoughtBatch(thoughts=thoughts, context=context)

    async def generate_thoughts_async(
        self,
        prompt: str,
        context: str = "",
    ) -> ThoughtBatch:
        """Generate thoughts asynchronously for parallel processing.

        Args:
            prompt: Input prompt for thought generation
            context: Additional context for generation

        Returns:
            ThoughtBatch with generated thoughts
        """
        tasks = [
            self._generate_single_thought_async(prompt, context, i) for i in range(self.batch_size)
        ]

        thoughts = await asyncio.gather(*tasks)

        return ThoughtBatch(thoughts=thoughts, context=context)

    def _generate_single_thought(
        self,
        prompt: str,
        context: str,
        index: int,
    ) -> Thought:
        """Generate a single thought with diversity."""
        # Simulate different thought strategies
        strategies = [
            "aggressive",
            "defensive",
            "positional",
            "tactical",
            "strategic",
            "endgame-focused",
            "development",
            "control",
            "sacrifice",
            "simplify",
        ]

        strategy = strategies[index % len(strategies)]

        # Add randomness based on temperature
        confidence = 0.5 + (random.random() * 0.5 * self.temperature)

        # Generate unique content
        content = f"{strategy.capitalize()} approach: {prompt[:30]}... (variant {index})"
        reasoning = f"Using {strategy} strategy based on {context or 'current position'}"

        return Thought(
            content=content,
            confidence=confidence,
            reasoning=reasoning,
        )

    async def _generate_single_thought_async(
        self,
        prompt: str,
        context: str,
        index: int,
    ) -> Thought:
        """Async version of single thought generation."""
        # Simulate async processing
        await asyncio.sleep(0.001)  # Minimal delay for testing
        return self._generate_single_thought(prompt, context, index)


class ThoughtScorer:
    """Score and evaluate thoughts in a batch."""

    def __init__(
        self,
        criteria: dict[str, float] | None = None,
        scoring_fn: Callable[[Thought, str], float] | None = None,
    ):
        """Initialize scorer.

        Args:
            criteria: Weighted criteria for scoring (must sum to 1.0)
            scoring_fn: Custom scoring function
        """
        self.criteria = criteria or {
            "relevance": 0.4,
            "depth": 0.3,
            "creativity": 0.3,
        }
        self.scoring_fn = scoring_fn or self._default_score

    def score_thought(self, thought: Thought, context: str) -> float:
        """Score a single thought.

        Args:
            thought: Thought to score
            context: Context for evaluation

        Returns:
            Score between 0 and 1
        """
        return self.scoring_fn(thought, context)

    def score_batch(self, batch: ThoughtBatch) -> ThoughtBatch:
        """Score all thoughts in batch and select best.

        Args:
            batch: ThoughtBatch to evaluate

        Returns:
            ThoughtBatch with scores and best_thought selected
        """
        for thought in batch.thoughts:
            thought.score = self.score_thought(thought, batch.context)

        # Select best thought
        batch.best_thought = max(batch.thoughts, key=lambda t: t.score or 0)

        return batch

    def _default_score(self, thought: Thought, context: str) -> float:
        """Default scoring function.

        Args:
            thought: Thought to score
            context: Context for evaluation

        Returns:
            Score between 0 and 1
        """
        base_score = thought.confidence

        # Adjust based on content characteristics
        if thought.reasoning:
            base_score += 0.1

        if len(thought.content) > 50:
            base_score += 0.05

        # Keep in valid range
        return min(1.0, max(0.0, base_score))
