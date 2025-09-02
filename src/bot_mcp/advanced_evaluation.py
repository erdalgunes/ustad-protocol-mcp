"""Advanced chess evaluation system to beat Stockfish 1500 ELO."""

import chess
import asyncio
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from collections import Counter
import concurrent.futures


class PieceSquareTables:
    """Piece-square tables for positional evaluation."""
    
    # Piece-square tables (from white's perspective, rank 8 to rank 1)
    PAWN_TABLE = [
        [ 0,  0,  0,  0,  0,  0,  0,  0],  # Rank 8 (black's back rank)
        [50, 50, 50, 50, 50, 50, 50, 50],  # Rank 7 (promotion imminent!)
        [10, 10, 20, 30, 30, 20, 10, 10],  # Rank 6
        [ 5,  5, 10, 25, 25, 10,  5,  5],  # Rank 5
        [ 0,  0,  0, 20, 20,  0,  0,  0],  # Rank 4
        [ 5, -5,-10,  0,  0,-10, -5,  5],  # Rank 3
        [ 5, 10, 10,-20,-20, 10, 10,  5],  # Rank 2
        [ 0,  0,  0,  0,  0,  0,  0,  0],  # Rank 1 (white's back rank)
    ]
    
    KNIGHT_TABLE = [
        [-50,-40,-30,-30,-30,-30,-40,-50],
        [-40,-20,  0,  0,  0,  0,-20,-40],
        [-30,  0, 10, 15, 15, 10,  0,-30],
        [-30,  5, 15, 20, 20, 15,  5,-30],
        [-30,  0, 15, 20, 20, 15,  0,-30],
        [-30,  5, 10, 15, 15, 10,  5,-30],
        [-40,-20,  0,  5,  5,  0,-20,-40],
        [-50,-40,-30,-30,-30,-30,-40,-50],
    ]
    
    BISHOP_TABLE = [
        [-20,-10,-10,-10,-10,-10,-10,-20],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-10,  0,  5, 10, 10,  5,  0,-10],
        [-10,  5,  5, 10, 10,  5,  5,-10],
        [-10,  0, 10, 10, 10, 10,  0,-10],
        [-10, 10, 10, 10, 10, 10, 10,-10],
        [-10,  5,  0,  0,  0,  0,  5,-10],
        [-20,-10,-10,-10,-10,-10,-10,-20],
    ]
    
    ROOK_TABLE = [
        [ 0,  0,  0,  0,  0,  0,  0,  0],
        [ 5, 10, 10, 10, 10, 10, 10,  5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [-5,  0,  0,  0,  0,  0,  0, -5],
        [ 0,  0,  0,  5,  5,  0,  0,  0],
    ]
    
    QUEEN_TABLE = [
        [-20,-10,-10, -5, -5,-10,-10,-20],
        [-10,  0,  0,  0,  0,  0,  0,-10],
        [-10,  0,  5,  5,  5,  5,  0,-10],
        [ -5,  0,  5,  5,  5,  5,  0, -5],
        [  0,  0,  5,  5,  5,  5,  0, -5],
        [-10,  5,  5,  5,  5,  5,  0,-10],
        [-10,  0,  5,  0,  0,  0,  0,-10],
        [-20,-10,-10, -5, -5,-10,-10,-20],
    ]
    
    KING_MIDDLEGAME_TABLE = [
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-30,-40,-40,-50,-50,-40,-40,-30],
        [-20,-30,-30,-40,-40,-30,-30,-20],
        [-10,-20,-20,-20,-20,-20,-20,-10],
        [ 20, 20,  0,  0,  0,  0, 20, 20],
        [ 20, 30, 10,  0,  0, 10, 30, 20],
    ]
    
    KING_ENDGAME_TABLE = [
        [-50,-40,-30,-20,-20,-30,-40,-50],
        [-30,-20,-10,  0,  0,-10,-20,-30],
        [-30,-10, 20, 30, 30, 20,-10,-30],
        [-30,-10, 30, 40, 40, 30,-10,-30],
        [-30,-10, 30, 40, 40, 30,-10,-30],
        [-30,-10, 20, 30, 30, 20,-10,-30],
        [-30,-30,  0,  0,  0,  0,-30,-30],
        [-50,-30,-30,-30,-30,-30,-30,-50],
    ]
    
    def get_square_value(self, piece_type: int, square: int, color: bool, endgame: bool = False) -> int:
        """Get piece-square table value for a piece on a square."""
        # Get rank and file (0-7)
        rank = chess.square_rank(square)
        file = chess.square_file(square)
        
        # For black pieces, flip the rank
        if not color:
            rank = 7 - rank
        
        # Select appropriate table
        if piece_type == chess.PAWN:
            value = self.PAWN_TABLE[7-rank][file]
        elif piece_type == chess.KNIGHT:
            value = self.KNIGHT_TABLE[7-rank][file]
        elif piece_type == chess.BISHOP:
            value = self.BISHOP_TABLE[7-rank][file]
        elif piece_type == chess.ROOK:
            value = self.ROOK_TABLE[7-rank][file]
        elif piece_type == chess.QUEEN:
            value = self.QUEEN_TABLE[7-rank][file]
        elif piece_type == chess.KING:
            if endgame:
                value = self.KING_ENDGAME_TABLE[7-rank][file]
            else:
                value = self.KING_MIDDLEGAME_TABLE[7-rank][file]
        else:
            value = 0
        
        return value
    
    def evaluate_position(self, board: chess.Board) -> int:
        """Evaluate position using piece-square tables."""
        score = 0
        
        # Determine if endgame (simplified: few pieces left)
        num_pieces = len(board.piece_map())
        endgame = num_pieces < 14
        
        for square, piece in board.piece_map().items():
            pst_value = self.get_square_value(
                piece.piece_type, square, piece.color, endgame
            )
            
            if piece.color == chess.WHITE:
                score += pst_value
            else:
                score -= pst_value
        
        return score


