"""Sequential Thinking Orchestrator - Meta-layer for GPT-5 and other reasoning models.
Implements cognitive scaffolding USING external reasoning capabilities, not replacing them.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal

from src.sequential_thinking import SequentialThinkingServer

ReasoningEffort = Literal["minimal", "low", "medium", "high", "maximum"]
ReasoningModel = Literal["gpt-5", "gpt-5-thinking", "o3", "deepseek-r1", "local"]


@dataclass
class ReasoningRequest:
    """Request for reasoning with controllable parameters"""

    thought: str
    effort: ReasoningEffort = "medium"
    model: ReasoningModel = "local"
    context: dict[str, Any] | None = None
    require_verification: bool = True
    max_reasoning_tokens: int | None = None


class ReasoningProvider(ABC):
    """Abstract base for different reasoning providers"""

    @abstractmethod
    async def reason(self, request: ReasoningRequest) -> dict[str, Any]:
        """Execute reasoning with given parameters"""


class LocalReasoningProvider(ReasoningProvider):
    """Our local sequential thinking implementation"""

    def __init__(self) -> None:
        self.server = SequentialThinkingServer()

    async def reason(self, request: ReasoningRequest) -> dict[str, Any]:
        """Use local implementation for basic reasoning"""
        # Map effort to number of thoughts
        effort_map = {"minimal": 1, "low": 3, "medium": 5, "high": 8, "maximum": 15}

        total_thoughts = effort_map[request.effort]

        # Process as single thought for now (YAGNI)
        result = self.server.process_thought(
            {
                "thought": request.thought,
                "thoughtNumber": 1,
                "totalThoughts": total_thoughts,
                "nextThoughtNeeded": total_thoughts > 1,
            }
        )

        return {"reasoning": result, "model": "local", "effort": request.effort}


class GPT5ReasoningProvider(ReasoningProvider):
    """Provider for GPT-5 reasoning capabilities"""

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        # In real implementation, initialize OpenAI client

    async def reason(self, request: ReasoningRequest) -> dict[str, Any]:
        """Use GPT-5's native reasoning capabilities.
        This would make actual API calls in production.
        """
        # Placeholder for actual GPT-5 API call
        # In production:
        # response = await openai.ChatCompletion.create(
        #     model="gpt-5-thinking",
        #     messages=[{"role": "user", "content": request.thought}],
        #     reasoning_effort=request.effort,
        #     max_reasoning_tokens=request.max_reasoning_tokens
        # )

        return {
            "reasoning": {
                "thought": request.thought,
                "reasoning_steps": [
                    "Breaking down the problem",
                    "Analyzing components",
                    "Synthesizing solution",
                ],
                "conclusion": "Placeholder GPT-5 reasoning result",
            },
            "model": "gpt-5",
            "effort": request.effort,
            "tokens_used": 0,  # Would be actual token count
        }


class SequentialThinkingOrchestrator:
    """Orchestrates reasoning using best available models.
    Implements CBT/HiTOP scaffolding ON TOP OF existing reasoning capabilities.
    """

    def __init__(self) -> None:
        self.providers: dict[str, ReasoningProvider] = {
            "local": LocalReasoningProvider(),
            "gpt-5": GPT5ReasoningProvider(),
        }
        self.history: list[dict[str, Any]] = []
        self.maintenance_factors_identified: list[str] = []

    async def think_with_scaffolding(
        self,
        problem: str,
        effort: ReasoningEffort = "medium",
        preferred_model: ReasoningModel | None = None,
    ) -> dict[str, Any]:
        """Apply cognitive scaffolding to reasoning process.
        Uses external models when available, falls back to local.
        """
        # 1. Reality Testing (CBT principle)
        if self._needs_fact_checking(problem):
            # In production, would call Tavily or similar
            fact_check_result = await self._reality_test(problem)
            if fact_check_result.get("corrections"):
                problem = self._incorporate_facts(problem, fact_check_result)

        # 2. Identify Maintenance Factors (what might perpetuate errors)
        maintenance_factors = self._identify_maintenance_factors(problem)
        self.maintenance_factors_identified.extend(maintenance_factors)

        # 3. Choose best reasoning model
        model = self._select_model(preferred_model, effort)
        provider = self._get_provider(model)

        # 4. Create scaffolded request
        request = ReasoningRequest(
            thought=self._scaffold_prompt(problem, maintenance_factors),
            effort=effort,
            model=model,
            require_verification=True,
        )

        # 5. Execute reasoning with selected provider
        result = await provider.reason(request)

        # 6. Apply dimensional assessment (HiTOP)
        dimensional_assessment = self._assess_dimensions(result)
        result["dimensional_assessment"] = dimensional_assessment

        # 7. Check for cognitive biases
        bias_check = self._check_biases(result)
        if bias_check["biases_detected"]:
            result = await self._mitigate_biases(result, bias_check, provider)

        # 8. Store in history
        self.history.append(result)

        return result

    def _needs_fact_checking(self, problem: str) -> bool:
        """Determine if the problem contains factual claims"""
        fact_indicators = ["is", "are", "was", "were", "will be", "has been"]
        return any(indicator in problem.lower() for indicator in fact_indicators)

    async def _reality_test(self, problem: str) -> dict[str, Any]:
        """Reality test factual claims (would use Tavily in production)"""
        # Placeholder for Tavily integration
        return {"verified": True, "corrections": []}

    def _identify_maintenance_factors(self, problem: str) -> list[str]:
        """Identify what might maintain problematic patterns"""
        factors = []

        if "always" in problem or "never" in problem:
            factors.append("black_and_white_thinking")

        if "should" in problem or "must" in problem:
            factors.append("rigid_rules")

        if len(problem) > 500:
            factors.append("over_complexity")

        return factors

    def _scaffold_prompt(self, problem: str, maintenance_factors: list[str]) -> str:
        """Add cognitive scaffolding to the prompt"""
        scaffold = problem

        if maintenance_factors:
            scaffold += "\n\nConsider these patterns that might affect reasoning:"
            for factor in maintenance_factors:
                if factor == "black_and_white_thinking":
                    scaffold += "\n- Avoid absolute thinking; consider nuances"
                elif factor == "rigid_rules":
                    scaffold += "\n- Question assumptions; consider flexibility"
                elif factor == "over_complexity":
                    scaffold += "\n- Start simple; add complexity only if needed"

        return scaffold

    def _select_model(
        self, preferred: ReasoningModel | None, effort: ReasoningEffort
    ) -> ReasoningModel:
        """Select appropriate model based on effort and availability"""
        if preferred and preferred in self.providers:
            return preferred

        # Route based on effort level (following GPT-5 routing pattern)
        if effort in ["minimal", "low"]:
            return "local"  # Use lightweight model for simple tasks
        if effort in ["high", "maximum"]:
            return "gpt-5" if "gpt-5" in self.providers else "local"
        return "local"  # Default to local for medium tasks

    def _get_provider(self, model: ReasoningModel) -> ReasoningProvider:
        """Get provider for model, with fallback"""
        # Map model names to provider keys
        provider_map = {
            "gpt-5": "gpt-5",
            "gpt-5-thinking": "gpt-5",
            "o3": "gpt-5",  # Would have separate provider in production
            "deepseek-r1": "local",  # Fallback for now
            "local": "local",
        }

        provider_key = provider_map.get(model, "local")
        return self.providers.get(provider_key, self.providers["local"])

    def _assess_dimensions(self, result: dict[str, Any]) -> dict[str, float]:
        """Apply HiTOP dimensional assessment"""
        return {
            "thought_disorder": 0.0,  # Would analyze for tangentiality
            "detachment": 0.0,  # Would analyze for concreteness
            "cognitive_dysfunction": 0.0,  # Would analyze for coherence
            "social_cognition": 0.0,  # Would analyze for perspective-taking
        }

    def _check_biases(self, result: dict[str, Any]) -> dict[str, Any]:
        """Check for cognitive biases in reasoning"""
        biases = []

        # Simple heuristic checks (would be more sophisticated)
        reasoning_text = str(result.get("reasoning", ""))

        if "obviously" in reasoning_text or "clearly" in reasoning_text:
            biases.append("overconfidence")

        if "always" in reasoning_text or "never" in reasoning_text:
            biases.append("absolutism")

        return {"biases_detected": biases, "confidence": 0.7 if biases else 0.9}

    async def _mitigate_biases(
        self, result: dict[str, Any], bias_check: dict[str, Any], provider: ReasoningProvider
    ) -> dict[str, Any]:
        """Mitigate detected biases through re-reasoning"""
        if "overconfidence" in bias_check["biases_detected"]:
            # Re-reason with uncertainty prompting
            request = ReasoningRequest(
                thought=f"Reconsider with uncertainty: {result['reasoning'].get('thought', '')}",
                effort="high",
                require_verification=True,
            )
            result = await provider.reason(request)

        return result

    def get_reasoning_chain(self) -> list[dict[str, Any]]:
        """Get the complete reasoning chain"""
        return self.history

    def reset(self) -> None:
        """Reset orchestrator state"""
        self.history.clear()
        self.maintenance_factors_identified.clear()
        for provider in self.providers.values():
            if hasattr(provider, "server"):
                provider.server.reset()
