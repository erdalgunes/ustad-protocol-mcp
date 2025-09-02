#!/usr/bin/env python3
"""Batch of Thought MCP Server for Chess Analysis."""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional

import chess
from mcp import Server, Tool, TextContent, ImageContent
from mcp.server import Request, Response, NotificationHandler
from mcp.server.stdio import stdio_server

from .advanced_evaluation import ParallelBotAnalyzer, AdvancedEvaluator, MinimaxSearcher
from .chess_analyzer import ChessPosition, ChessAnalyzer


class BotMCPServer:
    """MCP Server for Batch of Thought Chess Analysis."""
    
    def __init__(self):
        self.server = Server("batch-of-thought-chess")
        self.bot = ParallelBotAnalyzer(num_threads=5, depth=3)
        self.evaluator = AdvancedEvaluator()
        self.analyzer = ChessAnalyzer()
        
        # Register tools
        self._register_tools()
    
    def _register_tools(self):
        """Register all available tools."""
        
        @self.server.tool()
        async def analyze_position(fen: str) -> str:
            """Analyze a chess position using Batch of Thought.
            
            Args:
                fen: FEN string of the position to analyze
                
            Returns:
                JSON string with analysis results
            """
            try:
                board = chess.Board(fen)
                
                # Get BoT analysis
                best_move, confidence, votes = self.bot.analyze(board)
                
                # Get evaluation
                eval_score = self.evaluator.evaluate(board)
                
                # Get top moves
                top_moves = []
                for move in list(board.legal_moves)[:10]:
                    board.push(move)
                    score = self.evaluator.evaluate(board)
                    board.pop()
                    top_moves.append({
                        "move": move.uci(),
                        "san": board.san(move),
                        "score": score
                    })
                
                top_moves.sort(key=lambda x: x["score"], reverse=board.turn)
                
                result = {
                    "fen": fen,
                    "best_move": best_move.uci(),
                    "best_move_san": board.san(best_move),
                    "confidence": confidence,
                    "evaluation": eval_score,
                    "thread_votes": votes,
                    "top_moves": top_moves[:5],
                    "turn": "white" if board.turn else "black"
                }
                
                return json.dumps(result, indent=2)
                
            except Exception as e:
                return json.dumps({"error": str(e)})
        
        @self.server.tool()
        async def find_best_move(fen: str, depth: int = 3) -> str:
            """Find the best move in a position using minimax search.
            
            Args:
                fen: FEN string of the position
                depth: Search depth (default 3)
                
            Returns:
                JSON string with best move and evaluation
            """
            try:
                board = chess.Board(fen)
                searcher = MinimaxSearcher(depth=depth)
                
                best_move, score = searcher.search(board)
                
                if best_move:
                    result = {
                        "fen": fen,
                        "best_move": best_move.uci(),
                        "best_move_san": board.san(best_move),
                        "evaluation": score,
                        "depth": depth,
                        "nodes_searched": searcher.nodes_searched
                    }
                else:
                    result = {"error": "No legal moves"}
                
                return json.dumps(result, indent=2)
                
            except Exception as e:
                return json.dumps({"error": str(e)})
        
        @self.server.tool()
        async def compare_moves(fen: str, moves: List[str]) -> str:
            """Compare multiple moves in a position.
            
            Args:
                fen: FEN string of the position
                moves: List of moves to compare (UCI format)
                
            Returns:
                JSON string with comparison results
            """
            try:
                board = chess.Board(fen)
                results = []
                
                for move_uci in moves:
                    try:
                        move = chess.Move.from_uci(move_uci)
                        if move in board.legal_moves:
                            board.push(move)
                            
                            # Evaluate position after move
                            score = self.evaluator.evaluate(board)
                            
                            # Check for tactics
                            is_check = board.is_check()
                            is_capture = board.is_capture(move)
                            
                            board.pop()
                            
                            results.append({
                                "move": move_uci,
                                "san": board.san(move),
                                "evaluation": score,
                                "is_check": is_check,
                                "is_capture": is_capture
                            })
                        else:
                            results.append({
                                "move": move_uci,
                                "error": "Illegal move"
                            })
                    except:
                        results.append({
                            "move": move_uci,
                            "error": "Invalid move format"
                        })
                
                return json.dumps({
                    "fen": fen,
                    "comparisons": results
                }, indent=2)
                
            except Exception as e:
                return json.dumps({"error": str(e)})
        
        @self.server.tool()
        async def soviet_chess_coach(fen: str, player_color: str = "black") -> str:
            """Get Soviet-style chess coaching for a position.
            
            Args:
                fen: FEN string of the position
                player_color: Color the player is playing ("white" or "black")
                
            Returns:
                Coaching advice in Soviet chess style
            """
            try:
                board = chess.Board(fen)
                is_white = player_color.lower() == "white"
                
                # Get analysis
                best_move, confidence, votes = self.bot.analyze(board)
                eval_score = self.evaluator.evaluate(board)
                
                # Adjust evaluation for player's perspective
                if not is_white:
                    eval_score = -eval_score
                
                # Generate Soviet-style advice
                advice = []
                
                if abs(eval_score) < 50:
                    advice.append("Position is balanced. Fight for initiative!")
                elif eval_score > 200:
                    advice.append("You have winning advantage! Technique is key.")
                elif eval_score > 50:
                    advice.append("You are better. Increase pressure!")
                elif eval_score < -200:
                    advice.append("Position is difficult. Create complications!")
                else:
                    advice.append("You are worse. Defend accurately!")
                
                # Move-specific advice
                san = board.san(best_move)
                piece = board.piece_at(best_move.from_square)
                
                if piece:
                    if piece.piece_type == chess.PAWN:
                        advice.append(f"Pawn to {san} - Control space like Petrosian!")
                    elif piece.piece_type == chess.KNIGHT:
                        advice.append(f"Knight to {san} - Maneuver like Tal!")
                    elif piece.piece_type == chess.BISHOP:
                        advice.append(f"Bishop to {san} - Dominate diagonals!")
                    elif piece.piece_type == chess.ROOK:
                        advice.append(f"Rook to {san} - Seize the file like Karpov!")
                    elif piece.piece_type == chess.QUEEN:
                        advice.append(f"Queen to {san} - Careful like Botvinnik!")
                    elif piece.piece_type == chess.KING:
                        advice.append(f"King to {san} - Safety first!")
                
                result = {
                    "fen": fen,
                    "best_move": best_move.uci(),
                    "best_move_san": san,
                    "evaluation": eval_score / 100,
                    "confidence": confidence,
                    "soviet_advice": advice,
                    "thread_consensus": votes
                }
                
                return json.dumps(result, indent=2)
                
            except Exception as e:
                return json.dumps({"error": str(e)})
        
        @self.server.tool()
        async def play_bot_move(fen: str) -> str:
            """Have the BoT engine play a move.
            
            Args:
                fen: Current position FEN
                
            Returns:
                JSON with the move played and new position
            """
            try:
                board = chess.Board(fen)
                
                # Get BoT's move
                best_move, confidence, votes = self.bot.analyze(board)
                
                # Play the move
                san = board.san(best_move)
                board.push(best_move)
                
                result = {
                    "previous_fen": fen,
                    "move_played": best_move.uci(),
                    "move_san": san,
                    "new_fen": board.fen(),
                    "confidence": confidence,
                    "is_check": board.is_check(),
                    "is_checkmate": board.is_checkmate(),
                    "is_stalemate": board.is_stalemate(),
                    "is_game_over": board.is_game_over()
                }
                
                return json.dumps(result, indent=2)
                
            except Exception as e:
                return json.dumps({"error": str(e)})
    
    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(read_stream, write_stream)


def main():
    """Main entry point."""
    server = BotMCPServer()
    asyncio.run(server.run())


if __name__ == "__main__":
    main()