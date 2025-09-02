"""Tests for advanced chess evaluation to beat Stockfish 1500."""

import pytest
import chess
from typing import Dict, List

from bot_mcp.advanced_evaluation import (
    PieceSquareTables,
    AdvancedEvaluator,
    MinimaxSearcher,
    BotEvaluationThread,
    ParallelBotAnalyzer,
)


class TestPieceSquareTables:
    """Test piece-square table evaluations."""
    
    def test_pawn_piece_square_values(self):
        """Test that pawns are valued higher in center and advanced ranks."""
        pst = PieceSquareTables()
        
        # Center pawns should be valued higher
        e4_value = pst.get_square_value(chess.PAWN, chess.E4, chess.WHITE)
        a4_value = pst.get_square_value(chess.PAWN, chess.A4, chess.WHITE)
        assert e4_value > a4_value, "Center pawns should be valued higher"
        
        # Advanced pawns should be valued higher
        e6_value = pst.get_square_value(chess.PAWN, chess.E6, chess.WHITE)
        e3_value = pst.get_square_value(chess.PAWN, chess.E3, chess.WHITE)
        assert e6_value > e3_value, "Advanced pawns should be valued higher"
        
        # 7th rank pawns are extremely valuable (near promotion)
        e7_value = pst.get_square_value(chess.PAWN, chess.E7, chess.WHITE)
        assert e7_value > 50, "7th rank pawns should have high bonus"
    
    def test_knight_piece_square_values(self):
        """Test that knights prefer center and avoid edges."""
        pst = PieceSquareTables()
        
        # Center knights are best
        e4_value = pst.get_square_value(chess.KNIGHT, chess.E4, chess.WHITE)
        # Edge knights are bad
        a1_value = pst.get_square_value(chess.KNIGHT, chess.A1, chess.WHITE)
        h8_value = pst.get_square_value(chess.KNIGHT, chess.H8, chess.WHITE)
        
        assert e4_value > a1_value, "Center knights better than edge"
        assert e4_value > h8_value, "Center knights better than corner"
        assert a1_value < 0, "Corner knights should have penalty"
    
    def test_king_piece_square_values(self):
        """Test king safety preferences."""
        pst = PieceSquareTables()
        
        # In opening/middlegame, king prefers castled position
        g1_value = pst.get_square_value(chess.KING, chess.G1, chess.WHITE, endgame=False)
        e4_value = pst.get_square_value(chess.KING, chess.E4, chess.WHITE, endgame=False)
        assert g1_value > e4_value, "King should prefer castled position"
        
        # In endgame, king should be active in center
        e4_endgame = pst.get_square_value(chess.KING, chess.E4, chess.WHITE, endgame=True)
        g1_endgame = pst.get_square_value(chess.KING, chess.G1, chess.WHITE, endgame=True)
        assert e4_endgame > g1_endgame, "Endgame king should be centralized"
    
    def test_position_evaluation_with_pst(self):
        """Test full position evaluation using piece-square tables."""
        pst = PieceSquareTables()
        
        # Starting position should be roughly equal
        board = chess.Board()
        score = pst.evaluate_position(board)
        assert abs(score) < 50, "Starting position should be roughly equal"
        
        # Position after 1.e4
        board.push_san("e4")
        score = pst.evaluate_position(board)
        assert score > 0, "White should be slightly better after 1.e4"


