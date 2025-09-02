#!/usr/bin/env python3
"""Interactive Chess Coach using Batch of Thought."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import chess
import chess.svg
from bot_mcp.advanced_evaluation import ParallelBotAnalyzer, AdvancedEvaluator


class BotChessCoach:
    """Chess coach powered by Batch of Thought."""
    
    def __init__(self):
        self.board = chess.Board()
        self.bot = ParallelBotAnalyzer(num_threads=5, depth=3)
        self.evaluator = AdvancedEvaluator()
        self.move_history = []
        
    def display_board(self):
        """Display the current board position."""
        print("\n" + "="*50)
        print(self.board)
        print("="*50)
        print(f"FEN: {self.board.fen()}")
        
    def analyze_position(self):
        """Analyze current position with BoT."""
        print("\n🤖 BoT Analysis (5 parallel threads thinking...)")
        print("-"*50)
        
        # Get BoT analysis
        best_move, confidence, votes = self.bot.analyze(self.board)
        
        # Get evaluation
        eval_score = self.evaluator.evaluate(self.board)
        
        print(f"📊 Position evaluation: {eval_score/100:+.2f} pawns")
        print(f"🎯 Best move: {best_move.uci()} ({self.board.san(best_move)})")
        print(f"💪 Confidence: {confidence*100:.0f}%")
        
        if len(votes) > 1:
            print(f"\n🧠 Thread consensus:")
            for move_uci, count in sorted(votes.items(), key=lambda x: x[1], reverse=True):
                move = chess.Move.from_uci(move_uci)
                san = self.board.san(move)
                print(f"  • {san} ({move_uci}): {count} votes")
        
        # Explain the move
        self.explain_move(best_move, eval_score)
        
        return best_move
    
    def explain_move(self, move: chess.Move, current_eval: float):
        """Explain why a move is good using BoT reasoning."""
        print(f"\n💭 Why {self.board.san(move)}?")
        
        # Simulate the move
        self.board.push(move)
        future_eval = self.evaluator.evaluate(self.board)
        self.board.pop()
        
        # Generate explanations based on move characteristics
        explanations = []
        
        # Check piece moved
        piece = self.board.piece_at(move.from_square)
        if piece:
            if piece.piece_type == chess.PAWN:
                if move.to_square in [chess.E4, chess.D4, chess.E5, chess.D5]:
                    explanations.append("Controls the center")
                if chess.square_rank(move.to_square) >= 5:
                    explanations.append("Advances pawn toward promotion")
            elif piece.piece_type == chess.KNIGHT:
                if move.to_square in [chess.E4, chess.D4, chess.E5, chess.D5, chess.C5, chess.F5]:
                    explanations.append("Knight to strong central outpost")
            elif piece.piece_type == chess.BISHOP:
                explanations.append("Develops bishop to active diagonal")
            elif piece.piece_type == chess.ROOK:
                if chess.square_file(move.to_square) in [3, 4]:  # d or e file
                    explanations.append("Rook to central file")
            elif piece.piece_type == chess.KING:
                if abs(chess.square_file(move.from_square) - chess.square_file(move.to_square)) == 2:
                    explanations.append("Castles for king safety")
        
        # Check if it's a capture
        if self.board.is_capture(move):
            captured = self.board.piece_at(move.to_square)
            if captured:
                explanations.append(f"Captures {chess.piece_name(captured.piece_type)}")
        
        # Check evaluation change
        eval_change = (future_eval - current_eval) / 100
        if self.board.turn == chess.WHITE:
            if eval_change > 0.5:
                explanations.append(f"Improves position by {eval_change:.1f} pawns")
        else:
            if eval_change < -0.5:
                explanations.append(f"Improves position by {-eval_change:.1f} pawns")
        
        # Check for checks
        self.board.push(move)
        if self.board.is_check():
            explanations.append("Gives check!")
        self.board.pop()
        
        if explanations:
            for exp in explanations[:3]:  # Show top 3 reasons
                print(f"  ✓ {exp}")
        else:
            print("  ✓ Solid developing move")
    
    def get_move_suggestions(self, num_suggestions=3):
        """Get top move suggestions with explanations."""
        print("\n🎓 Top moves to consider:")
        print("-"*50)
        
        # Get evaluations for all legal moves
        move_evals = []
        for move in list(self.board.legal_moves)[:20]:  # Limit for speed
            self.board.push(move)
            eval_score = self.evaluator.evaluate(self.board)
            self.board.pop()
            
            # Adjust score based on whose turn
            if not self.board.turn:  # Black's perspective
                eval_score = -eval_score
                
            move_evals.append((move, eval_score))
        
        # Sort by evaluation
        move_evals.sort(key=lambda x: x[1], reverse=self.board.turn)
        
        # Show top suggestions
        for i, (move, score) in enumerate(move_evals[:num_suggestions], 1):
            san = self.board.san(move)
            print(f"\n{i}. {san} (eval: {score/100:+.2f})")
            
            # Mini explanation
            piece = self.board.piece_at(move.from_square)
            if piece:
                if self.board.is_capture(move):
                    print(f"   → Captures on {chess.square_name(move.to_square)}")
                elif piece.piece_type == chess.PAWN and chess.square_rank(move.to_square) >= 6:
                    print(f"   → Advances pawn dangerously")
                elif piece.piece_type in [chess.KNIGHT, chess.BISHOP] and len(self.move_history) < 10:
                    print(f"   → Develops piece")
                else:
                    print(f"   → Improves {chess.piece_name(piece.piece_type)} position")
    
    def play_move(self, move_str: str) -> bool:
        """Play a move in algebraic notation."""
        try:
            # Try to parse as SAN (e4, Nf3, etc)
            try:
                move = self.board.parse_san(move_str)
            except:
                # Try UCI format (e2e4)
                move = chess.Move.from_uci(move_str)
            
            if move in self.board.legal_moves:
                self.board.push(move)
                self.move_history.append(move)
                return True
            else:
                print(f"❌ Illegal move: {move_str}")
                return False
        except Exception as e:
            print(f"❌ Invalid move format: {move_str}")
            print("   Use standard notation like: e4, Nf3, Bxc6, O-O")
            return False
    
    def undo_move(self):
        """Undo the last move."""
        if self.move_history:
            self.board.pop()
            self.move_history.pop()
            print("↶ Move undone")
            return True
        return False
    
    def reset_game(self):
        """Reset to starting position."""
        self.board = chess.Board()
        self.move_history = []
        print("♟ New game started")
    
    def check_game_status(self):
        """Check if game is over."""
        if self.board.is_checkmate():
            winner = "Black" if self.board.turn else "White"
            print(f"\n🏆 Checkmate! {winner} wins!")
            return True
        elif self.board.is_stalemate():
            print("\n🤝 Stalemate! It's a draw.")
            return True
        elif self.board.is_insufficient_material():
            print("\n🤝 Draw by insufficient material.")
            return True
        elif self.board.is_check():
            print("\n⚠️ Check!")
        return False


def main():
    """Interactive chess coaching session."""
    coach = BotChessCoach()
    
    print("="*50)
    print("♟ BATCH OF THOUGHT CHESS COACH")
    print("="*50)
    print("\nCommands:")
    print("  [move]  - Play a move (e.g., e4, Nf3, Bxc6)")
    print("  analyze - Get BoT analysis of position")
    print("  suggest - Get move suggestions")
    print("  undo    - Undo last move")
    print("  board   - Show current position")
    print("  new     - Start new game")
    print("  quit    - Exit")
    print("\nYou are playing WHITE. I'll coach you with BoT!\n")
    
    coach.display_board()
    
    while True:
        # Get user input
        if coach.board.turn == chess.WHITE:
            prompt = "Your move (White): "
        else:
            prompt = "Your move (Black): "
            
        try:
            user_input = input(f"\n{prompt}").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Thanks for playing!")
            break
        
        if not user_input:
            continue
            
        if user_input == 'quit':
            print("👋 Thanks for playing!")
            break
        elif user_input == 'analyze':
            coach.analyze_position()
        elif user_input == 'suggest':
            coach.get_move_suggestions()
        elif user_input == 'undo':
            if coach.undo_move():
                coach.display_board()
        elif user_input == 'board':
            coach.display_board()
        elif user_input == 'new':
            coach.reset_game()
            coach.display_board()
        else:
            # Try to play the move
            if coach.play_move(user_input):
                coach.display_board()
                
                # Check game status
                if coach.check_game_status():
                    print("\nGame over! Type 'new' for another game.")
                    continue
                
                # Auto-analyze after each move
                print("\n🤔 Let me analyze this position for you...")
                coach.analyze_position()
                coach.get_move_suggestions(2)


if __name__ == "__main__":
    main()