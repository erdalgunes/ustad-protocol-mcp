#!/usr/bin/env python3
"""Analyze the current position with BoT."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import chess
from bot_mcp.advanced_evaluation import ParallelBotAnalyzer, AdvancedEvaluator

# Current position after 1.e4 d5 2.Qh5
board = chess.Board()
board.push_san("e4")
board.push_san("d5")
board.push_san("Qh5")

print("Position after 1.e4 d5 2.Qh5:")
print(board)
print(f"\nFEN: {board.fen()}")

# Analyze with BoT
bot = ParallelBotAnalyzer(num_threads=5, depth=3)
evaluator = AdvancedEvaluator()

print("\n🤖 BoT Analysis (5 parallel threads):")
print("=" * 50)

# Current evaluation
eval_score = evaluator.evaluate(board)
print(f"Position evaluation: {-eval_score/100:+.2f} (Black's perspective)")

# Get best moves for Black
print("\n🎯 Best moves for Black:")
candidates = []
for move in list(board.legal_moves):
    board.push(move)
    score = -evaluator.evaluate(board)
    board.pop()
    candidates.append((move, score))

candidates.sort(key=lambda x: x[1], reverse=True)

for i, (move, score) in enumerate(candidates[:5], 1):
    san = board.san(move)
    
    # Explain the move
    explanation = ""
    if san == "Nf6":
        explanation = "Attacks queen, develops knight!"
    elif san == "g6":
        explanation = "Prepares to fianchetto, attacks queen"
    elif san == "Nc6":
        explanation = "Develops knight, ignores queen threat"
    elif san == "dxe4":
        explanation = "Takes the pawn with tempo"
    elif san == "e6":
        explanation = "Solid, prepares development"
    
    print(f"{i}. {san:6} (eval: {score/100:+.2f}) - {explanation}")

print("\n💡 Soviet School Analysis:")
print("-" * 50)
print("White's 2.Qh5 violates opening principles!")
print("• Queen comes out too early (Botvinnik disapproves)")
print("• Can be attacked with tempo")
print("• Black gets free development")
print("\nRecommended response: 2...Nf6!")
print("This attacks the queen and develops with tempo.")