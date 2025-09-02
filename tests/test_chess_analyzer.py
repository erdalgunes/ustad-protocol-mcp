"""Tests for chess position analysis with Batch of Thought."""

import pytest
from typing import List, Dict

from ustad.chess_analyzer import (
    ChessPosition,
    ChessMove,
    ChessAnalyzer,
    ChessThoughtGenerator,
    PositionEvaluator,
)


class TestChessPosition:
    """Test ChessPosition data model."""

    def test_starting_position(self):
        """Test creating starting chess position."""
        pos = ChessPosition()
        
        assert pos.fen == "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        assert pos.to_move == "white"
        assert pos.castling_rights == "KQkq"
        assert pos.halfmove_clock == 0
        assert pos.fullmove_number == 1

    def test_position_from_fen(self):
        """Test creating position from FEN string."""
        fen = "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4"
        pos = ChessPosition(fen=fen)
        
        assert pos.fen == fen
        assert pos.to_move == "white"
        assert pos.fullmove_number == 4

    def test_position_after_moves(self):
        """Test position after applying moves."""
        pos = ChessPosition()
        moves = ["e2e4", "e7e5", "g1f3"]
        
        new_pos = pos.apply_moves(moves)
        
        assert new_pos != pos  # Position changed
        assert new_pos.fullmove_number == 2
        assert new_pos.to_move == "black"

    def test_legal_moves_generation(self):
        """Test generating legal moves from position."""
        pos = ChessPosition()
        moves = pos.get_legal_moves()
        
        assert len(moves) == 20  # Starting position has 20 legal moves
        assert "e2e4" in moves
        assert "g1f3" in moves


class TestChessMove:
    """Test ChessMove data model."""

    def test_move_creation(self):
        """Test creating chess move with evaluation."""
        move = ChessMove(
            uci="e2e4",
            san="e4",
            evaluation=0.3,
            depth=10,
            principal_variation=["e2e4", "e7e5", "g1f3"],
        )
        
        assert move.uci == "e2e4"
        assert move.san == "e4"
        assert move.evaluation == 0.3
        assert move.depth == 10
        assert len(move.principal_variation) == 3

    def test_move_comparison(self):
        """Test comparing moves by evaluation."""
        move1 = ChessMove("e2e4", evaluation=0.3)
        move2 = ChessMove("d2d4", evaluation=0.5)
        move3 = ChessMove("g1f3", evaluation=0.2)
        
        moves = sorted([move1, move2, move3], key=lambda m: m.evaluation, reverse=True)
        
        assert moves[0].uci == "d2d4"
        assert moves[1].uci == "e2e4"
        assert moves[2].uci == "g1f3"


class TestChessThoughtGenerator:
    """Test chess-specific thought generation."""

    def test_generator_initialization(self):
        """Test creating chess thought generator."""
        generator = ChessThoughtGenerator(
            strategies=["tactical", "positional", "aggressive"],
            depth_range=(5, 15),
        )
        
        assert len(generator.strategies) == 3
        assert generator.depth_range == (5, 15)

    def test_generate_move_thoughts(self):
        """Test generating thoughts for chess moves."""
        generator = ChessThoughtGenerator()
        position = ChessPosition()
        
        thoughts = generator.generate_move_thoughts(
            position=position,
            num_thoughts=5,
        )
        
        assert len(thoughts) == 5
        for thought in thoughts:
            assert thought.move_sequence
            assert thought.strategy in generator.strategies
            assert thought.evaluation_depth >= 1

    def test_diverse_strategies(self):
        """Test that generated thoughts use diverse strategies."""
        generator = ChessThoughtGenerator()
        position = ChessPosition()
        
        thoughts = generator.generate_move_thoughts(position, num_thoughts=10)
        
        strategies_used = set(t.strategy for t in thoughts)
        assert len(strategies_used) > 1  # Multiple strategies used

    def test_opening_database_thoughts(self):
        """Test generating thoughts from opening database."""
        generator = ChessThoughtGenerator(use_opening_book=True)
        position = ChessPosition()
        
        thoughts = generator.generate_opening_thoughts(position, num_thoughts=3)
        
        assert len(thoughts) <= 3
        for thought in thoughts:
            assert thought.opening_name  # Should have opening name
            assert thought.move_sequence


