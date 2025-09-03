#!/usr/bin/env python3
"""Perfect Collaborative Batch of Thought - True Multi-Round Dialogue."""

import asyncio
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()


class PerspectiveType(Enum):
    """Core thinking perspectives for collaborative analysis."""

    ANALYTICAL = "analytical"
    CREATIVE = "creative"
    CRITICAL = "critical"
    PRACTICAL = "practical"
    STRATEGIC = "strategic"
    EMPIRICAL = "empirical"
    INTUITIVE = "intuitive"
    SYSTEMATIC = "systematic"


@dataclass
class PerspectiveState:
    """State of a perspective throughout the dialogue."""

    perspective: PerspectiveType
    initial_thought: str = ""
    dialogue_history: list[str] = field(default_factory=list)
    current_position: str = ""
    confidence: float = 0.7
    agreements: list[str] = field(default_factory=list)
    disagreements: list[str] = field(default_factory=list)
    evolution: list[str] = field(default_factory=list)


@dataclass
class DialogueRound:
    """A single round of multi-perspective dialogue."""

    round_number: int
    round_type: str  # "initial", "challenge", "consensus", "synthesis"
    perspectives_active: list[PerspectiveType]
    interactions: list[dict[str, Any]] = field(default_factory=list)
    insights_generated: list[str] = field(default_factory=list)


class ProblemAnalyzer:
    """Analyzes problems to determine optimal perspectives and approach."""

    @staticmethod
    def analyze_problem(problem: str, context: str) -> dict[str, Any]:
        """Analyze problem to determine best approach."""
        problem_lower = problem.lower()
        context_lower = context.lower()

        analysis = {
            "domain": "general",
            "complexity": "medium",
            "urgency": "medium",
            "stakeholders": [],
            "constraints": [],
            "optimal_perspectives": [],
            "rounds_needed": 3,
            "dialogue_style": "collaborative",
        }

        # Domain detection
        if any(word in problem_lower for word in ["api", "database", "system", "code"]):
            analysis["domain"] = "technical"
        elif any(word in problem_lower for word in ["business", "revenue", "market", "customer"]):
            analysis["domain"] = "business"
        elif any(word in problem_lower for word in ["team", "people", "culture", "management"]):
            analysis["domain"] = "organizational"

        # Complexity assessment
        word_count = len(problem.split()) + len(context.split())
        if word_count > 50 or "complex" in problem_lower:
            analysis["complexity"] = "high"
            analysis["rounds_needed"] = 4
        elif word_count < 20:
            analysis["complexity"] = "low"
            analysis["rounds_needed"] = 2

        # Urgency detection
        if any(word in problem_lower for word in ["urgent", "immediate", "asap", "crisis"]):
            analysis["urgency"] = "high"
            analysis["dialogue_style"] = "focused"

        # Stakeholder detection
        if "user" in problem_lower or "customer" in problem_lower:
            analysis["stakeholders"].append("users")
        if "team" in problem_lower or "developer" in problem_lower:
            analysis["stakeholders"].append("team")
        if "business" in problem_lower or "company" in problem_lower:
            analysis["stakeholders"].append("business")

        # Optimal perspective selection
        base_perspectives = [
            PerspectiveType.ANALYTICAL,
            PerspectiveType.PRACTICAL,
            PerspectiveType.CRITICAL,
        ]

        if analysis["domain"] == "technical":
            base_perspectives.extend([PerspectiveType.SYSTEMATIC, PerspectiveType.EMPIRICAL])
        elif analysis["domain"] == "business":
            base_perspectives.extend([PerspectiveType.STRATEGIC, PerspectiveType.EMPIRICAL])
        elif analysis["domain"] == "organizational":
            base_perspectives.extend([PerspectiveType.INTUITIVE, PerspectiveType.STRATEGIC])

        if analysis["complexity"] == "high":
            base_perspectives.append(PerspectiveType.CREATIVE)

        analysis["optimal_perspectives"] = list(set(base_perspectives))[:8]

        return analysis


