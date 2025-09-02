#!/usr/bin/env python3
"""Battle test: BoT vs Stockfish 1500 ELO."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import chess
import chess.engine
import chess.pgn
from datetime import datetime
import time
from bot_mcp.advanced_evaluation import ParallelBotAnalyzer


def play_game(bot_is_white=True, stockfish_elo=1500, max_moves=100):
    """Play a single game between BoT and Stockfish."""
    
    board = chess.Board()
    bot_analyzer = ParallelBotAnalyzer(num_threads=5, depth=4)
    
    # Try to find Stockfish
    stockfish_paths = [
        "/usr/local/bin/stockfish",
        "/opt/homebrew/bin/stockfish",
        "stockfish",
    ]
    
    engine = None
    for path in stockfish_paths:
        try:
            engine = chess.engine.SimpleEngine.popen_uci(path)
            print(f"✓ Found Stockfish at: {path}")
            break
        except:
            continue
    
    if not engine:
        print("❌ Stockfish not found! Install with: brew install stockfish")
        return None, "no_engine"
    
    # Configure Stockfish to play at 1500 ELO
    engine.configure({"UCI_LimitStrength": True, "UCI_Elo": stockfish_elo})
    
    game = chess.pgn.Game()
    game.headers["Event"] = f"BoT vs Stockfish {stockfish_elo}"
    game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
    game.headers["White"] = "BoT" if bot_is_white else f"Stockfish {stockfish_elo}"
    game.headers["Black"] = f"Stockfish {stockfish_elo}" if bot_is_white else "BoT"
    
    node = game
    move_count = 0
    
    print(f"\n🎮 Starting game: {'BoT' if bot_is_white else 'Stockfish'} vs {'Stockfish' if bot_is_white else 'BoT'}")
    print("=" * 60)
    
    while not board.is_game_over() and move_count < max_moves:
        move_count += 1
        is_bot_turn = (board.turn == chess.WHITE) == bot_is_white
        
        if is_bot_turn:
            # BoT's move
            print(f"\nMove {move_count}: BoT thinking...", end="", flush=True)
            start_time = time.time()
            
            move, confidence, votes = bot_analyzer.analyze(board)
            
            think_time = time.time() - start_time
            print(f" {move.uci()} (confidence: {confidence:.2f}, time: {think_time:.1f}s)")
            
            if len(votes) > 1:
                print(f"  Thread votes: {votes}")
        else:
            # Stockfish's move
            print(f"\nMove {move_count}: Stockfish thinking...", end="", flush=True)
            
            result = engine.play(board, chess.engine.Limit(time=0.1))
            move = result.move
            
            print(f" {move.uci()}")
        
        board.push(move)
        node = node.add_variation(move)
        
        # Show board every 10 moves
        if move_count % 10 == 0:
            print(f"\nPosition after move {move_count}:")
            print(board)
    
    # Game result
    result = board.result()
    game.headers["Result"] = result
    
    print("\n" + "=" * 60)
    print(f"🏁 Game Over after {move_count} moves!")
    print(f"Result: {result}")
    
    if board.is_checkmate():
        winner = "BoT" if (board.turn == chess.BLACK and bot_is_white) or (board.turn == chess.WHITE and not bot_is_white) else "Stockfish"
        print(f"Checkmate! {winner} wins!")
    elif board.is_stalemate():
        print("Stalemate!")
    elif board.is_insufficient_material():
        print("Draw by insufficient material")
    elif move_count >= max_moves:
        print("Draw by move limit")
    
    engine.quit()
    
    # Determine winner for statistics
    if result == "1-0":
        winner = "bot" if bot_is_white else "stockfish"
    elif result == "0-1":
        winner = "stockfish" if bot_is_white else "bot"
    else:
        winner = "draw"
    
    return game, winner


def run_match(num_games=10, stockfish_elo=1500):
    """Run a match between BoT and Stockfish."""
    
    print("=" * 60)
    print(f"🏆 BATCH OF THOUGHT vs STOCKFISH {stockfish_elo} ELO")
    print("=" * 60)
    
    wins = {"bot": 0, "stockfish": 0, "draw": 0}
    games = []
    
    for game_num in range(1, num_games + 1):
        print(f"\n\n{'='*60}")
        print(f"GAME {game_num}/{num_games}")
        print("="*60)
        
        # Alternate colors
        bot_is_white = (game_num % 2 == 1)
        
        game, winner = play_game(bot_is_white, stockfish_elo)
        
        if winner == "no_engine":
            print("\n❌ Cannot run match without Stockfish!")
            return
        
        games.append(game)
        wins[winner] += 1
        
        print(f"\nScore so far: BoT {wins['bot']} - {wins['stockfish']} Stockfish (Draws: {wins['draw']})")
    
    # Final results
    print("\n" + "=" * 60)
    print("🏆 FINAL RESULTS")
    print("=" * 60)
    print(f"BoT wins:       {wins['bot']}")
    print(f"Stockfish wins: {wins['stockfish']}")
    print(f"Draws:          {wins['draw']}")
    
    bot_score = wins['bot'] + (wins['draw'] * 0.5)
    total_games = num_games
    win_rate = (bot_score / total_games) * 100
    
    print(f"\nBoT Score: {bot_score}/{total_games} ({win_rate:.1f}%)")
    
    if win_rate >= 50:
        print("✅ BoT is competitive with Stockfish 1500!")
    elif win_rate >= 30:
        print("📈 BoT shows promise but needs improvement")
    else:
        print("📉 BoT needs significant improvements")
    
    # Save games
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"bot_vs_stockfish_{stockfish_elo}_{timestamp}.pgn"
    
    with open(filename, "w") as f:
        for game in games:
            print(game, file=f)
            print("", file=f)
    
    print(f"\nGames saved to: {filename}")


def test_single_position():
    """Test BoT on a specific position."""
    print("\n🧪 TESTING BOT ON SPECIFIC POSITION")
    print("=" * 60)
    
    # Test position: Italian Game
    fen = "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1"
    board = chess.Board(fen)
    
    print(f"Position: {fen}")
    print(board)
    
    bot_analyzer = ParallelBotAnalyzer(num_threads=5, depth=4)
    
    print("\nBoT Analysis:")
    start_time = time.time()
    move, confidence, votes = bot_analyzer.analyze(board)
    think_time = time.time() - start_time
    
    print(f"Best move: {move.uci()}")
    print(f"Confidence: {confidence:.2f}")
    print(f"Time: {think_time:.2f}s")
    print(f"Thread votes: {votes}")
    
    # Compare with Stockfish
    try:
        engine = chess.engine.SimpleEngine.popen_uci("/opt/homebrew/bin/stockfish")
        result = engine.play(board, chess.engine.Limit(time=1.0))
        print(f"\nStockfish recommends: {result.move.uci()}")
        
        if result.move.uci() == move.uci():
            print("✅ BoT agrees with Stockfish!")
        else:
            print("🤔 BoT and Stockfish disagree")
        
        engine.quit()
    except:
        print("\nCannot compare with Stockfish (not installed)")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Battle BoT against Stockfish")
    parser.add_argument("--games", type=int, default=2, help="Number of games to play")
    parser.add_argument("--elo", type=int, default=1500, help="Stockfish ELO rating")
    parser.add_argument("--test", action="store_true", help="Test single position")
    
    args = parser.parse_args()
    
    if args.test:
        test_single_position()
    else:
        run_match(args.games, args.elo)