class AdvancedEvaluator:
    """Advanced position evaluator with multiple factors."""
    
    # Standard piece values in centipawns
    PIECE_VALUES = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000,
    }
    
    def __init__(self):
        self.pst = PieceSquareTables()
    
    def evaluate_material(self, board: chess.Board) -> int:
        """Evaluate material balance."""
        score = 0
        for square, piece in board.piece_map().items():
            value = self.PIECE_VALUES[piece.piece_type]
            if piece.color == chess.WHITE:
                score += value
            else:
                score -= value
        return score
    
    def evaluate_mobility(self, board: chess.Board) -> int:
        """Evaluate piece mobility (number of legal moves)."""
        white_mobility = len(list(board.legal_moves)) if board.turn else 0
        
        board.push(chess.Move.null())  # Switch sides
        black_mobility = len(list(board.legal_moves)) if not board.turn else 0
        board.pop()
        
        return (white_mobility - black_mobility) * 2
    
    def evaluate_king_safety(self, board: chess.Board) -> int:
        """Evaluate king safety."""
        score = 0
        
        # Find kings
        white_king = board.king(chess.WHITE)
        black_king = board.king(chess.BLACK)
        
        if white_king:
            # Bonus for castling rights
            if board.has_kingside_castling_rights(chess.WHITE):
                score += 20
            if board.has_queenside_castling_rights(chess.WHITE):
                score += 10
            
            # Penalty for exposed king in center
            if chess.square_file(white_king) in [3, 4] and chess.square_rank(white_king) == 0:
                score -= 30
        
        if black_king:
            if board.has_kingside_castling_rights(chess.BLACK):
                score -= 20
            if board.has_queenside_castling_rights(chess.BLACK):
                score -= 10
            
            if chess.square_file(black_king) in [3, 4] and chess.square_rank(black_king) == 7:
                score += 30
        
        return score
    
    def evaluate_pawn_structure(self, board: chess.Board) -> int:
        """Evaluate pawn structure."""
        score = 0
        
        white_pawns = []
        black_pawns = []
        
        for square, piece in board.piece_map().items():
            if piece.piece_type == chess.PAWN:
                if piece.color == chess.WHITE:
                    white_pawns.append(square)
                else:
                    black_pawns.append(square)
        
        # Penalize doubled pawns
        white_files = [chess.square_file(sq) for sq in white_pawns]
        black_files = [chess.square_file(sq) for sq in black_pawns]
        
        for file in range(8):
            white_count = white_files.count(file)
            black_count = black_files.count(file)
            
            if white_count > 1:
                score -= 10 * (white_count - 1)
            if black_count > 1:
                score += 10 * (black_count - 1)
        
        # Bonus for passed pawns
        for pawn_sq in white_pawns:
            rank = chess.square_rank(pawn_sq)
            file = chess.square_file(pawn_sq)
            
            is_passed = True
            for enemy_sq in black_pawns:
                enemy_rank = chess.square_rank(enemy_sq)
                enemy_file = chess.square_file(enemy_sq)
                
                if enemy_rank <= rank and abs(enemy_file - file) <= 1:
                    is_passed = False
                    break
            
            if is_passed:
                score += 20 + (rank * 10)
        
        return score
    
    def evaluate(self, board: chess.Board) -> float:
        """Combined evaluation of position."""
        if board.is_checkmate():
            return -10000 if board.turn else 10000
        
        if board.is_stalemate() or board.is_insufficient_material():
            return 0
        
        material = self.evaluate_material(board)
        position = self.pst.evaluate_position(board)
        mobility = self.evaluate_mobility(board)
        king_safety = self.evaluate_king_safety(board)
        pawn_structure = self.evaluate_pawn_structure(board)
        
        total = (
            material * 1.0 +
            position * 0.3 +
            mobility * 0.2 +
            king_safety * 0.2 +
            pawn_structure * 0.1
        )
        
        return total