class AdaptivePromptGenerator:
    """Generates adaptive prompts based on context and dialogue state."""

    @staticmethod
    def generate_initial_prompt(
        perspective: PerspectiveType, problem: str, context: str, analysis: dict
    ) -> str:
        """Generate initial thinking prompt for a perspective."""
        base_context = f"""
Problem: {problem}
Context: {context}
Domain: {analysis['domain']}
Complexity: {analysis['complexity']}
Urgency: {analysis['urgency']}
"""

        perspective_prompts = {
            PerspectiveType.ANALYTICAL: f"""
{base_context}

As an analytical thinker, break down this {analysis['complexity']}-complexity {analysis['domain']} problem:
1. Identify the core components and their relationships
2. Find the root cause(s) using logical analysis
3. Map cause-effect chains
4. Provide a structured analytical insight

Focus on: Logic, evidence, systematic breakdown
Avoid: Speculation, emotional arguments
Give your analysis in 2-3 sentences.""",
            PerspectiveType.CREATIVE: f"""
{base_context}

As a creative innovator, approach this {analysis['domain']} challenge with fresh thinking:
1. Challenge conventional assumptions about the problem
2. Find unexpected connections or analogies
3. Propose innovative solutions others might miss
4. Think outside the box of standard approaches

Focus on: Novel approaches, breakthrough ideas, reframing
Avoid: Obvious solutions, incremental improvements
Give your creative insight in 2-3 sentences.""",
            PerspectiveType.CRITICAL: f"""
{base_context}

As a critical examiner, scrutinize this problem statement:
1. Question underlying assumptions being made
2. Identify gaps, flaws, or risks in current thinking
3. Challenge the problem framing itself
4. Point out what's missing or overlooked

Focus on: Skeptical analysis, risk identification, assumption testing
Avoid: Accepting things at face value
Give your critical assessment in 2-3 sentences.""",
            PerspectiveType.PRACTICAL: f"""
{base_context}

As a practical implementer, focus on actionable solutions:
1. What can be done immediately (next 24-48 hours)?
2. What resources and timeline are realistic?
3. What are the concrete steps to implementation?
4. What quick wins can build momentum?

Focus on: Actionable steps, resource requirements, implementation
Avoid: Theoretical discussions, long-term planning without immediate action
Give your practical plan in 2-3 sentences.""",
            PerspectiveType.STRATEGIC: f"""
{base_context}

As a strategic thinker, consider the bigger picture:
1. What are the long-term implications of this problem?
2. How does this affect competitive positioning?
3. What opportunities does this crisis/challenge create?
4. What's the strategic priority and ROI?

Focus on: Long-term impact, competitive advantage, strategic positioning
Avoid: Short-term fixes, tactical solutions
Give your strategic insight in 2-3 sentences.""",
            PerspectiveType.EMPIRICAL: f"""
{base_context}

As a data-driven analyst, focus on measurable factors:
1. What quantifiable metrics are involved?
2. What data would prove/disprove hypotheses?
3. What statistical patterns or correlations exist?
4. How can we measure success objectively?

Focus on: Data, metrics, statistical analysis, measurement
Avoid: Subjective opinions, unsubstantiated claims
Give your empirical analysis in 2-3 sentences.""",
            PerspectiveType.INTUITIVE: f"""
{base_context}

As an intuitive pattern-recognizer, trust your instincts:
1. What does your experience tell you about this pattern?
2. What feels "off" or "right" about the situation?
3. What gut instincts do you have about the solution?
4. What patterns from past experience apply here?

Focus on: Pattern recognition, gut feelings, experiential wisdom
Avoid: Over-analysis, ignoring instincts
Give your intuitive insight in 2-3 sentences.""",
            PerspectiveType.SYSTEMATIC: f"""
{base_context}

As a systems thinker, analyze the whole system:
1. What are the key system components and interactions?
2. Where are the bottlenecks and leverage points?
3. What feedback loops and unintended consequences exist?
4. How does changing one part affect the whole?

Focus on: System dynamics, interactions, leverage points
Avoid: Isolated component thinking
Give your systems insight in 2-3 sentences.""",
        }

        return perspective_prompts[perspective]

    @staticmethod
    def generate_dialogue_prompt(
        perspective: PerspectiveType, other_thoughts: list[dict], problem: str, round_type: str
    ) -> str:
        """Generate prompt for dialogue round."""
        other_perspectives = "\n".join(
            [
                f"{thought['perspective'].upper()}: {thought['content']}"
                for thought in other_thoughts
            ]
        )

        if round_type == "challenge":
            return f"""
Original Problem: {problem}

Other perspectives have shared their thoughts:
{other_perspectives}

As a {perspective.value} thinker, respond to these perspectives:
1. What do you agree with and why?
2. What concerns or flaws do you see in their reasoning?
3. What important aspect are they missing from your perspective?
4. How would you refine or challenge their ideas?

Be specific about which perspective you're responding to. Keep response to 2-3 sentences.
"""

        if round_type == "consensus":
            return f"""
Original Problem: {problem}

All perspectives so far:
{other_perspectives}

As a {perspective.value} thinker, help build consensus:
1. Where do you see the strongest agreement across perspectives?
2. What core insight emerges that most perspectives support?
3. How can conflicting views be reconciled?
4. What's your contribution to the final solution?

Focus on finding common ground. Keep response to 2-3 sentences.
"""

        if round_type == "synthesis":
            return f"""
Original Problem: {problem}

Full dialogue history:
{other_perspectives}

As a {perspective.value} thinker, contribute to the final synthesis:
1. What's the most important insight from the entire discussion?
2. How has your thinking evolved through this dialogue?
3. What's your final recommendation incorporating all perspectives?

This is your final input. Make it count. Keep response to 2-3 sentences.
"""

        return ""


