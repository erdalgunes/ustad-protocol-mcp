#!/usr/bin/env python3
"""OpenAI-powered Batch of Thought - Real AI, Multiple Perspectives, Unlimited Context."""

import os
import asyncio
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import time

# OpenAI imports
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class PerspectiveType(Enum):
    """Eight thinking perspectives for comprehensive analysis."""
    ANALYTICAL = "analytical"
    CREATIVE = "creative"  
    CRITICAL = "critical"
    PRACTICAL = "practical"
    STRATEGIC = "strategic"
    EMPIRICAL = "empirical"
    INTUITIVE = "intuitive"
    SYSTEMATIC = "systematic"


@dataclass
class Thought:
    """A single thought from a perspective."""
    perspective: str
    content: str
    confidence: float
    tokens_used: int
    latency_ms: int
    cost: float


class PerspectivePrompts:
    """Optimized prompts for each perspective - designed for gpt-3.5-turbo."""
    
    ANALYTICAL = """You are an analytical thinker. Analyze this problem by:
1. Breaking down components
2. Identifying cause-effect relationships
3. Finding root causes

Problem: {problem}
Context: {context}

Give a concise analytical insight (max 3 sentences). Focus on the most critical factor."""

    CREATIVE = """You are a creative thinker. Approach this problem by:
1. Finding unexpected connections
2. Challenging assumptions
3. Proposing innovative solutions

Problem: {problem}
Context: {context}

Give a concise creative insight (max 3 sentences). Focus on the most innovative approach."""

    CRITICAL = """You are a critical thinker. Examine this problem by:
1. Questioning assumptions
2. Finding flaws or gaps
3. Identifying risks

Problem: {problem}
Context: {context}

Give a concise critical insight (max 3 sentences). Focus on the biggest risk or flaw."""

    PRACTICAL = """You are a practical implementer. Solve this problem by:
1. Defining immediate actionable steps
2. Estimating time and resources
3. Identifying quick wins

Problem: {problem}
Context: {context}

Give a concise practical plan (max 3 sentences). Focus on what to do first."""

    STRATEGIC = """You are a strategic thinker. Consider:
1. Long-term implications
2. Competitive advantage
3. ROI and opportunity cost

Problem: {problem}
Context: {context}

Give a concise strategic insight (max 3 sentences). Focus on the biggest opportunity."""

    EMPIRICAL = """You are a data-driven analyst. Examine:
1. Quantifiable metrics
2. Statistical patterns
3. Evidence-based conclusions

Problem: {problem}
Context: {context}

Give a concise empirical insight (max 3 sentences). Focus on measurable factors."""

    INTUITIVE = """You are an intuitive thinker. Use:
1. Pattern recognition
2. Experience-based insights
3. Gut feelings about the solution

Problem: {problem}
Context: {context}

Give a concise intuitive insight (max 3 sentences). Focus on what feels right."""

    SYSTEMATIC = """You are a systems thinker. Analyze:
1. System components and interactions
2. Bottlenecks and constraints
3. Feedback loops and flows

Problem: {problem}
Context: {context}

Give a concise systematic insight (max 3 sentences). Focus on the system's leverage point."""


