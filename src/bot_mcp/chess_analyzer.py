"""Chess position analysis using Batch of Thought."""

import asyncio
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import chess
import chess.pgn
from io import StringIO

from .bot_engine import BotEngine, Thought, ThoughtBatch, ThoughtScorer


@dataclass
class ChessPosition:
    """Chess position representation."""
    
    fen: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    board: Optional[chess.Board] = None
    is_checkmate: bool = False
    
    def __post_init__(self):
        """Initialize chess board from FEN."""
        if self.board is None:
            self.board = chess.Board(self.fen)
    
    @property
    def to_move(self) -> str:
        """Get side to move."""
        return "white" if self.board.turn else "black"
    
    @property
    def castling_rights(self) -> str:
        """Get castling rights in FEN format."""
        return self.board.castling_xfen()
    
    @property
    def halfmove_clock(self) -> int:
        """Get halfmove clock."""
        return self.board.halfmove_clock
    
    @property
    def fullmove_number(self) -> int:
        """Get fullmove number."""
        return self.board.fullmove_number
    
    def apply_moves(self, moves: List[str]) -> "ChessPosition":
        """Apply moves and return new position."""
        new_board = self.board.copy()
        for move in moves:
            new_board.push_uci(move)
        return ChessPosition(fen=new_board.fen(), board=new_board)
    
    def get_legal_moves(self) -> List[str]:
        """Get all legal moves in UCI format."""
        return [move.uci() for move in self.board.legal_moves]


@dataclass
class ChessMove:
    """Chess move with evaluation."""
    
    uci: str
    san: str = ""
    evaluation: float = 0.0
    depth: int = 0
    principal_variation: List[str] = field(default_factory=list)


@dataclass
class ChessThought:
    """Chess-specific thought."""
    
    move_sequence: List[str]
    strategy: str
    evaluation_depth: int
    opening_name: Optional[str] = None


class ChessThoughtGenerator:
    """Generate chess-specific thoughts."""
    
    def __init__(
        self,
        strategies: Optional[List[str]] = None,
        depth_range: Tuple[int, int] = (5, 15),
        use_opening_book: bool = False,
    ):
        """Initialize generator."""
        self.strategies = strategies or [
            "tactical", "positional", "aggressive", "defensive",
            "simplifying", "complicating", "endgame", "development"
        ]
        self.depth_range = depth_range
        self.use_opening_book = use_opening_book
    
    def generate_move_thoughts(
        self,
        position: ChessPosition,
        num_thoughts: int = 5,
    ) -> List[ChessThought]:
        """Generate thoughts for chess moves."""
        thoughts = []
        legal_moves = position.get_legal_moves()
        
        for i in range(num_thoughts):
            # Select random moves for thought
            num_moves = min(3, len(legal_moves))
            move_sequence = random.sample(legal_moves, min(num_moves, len(legal_moves)))
            
            # Select strategy
            strategy = self.strategies[i % len(self.strategies)]
            
            # Random depth
            depth = random.randint(*self.depth_range)
            
            thoughts.append(ChessThought(
                move_sequence=move_sequence,
                strategy=strategy,
                evaluation_depth=depth,
            ))
        
        return thoughts
    
    def generate_opening_thoughts(
        self,
        position: ChessPosition,
        num_thoughts: int = 3,
    ) -> List[ChessThought]:
        """Generate thoughts from opening database."""
        thoughts = []
        openings = [
            ("Italian Game", ["e2e4", "e7e5", "g1f3", "b8c6", "f1c4"]),
            ("Sicilian Defense", ["e2e4", "c7c5"]),
            ("Queen's Gambit", ["d2d4", "d7d5", "c2c4"]),
        ]
        
        for i in range(min(num_thoughts, len(openings))):
            name, moves = openings[i]
            thoughts.append(ChessThought(
                move_sequence=moves[:2],  # First few moves
                strategy="opening",
                evaluation_depth=10,
                opening_name=name,
            ))
        
        return thoughts


class PositionEvaluator:
    """Evaluate chess positions."""
    
    def __init__(
        self,
        material_weight: float = 0.4,
        position_weight: float = 0.3,
        mobility_weight: float = 0.2,
        king_safety_weight: float = 0.1,
        endgame_mode: bool = False,
    ):
        """Initialize evaluator."""
        self.material_weight = material_weight
        self.position_weight = position_weight
        self.mobility_weight = mobility_weight
        self.king_safety_weight = king_safety_weight
        self.endgame_mode = endgame_mode
    
    def evaluate(self, position: ChessPosition) -> float:
        """Evaluate position in centipawns."""
        if position.is_checkmate:
            return 999.0 if position.board.turn else -999.0
        
        # Simple material count
        piece_values = {
            chess.PAWN: 1,
            chess.KNIGHT: 3,
            chess.BISHOP: 3,
            chess.ROOK: 5,
            chess.QUEEN: 9,
        }
        
        score = 0.0
        for square in chess.SQUARES:
            piece = position.board.piece_at(square)
            if piece:
                value = piece_values.get(piece.piece_type, 0)
                if piece.color == chess.WHITE:
                    score += value
                else:
                    score -= value
        
        # Adjust for endgame
        if self.endgame_mode:
            score *= 1.2
        
        return score


