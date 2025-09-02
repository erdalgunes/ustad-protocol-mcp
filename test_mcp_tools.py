#!/usr/bin/env python3
"""Test MCP tools work correctly (without actual MCP server)."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import json
from bot_mcp.generic_bot import BatchOfThought

def simulate_batch_think(problem: str, context: str = "", num_thoughts: int = 8):
    """Simulate the batch_think MCP tool."""
    print(f"\n📞 Calling: batch_think")
    print(f"   Problem: {problem}")
    print(f"   Context: {context}")
    print(f"   Thoughts: {num_thoughts}")
    
    bot = BatchOfThought(num_thoughts=num_thoughts, parallel=True)
    batch = bot.think(problem, context)
    
    result = {
        "problem": problem,
        "context": context,
        "num_thoughts": len(batch.thoughts),
        "thoughts": [
            {
                "perspective": t.perspective,
                "score": t.score,
                "confidence": t.confidence
            }
            for t in sorted(batch.thoughts, key=lambda x: x.score or 0, reverse=True)[:3]
        ],
        "best_thought": {
            "perspective": batch.best_thought.perspective,
            "score": batch.best_thought.score
        } if batch.best_thought else None,
        "consensus": batch.consensus
    }
    
    print(f"\n✅ Result:")
    print(json.dumps(result, indent=2))
    return result


def simulate_iterative_think(problem: str, max_iterations: int = 3):
    """Simulate the iterative_think MCP tool."""
    print(f"\n📞 Calling: iterative_think")
    print(f"   Problem: {problem}")
    print(f"   Max iterations: {max_iterations}")
    
    bot = BatchOfThought(parallel=True)
    batches = bot.think_iteratively(problem, max_iterations=max_iterations)
    
    result = {
        "problem": problem,
        "num_iterations": len(batches),
        "final_score": batches[-1].best_thought.score if batches and batches[-1].best_thought else 0
    }
    
    print(f"\n✅ Result:")
    print(json.dumps(result, indent=2))
    return result


def main():
    """Test MCP tools."""
    print("=" * 60)
    print("🧠 TESTING MCP TOOLS (Simulated)")
    print("=" * 60)
    
    # Test 1: batch_think
    print("\n1️⃣ Testing batch_think tool:")
    result1 = simulate_batch_think(
        problem="How do we scale our database to handle 10x traffic?",
        context="Currently using PostgreSQL with 1000 req/s",
        num_thoughts=8
    )
    assert result1["num_thoughts"] == 8
    assert result1["best_thought"] is not None
    
    # Test 2: iterative_think
    print("\n2️⃣ Testing iterative_think tool:")
    result2 = simulate_iterative_think(
        problem="Design a recommendation system for e-commerce",
        max_iterations=2
    )
    assert result2["num_iterations"] <= 2
    
    # Test 3: Real-world problem
    print("\n3️⃣ Testing on real problem:")
    result3 = simulate_batch_think(
        problem="Our CI/CD pipeline takes 45 minutes. How can we reduce it to under 10 minutes?",
        context="Using Jenkins, 500 tests, monorepo with 5 services",
        num_thoughts=6
    )
    
    print("\n" + "=" * 60)
    print("✅ All MCP tool tests passed!")
    print("\nThe MCP tools are structured correctly and will work when:")
    print("1. MCP package is properly installed")
    print("2. Server is registered with Claude Code")
    print("3. Called via: claude mcp add /Users/erdalgunes/batch-of-thought-mcp")


if __name__ == "__main__":
    main()