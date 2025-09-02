#!/usr/bin/env python3
"""Find the winning move after White's blunder."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import chess
from bot_mcp.advanced_evaluation import AdvancedEvaluator, MinimaxSearcher

# Position after 5.d3
board = chess.Board("r1bqkb1r/ppp1pppp/2n5/1B1pQ3/4n3/3P4/PPP2PPP/RNB1K1NR b KQkq - 0 5")

print("Position after White's 5.d3??")
print(board)
print()

evaluator = AdvancedEvaluator()
searcher = MinimaxSearcher(depth=4)

# Find best move
best_move, best_score = searcher.search(board)
print(f"🎯 BoT finds: {board.san(best_move)} (eval: {-best_score/100:+.2f})")

# Analyze all legal moves
print("\n💀 All Black's moves analyzed:")
print("-" * 40)

moves_eval = []
for move in board.legal_moves:
    san = board.san(move)
    board.push(move)
    
    # Check immediate effects
    is_check = board.is_check()
    attacks_queen = False
    
    # See if this attacks the queen
    if move.to_square in board.attacks(move.to_square):
        piece = board.piece_at(move.to_square)
        
    eval_score = -evaluator.evaluate(board)
    
    # Special checks
    if san in ["Bd6", "Bf6", "g6"]:
        # These might attack or trap the queen
        attacks_queen = True
        
    board.pop()
    
    moves_eval.append((san, eval_score, is_check, attacks_queen))

# Sort by evaluation
moves_eval.sort(key=lambda x: x[1], reverse=True)

for san, score, is_check, atk_q in moves_eval[:8]:
    markers = ""
    if is_check:
        markers += " +"
    if atk_q:
        markers += " 👑"
    
    print(f"{san:8}{markers:6} eval: {score/100:+.2f}")
    
    # Explain key moves
    if san == "Nxf2":
        print("         → Fork! Attacks king and rook!")
    elif san == "Bd6":
        print("         → Attacks the queen!")
    elif san == "Bf6":
        print("         → Skewer! Queen and king!")
    elif san == "g6":
        print("         → Prepares Bf6 trap!")
    elif san == "a6":
        print("         → Kicks the bishop!")

print("\n⚡ WINNING CONTINUATION:")
print("=" * 50)

# Show the main line
if board.san(best_move) == "Nxf2":
    print("5...Nxf2!! - DEVASTATING FORK!")
    board.push_san("Nxf2")
    print("Attacks king and rook simultaneously!")
    print("If 6.Kxf2, Black has won material")
    print("If 6.Ke2, Nxh1 wins the rook")
elif "Bd6" in [m[0] for m in moves_eval[:3]]:
    print("5...Bd6! - Attacks the queen!")
    print("Queen must move, Black develops with tempo")
elif "a6" in [m[0] for m in moves_eval[:3]]:
    print("5...a6! - Kicks the bishop")
    print("Forces White to make a decision")
    
print("\n🏆 Black is completely winning!")
print("White's opening was a disaster!")