class MinimaxSearcher:
    """Minimax search with alpha-beta pruning."""
    
    def __init__(self, depth: int = 4, use_pruning: bool = True):
        self.depth = depth
        self.use_pruning = use_pruning
        self.evaluator = AdvancedEvaluator()
        self.nodes_searched = 0
    
    def search(self, board: chess.Board) -> Tuple[Optional[chess.Move], float]:
        """Search for best move using minimax."""
        self.nodes_searched = 0
        
        if self.use_pruning:
            return self._minimax_alpha_beta(board, self.depth, -float('inf'), float('inf'), board.turn)
        else:
            return self._minimax(board, self.depth, board.turn)
    
    def search_with_stats(self, board: chess.Board) -> Tuple[Optional[chess.Move], float, int]:
        """Search and return statistics."""
        move, score = self.search(board)
        return move, score, self.nodes_searched
    
    def _minimax(self, board: chess.Board, depth: int, maximizing: bool) -> Tuple[Optional[chess.Move], float]:
        """Basic minimax without pruning."""
        self.nodes_searched += 1
        
        if depth == 0 or board.is_game_over():
            return None, self.evaluator.evaluate(board)
        
        best_move = None
        
        if maximizing:
            max_eval = -float('inf')
            for move in board.legal_moves:
                board.push(move)
                _, eval_score = self._minimax(board, depth - 1, False)
                board.pop()
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
            
            return best_move, max_eval
        else:
            min_eval = float('inf')
            for move in board.legal_moves:
                board.push(move)
                _, eval_score = self._minimax(board, depth - 1, True)
                board.pop()
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
            
            return best_move, min_eval
    
    def _minimax_alpha_beta(self, board: chess.Board, depth: int, alpha: float, beta: float, maximizing: bool) -> Tuple[Optional[chess.Move], float]:
        """Minimax with alpha-beta pruning."""
        self.nodes_searched += 1
        
        if depth == 0 or board.is_game_over():
            return None, self.evaluator.evaluate(board)
        
        best_move = None
        
        if maximizing:
            max_eval = -float('inf')
            for move in board.legal_moves:
                board.push(move)
                _, eval_score = self._minimax_alpha_beta(board, depth - 1, alpha, beta, False)
                board.pop()
                
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                
                alpha = max(alpha, eval_score)
                if self.use_pruning and beta <= alpha:
                    break  # Beta cutoff
            
            return best_move, max_eval
        else:
            min_eval = float('inf')
            for move in board.legal_moves:
                board.push(move)
                _, eval_score = self._minimax_alpha_beta(board, depth - 1, alpha, beta, True)
                board.pop()
                
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                
                beta = min(beta, eval_score)
                if self.use_pruning and beta <= alpha:
                    break  # Alpha cutoff
            
            return best_move, min_eval


@dataclass
class BotEvaluationThread:
    """Single BoT evaluation thread with specific weights."""
    
    name: str
    weights: Dict[str, float]
    depth: int = 3
    
    def evaluate(self, board: chess.Board) -> Tuple[Optional[chess.Move], float]:
        """Evaluate position with this thread's perspective."""
        evaluator = AdvancedEvaluator()
        searcher = MinimaxSearcher(depth=self.depth)
        
        # Custom evaluation based on weights
        # For now, use standard evaluation (can be customized later)
        return searcher.search(board)


class ParallelBotAnalyzer:
    """Parallel BoT analyzer with multiple evaluation threads."""
    
    def __init__(self, num_threads: int = 5, depth: int = 4):
        self.num_threads = num_threads
        self.depth = depth
        
        # Create diverse evaluation threads
        self.threads = [
            BotEvaluationThread("Material", {"material": 0.7, "position": 0.3}, depth),
            BotEvaluationThread("Tactical", {"tactics": 0.6, "material": 0.4}, depth),
            BotEvaluationThread("Positional", {"position": 0.6, "pawn_structure": 0.4}, depth),
            BotEvaluationThread("Safety", {"king_safety": 0.5, "material": 0.5}, depth),
            BotEvaluationThread("Dynamic", {"mobility": 0.5, "tactics": 0.5}, depth),
        ][:num_threads]
    
    def analyze(self, board: chess.Board) -> Tuple[chess.Move, float, Dict[str, int]]:
        """Analyze position with parallel threads and vote on best move."""
        move_votes = Counter()
        move_scores = {}
        
        # Run threads in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = [executor.submit(thread.evaluate, board.copy()) for thread in self.threads]
            
            for future, thread in zip(futures, self.threads):
                move, score = future.result()
                if move:
                    move_votes[move.uci()] += 1
                    if move.uci() not in move_scores or score > move_scores[move.uci()]:
                        move_scores[move.uci()] = score
        
        # Select move with most votes
        if move_votes:
            best_move_uci = move_votes.most_common(1)[0][0]
            best_move = chess.Move.from_uci(best_move_uci)
            confidence = move_votes[best_move_uci] / self.num_threads
            
            return best_move, confidence, dict(move_votes)
        
        # Fallback to first legal move
        return list(board.legal_moves)[0], 0.0, {}
    
    async def analyze_async(self, board: chess.Board) -> Tuple[chess.Move, float, Dict[str, int]]:
        """Async version of analyze."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.analyze, board)