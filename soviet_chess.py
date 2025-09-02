#!/usr/bin/env python3
"""Soviet Chess Training with BoT - You play Black against the engine."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import chess
from bot_mcp.advanced_evaluation import ParallelBotAnalyzer, AdvancedEvaluator, MinimaxSearcher


def soviet_chess_game():
    """Play Soviet-style chess where human is Black and BoT is White."""
    
    board = chess.Board()
    bot = ParallelBotAnalyzer(num_threads=5, depth=3)
    evaluator = AdvancedEvaluator()
    
    print("=" * 60)
    print("⚒️ SOVIET CHESS TRAINING - Batch of Thought Analysis")
    print("=" * 60)
    print("\n📚 Soviet Chess Philosophy:")
    print("• Control the center with pawns")
    print("• Develop pieces toward the center")
    print("• King safety before attacking")
    print("• Create pawn chains and space advantage")
    print("• Tactical awareness in every position")
    print("\nYou are BLACK. BoT plays White.\n")
    
    move_count = 0
    
    while not board.is_game_over():
        move_count += 1
        print(f"\n{'='*60}")
        print(f"Position after move {(move_count-1)//2 + 1}:")
        print(board)
        print(f"FEN: {board.fen()}")
        
        if board.turn == chess.WHITE:
            # BoT plays White
            print(f"\n🤖 BoT thinking (5 parallel threads)...")
            
            # Get BoT move
            move, confidence, votes = bot.analyze(board)
            
            print(f"BoT plays: {board.san(move)} ({move.uci()})")
            print(f"Confidence: {confidence*100:.0f}%")
            
            if len(votes) > 1:
                print("Thread votes:", votes)
            
            board.push(move)
            
        else:
            # Human plays Black
            print(f"\n♟ YOUR MOVE (Black):")
            
            # Analyze position for Black
            print("\n💭 BoT Analysis for Black:")
            print("-" * 40)
            
            # Get current evaluation
            eval_score = evaluator.evaluate(board)
            print(f"Position: {-eval_score/100:+.2f} (from Black's view)")
            
            # Get top 3 candidate moves
            candidates = []
            for move in list(board.legal_moves)[:15]:
                board.push(move)
                score = -evaluator.evaluate(board)  # Negative for Black's perspective
                board.pop()
                candidates.append((move, score))
            
            candidates.sort(key=lambda x: x[1], reverse=True)
            
            print("\n🎯 Top Soviet-style moves:")
            for i, (move, score) in enumerate(candidates[:3], 1):
                san = board.san(move)
                explanation = get_soviet_explanation(board, move)
                print(f"{i}. {san:6} (eval: {score/100:+.2f}) - {explanation}")
            
            # Get user move
            while True:
                try:
                    user_input = input("\nYour move (or 'quit'): ").strip()
                    
                    if user_input.lower() == 'quit':
                        print("До свидания! (Goodbye!)")
                        return
                    
                    # Parse move
                    try:
                        move = board.parse_san(user_input)
                    except:
                        move = chess.Move.from_uci(user_input)
                    
                    if move in board.legal_moves:
                        board.push(move)
                        
                        # Analyze the move
                        new_eval = evaluator.evaluate(board)
                        eval_change = (-new_eval - (-eval_score)) / 100
                        
                        if eval_change > 0:
                            print(f"✅ Good move! Improved position by {eval_change:.2f} pawns")
                        elif eval_change < -0.5:
                            print(f"⚠️ This loses {-eval_change:.2f} pawns of advantage")
                        else:
                            print(f"✓ Solid move")
                        
                        break
                    else:
                        print("Illegal move! Try again.")
                        
                except Exception as e:
                    print(f"Invalid input: {e}")
                    print("Use notation like: e5, Nf6, Bxc3, O-O")
    
    # Game over
    print("\n" + "="*60)
    if board.is_checkmate():
        if board.turn == chess.BLACK:
            print("🏆 VICTORY! You defeated the BoT engine!")
            print("Excellent Soviet-style chess!")
        else:
            print("❌ Checkmate. BoT wins.")
            print("Study the game and try again, comrade!")
    elif board.is_stalemate():
        print("🤝 Stalemate - Draw")
    else:
        print("🤝 Draw")
    
    # Show game moves
    print(f"\nGame moves: {' '.join([board.san(m) for m in board.move_stack[:20]])}...")


def get_soviet_explanation(board: chess.Board, move: chess.Move) -> str:
    """Get Soviet chess school explanation for a move."""
    
    piece = board.piece_at(move.from_square)
    if not piece:
        return "Develops piece"
    
    # Soviet principles
    if piece.piece_type == chess.PAWN:
        to_rank = chess.square_rank(move.to_square)
        to_file = chess.square_file(move.to_square)
        
        if move.to_square in [chess.E5, chess.D5, chess.E4, chess.D4]:
            return "Controls center (Nimzowitsch)"
        elif to_rank >= 5 and board.turn == chess.BLACK:
            return "Space advantage (Petrosian)"
        elif to_file in [3, 4]:  # d or e file
            return "Central pawn chain"
        else:
            return "Pawn structure"
            
    elif piece.piece_type == chess.KNIGHT:
        if move.to_square in [chess.F6, chess.C6] and board.turn == chess.BLACK:
            return "Classical development (Chigorin)"
        elif move.to_square in [chess.E4, chess.D4, chess.E5, chess.D5]:
            return "Centralized knight (Botvinnik)"
        else:
            return "Knight maneuver"
            
    elif piece.piece_type == chess.BISHOP:
        if board.is_capture(move):
            return "Exchanges piece (simplification)"
        else:
            return "Bishop to active diagonal (Tal)"
            
    elif piece.piece_type == chess.ROOK:
        to_file = chess.square_file(move.to_square)
        if to_file in [3, 4]:
            return "Rook to central file (Karpov)"
        else:
            return "Rook activation"
            
    elif piece.piece_type == chess.QUEEN:
        return "Queen development (careful!)"
        
    elif piece.piece_type == chess.KING:
        if abs(chess.square_file(move.from_square) - chess.square_file(move.to_square)) == 2:
            return "Castles (king safety first!)"
        else:
            return "King move"
    
    return "Develops position"


if __name__ == "__main__":
    print("\n🚩 Welcome to Soviet Chess School with Batch of Thought!\n")
    print("You will play the Black pieces against our BoT engine.")
    print("The engine uses 5 parallel evaluation threads:\n")
    print("• Material Thread (Tal)")
    print("• Positional Thread (Petrosian)") 
    print("• Tactical Thread (Kasparov)")
    print("• Safety Thread (Karpov)")
    print("• Dynamic Thread (Botvinnik)\n")
    
    soviet_chess_game()