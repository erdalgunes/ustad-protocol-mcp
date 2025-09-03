"""Performance benchmarks for Ustad Protocol MCP Server.

Run with: pytest tests/test_benchmark.py::TestPerformanceBenchmarks -v
Note: Requires pytest-benchmark to be installed
"""

import pytest

pytest_plugins = ["pytest_benchmark"]  # Ensure benchmark plugin is loaded

from src.sequential_thinking import SequentialThinkingServer


class TestPerformanceBenchmarks:
    """Performance benchmarks for critical operations."""

    def test_benchmark_single_thought_processing(self, benchmark):
        """Benchmark processing a single thought."""
        server = SequentialThinkingServer()

        def process_single_thought():
            return server.process_thought(
                {
                    "thought": "This is a test thought for benchmarking",
                    "thoughtNumber": 1,
                    "totalThoughts": 5,
                    "nextThoughtNeeded": True,
                }
            )

        result = benchmark(process_single_thought)
        assert result["thoughtNumber"] == 1

    def test_benchmark_thought_chain(self, benchmark):
        """Benchmark processing a chain of thoughts."""
        server = SequentialThinkingServer()

        def process_thought_chain():
            results = []
            for i in range(1, 11):
                result = server.process_thought(
                    {
                        "thought": f"Thought {i} in chain",
                        "thoughtNumber": i,
                        "totalThoughts": 10,
                        "nextThoughtNeeded": i < 10,
                    }
                )
                results.append(result)
            return results

        results = benchmark(process_thought_chain)
        assert len(results) == 10
        assert results[-1]["nextThoughtNeeded"] is False

    def test_benchmark_thought_with_revision(self, benchmark):
        """Benchmark thought processing with revisions."""
        server = SequentialThinkingServer()

        def process_with_revision():
            # First thought
            server.process_thought(
                {
                    "thought": "Initial thought",
                    "thoughtNumber": 1,
                    "totalThoughts": 3,
                    "nextThoughtNeeded": True,
                }
            )

            # Revision
            return server.process_thought(
                {
                    "thought": "Revised thought",
                    "thoughtNumber": 2,
                    "totalThoughts": 3,
                    "nextThoughtNeeded": True,
                    "isRevision": True,
                    "revisesThought": 1,
                }
            )

        result = benchmark(process_with_revision)
        assert result["isRevision"] is True

    def test_benchmark_branching(self, benchmark):
        """Benchmark branching operations."""
        server = SequentialThinkingServer()

        def process_with_branching():
            # Main branch
            server.process_thought(
                {
                    "thought": "Main branch",
                    "thoughtNumber": 1,
                    "totalThoughts": 5,
                    "nextThoughtNeeded": True,
                }
            )

            # Create branches
            results = []
            for branch_id in ["alpha", "beta", "gamma"]:
                result = server.process_thought(
                    {
                        "thought": f"Branch {branch_id}",
                        "thoughtNumber": 2,
                        "totalThoughts": 5,
                        "nextThoughtNeeded": True,
                        "branchFromThought": 1,
                        "branchId": branch_id,
                    }
                )
                results.append(result)
            return results

        results = benchmark(process_with_branching)
        assert len(results) == 3

    def test_benchmark_large_thought_history(self, benchmark):
        """Benchmark performance with large thought history."""
        server = SequentialThinkingServer()

        # Pre-populate with many thoughts
        for i in range(1, 101):
            server.process_thought(
                {
                    "thought": f"Thought {i}",
                    "thoughtNumber": i,
                    "totalThoughts": 100,
                    "nextThoughtNeeded": True,
                }
            )

        def process_with_large_history():
            return server.get_summary()

        summary = benchmark(process_with_large_history)
        assert summary["total_thoughts"] == 100

    def test_benchmark_exception_handling(self, benchmark):
        """Benchmark error path performance."""
        from src.exceptions import ThoughtValidationError

        server = SequentialThinkingServer()

        def process_invalid_thought():
            try:
                server.process_thought(
                    {
                        "thought": "",  # Invalid: empty thought
                        "thoughtNumber": 1,
                        "totalThoughts": 5,
                        "nextThoughtNeeded": True,
                    }
                )
            except ThoughtValidationError as e:
                return e.to_dict()
            return None

        result = benchmark(process_invalid_thought)
        assert result is not None
        assert "error" in result

    @pytest.mark.parametrize("num_thoughts", [10, 25, 50])
    def test_benchmark_scaling(self, benchmark, num_thoughts):
        """Benchmark how performance scales with number of thoughts."""
        server = SequentialThinkingServer()

        def process_n_thoughts():
            for i in range(1, num_thoughts + 1):
                server.process_thought(
                    {
                        "thought": f"Thought {i} of {num_thoughts}",
                        "thoughtNumber": i,
                        "totalThoughts": num_thoughts,
                        "nextThoughtNeeded": i < num_thoughts,
                    }
                )
            return server.get_thought_history()

        history = benchmark(process_n_thoughts)
        assert len(history) == num_thoughts


class TestMemoryBenchmarks:
    """Memory usage benchmarks."""

    def test_memory_usage_thought_history(self, benchmark):
        """Benchmark memory usage as thought history grows."""
        import sys

        def measure_memory():
            server = SequentialThinkingServer()
            sizes = []

            for i in range(1, 101):
                server.process_thought(
                    {
                        "thought": "x" * 100,  # 100 char thought
                        "thoughtNumber": i,
                        "totalThoughts": 100,
                        "nextThoughtNeeded": True,
                    }
                )

                if i % 25 == 0:
                    # Measure size every 50 thoughts
                    size = sys.getsizeof(server.thought_history)
                    sizes.append((i, size))

            return sizes

        sizes = benchmark(measure_memory)
        # Verify memory grows linearly, not exponentially
        assert len(sizes) > 0
        if len(sizes) >= 2:
            # Check that growth is reasonable
            growth_rate = sizes[-1][1] / sizes[0][1]
            assert growth_rate < 20  # Should grow less than 20x for 10x thoughts