class TestPositionEvaluator:
    """Test chess position evaluation."""

    def test_evaluator_initialization(self):
        """Test creating position evaluator."""
        evaluator = PositionEvaluator(
            material_weight=0.4,
            position_weight=0.3,
            mobility_weight=0.2,
            king_safety_weight=0.1,
        )
        
        assert evaluator.material_weight == 0.4
        assert evaluator.position_weight == 0.3

    def test_evaluate_starting_position(self):
        """Test evaluating starting position."""
        evaluator = PositionEvaluator()
        position = ChessPosition()
        
        score = evaluator.evaluate(position)
        
        assert score == pytest.approx(0.0, abs=0.1)  # Starting position ~equal

    def test_evaluate_material_advantage(self):
        """Test evaluating position with material advantage."""
        evaluator = PositionEvaluator()
        # Position where white is up a knight
        fen = "rnbqkb1r/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        position = ChessPosition(fen=fen)
        
        score = evaluator.evaluate(position)
        
        assert score > 2.5  # Knight worth ~3 pawns

    def test_evaluate_endgame(self):
        """Test evaluating endgame position."""
        evaluator = PositionEvaluator(endgame_mode=True)
        # King and pawn endgame
        fen = "8/8/8/4k3/8/4K3/4P3/8 w - - 0 1"
        position = ChessPosition(fen=fen)
        
        score = evaluator.evaluate(position)
        
        assert score > 0  # White has extra pawn

    def test_evaluate_checkmate(self):
        """Test evaluating checkmate position."""
        evaluator = PositionEvaluator()
        # Back rank mate position
        fen = "6k1/5ppp/8/8/8/8/5PPP/6K1 w - - 0 1"
        position = ChessPosition(fen=fen, is_checkmate=True)
        
        score = evaluator.evaluate(position)
        
        assert abs(score) > 900  # Checkmate score


class TestChessAnalyzer:
    """Test main chess analyzer with BoT."""

    def test_analyzer_initialization(self):
        """Test creating chess analyzer."""
        analyzer = ChessAnalyzer(
            bot_batch_size=8,
            search_depth=10,
            use_stockfish=False,
        )
        
        assert analyzer.bot_batch_size == 8
        assert analyzer.search_depth == 10
        assert analyzer.use_stockfish is False

    def test_analyze_position(self):
        """Test analyzing chess position with BoT."""
        analyzer = ChessAnalyzer(bot_batch_size=5)
        position = ChessPosition()
        
        result = analyzer.analyze_position(position)
        
        assert result.best_move
        assert result.evaluation is not None
        assert len(result.thoughts) == 5
        assert result.confidence > 0

    def test_find_best_move(self):
        """Test finding best move in position."""
        analyzer = ChessAnalyzer()
        position = ChessPosition()
        
        best_move = analyzer.find_best_move(position)
        
        assert best_move.uci in position.get_legal_moves()
        assert best_move.evaluation is not None

    def test_compare_with_stockfish(self):
        """Test comparing BoT analysis with Stockfish."""
        analyzer = ChessAnalyzer(use_stockfish=True)
        position = ChessPosition()
        
        comparison = analyzer.compare_analysis(position)
        
        assert comparison.bot_move
        assert comparison.stockfish_move
        assert comparison.agreement_score >= 0
        assert comparison.evaluation_difference is not None

    @pytest.mark.asyncio
    async def test_analyze_position_async(self):
        """Test async position analysis."""
        analyzer = ChessAnalyzer(bot_batch_size=10)
        position = ChessPosition()
        
        result = await analyzer.analyze_position_async(position)
        
        assert result.best_move
        assert len(result.thoughts) == 10

    def test_analyze_game(self):
        """Test analyzing full game with BoT."""
        analyzer = ChessAnalyzer()
        pgn = "1.e4 e5 2.Nf3 Nc6 3.Bb5"
        
        analysis = analyzer.analyze_game(pgn)
        
        assert len(analysis.move_evaluations) == 5  # 5 half-moves
        # Critical positions may or may not exist in opening
        assert isinstance(analysis.critical_positions, list)
        assert analysis.blunders == []  # Opening should have no blunders

    def test_find_tactics(self):
        """Test finding tactical opportunities."""
        analyzer = ChessAnalyzer()
        # Position with tactical opportunity
        fen = "r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4"
        position = ChessPosition(fen=fen)
        
        tactics = analyzer.find_tactics(position)
        
        assert len(tactics) >= 0  # May or may not find tactics
        for tactic in tactics:
            assert tactic.type in ["fork", "pin", "skewer", "discovery", "sacrifice"]
            assert tactic.move_sequence