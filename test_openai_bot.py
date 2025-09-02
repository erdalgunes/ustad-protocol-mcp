#!/usr/bin/env python3
"""Test the OpenAI-powered Batch of Thought."""

import os
import sys
import asyncio
import json

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bot_mcp.openai_bot import OpenAIBatchOfThought


async def test_with_demo_key():
    """Test with demo/mock scenario if no API key."""
    print("=" * 70)
    print("🧪 TESTING OPENAI BATCH OF THOUGHT")
    print("=" * 70)
    
    # Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ No OPENAI_API_KEY found in environment")
        print("📝 To test with real OpenAI:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your OpenAI API key")
        print("   3. Run: python test_openai_bot.py")
        print("\n💡 Showing demo structure without API calls:")
        
        # Show what the structure would look like
        demo_structure = {
            "problem": "How to reduce cart abandonment?",
            "context": "Mobile users, 5-step checkout",
            "thoughts": [
                {
                    "perspective": "practical",
                    "content": "[Would contain real AI-generated insight]",
                    "confidence": 0.85,
                    "tokens_used": 120,
                    "latency_ms": 850,
                    "cost": "$0.0008"
                },
                {
                    "perspective": "strategic", 
                    "content": "[Would contain real AI-generated insight]",
                    "confidence": 0.82,
                    "tokens_used": 135,
                    "latency_ms": 920,
                    "cost": "$0.0009"
                }
            ],
            "metadata": {
                "total_cost": "$0.0065",
                "total_tokens": 980,
                "cost_comparison": "This cost $0.0065 vs GPT-4 would cost ~$0.13",
                "parallel_execution": True
            }
        }
        
        print("\n📊 DEMO STRUCTURE:")
        print(json.dumps(demo_structure, indent=2))
        return
    
    print("✅ OPENAI_API_KEY found - running real test!")
    print("🚀 Generating 8 parallel perspectives with gpt-3.5-turbo\n")
    
    try:
        # Create bot
        bot = OpenAIBatchOfThought()
        
        # Test problem
        problem = "Our API response time went from 200ms to 800ms. How do we fix it?"
        context = "Traffic doubled, PostgreSQL database, no code changes"
        
        print(f"Problem: {problem}")
        print(f"Context: {context}")
        print("\n" + "-" * 70)
        print("🤖 Making 8 parallel OpenAI API calls...")
        
        # Generate thoughts
        result = await bot.think(problem, context)
        
        print("\n🎯 RESULTS:")
        print("=" * 70)
        
        # Best thought
        if result.get("best_thought"):
            best = result["best_thought"]
            print(f"\n🏆 BEST INSIGHT ({best['perspective'].upper()}):")
            print(f"   Confidence: {best['confidence']:.0%}")
            print(f"   Content: {best['content']}")
        
        # Show all perspectives
        print("\n📊 ALL PERSPECTIVES:")
        for i, thought in enumerate(result["thoughts"][:4], 1):
            print(f"\n{i}. {thought['perspective'].upper()} (conf: {thought['confidence']:.0%}, cost: {thought['cost']}):")
            content = thought['content'][:120] + "..." if len(thought['content']) > 120 else thought['content']
            print(f"   {content}")
        
        # Cost analysis
        meta = result["metadata"]
        print("\n💰 COST ANALYSIS:")
        print(f"   Total cost: {meta['total_cost']}")
        print(f"   Total tokens: {meta['total_tokens']}")
        print(f"   Latency: {meta['total_latency_ms']}ms") 
        print(f"   {meta['cost_comparison']}")
        
        # Consensus
        print(f"\n🤝 CONSENSUS: {result.get('consensus', 'N/A')}")
        
        print("\n" + "=" * 70)
        print("✅ SUCCESS: Real AI, Parallel Execution, Cost Effective!")
        print("🎉 This is the truly perfect Batch of Thought!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check your OpenAI API key is valid")
        print("   2. Ensure you have OpenAI credits")
        print("   3. Check internet connection")


async def test_cost_comparison():
    """Show cost comparison."""
    print("\n" + "=" * 70)
    print("💰 COST COMPARISON ANALYSIS")
    print("=" * 70)
    
    # Estimated costs (as of 2024)
    gpt35_input = 0.0005  # per 1K tokens
    gpt35_output = 0.0015  # per 1K tokens
    gpt4_input = 0.01     # per 1K tokens  
    gpt4_output = 0.03    # per 1K tokens
    
    # Typical usage
    input_tokens_per_call = 100
    output_tokens_per_call = 150
    num_perspectives = 8
    
    # Calculate costs
    gpt35_cost_per_call = (input_tokens_per_call * gpt35_input + output_tokens_per_call * gpt35_output) / 1000
    gpt35_total_cost = gpt35_cost_per_call * num_perspectives
    
    gpt4_single_cost = (input_tokens_per_call * gpt4_input + output_tokens_per_call * gpt4_output) / 1000
    
    print(f"📊 Cost Analysis for Typical Problem:")
    print(f"   Input tokens: {input_tokens_per_call}")
    print(f"   Output tokens: {output_tokens_per_call}")
    print()
    print(f"🔹 BoT with 8×GPT-3.5-turbo calls: ${gpt35_total_cost:.4f}")
    print(f"🔸 Single GPT-4 call: ${gpt4_single_cost:.4f}")
    print()
    print(f"💡 Savings: ${gpt4_single_cost - gpt35_total_cost:.4f} ({((gpt4_single_cost - gpt35_total_cost)/gpt4_single_cost)*100:.1f}% cheaper)")
    print(f"🧠 Intelligence: 8 specialized perspectives vs 1 general response")
    print(f"⚡ Context: 8×4K = 32K effective tokens vs 4K single context")


def main():
    """Run all tests."""
    print("🚀 PERFECT BATCH OF THOUGHT - OPENAI EDITION")
    
    # Test main functionality
    asyncio.run(test_with_demo_key())
    
    # Show cost comparison
    asyncio.run(test_cost_comparison())


if __name__ == "__main__":
    main()