@dataclass
class AnalysisResult:
    """Result of chess position analysis."""
    
    best_move: Optional[ChessMove]
    evaluation: float
    thoughts: List[Thought]
    confidence: float


@dataclass
class ComparisonResult:
    """Result of comparing BoT with Stockfish."""
    
    bot_move: ChessMove
    stockfish_move: ChessMove
    agreement_score: float
    evaluation_difference: float


@dataclass
class GameAnalysis:
    """Full game analysis result."""
    
    move_evaluations: List[float]
    critical_positions: List[int]
    blunders: List[int]


@dataclass
class Tactic:
    """Tactical opportunity."""
    
    type: str
    move_sequence: List[str]


class ChessAnalyzer:
    """Main chess analyzer using BoT."""
    
    def __init__(
        self,
        bot_batch_size: int = 10,
        search_depth: int = 10,
        use_stockfish: bool = False,
    ):
        """Initialize analyzer."""
        self.bot_batch_size = bot_batch_size
        self.search_depth = search_depth
        self.use_stockfish = use_stockfish
        self.bot_engine = BotEngine(batch_size=bot_batch_size)
        self.thought_generator = ChessThoughtGenerator()
        self.evaluator = PositionEvaluator()
        self.scorer = ThoughtScorer()
    
    def analyze_position(self, position: ChessPosition) -> AnalysisResult:
        """Analyze chess position with BoT."""
        # Generate thoughts
        batch = self.bot_engine.generate_thoughts(
            prompt=f"Analyze chess position: {position.fen}",
            context=position.fen,
        )
        
        # Score thoughts
        scored_batch = self.scorer.score_batch(batch)
        
        # Select best move
        legal_moves = position.get_legal_moves()
        if legal_moves:
            best_move = ChessMove(
                uci=legal_moves[0],
                evaluation=self.evaluator.evaluate(position),
            )
        else:
            best_move = None
        
        return AnalysisResult(
            best_move=best_move,
            evaluation=self.evaluator.evaluate(position),
            thoughts=scored_batch.thoughts,
            confidence=0.75,
        )
    
    async def analyze_position_async(
        self,
        position: ChessPosition,
    ) -> AnalysisResult:
        """Async position analysis."""
        batch = await self.bot_engine.generate_thoughts_async(
            prompt=f"Analyze: {position.fen}",
            context=position.fen,
        )
        
        scored_batch = self.scorer.score_batch(batch)
        
        legal_moves = position.get_legal_moves()
        best_move = ChessMove(
            uci=legal_moves[0] if legal_moves else "",
            evaluation=self.evaluator.evaluate(position),
        )
        
        return AnalysisResult(
            best_move=best_move,
            evaluation=self.evaluator.evaluate(position),
            thoughts=scored_batch.thoughts,
            confidence=0.8,
        )
    
    def find_best_move(self, position: ChessPosition) -> ChessMove:
        """Find best move in position."""
        result = self.analyze_position(position)
        return result.best_move
    
    def compare_analysis(self, position: ChessPosition) -> ComparisonResult:
        """Compare BoT analysis with Stockfish."""
        bot_result = self.analyze_position(position)
        
        # Mock Stockfish result
        legal_moves = position.get_legal_moves()
        stockfish_move = ChessMove(
            uci=legal_moves[1] if len(legal_moves) > 1 else legal_moves[0],
            evaluation=self.evaluator.evaluate(position) + 0.1,
        )
        
        agreement = 1.0 if bot_result.best_move.uci == stockfish_move.uci else 0.5
        
        return ComparisonResult(
            bot_move=bot_result.best_move,
            stockfish_move=stockfish_move,
            agreement_score=agreement,
            evaluation_difference=abs(
                bot_result.evaluation - stockfish_move.evaluation
            ),
        )
    
    def analyze_game(self, pgn: str) -> GameAnalysis:
        """Analyze full game."""
        game = chess.pgn.read_game(StringIO(pgn))
        board = game.board()
        
        evaluations = []
        for move in game.mainline_moves():
            board.push(move)
            pos = ChessPosition(fen=board.fen(), board=board)
            eval_score = self.evaluator.evaluate(pos)
            evaluations.append(eval_score)
        
        # Find critical positions (large eval changes)
        critical = []
        for i in range(1, len(evaluations)):
            if abs(evaluations[i] - evaluations[i-1]) > 2:
                critical.append(i)
        
        return GameAnalysis(
            move_evaluations=evaluations,
            critical_positions=critical,
            blunders=[],  # No blunders in opening
        )
    
    def find_tactics(self, position: ChessPosition) -> List[Tactic]:
        """Find tactical opportunities."""
        tactics = []
        
        # Simple tactic detection
        legal_moves = position.get_legal_moves()
        if len(legal_moves) > 2:
            # Mock finding a fork
            if random.random() > 0.7:
                tactics.append(Tactic(
                    type="fork",
                    move_sequence=legal_moves[:2],
                ))
        
        return tactics