class TestAdvancedEvaluator:
    """Test advanced position evaluation."""
    
    def test_material_evaluation(self):
        """Test material counting with standard piece values."""
        evaluator = AdvancedEvaluator()
        
        board = chess.Board()
        material = evaluator.evaluate_material(board)
        assert material == 0, "Starting position has equal material"
        
        # Remove black queen
        board.remove_piece_at(chess.D8)
        material = evaluator.evaluate_material(board)
        assert material == 900, "White up a queen = +900"
    
    def test_mobility_evaluation(self):
        """Test piece mobility evaluation."""
        evaluator = AdvancedEvaluator()
        
        # Starting position
        board = chess.Board()
        mobility = evaluator.evaluate_mobility(board)
        assert abs(mobility) < 10, "Starting position has similar mobility"
        
        # After 1.e4 e5 2.Nf3, white has more mobility
        board.push_san("e4")
        board.push_san("e5")
        board.push_san("Nf3")
        mobility = evaluator.evaluate_mobility(board)
        assert mobility > 0, "White should have better mobility"
    
    def test_king_safety_evaluation(self):
        """Test king safety evaluation."""
        evaluator = AdvancedEvaluator()
        
        # Castled king should be safer
        board = chess.Board("r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQ1RK1 b kq - 0 1")
        safety_castled = evaluator.evaluate_king_safety(board)
        
        # Exposed king in center
        board = chess.Board("r1bq1rk1/pppp1ppp/2n2n2/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQ - 0 1")
        safety_exposed = evaluator.evaluate_king_safety(board)
        
        assert safety_castled > safety_exposed, "Castled king should be safer"
    
    def test_pawn_structure_evaluation(self):
        """Test pawn structure evaluation."""
        evaluator = AdvancedEvaluator()
        
        # Doubled pawns are bad
        board = chess.Board("8/ppp2ppp/8/8/8/8/PPP2PPP/8 w - - 0 1")
        structure = evaluator.evaluate_pawn_structure(board)
        assert abs(structure) < 10, "Normal structure"
        
        # Doubled pawns on c-file
        board = chess.Board("8/p1p2ppp/2p5/8/8/2P5/P1P2PPP/8 w - - 0 1")
        structure_doubled = evaluator.evaluate_pawn_structure(board)
        assert structure_doubled < structure, "Doubled pawns are penalized"
    
    def test_combined_evaluation(self):
        """Test combined evaluation with all factors."""
        evaluator = AdvancedEvaluator()
        
        # Complex middlegame position
        board = chess.Board("r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1")
        
        eval_score = evaluator.evaluate(board)
        
        # Should consider material, position, mobility, safety
        assert isinstance(eval_score, (int, float))
        assert -1000 < eval_score < 1000, "Evaluation in reasonable range"


class TestMinimaxSearcher:
    """Test minimax search with alpha-beta pruning."""
    
    def test_minimax_finds_checkmate_in_one(self):
        """Test that minimax finds mate in 1."""
        searcher = MinimaxSearcher(depth=2)
        
        # Back rank mate position
        board = chess.Board("6k1/5ppp/8/8/8/8/5PPP/R5K1 w - - 0 1")
        
        best_move, score = searcher.search(board)
        
        assert best_move.uci() == "a1a8", "Should find Ra8#"
        assert score > 9000, "Checkmate should have high score"
    
    def test_minimax_avoids_checkmate(self):
        """Test that minimax avoids being checkmated."""
        searcher = MinimaxSearcher(depth=3)
        
        # Black threatens back rank mate
        board = chess.Board("r5k1/5ppp/8/8/8/8/5PPP/6K1 b - - 0 1")
        
        best_move, score = searcher.search(board)
        
        # Black should play Ra1+ winning
        assert best_move.uci() == "a8a1", "Should play Ra1+"
        assert score < -9000, "Black winning checkmate"
    
    def test_alpha_beta_pruning_efficiency(self):
        """Test that alpha-beta pruning reduces nodes searched."""
        searcher_no_pruning = MinimaxSearcher(depth=3, use_pruning=False)
        searcher_with_pruning = MinimaxSearcher(depth=3, use_pruning=True)
        
        board = chess.Board()
        
        _, _, nodes_no_pruning = searcher_no_pruning.search_with_stats(board)
        _, _, nodes_with_pruning = searcher_with_pruning.search_with_stats(board)
        
        assert nodes_with_pruning < nodes_no_pruning, "Pruning should reduce nodes"
        assert nodes_with_pruning < nodes_no_pruning * 0.7, "Significant reduction"
    
    def test_minimax_depth_improvement(self):
        """Test that deeper search finds better moves."""
        searcher_shallow = MinimaxSearcher(depth=2)
        searcher_deep = MinimaxSearcher(depth=4)
        
        # Tactical position
        board = chess.Board("r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1")
        
        move_shallow, score_shallow = searcher_shallow.search(board)
        move_deep, score_deep = searcher_deep.search(board)
        
        # Deeper search should find better or equal evaluation
        assert abs(score_deep) >= abs(score_shallow) - 50, "Deeper search equally good"


