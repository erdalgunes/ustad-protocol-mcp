#!/usr/bin/env python3
"""Generic Batch of Thought MCP Server for the Quetiapine Protocol."""

import asyncio
import json

from mcp import Server
from mcp.server.stdio import stdio_server

from .generic_bot import BatchOfThought, ThoughtGenerator, ThoughtScorer


class BotMCPServer:
    """MCP Server for generic Batch of Thought analysis."""

    def __init__(self):
        self.server = Server("batch-of-thought")
        self.bot = BatchOfThought(num_thoughts=8, parallel=True)

        # Register tools
        self._register_tools()

    def _register_tools(self):
        """Register all available tools."""

        @self.server.tool()
        async def batch_think(
            problem: str,
            context: str = "",
            num_thoughts: int = 8,
            perspectives: list[str] | None = None,
        ) -> str:
            """Generate a batch of thoughts for any problem.

            This replaces sequential thinking with parallel thought generation
            from multiple perspectives, as per the Quetiapine Protocol.

            Args:
                problem: The problem or question to think about
                context: Additional context or constraints
                num_thoughts: Number of parallel thoughts to generate (default 8)
                perspectives: Optional list of specific perspectives to use

            Returns:
                JSON string with thought batch analysis
            """
            try:
                # Configure perspectives if specified
                if perspectives:
                    available = {p["name"]: p for p in ThoughtGenerator.PERSPECTIVES}
                    selected = [available.get(p, available["Analytical"]) for p in perspectives]
                    bot = BatchOfThought(
                        num_thoughts=num_thoughts, perspectives=selected, parallel=True
                    )
                else:
                    bot = BatchOfThought(num_thoughts=num_thoughts, parallel=True)

                # Generate thoughts
                batch = bot.think(problem, context)

                # Prepare response
                result = {
                    "problem": problem,
                    "context": context,
                    "num_thoughts": len(batch.thoughts),
                    "thoughts": [
                        {
                            "content": t.content,
                            "perspective": t.perspective,
                            "confidence": t.confidence,
                            "score": t.score,
                            "reasoning": t.reasoning,
                        }
                        for t in sorted(batch.thoughts, key=lambda x: x.score or 0, reverse=True)
                    ],
                    "best_thought": {
                        "content": batch.best_thought.content,
                        "perspective": batch.best_thought.perspective,
                        "score": batch.best_thought.score,
                        "reasoning": batch.best_thought.reasoning,
                    }
                    if batch.best_thought
                    else None,
                    "consensus": batch.consensus,
                }

                return json.dumps(result, indent=2)

            except Exception as e:
                return json.dumps({"error": str(e)})

        @self.server.tool()
        async def iterative_think(
            problem: str,
            context: str = "",
            max_iterations: int = 3,
            convergence_threshold: float = 0.8,
        ) -> str:
            """Think iteratively about a problem, refining thoughts.

            Each iteration builds on insights from the previous one,
            continuing until convergence or max iterations.

            Args:
                problem: The problem to solve
                context: Initial context
                max_iterations: Maximum thinking iterations (default 3)
                convergence_threshold: Score threshold for convergence (default 0.8)

            Returns:
                JSON string with all iteration results
            """
            try:
                bot = BatchOfThought(parallel=True)
                batches = bot.think_iteratively(
                    problem, context, max_iterations, convergence_threshold
                )

                result = {
                    "problem": problem,
                    "initial_context": context,
                    "num_iterations": len(batches),
                    "iterations": [],
                }

                for i, batch in enumerate(batches):
                    iteration_data = {
                        "iteration": i + 1,
                        "num_thoughts": len(batch.thoughts),
                        "best_thought": {
                            "content": batch.best_thought.content,
                            "perspective": batch.best_thought.perspective,
                            "score": batch.best_thought.score,
                        }
                        if batch.best_thought
                        else None,
                        "consensus": batch.consensus,
                        "converged": batch.best_thought.score >= convergence_threshold
                        if batch.best_thought and batch.best_thought.score
                        else False,
                    }
                    result["iterations"].append(iteration_data)

                # Final recommendation
                if batches:
                    final_batch = batches[-1]
                    if final_batch.best_thought:
                        result["final_recommendation"] = {
                            "content": final_batch.best_thought.content,
                            "confidence": final_batch.best_thought.confidence,
                            "reasoning": final_batch.best_thought.reasoning,
                        }

                return json.dumps(result, indent=2)

            except Exception as e:
                return json.dumps({"error": str(e)})

        @self.server.tool()
        async def compare_perspectives(
            problem: str, perspectives: list[str], context: str = ""
        ) -> str:
            """Compare different thinking perspectives on a problem.

            Useful for understanding how different approaches would
            tackle the same problem.

            Args:
                problem: The problem to analyze
                perspectives: List of perspective names to compare
                context: Additional context

            Returns:
                JSON string with perspective comparison
            """
            try:
                generator = ThoughtGenerator()
                scorer = ThoughtScorer()

                results = []
                all_perspectives = {p["name"]: p for p in ThoughtGenerator.PERSPECTIVES}

                for perspective_name in perspectives:
                    if perspective_name in all_perspectives:
                        perspective = all_perspectives[perspective_name]
                        thought = generator.generate_thought(problem, context, perspective, 0)
                        score = scorer.score_thought(thought, problem)

                        results.append(
                            {
                                "perspective": perspective_name,
                                "approach": perspective["approach"],
                                "focus": perspective["focus"],
                                "thought": thought.content,
                                "reasoning": thought.reasoning,
                                "confidence": thought.confidence,
                                "score": score,
                            }
                        )

                # Sort by score
                results.sort(key=lambda x: x["score"], reverse=True)

                response = {
                    "problem": problem,
                    "context": context,
                    "num_perspectives": len(results),
                    "perspectives": results,
                    "best_perspective": results[0]["perspective"] if results else None,
                }

                return json.dumps(response, indent=2)

            except Exception as e:
                return json.dumps({"error": str(e)})

        @self.server.tool()
        async def get_perspectives() -> str:
            """Get list of all available thinking perspectives.

            Returns:
                JSON string with all perspective details
            """
            try:
                perspectives = [
                    {"name": p["name"], "approach": p["approach"], "focus": p["focus"]}
                    for p in ThoughtGenerator.PERSPECTIVES
                ]

                return json.dumps(
                    {"num_perspectives": len(perspectives), "perspectives": perspectives}, indent=2
                )

            except Exception as e:
                return json.dumps({"error": str(e)})

        @self.server.tool()
        async def custom_scored_think(
            problem: str, context: str = "", scoring_criteria: dict[str, float] | None = None
        ) -> str:
            """Think about a problem with custom scoring criteria.

            Allows you to weight different aspects of thought quality
            according to your specific needs.

            Args:
                problem: The problem to think about
                context: Additional context
                scoring_criteria: Dict of criteria weights (must sum to 1.0)
                    Default: relevance=0.3, coherence=0.2, depth=0.2,
                            practicality=0.15, innovation=0.15

            Returns:
                JSON string with scored thoughts
            """
            try:
                # Validate scoring criteria
                if scoring_criteria:
                    total = sum(scoring_criteria.values())
                    if abs(total - 1.0) > 0.01:
                        return json.dumps(
                            {"error": f"Scoring criteria weights must sum to 1.0 (got {total})"}
                        )
                    scorer = ThoughtScorer(scoring_criteria)
                else:
                    scorer = ThoughtScorer()

                bot = BatchOfThought(scorer=scorer, parallel=True)
                batch = bot.think(problem, context)

                result = {
                    "problem": problem,
                    "context": context,
                    "scoring_criteria": scoring_criteria or scorer.criteria,
                    "thoughts": [
                        {
                            "content": t.content,
                            "perspective": t.perspective,
                            "score": t.score,
                            "score_breakdown": {
                                "relevance": t.metadata.get("score_relevance", 0),
                                "coherence": t.metadata.get("score_coherence", 0),
                                "depth": t.metadata.get("score_depth", 0),
                                "practicality": t.metadata.get("score_practicality", 0),
                                "innovation": t.metadata.get("score_innovation", 0),
                            },
                        }
                        for t in sorted(batch.thoughts, key=lambda x: x.score or 0, reverse=True)
                    ],
                    "best_thought": batch.best_thought.to_dict() if batch.best_thought else None,
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
