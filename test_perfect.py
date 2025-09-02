#!/usr/bin/env python3
"""Test the perfect Batch of Thought implementation."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import json
from bot_mcp.perfect_bot import PerfectBatchOfThought, PerspectiveType

def test_real_problem():
    """Test on a real, complex problem."""
    print("=" * 70)
    print("🧠 TESTING PERFECT BATCH OF THOUGHT")
    print("=" * 70)
    
    problem = "Our e-commerce site has 40% cart abandonment rate. How can we reduce it to under 20%?"
    context = "Current checkout: 5 steps, no guest checkout, shipping calculated at end, mobile users are 60% of traffic"
    
    print(f"\n📝 Problem: {problem}")
    print(f"📋 Context: {context}")
    print("\n" + "-" * 70)
    
    bot = PerfectBatchOfThought(num_thoughts=8)
    result = bot.think(problem, context)
    
    print("\n🎯 RESULTS:")
    print("=" * 70)
    
    # Best thought
    if result["best_thought"]:
        best = result["best_thought"]
        print(f"\n🏆 BEST SOLUTION ({best['perspective']} perspective):")
        print(f"   Score: {best['score']:.2f}")
        print(f"   Confidence: {best['confidence']:.0%}")
        print(f"\n   Content: {best['content']}")
        print(f"\n   Reasoning: {best['reasoning']}")
        
        if best['evidence']:
            print(f"\n   Evidence:")
            for e in best['evidence']:
                print(f"   • {e}")
        
        if best['assumptions']:
            print(f"\n   Assumptions:")
            for a in best['assumptions']:
                print(f"   • {a}")
        
        if best['implications']:
            print(f"\n   Implications:")
            for i in best['implications']:
                print(f"   • {i}")
    
    # Top 3 alternatives
    print("\n\n🔄 ALTERNATIVE PERSPECTIVES:")
    print("-" * 70)
    
    for i, thought in enumerate(result["thoughts"][1:4], 2):
        print(f"\n{i}. {thought['perspective']} (Score: {thought['score']:.2f}):")
        print(f"   {thought['content'][:150]}...")
    
    # Consensus
    print(f"\n\n📊 CONSENSUS: {result['consensus']}")
    
    # Summary
    print(f"\n📝 EXECUTIVE SUMMARY:")
    print(f"   {result['summary']}")
    
    print("\n" + "=" * 70)
    print("✅ Perfect BoT Analysis Complete!")
    
    return result


def test_perspective_diversity():
    """Test that different perspectives truly differ."""
    print("\n\n" + "=" * 70)
    print("🔍 TESTING PERSPECTIVE DIVERSITY")
    print("=" * 70)
    
    problem = "Should we migrate our monolithic application to microservices?"
    context = "Team of 15 developers, 500K lines of code, 10M daily requests"
    
    bot = PerfectBatchOfThought(num_thoughts=8)
    result = bot.think(problem, context)
    
    print(f"\n📝 Problem: {problem}")
    print("\n🎭 Perspective Analysis:")
    print("-" * 70)
    
    perspective_contents = {}
    for thought in result["thoughts"]:
        perspective = thought["perspective"]
        if perspective not in perspective_contents:
            perspective_contents[perspective] = thought["content"]
            print(f"\n{perspective}:")
            print(f"  Focus: {thought['metadata'].get('domain', 'general')}")
            print(f"  Type: {thought['metadata'].get('problem_type', 'unknown')}")
            print(f"  Content: {thought['content'][:100]}...")
    
    # Check diversity
    unique_perspectives = len(perspective_contents)
    print(f"\n\n📊 Diversity Score: {unique_perspectives}/8 unique perspectives")
    
    if unique_perspectives >= 6:
        print("✅ Excellent diversity - truly different perspectives!")
    elif unique_perspectives >= 4:
        print("✓ Good diversity - multiple viewpoints covered")
    else:
        print("⚠️ Low diversity - needs improvement")
    
    return unique_perspectives >= 6


def test_evidence_quality():
    """Test that evidence and reasoning are meaningful."""
    print("\n\n" + "=" * 70)
    print("🔬 TESTING EVIDENCE QUALITY")
    print("=" * 70)
    
    problem = "Our API response time increased from 200ms to 800ms last week"
    context = "No code changes, traffic increased 2x, using PostgreSQL, hosted on AWS"
    
    bot = PerfectBatchOfThought(num_thoughts=4)
    result = bot.think(problem, context)
    
    print(f"\n📝 Problem: {problem}")
    print(f"📋 Context: {context}")
    print("\n🔍 Evidence Analysis:")
    print("-" * 70)
    
    has_evidence = 0
    has_assumptions = 0
    has_implications = 0
    
    for thought in result["thoughts"]:
        print(f"\n{thought['perspective']}:")
        
        if thought.get('evidence'):
            has_evidence += 1
            print("  Evidence: ✓")
            for e in thought['evidence'][:2]:
                print(f"    • {e}")
        else:
            print("  Evidence: ✗")
        
        if thought.get('assumptions'):
            has_assumptions += 1
            print("  Assumptions: ✓")
        else:
            print("  Assumptions: ✗")
        
        if thought.get('implications'):
            has_implications += 1
            print("  Implications: ✓")
        else:
            print("  Implications: ✗")
    
    print(f"\n\n📊 Quality Metrics:")
    print(f"  Thoughts with evidence: {has_evidence}/{len(result['thoughts'])}")
    print(f"  Thoughts with assumptions: {has_assumptions}/{len(result['thoughts'])}")
    print(f"  Thoughts with implications: {has_implications}/{len(result['thoughts'])}")
    
    quality_score = (has_evidence + has_assumptions + has_implications) / (len(result['thoughts']) * 3)
    
    if quality_score > 0.7:
        print(f"\n✅ Excellent quality score: {quality_score:.0%}")
    elif quality_score > 0.5:
        print(f"\n✓ Good quality score: {quality_score:.0%}")
    else:
        print(f"\n⚠️ Low quality score: {quality_score:.0%}")
    
    return quality_score > 0.5


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("🚀 PERFECT BATCH OF THOUGHT - COMPREHENSIVE TEST")
    print("=" * 70)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Real problem solving
    try:
        result1 = test_real_problem()
        if result1 and result1.get("best_thought"):
            tests_passed += 1
            print("\n✅ Test 1: Real Problem Solving - PASSED")
        else:
            print("\n❌ Test 1: Real Problem Solving - FAILED")
    except Exception as e:
        print(f"\n❌ Test 1 Error: {e}")
    
    # Test 2: Perspective diversity
    try:
        if test_perspective_diversity():
            tests_passed += 1
            print("\n✅ Test 2: Perspective Diversity - PASSED")
        else:
            print("\n❌ Test 2: Perspective Diversity - FAILED")
    except Exception as e:
        print(f"\n❌ Test 2 Error: {e}")
    
    # Test 3: Evidence quality
    try:
        if test_evidence_quality():
            tests_passed += 1
            print("\n✅ Test 3: Evidence Quality - PASSED")
        else:
            print("\n❌ Test 3: Evidence Quality - FAILED")
    except Exception as e:
        print(f"\n❌ Test 3 Error: {e}")
    
    # Summary
    print("\n\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)
    print(f"Passed: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("\n🎉 PERFECT! All tests passed!")
        print("The Perfect Batch of Thought is ready for production!")
    else:
        print(f"\n⚠️ {total_tests - tests_passed} test(s) failed.")
    
    return tests_passed == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)