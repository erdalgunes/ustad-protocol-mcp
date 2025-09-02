#!/usr/bin/env python3
"""Quick battle test with optimized BoT engine."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import chess
import chess.engine
import time
from bot_mcp.advanced_evaluation import ParallelBotAnalyzer, MinimaxSearcher, AdvancedEvaluator


def quick_game(stockfish_elo=1200):
    """Play a quick game with reduced depth for speed."""
    
    board = chess.Board()
    # Use depth 3 for speed, but with parallel threads
    bot = ParallelBotAnalyzer(num_threads=3, depth=3)
    
    try:
        engine = chess.engine.SimpleEngine.popen_uci("/opt/homebrew/bin/stockfish")
        engine.configure({"UCI_LimitStrength": True, "UCI_Elo": stockfish_elo})
    except:
        print("Stockfish not found!")
        return None
    
    print(f"\n🎮 BoT (White) vs Stockfish {stockfish_elo} (Black)")
    print("=" * 50)
    
    moves_played = []
    move_count = 0
    
    while not board.is_game_over() and move_count < 60:  # Limit to 60 moves
        move_count += 1
        
        if board.turn == chess.WHITE:
            # BoT plays White
            print(f"Move {move_count}: ", end="", flush=True)
            
            # Quick evaluation
            if move_count <= 10:
                # Opening: use simple heuristics
                legal_moves = list(board.legal_moves)
                
                # Prefer center control in opening
                center_moves = [m for m in legal_moves if 
                               m.to_square in [chess.E4, chess.D4, chess.E5, chess.D5] or
                               m.uci() in ["g1f3", "b1c3", "f1c4", "f1b5"]]
                
                if center_moves:
                    move = center_moves[0]
                else:
                    # Use quick depth-2 search
                    searcher = MinimaxSearcher(depth=2)
                    move, _ = searcher.search(board)
            else:
                # Middle/endgame: use BoT
                move, confidence, _ = bot.analyze(board)
            
            print(f"BoT: {move.uci()}")
        else:
            # Stockfish plays Black
            result = engine.play(board, chess.engine.Limit(time=0.05))  # Very fast
            move = result.move
            print(f"Move {move_count}: SF: {move.uci()}")
        
        board.push(move)
        moves_played.append(move.uci())
    
    # Result
    result = board.result()
    print(f"\n🏁 Result: {result}")
    
    if result == "1-0":
        print("✅ BoT WINS!")
        winner = "bot"
    elif result == "0-1":
        print("❌ Stockfish wins")
        winner = "stockfish"
    else:
        print("🤝 Draw")
        winner = "draw"
    
    print(f"Moves: {' '.join(moves_played[:20])}...")
    
    engine.quit()
    return winner


def test_evaluation_quality():
    """Test if our evaluation is reasonable."""
    print("\n🧪 TESTING EVALUATION QUALITY")
    print("=" * 50)
    
    evaluator = AdvancedEvaluator()
    
    positions = [
        ("Starting", "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"),
        ("After e4", "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1"),
        ("Italian", "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1"),
        ("Up Knight", "rnbqkb1r/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"),
    ]
    
    for name, fen in positions:
        board = chess.Board(fen)
        score = evaluator.evaluate(board)
        print(f"{name:12} eval: {score:+6.0f}")
    
    # Test tactical position
    print("\n🎯 Tactical Test (Back rank mate):")
    board = chess.Board("6k1/5ppp/8/8/8/8/5PPP/R5K1 w - - 0 1")
    searcher = MinimaxSearcher(depth=2)
    move, score = searcher.search(board)
    
    if move.uci() == "a1a8":
        print(f"✅ Found mate! Move: {move.uci()}, Score: {score:+.0f}")
    else:
        print(f"❌ Missed mate. Found: {move.uci()}")


def main():
    """Run quick tests."""
    print("=" * 50)
    print("🚀 QUICK BOT BATTLE TEST")
    print("=" * 50)
    
    # Test evaluation
    test_evaluation_quality()
    
    # Play games at different levels
    results = {"bot": 0, "stockfish": 0, "draw": 0}
    
    for elo in [1000, 1200, 1400]:
        print(f"\n\n{'='*50}")
        print(f"Testing against Stockfish {elo} ELO")
        print("="*50)
        
        winner = quick_game(elo)
        if winner:
            results[winner] += 1
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 SUMMARY")
    print("=" * 50)
    print(f"BoT wins: {results['bot']}")
    print(f"Stockfish wins: {results['stockfish']}") 
    print(f"Draws: {results['draw']}")
    
    if results['bot'] > 0:
        print("\n✅ BoT can win games against Stockfish!")
        print("The Batch of Thought approach with parallel evaluation works!")
    elif results['draw'] > 0:
        print("\n📈 BoT can hold draws - showing competitive play")
    else:
        print("\n📉 Need more optimization to beat Stockfish consistently")


if __name__ == "__main__":
    main()