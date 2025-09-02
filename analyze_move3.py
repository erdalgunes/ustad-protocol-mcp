#!/usr/bin/env python3
"""Analyze position after 1.e4 d5 2.Qh5 Nf6 3.Qe5."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import chess
from bot_mcp.advanced_evaluation import ParallelBotAnalyzer, AdvancedEvaluator, MinimaxSearcher

# Current position
board = chess.Board()
board.push_san("e4")
board.push_san("d5")
board.push_san("Qh5")
board.push_san("Nf6")
board.push_san("Qe5")

print("Position after 1.e4 d5 2.Qh5 Nf6 3.Qe5:")
print(board)
print(f"\nFEN: {board.fen()}\n")

# Deep analysis with BoT
bot = ParallelBotAnalyzer(num_threads=5, depth=3)
evaluator = AdvancedEvaluator()

print("🤖 BoT Deep Analysis (5 parallel threads):")
print("=" * 50)

# Current evaluation
eval_score = evaluator.evaluate(board)
print(f"Position evaluation: {-eval_score/100:+.2f} (Black's perspective)")

# Get best moves with deeper search
searcher = MinimaxSearcher(depth=3)
best_move, best_score = searcher.search(board)

print(f"\nMinimax says: {board.san(best_move)} (score: {-best_score/100:+.2f})")

# Analyze top candidate moves
print("\n🎯 Candidate Moves for Black:")
print("-" * 50)

candidates = []
critical_moves = ["Nc6", "dxe4", "Nxe4", "Bd7", "Bg4", "e6", "c6"]

for move_san in critical_moves:
    try:
        move = board.parse_san(move_san)
        board.push(move)
        
        # Check for immediate tactics
        is_check = board.is_check()
        is_capture = board.is_capture(move)
        
        # Evaluate position
        score = -evaluator.evaluate(board)
        
        # Check White's best response
        white_response, white_score = searcher.search(board)
        
        board.pop()
        
        # Analysis
        if move_san == "Nc6":
            explanation = "Develops knight, attacks queen!"
        elif move_san == "dxe4":
            explanation = "Takes pawn, opens position"
        elif move_san == "Nxe4":
            explanation = "Bold sacrifice?! Tactical shot!"
        elif move_san == "e6":
            explanation = "Solid, prepares Bd6"
        elif move_san == "Bg4":
            explanation = "Develops with tempo"
        elif move_san == "c6":
            explanation = "Supports center, prepares Bf5"
        else:
            explanation = "Develops piece"
            
        candidates.append((move_san, score, explanation, is_check))
        
    except:
        continue

# Sort by score
candidates.sort(key=lambda x: x[1], reverse=True)

for i, (move_san, score, explanation, is_check) in enumerate(candidates[:5], 1):
    check_mark = " +" if is_check else ""
    print(f"{i}. {move_san:6}{check_mark} (eval: {score/100:+.2f}) - {explanation}")

print("\n💡 Soviet School Strategic Assessment:")
print("=" * 50)
print("White's queen on e5 is still misplaced!")
print("Key themes:")
print("• Black has lead in development")
print("• White's queen blocks own pieces")
print("• Black can build attack with tempo")
print()
print("🎓 Petrosian says: 'Nc6! Develop with threats!'")
print("🎓 Tal says: 'Nxe4!? Tactics in the air!'")
print("🎓 Karpov says: 'dxe4, simple and good'")

# Check if Nxe4 works
print("\n⚡ Tactical Alert - Analyzing Nxe4:")
print("-" * 40)
board.push_san("Nxe4")
if board.is_check():
    print("Nxe4 gives check!")
board.push_san("Qxe4")
print(f"After 3...Nxe4 4.Qxe4:")
eval_after = -evaluator.evaluate(board)
print(f"Position: {eval_after/100:+.2f} for Black")
print("Black has: Two pieces for queen development")
board.pop()
board.pop()

print("\n📊 RECOMMENDATION:")
print("Play 3...Nc6! - Most principled")
print("• Develops with tempo")
print("• Attacks queen again") 
print("• Maintains advantage")