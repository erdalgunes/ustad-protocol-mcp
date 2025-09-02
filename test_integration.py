#!/usr/bin/env python3
"""Integration test to verify BoT actually works for chess analysis."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from bot_mcp.chess_analyzer import ChessAnalyzer, ChessPosition
from bot_mcp.bot_engine import BotEngine

def test_bot_engine_actually_generates_thoughts():
    """Test that BoT engine actually generates diverse thoughts."""
    print("\n=== Testing BoT Engine ===")
    engine = BotEngine(batch_size=5, temperature=0.8)
    
    # Generate thoughts for a chess problem
    batch = engine.generate_thoughts(
        prompt="What's the best move in this position?",
        context="Complex middlegame position"
    )
    
    print(f"Generated {len(batch.thoughts)} thoughts:")
    for i, thought in enumerate(batch.thoughts, 1):
        print(f"  {i}. {thought.content[:50]}... (confidence: {thought.confidence:.2f})")
    
    # Check diversity
    contents = [t.content for t in batch.thoughts]
    unique_contents = set(contents)
    print(f"\nDiversity check: {len(unique_contents)}/{len(contents)} unique thoughts")
    
    assert len(unique_contents) == len(contents), "Thoughts should be diverse!"
    print("✓ BoT engine generates diverse thoughts")


def test_chess_analyzer_finds_moves():
    """Test that chess analyzer actually finds and evaluates moves."""
    print("\n=== Testing Chess Analyzer ===")
    analyzer = ChessAnalyzer(bot_batch_size=8)
    
    # Test on starting position
    position = ChessPosition()
    print(f"Analyzing starting position: {position.fen}")
    
    result = analyzer.analyze_position(position)
    
    print(f"\nAnalysis results:")
    print(f"  Best move: {result.best_move.uci}")
    print(f"  Evaluation: {result.evaluation:.2f}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Thoughts generated: {len(result.thoughts)}")
    
    # Verify best move is legal
    legal_moves = position.get_legal_moves()
    assert result.best_move.uci in legal_moves, f"Best move {result.best_move.uci} not in legal moves!"
    print("✓ Chess analyzer finds legal moves")


def test_position_after_moves():
    """Test analyzing position after some moves."""
    print("\n=== Testing Position After Moves ===")
    analyzer = ChessAnalyzer()
    
    # Italian opening position
    position = ChessPosition()
    moves = ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4"]
    
    print("Applying moves:", " ".join(moves))
    new_position = position.apply_moves(moves)
    
    result = analyzer.analyze_position(new_position)
    
    print(f"\nPosition after moves:")
    print(f"  FEN: {new_position.fen[:40]}...")
    print(f"  To move: {new_position.to_move}")
    print(f"  Best move: {result.best_move.uci}")
    print(f"  Evaluation: {result.evaluation:.2f}")
    
    assert result.best_move is not None, "Should find a best move!"
    print("✓ Can analyze positions after moves")


def test_thought_scoring_actually_works():
    """Test that thought scoring produces meaningful results."""
    print("\n=== Testing Thought Scoring ===")
    
    from bot_mcp.bot_engine import ThoughtScorer, Thought, ThoughtBatch
    
    # Create thoughts with different qualities
    thoughts = [
        Thought("Aggressive attack on kingside", confidence=0.9, reasoning="King exposed"),
        Thought("Defensive consolidation", confidence=0.6, reasoning=""),
        Thought("Random move", confidence=0.3, reasoning=""),
    ]
    
    batch = ThoughtBatch(thoughts=thoughts, context="Tactical position")
    scorer = ThoughtScorer()
    
    scored_batch = scorer.score_batch(batch)
    
    print("Thought scores:")
    for thought in scored_batch.thoughts:
        print(f"  '{thought.content[:30]}...' -> Score: {thought.score:.2f}")
    
    print(f"\nBest thought: '{scored_batch.best_thought.content}'")
    print(f"Best score: {scored_batch.best_thought.score:.2f}")
    
    # Verify scoring makes sense
    assert scored_batch.best_thought.score > 0.5, "Best thought should have good score"
    assert scored_batch.thoughts[0].score > scored_batch.thoughts[2].score, "Better thoughts should score higher"
    print("✓ Thought scoring produces meaningful rankings")


def test_comparison_with_stockfish_mock():
    """Test that comparison functionality works."""
    print("\n=== Testing Stockfish Comparison (Mock) ===")
    
    analyzer = ChessAnalyzer(use_stockfish=True)
    position = ChessPosition()
    
    comparison = analyzer.compare_analysis(position)
    
    print(f"BoT move: {comparison.bot_move.uci}")
    print(f"Stockfish move: {comparison.stockfish_move.uci}")
    print(f"Agreement score: {comparison.agreement_score:.2f}")
    print(f"Evaluation difference: {comparison.evaluation_difference:.2f}")
    
    assert comparison.bot_move is not None
    assert comparison.stockfish_move is not None
    print("✓ Comparison framework works")


def main():
    """Run all integration tests."""
    print("=" * 60)
    print("BATCH OF THOUGHT MCP - INTEGRATION TESTS")
    print("=" * 60)
    
    try:
        test_bot_engine_actually_generates_thoughts()
        test_chess_analyzer_finds_moves()
        test_position_after_moves()
        test_thought_scoring_actually_works()
        test_comparison_with_stockfish_mock()
        
        print("\n" + "=" * 60)
        print("✅ ALL INTEGRATION TESTS PASSED!")
        print("=" * 60)
        print("\nThe BoT system is working correctly:")
        print("- Generates diverse thoughts in batches")
        print("- Analyzes chess positions and finds legal moves")
        print("- Scores and ranks thoughts meaningfully")
        print("- Ready for MCP server implementation")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()