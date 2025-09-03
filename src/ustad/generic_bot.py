"""Generic Batch of Thought implementation for any task."""

import asyncio
import hashlib
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Thought:
    """Single thought in a batch."""

    content: str
    reasoning: str = ""
    confidence: float = 0.5
    perspective: str = ""  # Which perspective/thread generated this
    score: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "content": self.content,
            "reasoning": self.reasoning,
            "confidence": self.confidence,
            "perspective": self.perspective,
            "score": self.score,
            "metadata": self.metadata,
        }


@dataclass
class ThoughtBatch:
    """Collection of thoughts for a problem."""

    thoughts: list[Thought]
    problem: str
    context: str = ""
    best_thought: Thought | None = None
    consensus: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "problem": self.problem,
            "context": self.context,
            "num_thoughts": len(self.thoughts),
            "thoughts": [t.to_dict() for t in self.thoughts],
            "best_thought": self.best_thought.to_dict() if self.best_thought else None,
            "consensus": self.consensus,
        }


class ThoughtGenerator:
    """Generates diverse thoughts from different perspectives."""

    # Different thinking perspectives/strategies
    PERSPECTIVES = [
        {
            "name": "Analytical",
            "approach": "Break down the problem into components, analyze each part systematically",
            "focus": "logic, structure, cause-effect",
        },
        {
            "name": "Creative",
            "approach": "Think outside the box, consider unconventional solutions",
            "focus": "innovation, alternatives, possibilities",
        },
        {
            "name": "Critical",
            "approach": "Question assumptions, identify weaknesses and risks",
            "focus": "problems, edge cases, validation",
        },
        {
            "name": "Practical",
            "approach": "Focus on implementation, feasibility, and real-world application",
            "focus": "execution, resources, constraints",
        },
        {
            "name": "Strategic",
            "approach": "Consider long-term implications, broader context, and goals",
            "focus": "objectives, planning, optimization",
        },
        {
            "name": "Empirical",
            "approach": "Base reasoning on data, evidence, and proven methods",
            "focus": "facts, measurement, validation",
        },
        {
            "name": "Intuitive",
            "approach": "Use pattern recognition and holistic understanding",
            "focus": "patterns, connections, insights",
        },
        {
            "name": "Systematic",
            "approach": "Follow established procedures and best practices",
            "focus": "methodology, standards, consistency",
        },
    ]

    def generate_thought(
        self, problem: str, context: str, perspective: dict[str, str], iteration: int = 0
    ) -> Thought:
        """Generate a single thought from a specific perspective."""
        # Create unique seed for deterministic but diverse generation
        seed = f"{problem}_{perspective['name']}_{iteration}_{context}"
        thought_id = hashlib.md5(seed.encode()).hexdigest()[:8]

        # Simulate thought generation with perspective
        thought_content = self._create_thought_content(problem, perspective, iteration, thought_id)

        reasoning = self._create_reasoning(problem, perspective, context)

        # Confidence varies by perspective and iteration
        base_confidence = 0.5
        if "Empirical" in perspective["name"]:
            base_confidence += 0.2
        elif "Creative" in perspective["name"]:
            base_confidence += 0.1 * (iteration % 2)
        elif "Critical" in perspective["name"]:
            base_confidence -= 0.1

        confidence = max(0.1, min(0.95, base_confidence + (iteration * 0.05)))

        return Thought(
            content=thought_content,
            reasoning=reasoning,
            confidence=confidence,
            perspective=perspective["name"],
            metadata={
                "iteration": iteration,
                "thought_id": thought_id,
                "approach": perspective["approach"],
                "focus": perspective["focus"],
            },
        )

    def _create_thought_content(
        self, problem: str, perspective: dict[str, str], iteration: int, thought_id: str
    ) -> str:
        """Create thought content based on perspective."""
        # Extract key terms from problem
        problem_words = problem.lower().split()

        # Generate perspective-specific response
        templates = {
            "Analytical": f"Breaking down the problem: The core issue involves {' and '.join(problem_words[:3])}. "
            f"Component analysis suggests focusing on systematic evaluation of each element.",
            "Creative": f"Alternative approach: What if we reframe {problem[:50]}... "
            f"Consider inverting assumptions or combining unexpected elements.",
            "Critical": f"Potential issues to consider: The problem statement assumes certain conditions. "
            f"We should validate whether {problem_words[0] if problem_words else 'this'} is actually the right focus.",
            "Practical": f"Implementation path: Start with the most actionable step. "
            f"Given current resources, prioritize {problem_words[0] if problem_words else 'core functionality'}.",
            "Strategic": "Long-term perspective: This problem connects to broader objectives. "
            "Optimizing for future scalability while addressing immediate needs.",
            "Empirical": "Based on data and precedent: Similar problems have been solved using proven methods. "
            "Evidence suggests focusing on measurable outcomes.",
            "Intuitive": "Pattern recognition suggests: This resembles common patterns in problem-solving. "
            "The underlying structure points toward holistic solutions.",
            "Systematic": f"Following established methodology: Apply standard procedures for {problem_words[0] if problem_words else 'this type of problem'}. "
            f"Step-by-step approach ensures completeness.",
        }

        base = templates.get(
            perspective["name"], f"Approaching from {perspective['name']} perspective"
        )
        return f"{base} [Iteration {iteration}, ID: {thought_id}]"

    def _create_reasoning(self, problem: str, perspective: dict[str, str], context: str) -> str:
        """Create reasoning for the thought."""
        reasoning = f"Using {perspective['name']} perspective: {perspective['approach']}. "

        if context:
            reasoning += f"Considering context: {context[:100]}. "

        reasoning += f"Focus areas: {perspective['focus']}."

        return reasoning


