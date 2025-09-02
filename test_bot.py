#!/usr/bin/env python3
"""Test the generic Batch of Thought implementation."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import json
from bot_mcp.generic_bot import BatchOfThought, ThoughtGenerator

def test_basic_problem():
    """Test on a basic problem."""
    print("=" * 60)
    print("TEST 1: Basic Problem Solving")
    print("=" * 60)
    
    bot = BatchOfThought(num_thoughts=8)
    problem = "How can we reduce latency in our API?"
    context = "Current latency is 500ms, target is 200ms"
    
    batch = bot.think(problem, context)
    
    print(f"\nProblem: {problem}")
    print(f"Context: {context}")
    print(f"\nGenerated {len(batch.thoughts)} thoughts:")
    print("-" * 40)
    
    for i, thought in enumerate(sorted(batch.thoughts, key=lambda t: t.score or 0, reverse=True)[:3], 1):
        print(f"\n{i}. {thought.perspective} (score: {thought.score:.2f})")
        print(f"   {thought.content[:100]}...")
        print(f"   Confidence: {thought.confidence:.2f}")
    
    if batch.best_thought:
        print(f"\n✓ Best thought: {batch.best_thought.perspective}")
        print(f"  Score: {batch.best_thought.score:.2f}")
    
    if batch.consensus:
        print(f"\n✓ {batch.consensus}")
    
    return len(batch.thoughts) == 8 and batch.best_thought is not None


def test_iterative_thinking():
    """Test iterative refinement."""
    print("\n" + "=" * 60)
    print("TEST 2: Iterative Thinking")
    print("=" * 60)
    
    bot = BatchOfThought()
    problem = "Design a fault-tolerant distributed system"
    
    batches = bot.think_iteratively(problem, max_iterations=3)
    
    print(f"\nProblem: {problem}")
    print(f"Iterations: {len(batches)}")
    print("-" * 40)
    
    for i, batch in enumerate(batches, 1):
        if batch.best_thought:
            print(f"\nIteration {i}:")
            print(f"  Best: {batch.best_thought.perspective}")
            print(f"  Score: {batch.best_thought.score:.2f}")
            print(f"  Content: {batch.best_thought.content[:80]}...")
    
    # Check for improvement
    if len(batches) > 1:
        first_score = batches[0].best_thought.score if batches[0].best_thought else 0
        last_score = batches[-1].best_thought.score if batches[-1].best_thought else 0
        print(f"\n✓ Score improvement: {first_score:.2f} → {last_score:.2f}")
    
    return len(batches) > 0


def test_perspective_comparison():
    """Test comparing different perspectives."""
    print("\n" + "=" * 60)
    print("TEST 3: Perspective Comparison")
    print("=" * 60)
    
    problem = "Should we migrate from monolith to microservices?"
    perspectives_to_compare = ["Practical", "Strategic", "Critical"]
    
    print(f"\nProblem: {problem}")
    print(f"Comparing: {', '.join(perspectives_to_compare)}")
    print("-" * 40)
    
    generator = ThoughtGenerator()
    all_perspectives = {p["name"]: p for p in ThoughtGenerator.PERSPECTIVES}
    
    for perspective_name in perspectives_to_compare:
        if perspective_name in all_perspectives:
            perspective = all_perspectives[perspective_name]
            thought = generator.generate_thought(problem, "", perspective, 0)
            print(f"\n{perspective_name}:")
            print(f"  {thought.content[:100]}...")
            print(f"  Focus: {perspective['focus']}")
    
    return True


def test_diverse_problems():
    """Test on various problem types."""
    print("\n" + "=" * 60)
    print("TEST 4: Diverse Problem Types")
    print("=" * 60)
    
    problems = [
        ("Technical", "How to implement OAuth2 securely?"),
        ("Business", "Should we expand to European markets?"),
        ("Creative", "Design a logo for a tech startup"),
        ("Analytical", "Why is our conversion rate dropping?"),
    ]
    
    bot = BatchOfThought(num_thoughts=4)
    
    for problem_type, problem in problems:
        print(f"\n{problem_type}: {problem}")
        batch = bot.think(problem, time_limit=1.0)
        
        if batch.best_thought:
            print(f"  → {batch.best_thought.perspective}: {batch.best_thought.content[:60]}...")
        else:
            print("  → No thoughts generated")
    
    return True


def test_scoring_consistency():
    """Test that scoring is consistent and meaningful."""
    print("\n" + "=" * 60)
    print("TEST 5: Scoring Consistency")
    print("=" * 60)
    
    bot = BatchOfThought(num_thoughts=8)
    problem = "Optimize database query performance"
    
    batch = bot.think(problem)
    
    # Check all thoughts have scores
    all_scored = all(t.score is not None for t in batch.thoughts)
    print(f"\n✓ All thoughts scored: {all_scored}")
    
    # Check score distribution
    scores = [t.score for t in batch.thoughts if t.score is not None]
    if scores:
        print(f"✓ Score range: {min(scores):.2f} - {max(scores):.2f}")
        print(f"✓ Average score: {sum(scores)/len(scores):.2f}")
    
    # Check best thought has highest score
    if batch.best_thought and batch.best_thought.score:
        is_best = batch.best_thought.score == max(scores)
        print(f"✓ Best thought has highest score: {is_best}")
    
    return all_scored and len(scores) > 0


def main():
    """Run all tests."""
    print("\n🧠 BATCH OF THOUGHT TESTING")
    print("=" * 60)
    
    tests = [
        ("Basic Problem Solving", test_basic_problem),
        ("Iterative Thinking", test_iterative_thinking),
        ("Perspective Comparison", test_perspective_comparison),
        ("Diverse Problems", test_diverse_problems),
        ("Scoring Consistency", test_scoring_consistency),
    ]
    
    results = []
    for name, test_fn in tests:
        try:
            passed = test_fn()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ Error in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    passed_count = sum(1 for _, p in results if p)
    total_count = len(results)
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 All tests passed! BoT is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Needs debugging.")
    
    return passed_count == total_count


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)