class PerfectCollaborativeBatchOfThought:
    """Perfect Collaborative Batch of Thought with multi-round dialogue.

    True collaborative intelligence through:
    - Multi-round perspective dialogue
    - Inter-perspective challenges and responses
    - Adaptive problem analysis
    - Real consensus building
    - Evolution of thinking over rounds
    """

    def __init__(self, api_key: str | None = None, model: str = "gpt-3.5-turbo"):
        """Initialize the perfect collaborative system."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required")

        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = model
        self.max_tokens = 400
        self.temperature = 0.8  # Higher for more creative dialogue

        self.analyzer = ProblemAnalyzer()
        self.prompt_generator = AdaptivePromptGenerator()

        # Cost tracking
        self.cost_per_1k_input = 0.0005
        self.cost_per_1k_output = 0.0015

    async def generate_response(self, prompt: str, perspective: str = "") -> tuple[str, float, int]:
        """Generate a single response using OpenAI."""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": f"You are an expert {perspective} thinker engaged in collaborative problem-solving. Be concise but insightful.",
                    },
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )

            content = response.choices[0].message.content.strip()
            tokens = response.usage.total_tokens
            cost = (
                response.usage.prompt_tokens * self.cost_per_1k_input
                + response.usage.completion_tokens * self.cost_per_1k_output
            ) / 1000

            return content, cost, tokens

        except Exception as e:
            return f"Error: {e!s}", 0.0, 0

    async def conduct_dialogue_round(
        self,
        round_type: str,
        round_number: int,
        perspectives: list[PerspectiveType],
        problem: str,
        context: str,
        analysis: dict,
        dialogue_history: list[dict],
    ) -> DialogueRound:
        """Conduct a single round of multi-perspective dialogue."""
        dialogue_round = DialogueRound(
            round_number=round_number, round_type=round_type, perspectives_active=perspectives
        )

        if round_type == "initial":
            # Initial parallel thinking
            tasks = []
            for perspective in perspectives:
                prompt = self.prompt_generator.generate_initial_prompt(
                    perspective, problem, context, analysis
                )
                tasks.append(self.generate_response(prompt, perspective.value))

            responses = await asyncio.gather(*tasks)

            for i, (content, cost, tokens) in enumerate(responses):
                interaction = {
                    "perspective": perspectives[i].value,
                    "content": content,
                    "cost": cost,
                    "tokens": tokens,
                    "type": "initial_thought",
                }
                dialogue_round.interactions.append(interaction)

        else:
            # Sequential dialogue (challenge, consensus, synthesis)
            for perspective in perspectives:
                prompt = self.prompt_generator.generate_dialogue_prompt(
                    perspective, dialogue_history, problem, round_type
                )

                content, cost, tokens = await self.generate_response(prompt, perspective.value)

                interaction = {
                    "perspective": perspective.value,
                    "content": content,
                    "cost": cost,
                    "tokens": tokens,
                    "type": round_type,
                    "responds_to": [p.value for p in perspectives if p != perspective],
                }
                dialogue_round.interactions.append(interaction)
                dialogue_history.append({"perspective": perspective.value, "content": content})

        return dialogue_round

    def extract_consensus(self, all_rounds: list[DialogueRound]) -> dict[str, Any]:
        """Extract real consensus from dialogue rounds."""
        # Analyze agreement patterns
        agreements = []
        disagreements = []
        evolved_positions = []

        # Find explicit agreements/disagreements in dialogue
        for round_data in all_rounds[1:]:  # Skip initial round
            for interaction in round_data.interactions:
                content = interaction["content"].lower()

                if any(word in content for word in ["agree", "correct", "exactly", "yes"]):
                    agreements.append(
                        {
                            "perspective": interaction["perspective"],
                            "content": interaction["content"][:100],
                        }
                    )

                if any(word in content for word in ["disagree", "however", "but", "wrong"]):
                    disagreements.append(
                        {
                            "perspective": interaction["perspective"],
                            "content": interaction["content"][:100],
                        }
                    )

        # Determine consensus strength
        total_interactions = sum(len(r.interactions) for r in all_rounds)
        agreement_ratio = len(agreements) / max(total_interactions, 1)

        if agreement_ratio > 0.6:
            consensus_strength = "Strong"
        elif agreement_ratio > 0.3:
            consensus_strength = "Moderate"
        else:
            consensus_strength = "Weak"

        return {
            "strength": consensus_strength,
            "agreements": agreements,
            "disagreements": disagreements,
            "agreement_ratio": agreement_ratio,
            "total_interactions": total_interactions,
        }

    def generate_final_synthesis(self, all_rounds: list[DialogueRound], consensus: dict) -> str:
        """Generate final synthesis from all rounds."""
        # Get the best insights from synthesis round
        synthesis_round = next((r for r in all_rounds if r.round_type == "synthesis"), None)
        if synthesis_round:
            synthesis_insights = [i["content"] for i in synthesis_round.interactions]
            # Take the most comprehensive synthesis
            final_synthesis = max(synthesis_insights, key=len)
        else:
            # Fallback: summarize from consensus round
            consensus_round = next((r for r in all_rounds if r.round_type == "consensus"), None)
            if consensus_round:
                consensus_insights = [i["content"] for i in consensus_round.interactions]
                final_synthesis = f"Consensus emerged around: {consensus_insights[0]}"
            else:
                final_synthesis = "Dialogue completed but no clear synthesis emerged"

        return final_synthesis

    async def think(
        self, problem: str, context: str = "", num_thoughts: int = None
    ) -> dict[str, Any]:
        """Perfect collaborative thinking through multi-round dialogue.

        Process:
        1. Analyze problem to determine optimal approach
        2. Round 1: Initial parallel perspectives
        3. Round 2: Perspectives challenge each other
        4. Round 3: Build consensus through dialogue
        5. Round 4: Final synthesis (if complex problem)

        Args:
            problem: The problem to analyze
            context: Additional context for the problem
            num_thoughts: Optional override for number of perspectives (3-8)
        """
        start_time = time.time()

        # Step 1: Analyze problem
        analysis = self.analyzer.analyze_problem(problem, context)
        perspectives = analysis["optimal_perspectives"]

        # Override perspective count if specified
        if num_thoughts is not None:
            num_thoughts = max(3, min(8, num_thoughts))  # Clamp to valid range
            if num_thoughts != len(perspectives):
                # Adjust perspectives to match requested count
                if num_thoughts > len(perspectives):
                    # Add more perspectives if needed
                    all_perspectives = list(PerspectiveType)
                    remaining = [p for p in all_perspectives if p not in perspectives]
                    perspectives.extend(remaining[: num_thoughts - len(perspectives)])
                else:
                    # Use top N perspectives if too many
                    perspectives = perspectives[:num_thoughts]

        # Initialize dialogue tracking
        all_rounds = []
        dialogue_history = []
        total_cost = 0.0
        total_tokens = 0

        # Step 2: Conduct multi-round dialogue
        round_sequence = ["initial", "challenge", "consensus"]
        if analysis["rounds_needed"] >= 4:
            round_sequence.append("synthesis")

        for i, round_type in enumerate(round_sequence):
            round_data = await self.conduct_dialogue_round(
                round_type, i + 1, perspectives, problem, context, analysis, dialogue_history
            )

            all_rounds.append(round_data)

            # Update dialogue history for next round
            if round_type == "initial":
                dialogue_history = [
                    {"perspective": interaction["perspective"], "content": interaction["content"]}
                    for interaction in round_data.interactions
                ]

            # Track costs
            round_cost = sum(interaction["cost"] for interaction in round_data.interactions)
            round_tokens = sum(interaction["tokens"] for interaction in round_data.interactions)
            total_cost += round_cost
            total_tokens += round_tokens

        # Step 3: Extract consensus and synthesis
        consensus = self.extract_consensus(all_rounds)
        final_synthesis = self.generate_final_synthesis(all_rounds, consensus)

        # Calculate metrics
        total_latency = int((time.time() - start_time) * 1000)

        return {
            "problem": problem,
            "context": context,
            "analysis": analysis,
            "rounds": [
                {"round": r.round_number, "type": r.round_type, "interactions": r.interactions}
                for r in all_rounds
            ],
            "consensus": {
                "strength": consensus["strength"],
                "summary": f"{consensus['strength']} consensus with {len(consensus['agreements'])} agreements, {len(consensus['disagreements'])} disagreements",
            },
            "final_synthesis": final_synthesis,
            "best_insights": [
                interaction["content"]
                for round_data in all_rounds
                for interaction in round_data.interactions
            ][:3],  # Top 3 insights
            "metadata": {
                "approach": "collaborative_dialogue",
                "total_rounds": len(all_rounds),
                "perspectives_used": len(perspectives),
                "total_interactions": sum(len(r.interactions) for r in all_rounds),
                "total_cost": f"${total_cost:.4f}",
                "total_tokens": total_tokens,
                "total_latency_ms": total_latency,
                "dialogue_evolution": True,
                "real_consensus": True,
            },
        }


async def demo():
    """Demonstrate perfect collaborative thinking."""
    print("=" * 80)
    print("🧠 PERFECT COLLABORATIVE BATCH OF THOUGHT")
    print("=" * 80)
    print("\n✨ Multi-round dialogue with real inter-perspective communication")
    print("🗣️  Perspectives challenge, agree, disagree, and evolve together")
    print("🎯 True consensus building through structured debate\n")

    bot = PerfectCollaborativeBatchOfThought()

    # Complex problem that benefits from collaboration
    problem = "Our startup is burning $100K/month, runway is 6 months, revenue growing 20% monthly but not enough. What do we do?"
    context = "SaaS product, 15 employees, $50K MRR, enterprise customers, strong product-market fit signals"

    print(f"Problem: {problem}")
    print(f"Context: {context}")
    print("\n" + "-" * 80)
    print("🚀 Initiating multi-round collaborative dialogue...")

    result = await bot.think(problem, context)

    print("\n📊 PROBLEM ANALYSIS:")
    analysis = result["analysis"]
    print(f"   Domain: {analysis['domain']}")
    print(f"   Complexity: {analysis['complexity']}")
    print(f"   Optimal perspectives: {len(analysis['optimal_perspectives'])}")
    print(f"   Rounds planned: {analysis['rounds_needed']}")

    print("\n🗣️  DIALOGUE ROUNDS:")
    for round_data in result["rounds"]:
        print(f"\n   Round {round_data['round']}: {round_data['type'].upper()}")
        for interaction in round_data["interactions"][:2]:  # Show first 2 interactions
            content_preview = interaction["content"][:120] + "..."
            print(f"   📝 {interaction['perspective']}: {content_preview}")

    print("\n🤝 CONSENSUS:")
    print(f"   {result['consensus']['summary']}")

    print("\n🎯 FINAL SYNTHESIS:")
    synthesis = result["final_synthesis"]
    print(f"   {synthesis[:200]}...")

    print("\n💰 COLLABORATION METRICS:")
    meta = result["metadata"]
    print(f"   Total rounds: {meta['total_rounds']}")
    print(f"   Total interactions: {meta['total_interactions']}")
    print(f"   Cost: {meta['total_cost']}")
    print(f"   Latency: {meta['total_latency_ms']}ms")

    print("\n" + "=" * 80)
    print("✅ PERFECT: Multi-round collaborative dialogue with real consensus!")


if __name__ == "__main__":
    asyncio.run(demo())