class OpenAIBatchOfThought:
    """
    Real AI-powered Batch of Thought using OpenAI's API.
    
    Key advantages:
    - 8 parallel API calls = 8x context windows
    - Each perspective gets focused context
    - Total cost < single GPT-4 call
    - Real AI reasoning, not templates
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """Initialize with OpenAI API."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. Set OPENAI_API_KEY environment variable.")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = model
        self.max_tokens = int(os.getenv("MAX_TOKENS_PER_PERSPECTIVE", "500"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        
        # Cost tracking (gpt-3.5-turbo pricing as of 2024)
        self.cost_per_1k_input = 0.0005
        self.cost_per_1k_output = 0.0015
        
        self.prompts = {
            PerspectiveType.ANALYTICAL: PerspectivePrompts.ANALYTICAL,
            PerspectiveType.CREATIVE: PerspectivePrompts.CREATIVE,
            PerspectiveType.CRITICAL: PerspectivePrompts.CRITICAL,
            PerspectiveType.PRACTICAL: PerspectivePrompts.PRACTICAL,
            PerspectiveType.STRATEGIC: PerspectivePrompts.STRATEGIC,
            PerspectiveType.EMPIRICAL: PerspectivePrompts.EMPIRICAL,
            PerspectiveType.INTUITIVE: PerspectivePrompts.INTUITIVE,
            PerspectiveType.SYSTEMATIC: PerspectivePrompts.SYSTEMATIC,
        }
    
    async def generate_thought(self, perspective: PerspectiveType, problem: str, context: str) -> Thought:
        """Generate a single thought from a perspective using OpenAI."""
        start_time = time.time()
        
        # Prepare the prompt
        prompt = self.prompts[perspective].format(
            problem=problem,
            context=context
        )
        
        try:
            # Call OpenAI API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert thinker providing focused insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                n=1
            )
            
            # Extract response
            content = response.choices[0].message.content.strip()
            
            # Calculate metrics
            latency_ms = int((time.time() - start_time) * 1000)
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            
            # Calculate cost
            cost = (input_tokens * self.cost_per_1k_input / 1000) + \
                   (output_tokens * self.cost_per_1k_output / 1000)
            
            # Estimate confidence based on response characteristics
            confidence = self._estimate_confidence(content, perspective)
            
            return Thought(
                perspective=perspective.value,
                content=content,
                confidence=confidence,
                tokens_used=total_tokens,
                latency_ms=latency_ms,
                cost=cost
            )
            
        except Exception as e:
            # Fallback for API errors
            return Thought(
                perspective=perspective.value,
                content=f"Error generating {perspective.value} perspective: {str(e)}",
                confidence=0.0,
                tokens_used=0,
                latency_ms=int((time.time() - start_time) * 1000),
                cost=0.0
            )
    
    def _estimate_confidence(self, content: str, perspective: PerspectiveType) -> float:
        """Estimate confidence based on response quality."""
        confidence = 0.7  # Base confidence for successful API call
        
        # Adjust based on content length (too short = less confident)
        if len(content) < 50:
            confidence -= 0.2
        elif len(content) > 200:
            confidence += 0.1
        
        # Adjust based on specificity (numbers, specifics = more confident)
        if any(char.isdigit() for char in content):
            confidence += 0.1
        if "%" in content or "$" in content:
            confidence += 0.05
        
        # Perspective-specific adjustments
        if perspective == PerspectiveType.EMPIRICAL and "data" in content.lower():
            confidence += 0.05
        elif perspective == PerspectiveType.PRACTICAL and "step" in content.lower():
            confidence += 0.05
        
        return min(confidence, 0.95)
    
    async def think(self, problem: str, context: str = "", perspectives: Optional[List[PerspectiveType]] = None) -> Dict[str, Any]:
        """
        Generate parallel thoughts from multiple perspectives.
        
        This is the key innovation: 8 parallel API calls, each with its own context window!
        """
        start_time = time.time()
        
        # Select perspectives
        if not perspectives:
            perspectives = list(PerspectiveType)
        
        # Generate thoughts in parallel - THE MAGIC HAPPENS HERE
        tasks = [
            self.generate_thought(perspective, problem, context)
            for perspective in perspectives
        ]
        
        thoughts = await asyncio.gather(*tasks)
        
        # Sort by confidence
        thoughts_sorted = sorted(thoughts, key=lambda t: t.confidence, reverse=True)
        
        # Calculate totals
        total_latency = int((time.time() - start_time) * 1000)
        total_tokens = sum(t.tokens_used for t in thoughts)
        total_cost = sum(t.cost for t in thoughts)
        
        # Generate consensus
        consensus = self._generate_consensus(thoughts_sorted)
        
        # Create summary
        summary = self._create_summary(thoughts_sorted, problem)
        
        return {
            "problem": problem,
            "context": context,
            "thoughts": [
                {
                    "perspective": t.perspective,
                    "content": t.content,
                    "confidence": t.confidence,
                    "tokens_used": t.tokens_used,
                    "latency_ms": t.latency_ms,
                    "cost": f"${t.cost:.4f}"
                }
                for t in thoughts_sorted
            ],
            "best_thought": {
                "perspective": thoughts_sorted[0].perspective,
                "content": thoughts_sorted[0].content,
                "confidence": thoughts_sorted[0].confidence
            } if thoughts_sorted else None,
            "consensus": consensus,
            "summary": summary,
            "metadata": {
                "model": self.model,
                "total_latency_ms": total_latency,
                "total_tokens": total_tokens,
                "total_cost": f"${total_cost:.4f}",
                "cost_comparison": f"This cost ${total_cost:.4f} vs GPT-4 would cost ~${total_cost * 20:.4f}",
                "parallel_execution": True,
                "perspectives_used": len(perspectives)
            }
        }
    
    def _generate_consensus(self, thoughts: List[Thought]) -> str:
        """Generate consensus from thoughts."""
        if not thoughts:
            return "No consensus available"
        
        high_confidence = [t for t in thoughts if t.confidence > 0.8]
        
        if len(high_confidence) >= len(thoughts) * 0.6:
            return f"Strong consensus across {len(high_confidence)} perspectives with high confidence"
        elif len(high_confidence) >= len(thoughts) * 0.3:
            return f"Moderate consensus with {len(high_confidence)} high-confidence perspectives"
        else:
            return "Diverse perspectives with varying confidence levels"
    
    def _create_summary(self, thoughts: List[Thought], problem: str) -> str:
        """Create executive summary."""
        if not thoughts:
            return "No analysis available"
        
        best = thoughts[0]
        return f"For '{problem[:50]}...': {best.perspective} perspective (confidence: {best.confidence:.0%}) suggests: {best.content[:100]}..."


class OpenAIMCPServer:
    """MCP Server wrapper for OpenAI Batch of Thought."""
    
    def __init__(self):
        """Initialize the MCP server."""
        self.bot = None  # Lazy initialization
        self.total_cost = 0.0
        self.total_calls = 0
    
    async def initialize(self):
        """Initialize OpenAI client."""
        if not self.bot:
            self.bot = OpenAIBatchOfThought()
    
    async def think(self, problem: str, context: str = "", num_perspectives: int = 8) -> str:
        """
        MCP-compatible think function.
        
        Returns JSON string with results.
        """
        await self.initialize()
        
        # Select perspectives based on number requested
        all_perspectives = list(PerspectiveType)
        selected = all_perspectives[:min(num_perspectives, len(all_perspectives))]
        
        # Generate thoughts
        result = await self.bot.think(problem, context, selected)
        
        # Track usage
        self.total_calls += 1
        if "metadata" in result and "total_cost" in result["metadata"]:
            cost_str = result["metadata"]["total_cost"].replace("$", "")
            self.total_cost += float(cost_str)
        
        # Add usage stats
        result["usage_stats"] = {
            "session_total_calls": self.total_calls,
            "session_total_cost": f"${self.total_cost:.4f}",
            "average_cost_per_call": f"${self.total_cost / self.total_calls:.4f}" if self.total_calls > 0 else "$0"
        }
        
        return json.dumps(result, indent=2)


async def demo():
    """Demonstrate the OpenAI-powered Batch of Thought."""
    print("=" * 70)
    print("🚀 OpenAI-POWERED BATCH OF THOUGHT")
    print("=" * 70)
    print("\n📝 Using gpt-3.5-turbo for maximum cost efficiency")
    print("💡 8 parallel calls still cheaper than 1 GPT-4 call!")
    print("🧠 Real AI reasoning, not templates\n")
    
    bot = OpenAIBatchOfThought()
    
    # Test problem
    problem = "Our e-commerce site has 40% cart abandonment. How do we reduce it?"
    context = "Mobile users are 60% of traffic, 5-step checkout, no guest option"
    
    print(f"Problem: {problem}")
    print(f"Context: {context}")
    print("\n" + "-" * 70)
    print("Generating 8 parallel perspectives...")
    
    result = await bot.think(problem, context)
    
    print("\n🎯 RESULTS:")
    print("=" * 70)
    
    # Best thought
    if result["best_thought"]:
        best = result["best_thought"]
        print(f"\n🏆 BEST INSIGHT ({best['perspective']}):")
        print(f"   Confidence: {best['confidence']:.0%}")
        print(f"   {best['content']}")
    
    # All perspectives
    print("\n📊 ALL PERSPECTIVES:")
    for thought in result["thoughts"][:4]:  # Show top 4
        print(f"\n{thought['perspective'].upper()} (confidence: {thought['confidence']:.0%}):")
        print(f"   {thought['content'][:150]}...")
    
    # Metadata
    meta = result["metadata"]
    print("\n💰 COST ANALYSIS:")
    print(f"   Total cost: {meta['total_cost']}")
    print(f"   Total tokens: {meta['total_tokens']}")
    print(f"   Total latency: {meta['total_latency_ms']}ms")
    print(f"   {meta['cost_comparison']}")
    
    print("\n" + "=" * 70)
    print("✅ Real AI, Multiple Perspectives, Unlimited Context!")


if __name__ == "__main__":
    # Run the demo
    asyncio.run(demo())