class ThoughtScorer:
    """Scores and evaluates thoughts."""

    def __init__(self, custom_criteria: dict[str, float] | None = None):
        """Initialize scorer with optional custom criteria."""
        self.criteria = custom_criteria or {
            "relevance": 0.3,
            "coherence": 0.2,
            "depth": 0.2,
            "practicality": 0.15,
            "innovation": 0.15,
        }

    def score_thought(
        self, thought: Thought, problem: str, other_thoughts: list[Thought] = None
    ) -> float:
        """Score a single thought."""
        score = 0.0

        # Relevance: Does it address the problem?
        problem_words = set(problem.lower().split())
        thought_words = set(thought.content.lower().split())
        relevance = len(problem_words & thought_words) / max(len(problem_words), 1)
        score += relevance * self.criteria.get("relevance", 0.3)

        # Coherence: Based on confidence and reasoning
        coherence = thought.confidence
        if thought.reasoning:
            coherence += 0.2
        score += min(1.0, coherence) * self.criteria.get("coherence", 0.2)

        # Depth: Length and detail of thought
        depth = min(1.0, len(thought.content) / 200)
        if thought.reasoning:
            depth += 0.1
        score += min(1.0, depth) * self.criteria.get("depth", 0.2)

        # Practicality: Certain perspectives score higher
        practicality = 0.5
        if thought.perspective in ["Practical", "Systematic", "Empirical"]:
            practicality += 0.3
        score += practicality * self.criteria.get("practicality", 0.15)

        # Innovation: Creative and unique perspectives
        innovation = 0.4
        if thought.perspective in ["Creative", "Intuitive"]:
            innovation += 0.3
        if other_thoughts:
            # Uniqueness compared to other thoughts
            similar_count = sum(
                1 for t in other_thoughts if t != thought and t.perspective == thought.perspective
            )
            innovation += 0.2 * (1 - similar_count / max(len(other_thoughts), 1))
        score += innovation * self.criteria.get("innovation", 0.15)

        return min(1.0, max(0.0, score))

    def score_batch(self, batch: ThoughtBatch) -> ThoughtBatch:
        """Score all thoughts in a batch and select best."""
        # Score each thought
        for thought in batch.thoughts:
            thought.score = self.score_thought(thought, batch.problem, batch.thoughts)

        # Select best thought
        if batch.thoughts:
            batch.best_thought = max(batch.thoughts, key=lambda t: t.score or 0)

        # Find consensus (most common perspective among top thoughts)
        top_thoughts = sorted(batch.thoughts, key=lambda t: t.score or 0, reverse=True)[:3]
        if top_thoughts:
            perspectives = [t.perspective for t in top_thoughts]
            most_common = Counter(perspectives).most_common(1)[0][0]
            batch.consensus = f"Consensus leans toward {most_common} approach"

        return batch


class BatchOfThought:
    """Main Batch of Thought engine for parallel thinking."""

    def __init__(
        self,
        num_thoughts: int = 8,
        perspectives: list[dict[str, str]] | None = None,
        scorer: ThoughtScorer | None = None,
        parallel: bool = True,
    ):
        """Initialize BoT engine."""
        self.num_thoughts = num_thoughts
        self.perspectives = perspectives or ThoughtGenerator.PERSPECTIVES
        self.generator = ThoughtGenerator()
        self.scorer = scorer or ThoughtScorer()
        self.parallel = parallel

    def think(
        self, problem: str, context: str = "", time_limit: float | None = None
    ) -> ThoughtBatch:
        """Generate batch of thoughts for a problem."""
        start_time = time.time()
        thoughts = []

        if self.parallel:
            # Generate thoughts in parallel
            with ThreadPoolExecutor(max_workers=min(self.num_thoughts, 8)) as executor:
                futures = []

                for i in range(self.num_thoughts):
                    perspective = self.perspectives[i % len(self.perspectives)]
                    future = executor.submit(
                        self.generator.generate_thought, problem, context, perspective, i
                    )
                    futures.append(future)

                # Collect results
                for future in futures:
                    if time_limit and (time.time() - start_time) > time_limit:
                        break
                    thoughts.append(future.result())
        else:
            # Sequential generation
            for i in range(self.num_thoughts):
                if time_limit and (time.time() - start_time) > time_limit:
                    break

                perspective = self.perspectives[i % len(self.perspectives)]
                thought = self.generator.generate_thought(problem, context, perspective, i)
                thoughts.append(thought)

        # Create and score batch
        batch = ThoughtBatch(thoughts=thoughts, problem=problem, context=context)

        return self.scorer.score_batch(batch)

    async def think_async(
        self, problem: str, context: str = "", time_limit: float | None = None
    ) -> ThoughtBatch:
        """Async version of think."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.think, problem, context, time_limit)

    def think_iteratively(
        self,
        problem: str,
        context: str = "",
        max_iterations: int = 3,
        convergence_threshold: float = 0.8,
    ) -> list[ThoughtBatch]:
        """Think iteratively, refining thoughts based on previous batches."""
        batches = []
        combined_context = context

        for iteration in range(max_iterations):
            # Generate new batch
            batch = self.think(problem, combined_context)
            batches.append(batch)

            # Check for convergence
            if batch.best_thought and batch.best_thought.score:
                if batch.best_thought.score >= convergence_threshold:
                    break

            # Update context with best thought from this iteration
            if batch.best_thought:
                combined_context = f"{context} Previous insight: {batch.best_thought.content[:100]}"

        return batches