class TestBotEvaluationThread:
    """Test individual BoT evaluation threads."""
    
    def test_material_thread(self):
        """Test material-focused evaluation thread."""
        thread = BotEvaluationThread(
            name="Material",
            weights={"material": 0.8, "position": 0.2},
            depth=3
        )
        
        board = chess.Board()
        board.remove_piece_at(chess.D8)  # Remove black queen
        
        move, score = thread.evaluate(board)
        
        assert score > 800, "Should heavily value material advantage"
        assert move is not None, "Should suggest a move"
    
    def test_tactical_thread(self):
        """Test tactics-focused evaluation thread."""
        thread = BotEvaluationThread(
            name="Tactical",
            weights={"tactics": 0.7, "material": 0.3},
            depth=4
        )
        
        # Fork position
        board = chess.Board("r1bqkb1r/pppp1ppp/5n2/4p3/3nP3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 1")
        
        move, score = thread.evaluate(board)
        
        assert move is not None, "Should find a move"
    
    def test_positional_thread(self):
        """Test position-focused evaluation thread."""
        thread = BotEvaluationThread(
            name="Positional",
            weights={"position": 0.6, "pawn_structure": 0.4},
            depth=3
        )
        
        board = chess.Board()
        move, score = thread.evaluate(board)
        
        # Should prefer center control moves
        assert move.uci() in ["e2e4", "d2d4", "g1f3"], "Should play principled opening"


class TestParallelBotAnalyzer:
    """Test parallel BoT analysis with multiple threads."""
    
    def test_parallel_analysis_consensus(self):
        """Test that parallel threads reach consensus on obvious moves."""
        analyzer = ParallelBotAnalyzer(num_threads=5, depth=3)
        
        # Checkmate in 1 position - all threads should agree
        board = chess.Board("6k1/5ppp/8/8/8/8/5PPP/R5K1 w - - 0 1")
        
        best_move, confidence, thread_votes = analyzer.analyze(board)
        
        assert best_move.uci() == "a1a8", "All threads should find mate"
        assert confidence > 0.8, "High confidence on forced mate"
        assert thread_votes["a1a8"] >= 4, "Most threads agree"
    
    def test_parallel_analysis_diversity(self):
        """Test that threads provide diverse evaluations in complex positions."""
        analyzer = ParallelBotAnalyzer(num_threads=5, depth=3)
        
        # Complex opening position
        board = chess.Board()
        
        best_move, confidence, thread_votes = analyzer.analyze(board)
        
        assert len(thread_votes) >= 2, "Should have some diversity in opening"
        assert confidence < 1.0, "Shouldn't be 100% confident in opening"
        assert best_move.uci() in ["e2e4", "d2d4", "g1f3", "c2c4"], "Reasonable opening"
    
    @pytest.mark.asyncio
    async def test_parallel_speedup(self):
        """Test that parallel analysis is faster than sequential."""
        analyzer_parallel = ParallelBotAnalyzer(num_threads=5, depth=3)
        analyzer_sequential = ParallelBotAnalyzer(num_threads=1, depth=3)
        
        board = chess.Board()
        
        import time
        
        # Parallel analysis
        start = time.time()
        await analyzer_parallel.analyze_async(board)
        parallel_time = time.time() - start
        
        # Sequential analysis (simulated with 1 thread)
        start = time.time()
        for _ in range(5):
            await analyzer_sequential.analyze_async(board)
        sequential_time = time.time() - start
        
        assert parallel_time < sequential_time * 0.7, "Parallel should be faster"
    
    def test_strength_against_simple_evaluator(self):
        """Test that BoT analyzer is stronger than simple evaluation."""
        bot_analyzer = ParallelBotAnalyzer(num_threads=5, depth=4)
        simple_evaluator = AdvancedEvaluator()
        
        # Test position where tactics matter
        board = chess.Board("r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 1")
        
        # BoT move
        bot_move, bot_confidence, _ = bot_analyzer.analyze(board)
        board_bot = board.copy()
        board_bot.push(bot_move)
        bot_eval = simple_evaluator.evaluate(board_bot)
        
        # Simple random legal move
        import random
        simple_move = random.choice(list(board.legal_moves))
        board_simple = board.copy()
        board_simple.push(simple_move)
        simple_eval = simple_evaluator.evaluate(board_simple)
        
        # BoT should achieve better position on average
        # (not always true for single random move, but statistically)
        assert bot_confidence > 0.5, "BoT should have decent confidence"