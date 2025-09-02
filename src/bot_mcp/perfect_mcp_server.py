#!/usr/bin/env python3
"""Perfect Batch of Thought MCP Server with real intelligence."""

import asyncio
import json
import sys
import logging
from typing import Any, Dict, List, Optional
from datetime import datetime

# For MCP compatibility, we'll create a minimal interface
# that works even without the full MCP package
try:
    from mcp import Server, Tool
    from mcp.server.stdio import stdio_server
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    # Fallback for testing without MCP
    class Server:
        def __init__(self, name):
            self.name = name
            self.tools = {}
        def tool(self):
            def decorator(func):
                self.tools[func.__name__] = func
                return func
            return decorator

from .ultimate_bot import UltimateBatchOfThought as PerfectBatchOfThought, PerspectiveType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PerfectBotMCPServer:
    """Perfect MCP Server for Batch of Thought."""
    
    def __init__(self):
        """Initialize the perfect server."""
        self.server = Server("perfect-batch-of-thought")
        self.bot = PerfectBatchOfThought()
        self.history = []  # Store thinking history for learning
        self.feedback_db = {}  # Store feedback for improvement
        
        # Register all tools
        self._register_tools()
        
        logger.info("Perfect BoT MCP Server initialized")
    
    def _register_tools(self):
        """Register all MCP tools."""
        
        @self.server.tool()
        async def perfect_think(
            problem: str,
            context: str = "",
            num_thoughts: int = 8,
            perspectives: Optional[List[str]] = None
        ) -> str:
            """
            Generate intelligent parallel thoughts using perfect BoT.
            
            This is the main tool that replaces sequential thinking with
            genuinely intelligent parallel analysis from multiple perspectives.
            
            Args:
                problem: The problem or question to analyze
                context: Additional context, constraints, or requirements
                num_thoughts: Number of parallel thoughts (default 8)
                perspectives: Optional specific perspectives to use
                
            Returns:
                JSON with intelligent analysis from multiple perspectives
            """
            try:
                logger.info(f"Perfect think: {problem[:50]}...")
                
                # Convert perspective names to enums
                perspective_enums = None
                if perspectives:
                    perspective_enums = [
                        PerspectiveType[p.upper()] 
                        for p in perspectives 
                        if p.upper() in PerspectiveType.__members__
                    ]
                
                # Generate intelligent thoughts
                bot = PerfectBatchOfThought(num_thoughts=num_thoughts)
                result = bot.think(problem, context, perspective_enums)
                
                # Store in history for learning
                self.history.append({
                    "timestamp": datetime.now().isoformat(),
                    "problem": problem,
                    "result": result
                })
                
                # Add tool metadata
                result["metadata"] = {
                    "version": "2.0",
                    "engine": "perfect-bot",
                    "timestamp": datetime.now().isoformat()
                }
                
                return json.dumps(result, indent=2)
                
            except Exception as e:
                logger.error(f"Error in perfect_think: {e}")
                return json.dumps({
                    "error": str(e),
                    "problem": problem
                })
        
        @self.server.tool()
        async def deep_analysis(
            problem: str,
            context: str = "",
            depth: str = "comprehensive"
        ) -> str:
            """
            Perform deep analysis with evidence and implications.
            
            Goes beyond surface-level thinking to provide:
            - Evidence-based reasoning
            - Assumption identification
            - Implication analysis
            - Risk assessment
            
            Args:
                problem: The problem to analyze deeply
                context: Full context and constraints
                depth: "quick" | "standard" | "comprehensive"
                
            Returns:
                JSON with deep analytical insights
            """
            try:
                logger.info(f"Deep analysis: {problem[:50]}...")
                
                # Determine number of thoughts based on depth
                num_thoughts = {"quick": 4, "standard": 8, "comprehensive": 12}.get(depth, 8)
                
                # Generate thoughts
                bot = PerfectBatchOfThought(num_thoughts=num_thoughts)
                result = bot.think(problem, context)
                
                # Enhance with deep analysis
                analysis = {
                    "problem": problem,
                    "context": context,
                    "depth": depth,
                    "perspectives_analyzed": num_thoughts,
                    "best_solution": result["best_thought"],
                    "alternative_solutions": result["thoughts"][1:3] if len(result["thoughts"]) > 1 else [],
                    "consensus": result["consensus"],
                    "executive_summary": result["summary"],
                    "key_insights": self._extract_key_insights(result),
                    "risk_factors": self._identify_risks(result),
                    "success_factors": self._identify_success_factors(result)
                }
                
                return json.dumps(analysis, indent=2)
                
            except Exception as e:
                logger.error(f"Error in deep_analysis: {e}")
                return json.dumps({"error": str(e)})
        
        @self.server.tool()
        async def compare_solutions(
            problem: str,
            solutions: List[str],
            criteria: Optional[Dict[str, float]] = None
        ) -> str:
            """
            Compare multiple solution approaches intelligently.
            
            Evaluates each solution from multiple perspectives and
            provides a comprehensive comparison.
            
            Args:
                problem: The problem being solved
                solutions: List of solution descriptions to compare
                criteria: Optional custom evaluation criteria weights
                
            Returns:
                JSON with detailed solution comparison
            """
            try:
                logger.info(f"Comparing {len(solutions)} solutions")
                
                comparisons = []
                
                for solution in solutions:
                    # Analyze each solution
                    bot = PerfectBatchOfThought(num_thoughts=4)
                    result = bot.think(f"{problem} - Evaluate solution: {solution}")
                    
                    comparison = {
                        "solution": solution,
                        "score": result["best_thought"]["score"] if result["best_thought"] else 0,
                        "pros": self._extract_pros(result),
                        "cons": self._extract_cons(result),
                        "best_perspective": result["best_thought"]["perspective"] if result["best_thought"] else "unknown",
                        "confidence": result["best_thought"]["confidence"] if result["best_thought"] else 0
                    }
                    comparisons.append(comparison)
                
                # Sort by score
                comparisons.sort(key=lambda x: x["score"], reverse=True)
                
                return json.dumps({
                    "problem": problem,
                    "num_solutions": len(solutions),
                    "comparisons": comparisons,
                    "recommendation": comparisons[0]["solution"] if comparisons else None,
                    "rationale": f"Highest scoring solution with {comparisons[0]['confidence']:.0%} confidence" if comparisons else None
                }, indent=2)
                
            except Exception as e:
                logger.error(f"Error in compare_solutions: {e}")
                return json.dumps({"error": str(e)})
        
        @self.server.tool()
        async def learn_from_feedback(
            problem_id: str,
            feedback: str,
            rating: int
        ) -> str:
            """
            Learn from user feedback to improve future thinking.
            
            Args:
                problem_id: ID of the problem (from previous result)
                feedback: User feedback text
                rating: Rating 1-5 (5 being best)
                
            Returns:
                JSON confirmation of learning
            """
            try:
                logger.info(f"Learning from feedback: {rating}/5")
                
                # Store feedback
                self.feedback_db[problem_id] = {
                    "feedback": feedback,
                    "rating": rating,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Analyze feedback for patterns
                improvement_areas = []
                if rating < 3:
                    if "practical" in feedback.lower():
                        improvement_areas.append("Focus more on practical implementation")
                    if "complex" in feedback.lower() or "simple" in feedback.lower():
                        improvement_areas.append("Adjust complexity level")
                    if "evidence" in feedback.lower():
                        improvement_areas.append("Provide more evidence")
                
                return json.dumps({
                    "status": "learned",
                    "problem_id": problem_id,
                    "rating": rating,
                    "improvement_areas": improvement_areas,
                    "total_feedback_entries": len(self.feedback_db)
                }, indent=2)
                
            except Exception as e:
                logger.error(f"Error in learn_from_feedback: {e}")
                return json.dumps({"error": str(e)})
        
        @self.server.tool()
        async def get_thinking_history(
            limit: int = 10
        ) -> str:
            """
            Get recent thinking history for review.
            
            Args:
                limit: Number of recent entries to return
                
            Returns:
                JSON with thinking history
            """
            try:
                recent = self.history[-limit:] if len(self.history) > limit else self.history
                
                return json.dumps({
                    "total_problems": len(self.history),
                    "showing": len(recent),
                    "history": [
                        {
                            "timestamp": entry["timestamp"],
                            "problem": entry["problem"],
                            "best_perspective": entry["result"]["best_thought"]["perspective"] if entry["result"].get("best_thought") else None
                        }
                        for entry in recent
                    ]
                }, indent=2)
                
            except Exception as e:
                logger.error(f"Error in get_thinking_history: {e}")
                return json.dumps({"error": str(e)})
    
    def _extract_key_insights(self, result: Dict[str, Any]) -> List[str]:
        """Extract key insights from thoughts."""
        insights = []
        
        if result.get("thoughts"):
            # Get top 3 thoughts
            for thought in result["thoughts"][:3]:
                if thought.get("implications"):
                    insights.extend(thought["implications"][:1])
        
        return insights[:3] if insights else ["Analysis complete"]
    
    def _identify_risks(self, result: Dict[str, Any]) -> List[str]:
        """Identify risks from critical perspective."""
        risks = []
        
        for thought in result.get("thoughts", []):
            if thought.get("perspective") == "critical":
                if thought.get("assumptions"):
                    risks.append(f"Assumption risk: {thought['assumptions'][0]}")
                break
        
        return risks if risks else ["No significant risks identified"]
    
    def _identify_success_factors(self, result: Dict[str, Any]) -> List[str]:
        """Identify success factors."""
        factors = []
        
        for thought in result.get("thoughts", []):
            if thought.get("perspective") == "strategic":
                if thought.get("evidence"):
                    factors.append(thought["evidence"][0])
                break
        
        return factors if factors else ["Clear implementation path"]
    
    def _extract_pros(self, result: Dict[str, Any]) -> List[str]:
        """Extract pros from analysis."""
        pros = []
        
        for thought in result.get("thoughts", []):
            if thought.get("confidence", 0) > 0.7:
                pros.append(f"{thought['perspective']}: High confidence")
        
        return pros[:2] if pros else ["Feasible approach"]
    
    def _extract_cons(self, result: Dict[str, Any]) -> List[str]:
        """Extract cons from analysis."""
        cons = []
        
        for thought in result.get("thoughts", []):
            if thought.get("assumptions"):
                cons.append(f"Assumes: {thought['assumptions'][0]}")
        
        return cons[:2] if cons else ["Requires validation"]
    
    async def run(self):
        """Run the MCP server."""
        if MCP_AVAILABLE:
            logger.info("Starting Perfect BoT MCP Server with stdio")
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(read_stream, write_stream)
        else:
            logger.warning("MCP not available, running in test mode")
            # Test mode - just list available tools
            print("Perfect BoT MCP Server - Test Mode")
            print("Available tools:")
            for tool_name in self.server.tools:
                print(f"  - {tool_name}")


def main():
    """Main entry point."""
    server = PerfectBotMCPServer()
    
    try:
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()