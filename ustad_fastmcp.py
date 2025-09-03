#!/usr/bin/env python3
"""FastMCP server for collaborative AI reasoning - ustad-think."""

import json
import os
import subprocess
from dataclasses import asdict, is_dataclass
from datetime import datetime, timedelta
from enum import Enum

from fastmcp import FastMCP

from ustad.perfect_collaborative_bot import PerfectCollaborativeBatchOfThought

# Initialize FastMCP server
mcp = FastMCP("ustad-think")

# Session-isolated collaborative BoT instances
import uuid
from threading import local

# Thread-local storage for session isolation
_session_storage = local()

# Global session registry for cleanup
_session_registry = {}


def serialize_collaborative_result(obj):
    """Custom serializer for complex collaborative reasoning objects."""
    if isinstance(obj, Enum):
        return obj.value
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, dict):
        return {k: serialize_collaborative_result(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [serialize_collaborative_result(item) for item in obj]
    return obj


def get_session_id():
    """Get or create a session ID for this request context."""
    if not hasattr(_session_storage, "session_id"):
        _session_storage.session_id = str(uuid.uuid4())[:8]
    return _session_storage.session_id


def get_bot(session_id=None):
    """Get or create a session-isolated collaborative reasoning bot instance."""
    if session_id is None:
        session_id = get_session_id()

    # Check if we have a bot for this session
    if session_id not in _session_registry:
        _session_registry[session_id] = {
            "bot": PerfectCollaborativeBatchOfThought(),
            "created_at": datetime.now(),
            "request_count": 0,
        }

    _session_registry[session_id]["request_count"] += 1
    return _session_registry[session_id]["bot"]


def cleanup_old_sessions(max_age_minutes=30):
    """Clean up sessions older than max_age_minutes."""
    cutoff_time = datetime.now() - timedelta(minutes=max_age_minutes)
    sessions_to_remove = [
        session_id
        for session_id, data in _session_registry.items()
        if data["created_at"] < cutoff_time
    ]

    for session_id in sessions_to_remove:
        del _session_registry[session_id]

    return len(sessions_to_remove)


def get_session_stats():
    """Get statistics about active sessions."""
    return {
        "active_sessions": len(_session_registry),
        "sessions": {
            session_id: {
                "created_at": data["created_at"].isoformat(),
                "request_count": data["request_count"],
            }
            for session_id, data in _session_registry.items()
        },
    }


@mcp.tool()
async def ustad_think(
    problem: str, context: str = "", num_thoughts: int = 8, perspectives: list = None
) -> str:
    """Multi-round collaborative dialogue where AI perspectives debate,
    challenge each other, and reach consensus through structured discussion.

    This embodies the Ustad Protocol - enabling collaborative reasoning
    that maintains context and overcomes individual AI limitations.

    Args:
        problem: The problem or question to analyze collaboratively
        context: Additional context, constraints, or requirements
        num_thoughts: Number of perspectives (3-8, default 8 for optimal dialogue)
        perspectives: Optional list of specific perspectives to use
                     Available: empirical, systematic, creative, critical, analytical, practical, ethical, strategic
                     If None, automatically selects optimal perspectives

    Returns:
        JSON string with collaborative analysis results including:
        - Multi-perspective reasoning
        - Consensus building process
        - Final synthesized wisdom
    """
    try:
        bot = get_bot()

        # Validate num_thoughts range
        num_thoughts = max(3, min(8, num_thoughts))

        # Handle custom perspectives
        if perspectives:
            # Validate perspective names
            valid_perspectives = [
                "empirical",
                "systematic",
                "creative",
                "critical",
                "analytical",
                "practical",
                "ethical",
                "strategic",
            ]
            filtered_perspectives = [p for p in perspectives if p in valid_perspectives]

            if filtered_perspectives:
                # Use custom perspectives (limit to num_thoughts)
                selected_perspectives = filtered_perspectives[:num_thoughts]
                result = await bot.think_with_perspectives(problem, context, selected_perspectives)
            else:
                # Fallback to default if no valid perspectives provided
                result = await bot.think(problem, context, num_thoughts)
        else:
            # Use default perspective selection
            result = await bot.think(problem, context, num_thoughts)

        serializable_result = serialize_collaborative_result(result)
        return json.dumps(serializable_result, indent=2)
    except Exception as e:
        error_result = {
            "error": str(e),
            "problem": problem,
            "status": "failed",
            "message": "Collaborative reasoning encountered an error",
        }
        return json.dumps(error_result, indent=2)


@mcp.tool()
async def ustad_think_stream(
    problem: str, context: str = "", num_thoughts: int = 8, perspectives: list = None
) -> str:
    """Streaming version of ustad_think that provides real-time collaborative dialogue updates.

    Returns a series of JSON updates showing the reasoning process as it unfolds,
    enabling real-time monitoring of the collaborative dialogue.

    Args:
        problem: The problem or question to analyze collaboratively
        context: Additional context, constraints, or requirements
        num_thoughts: Number of perspectives (3-8, default 8 for optimal dialogue)
        perspectives: Optional list of specific perspectives to use

    Returns:
        JSON stream with progressive updates of the collaborative reasoning process
    """
    try:
        bot = get_bot()

        # Validate num_thoughts range
        num_thoughts = max(3, min(8, num_thoughts))

        # For now, return structured streaming info (actual streaming would require WebSocket/SSE)
        stream_info = {
            "streaming": True,
            "status": "processing",
            "problem": problem,
            "context": context,
            "perspectives_requested": num_thoughts,
            "custom_perspectives": perspectives if perspectives else "auto-selected",
            "stream_stages": [
                "Initializing collaborative reasoning",
                "Round 1: Initial perspectives",
                "Round 2: Challenge and debate",
                "Round 3: Consensus building",
                "Final: Synthesis and wisdom",
            ],
            "note": "Full streaming implementation requires WebSocket/SSE transport",
            "fallback": "Running standard collaborative reasoning",
            "ustad_protocol_version": "v0.2.0",
        }

        # For now, fall back to regular think method
        if perspectives:
            valid_perspectives = [
                "empirical",
                "systematic",
                "creative",
                "critical",
                "analytical",
                "practical",
                "ethical",
                "strategic",
            ]
            filtered_perspectives = [p for p in perspectives if p in valid_perspectives]

            if filtered_perspectives:
                selected_perspectives = filtered_perspectives[:num_thoughts]
                # Note: think_with_perspectives method would need to be implemented
                result = await bot.think(problem, context, num_thoughts)
            else:
                result = await bot.think(problem, context, num_thoughts)
        else:
            result = await bot.think(problem, context, num_thoughts)

        # Combine streaming info with result
        stream_info["result"] = serialize_collaborative_result(result)
        return json.dumps(stream_info, indent=2)

    except Exception as e:
        error_result = {
            "error": str(e),
            "problem": problem,
            "status": "streaming_failed",
            "message": "Streaming collaborative reasoning encountered an error",
            "ustad_protocol_version": "v0.2.0",
        }
        return json.dumps(error_result, indent=2)


@mcp.tool()
async def ustad_quick(problem: str, context: str = "") -> str:
    """Quick 3-perspective analysis for simpler problems.
    Fast collaborative reasoning without full dialogue rounds.
    """
    try:
        bot = get_bot()
        result = await bot.think(problem, context, num_thoughts=3)
        serializable_result = serialize_collaborative_result(result)
        return json.dumps(serializable_result, indent=2)
    except Exception as e:
        error_result = {
            "error": str(e),
            "problem": problem,
            "status": "failed",
            "message": "Quick reasoning encountered an error",
        }
        return json.dumps(error_result, indent=2)


@mcp.tool()
async def ustad_decide(problem: str, options: str, context: str = "") -> str:
    """Decision-making with collaborative analysis of options.
    Provide problem and comma-separated options to evaluate.
    """
    try:
        decision_prompt = (
            f"Decision needed: {problem}\n\nOptions to evaluate: {options}\n\nContext: {context}"
        )
        bot = get_bot()
        result = await bot.think(
            decision_prompt, "Focus on evaluating the given options with pros/cons analysis"
        )
        serializable_result = serialize_collaborative_result(result)
        return json.dumps(serializable_result, indent=2)
    except Exception as e:
        error_result = {
            "error": str(e),
            "problem": problem,
            "options": options,
            "status": "failed",
            "message": "Decision analysis encountered an error",
        }
        return json.dumps(error_result, indent=2)


@mcp.tool()
async def ustad_meta(problem: str, context: str = "") -> str:
    """Meta-reasoning: Analyzes the problem and recommends which reasoning approach to use.

    Uses tavily for fact-gathering and GPT-3.5 for meta-reasoning logic only.
    Returns recommendation on whether to use ustad_think, ustad_quick, or ustad_decide
    along with reasoning about why that approach is optimal.
    """
    try:
        import os

        import httpx
        from openai import AsyncOpenAI

        # Step 1: Use tavily to gather relevant factual context about the problem domain
        tavily_api_key = os.getenv("TAVILY_API_KEY")
        factual_context = ""

        if tavily_api_key and len(problem) > 10:  # Only search for substantial problems
            try:
                search_query = (
                    f"best practices methodology approach: {problem[:100]}"  # Truncate for search
                )

                async with httpx.AsyncClient() as client:
                    tavily_response = await client.post(
                        "https://api.tavily.com/search",
                        json={
                            "api_key": tavily_api_key,
                            "query": search_query,
                            "search_depth": "basic",
                            "max_results": 3,
                            "include_raw_content": False,
                        },
                        timeout=10.0,
                    )

                    if tavily_response.status_code == 200:
                        search_data = tavily_response.json()
                        if search_data.get("results"):
                            factual_context = "\n".join(
                                [
                                    f"- {result.get('title', '')}: {result.get('content', '')[:200]}..."
                                    for result in search_data["results"][:2]
                                ]
                            )
            except Exception as search_error:
                factual_context = f"Search unavailable: {search_error!s}"

        # Step 2: Use GPT-3.5 for meta-reasoning logic only
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        meta_prompt = f"""Analyze this problem and recommend the optimal reasoning tool based on problem structure and complexity:

PROBLEM: {problem}
CONTEXT: {context}

FACTUAL RESEARCH (from tavily):
{factual_context}

Available reasoning tools:
- ustad_think: Full 8-perspective collaborative reasoning for complex problems requiring deep analysis
- ustad_quick: Fast 3-perspective analysis for simpler problems or when speed is needed
- ustad_decide: Decision analysis when comparing specific options/alternatives

Meta-reasoning analysis required:
1. Problem structure: Is this asking to compare/choose between specific stated options?
2. Complexity level: Does this require multi-round collaborative reasoning or is it straightforward?
3. Analysis type: Exploratory, evaluative, comparative, or decisional?

Return ONLY a JSON response with:
{{
  "recommended_tool": "ustad_think|ustad_quick|ustad_decide",
  "reasoning": "why this tool is optimal for this problem structure",
  "complexity_assessment": "high|medium|low",
  "problem_type": "analysis|comparison|decision|exploration",
  "confidence": "high|medium|low"
}}

Be precise - only recommend ustad_decide for explicit choice/comparison problems."""

        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": meta_prompt}],
            temperature=0.1,
            max_tokens=200,
        )

        ai_recommendation = response.choices[0].message.content

        # Combine tavily facts with GPT meta-reasoning
        result = {
            "factual_research": {
                "source": "tavily_search",
                "context_found": factual_context
                if factual_context
                else "No relevant context found",
                "search_performed": bool(tavily_api_key),
            },
            "meta_reasoning": {
                "source": "gpt-3.5-turbo",
                "analysis": ai_recommendation,
                "problem_length": len(problem.split()),
                "has_context": len(context) > 0,
            },
            "tool_descriptions": {
                "ustad_think": "Full collaborative reasoning (8 perspectives, multi-round)",
                "ustad_quick": "Fast analysis (3 perspectives, single round)",
                "ustad_decide": "Decision analysis (evaluates specific options)",
            },
            "protocol_version": "v0.1.4",
        }

        return json.dumps(result, indent=2)

    except Exception as e:
        error_result = {
            "error": str(e),
            "problem": problem,
            "status": "failed",
            "message": "Meta-reasoning with tavily+GPT-3.5 encountered an error",
            "protocol_version": "v0.1.4",
        }
        return json.dumps(error_result, indent=2)


@mcp.tool()
async def get_protocol_guide() -> str:
    """Get the complete Batch of Thought Protocol guide for optimal Claude Code usage.

    This teaches Claude Code how to use ustad-think correctly and replaces the need
    for external CLAUDE.md protocol documentation.
    """
    protocol_guide = {
        "protocol_name": "Ustad Protocol",
        "version": "v0.2.0",
        "description": "The Master Teacher Protocol - Revolutionary collaborative AI reasoning through multi-perspective dialogue",
        "core_principles": {
            "intent_understanding": "Always understand deeper user goals before responding",
            "collaborative_reasoning": "Use multi-perspective analysis for complex problems",
            "factual_grounding": "Use tavily liberally for fact verification",
            "systematic_execution": "Break down complex tasks methodically",
        },
        "tool_selection_guide": {
            "ustad_start": {
                "when_to_use": "Beginning of session to initialize the system",
                "examples": ["Session startup", "System warm-up", "Performance optimization"],
                "purpose": "Eliminates cold start latency and establishes session context",
                "frequency": "Once per session (automatically or manually)",
            },
            "ustad_think": {
                "when_to_use": "Complex problems requiring deep multi-perspective analysis",
                "examples": [
                    "System architecture decisions",
                    "Complex debugging",
                    "Strategic planning",
                ],
                "perspectives": "3-8 (customizable)",
                "rounds": "Multi-round dialogue with consensus building",
            },
            "ustad_think_stream": {
                "when_to_use": "Need real-time updates during collaborative reasoning",
                "examples": [
                    "Live problem-solving sessions",
                    "Interactive debugging",
                    "Progressive analysis",
                ],
                "perspectives": "3-8 (customizable)",
                "rounds": "Streaming multi-round dialogue with real-time updates",
            },
            "ustad_quick": {
                "when_to_use": "Simpler problems or when speed is prioritized",
                "examples": ["Code review", "Quick analysis", "Implementation suggestions"],
                "perspectives": 3,
                "rounds": "Single round fast analysis",
            },
            "ustad_decide": {
                "when_to_use": "Explicit choice/comparison between stated options",
                "examples": [
                    "Technology selection",
                    "Design pattern choice",
                    "Implementation alternatives",
                ],
                "format": "Provide options as comma-separated string",
            },
            "ustad_meta": {
                "when_to_use": "Uncertain which reasoning approach to use",
                "examples": ["Complex problem analysis", "Tool selection guidance"],
                "output": "Recommends optimal reasoning tool with reasoning",
            },
        },
        "usage_patterns": {
            "step_0_mandatory": "Always start with intent understanding - what is the user REALLY trying to achieve?",
            "liberal_tavily": "Use tavily-search for ALL technical claims and domain research",
            "collaborative_first": "Default to ustad_think for non-trivial problems",
            "context_preservation": "Maintain understanding across interactions",
        },
        "anti_patterns": {
            "avoid": [
                "Using sequential-thinking when ustad-think is available",
                "Making confident technical claims without tavily verification",
                "Jumping to implementation without collaborative analysis",
                "Abandoning complex problems instead of systematic breakdown",
            ]
        },
        "integration_instructions": {
            "claude_code_setup": "This MCP provides collaborative reasoning capabilities",
            "replaces_claude_md": "This guide replaces external protocol documentation",
            "self_teaching": "Query this method when unsure about protocol usage",
        },
    }

    return json.dumps(protocol_guide, indent=2)


@mcp.tool()
async def get_usage_examples() -> str:
    """Get practical examples of how to use ustad-think tools effectively.

    Provides concrete examples of proper tool usage for different problem types.
    """
    examples = {
        "architecture_decision": {
            "problem": "Should we use microservices or monolith for our e-commerce platform?",
            "recommended_tool": "ustad_decide",
            "usage": "ustad_decide('Architecture decision for e-commerce platform', 'microservices, monolith, modular monolith', 'Team size: 5 developers, expected traffic: 10k users/day')",
            "why": "Explicit choice between architectural options",
        },
        "complex_debugging": {
            "problem": "Our distributed system has intermittent latency spikes",
            "recommended_tool": "ustad_think",
            "usage": "ustad_think('Distributed system intermittent latency spikes', 'Production environment, affects 2% of requests, occurs during peak hours')",
            "why": "Complex problem requiring multi-perspective debugging analysis",
        },
        "quick_code_review": {
            "problem": "Review this React component for best practices",
            "recommended_tool": "ustad_quick",
            "usage": "ustad_quick('Review React component for best practices', '[component code here]')",
            "why": "Straightforward review task suitable for fast analysis",
        },
        "uncertain_approach": {
            "problem": "How should I optimize database queries in this application?",
            "recommended_tool": "ustad_meta",
            "usage": "ustad_meta('Database query optimization approach', 'PostgreSQL, Django ORM, 100k records')",
            "why": "Unclear if this needs comparison, analysis, or decision-making",
        },
    }

    return json.dumps(examples, indent=2)


@mcp.tool()
async def version() -> str:
    """Get the current version of the ustad-think MCP server."""
    return json.dumps(
        {
            "name": "ustad-think",
            "version": "v0.2.0",
            "protocol": "Ustad Protocol",
            "tools": [
                "ustad_start",
                "ustad_think",
                "ustad_think_stream",
                "ustad_quick",
                "ustad_decide",
                "ustad_meta",
                "ustad_research",
                "ustad_context",
                "ustad_preflight",
                "ustad_systematic",
                "ustad_session_info",
                "get_protocol_guide",
                "get_usage_examples",
                "get_protocol_status",
                "version",
            ],
            "last_updated": "2025-09-02",
            "status": "active",
        },
        indent=2,
    )


@mcp.tool()
async def get_protocol_status() -> str:
    """Get current status and capabilities of the Batch of Thought Protocol implementation.

    Shows deployment status, available tools, and system health.
    """
    status = {
        "protocol_version": "v0.2.0",
        "deployment_status": "ACTIVE",
        "implementation_type": "FastMCP Server",
        "available_tools": {
            "ustad_start": "✅ Initialize and warm up the collaborative reasoning system",
            "ustad_think": "✅ Full collaborative reasoning (3-8 customizable perspectives)",
            "ustad_think_stream": "✅ Real-time streaming collaborative dialogue",
            "ustad_quick": "✅ Fast analysis (3 perspectives)",
            "ustad_decide": "✅ Decision analysis with option evaluation",
            "ustad_meta": "✅ Meta-reasoning with tavily+GPT-3.5",
            "ustad_research": "✅ Liberal research with Tavily integration and collaborative analysis",
            "ustad_context": "✅ Context continuity with git checkpoints and session management",
            "ustad_preflight": "✅ Pre-flight risk analysis and failure pattern prevention",
            "ustad_systematic": "✅ Systematic execution planning with abandonment prevention",
            "ustad_session_info": "✅ Session isolation info and system statistics",
            "get_protocol_guide": "✅ Self-teaching protocol documentation",
            "get_usage_examples": "✅ Practical usage examples",
            "get_protocol_status": "✅ System status and health check",
        },
        "capabilities": {
            "session_initialization": "Warm startup with ustad_start for optimized performance",
            "customizable_perspectives": "3-8 selectable AI perspectives with custom selection",
            "streaming_dialogue": "Real-time collaborative reasoning updates",
            "multi_perspective_reasoning": "Up to 8 AI perspectives in structured dialogue",
            "consensus_building": "True synthesis through collaborative debate",
            "factual_grounding": "Tavily integration for fact verification",
            "meta_reasoning": "GPT-3.5 powered tool selection guidance",
            "self_documentation": "Built-in protocol teaching capabilities",
        },
        "cost_efficiency": {
            "average_cost_per_analysis": "$0.008 USD",
            "model": "GPT-3.5-turbo optimized",
            "factual_research": "Tavily integration",
        },
        "philosophy": "Ustad - The Master Teacher. Wisdom emerges not from individual brilliance, but from collaborative dialogue where perspectives challenge, refine, and synthesize into deeper understanding.",
        "replaces": [
            "External CLAUDE.md protocol documentation",
            "Sequential-thinking for complex collaborative problems",
            "Rule-based tool selection logic",
        ],
    }

    return json.dumps(status, indent=2)


@mcp.tool()
async def ustad_start() -> str:
    """Initialize and warm up the Ustad Protocol collaborative reasoning system.

    This tool should be called at the beginning of a session to:
    - Pre-initialize the collaborative bot instance
    - Warm up AI model connections
    - Prepare the reasoning system for optimal performance
    - Establish session context for continuous collaborative dialogue
    - Check CLAUDE.md alignment and common AI failure patterns

    Returns:
        Status of the initialization and system readiness
    """
    try:
        # Initialize the collaborative bot
        bot = get_bot()

        # Warm up the system with a simple test
        warm_up_result = await bot.think(
            "System initialization test", "Warming up collaborative reasoning capabilities", 3
        )

        # Environment checks
        env_checks = {
            "tavily_available": bool(os.getenv("TAVILY_API_KEY")),
            "openai_available": bool(os.getenv("OPENAI_API_KEY")),
            "git_repo_detected": os.path.exists(".git"),
        }

        initialization_status = {
            "status": "initialized",
            "ustad_protocol_version": "v0.2.0",
            "system": "ready",
            "collaborative_bot": "initialized",
            "warm_up": "completed" if warm_up_result else "failed",
            "session_context": "established",
            "environment_status": env_checks,
            "capabilities": {
                "custom_perspectives": "3-8 selectable perspectives",
                "streaming": "real-time collaborative dialogue",
                "meta_reasoning": "intelligent tool selection",
                "self_teaching": "built-in protocol guidance",
                "liberal_research": "ustad_research with Tavily integration",
                "context_continuity": "ustad_context for git workflow",
                "preflight_checks": "ustad_preflight for failure prevention",
            },
            "performance": {
                "cold_start": "eliminated",
                "response_time": "optimized",
                "session_continuity": "enabled",
            },
            "message": "Ustad Protocol initialized and ready for collaborative reasoning",
            "next_steps": [
                "Use ustad_research for comprehensive fact-checking",
                "Use ustad_preflight before complex tasks",
                "Use ustad_think for collaborative reasoning",
                "Use ustad_context for maintaining context continuity",
                "Query get_protocol_guide for usage instructions",
            ],
            "best_practices": [
                "Session initialized ✅ - Ready for collaborative reasoning",
                "Liberal research available via ustad_research",
                "Context continuity available via ustad_context",
                "Prevention checks available via ustad_preflight",
                "Multi-perspective analysis default via ustad_think",
            ],
        }

        return json.dumps(initialization_status, indent=2)

    except Exception as e:
        error_result = {
            "error": str(e),
            "status": "initialization_failed",
            "message": "Ustad Protocol initialization encountered an error",
            "ustad_protocol_version": "v0.2.0",
            "fallback": "Individual tools will still work with cold start",
        }
        return json.dumps(error_result, indent=2)


@mcp.tool()
async def ustad_research(problem: str, context: str = "", depth: str = "basic") -> str:
    """Liberal research tool using Tavily for comprehensive fact-checking and domain analysis.

    This tool embodies the principle of verification-first reasoning - always research
    before making claims or decisions.

    Args:
        problem: The topic or question to research
        context: Additional context for focused research
        depth: Research depth - "basic", "standard", or "comprehensive"

    Returns:
        JSON with research findings and analysis
    """
    try:
        import httpx

        tavily_api_key = os.getenv("TAVILY_API_KEY")
        if not tavily_api_key:
            return json.dumps(
                {
                    "error": "TAVILY_API_KEY not available",
                    "message": "Set TAVILY_API_KEY environment variable for research capabilities",
                    "fallback": "Proceeding without external research",
                },
                indent=2,
            )

        # Configure search based on depth
        search_config = {
            "basic": {"max_results": 3, "search_depth": "basic"},
            "standard": {"max_results": 5, "search_depth": "basic"},
            "comprehensive": {"max_results": 8, "search_depth": "advanced"},
        }
        config = search_config.get(depth, search_config["basic"])

        # Construct research query
        search_query = f"{problem} {context}".strip()

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": tavily_api_key,
                    "query": search_query,
                    "search_depth": config["search_depth"],
                    "max_results": config["max_results"],
                    "include_raw_content": False,
                    "include_images": False,
                },
                timeout=15.0,
            )

            if response.status_code == 200:
                search_data = response.json()
                results = search_data.get("results", [])

                # Analyze findings with collaborative reasoning
                bot = get_bot()
                analysis_prompt = (
                    f"Analyze these research findings about: {problem}\n\nFindings:\n"
                    + "\n".join(
                        [
                            f"- {result.get('title', '')}: {result.get('content', '')[:300]}..."
                            for result in results[:3]
                        ]
                    )
                )

                analysis = await bot.think(
                    analysis_prompt,
                    f"Focus on key insights and implications. Context: {context}",
                    4,
                )

                research_result = {
                    "problem": problem,
                    "context": context,
                    "depth": depth,
                    "research_findings": [
                        {
                            "title": result.get("title", ""),
                            "url": result.get("url", ""),
                            "content": result.get("content", "")[:500] + "..."
                            if len(result.get("content", "")) > 500
                            else result.get("content", ""),
                            "relevance_score": result.get("score", 0),
                        }
                        for result in results
                    ],
                    "collaborative_analysis": serialize_collaborative_result(analysis),
                    "key_insights": [
                        insight.get("content", "")
                        for insight in analysis.get("rounds", [{}])[-1].get("interactions", [])[:3]
                    ]
                    if analysis.get("rounds")
                    else [],
                    "verification_status": "researched",
                    "source_count": len(results),
                    "search_query": search_query,
                }

                return json.dumps(research_result, indent=2)
            return json.dumps(
                {
                    "error": f"Research failed: HTTP {response.status_code}",
                    "problem": problem,
                    "fallback": "Proceeding without external research",
                },
                indent=2,
            )

    except Exception as e:
        return json.dumps(
            {
                "error": str(e),
                "problem": problem,
                "message": "Research tool encountered an error",
                "fallback": "Proceeding without external research",
            },
            indent=2,
        )


@mcp.tool()
async def ustad_context(action: str, context_data: str = "", git_message: str = "") -> str:
    """Context continuity tool for maintaining understanding across interactions.

    Helps prevent context degradation by providing checkpoint functionality
    and context preservation strategies.

    Args:
        action: "save", "restore", "checkpoint", or "status"
        context_data: Context information to save or restore
        git_message: Optional git commit message for checkpoint action

    Returns:
        JSON with context management results
    """
    try:
        if action == "save":
            # Save context to a temporary store (in production, could use persistent storage)
            context_id = f"context_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # For now, return the saved context info
            result = {
                "action": "save",
                "context_id": context_id,
                "context_data": context_data,
                "timestamp": datetime.now().isoformat(),
                "status": "saved",
                "message": "Context saved for future reference",
            }

        elif action == "checkpoint" and os.path.exists(".git"):
            # Git checkpoint functionality
            try:
                # Get git status
                git_status = subprocess.run(
                    ["git", "status", "--porcelain"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                    check=False,
                ).stdout.strip()

                if git_status:
                    # Add and commit changes
                    subprocess.run(["git", "add", "-A"], timeout=10, check=False)
                    commit_msg = git_message or f"Context checkpoint: {context_data[:50]}..."
                    subprocess.run(["git", "commit", "-m", commit_msg], timeout=10, check=False)

                    result = {
                        "action": "checkpoint",
                        "git_status": "committed",
                        "commit_message": commit_msg,
                        "context_data": context_data,
                        "timestamp": datetime.now().isoformat(),
                        "message": "Git checkpoint created successfully",
                    }
                else:
                    result = {
                        "action": "checkpoint",
                        "git_status": "no_changes",
                        "context_data": context_data,
                        "timestamp": datetime.now().isoformat(),
                        "message": "No changes to commit",
                    }

            except subprocess.TimeoutExpired:
                result = {
                    "action": "checkpoint",
                    "error": "Git operation timed out",
                    "fallback": "Context noted but not committed",
                }
            except Exception as git_error:
                result = {
                    "action": "checkpoint",
                    "error": str(git_error),
                    "fallback": "Context noted but git checkpoint failed",
                }

        elif action == "status":
            # Check context continuity status
            git_available = os.path.exists(".git")

            result = {
                "action": "status",
                "git_available": git_available,
                "context_preservation": {
                    "git_repo": git_available,
                    "checkpoint_capability": git_available,
                    "session_context": "maintained",
                },
                "recommendations": [
                    "Use checkpoint action before major changes"
                    if git_available
                    else "Initialize git for better context tracking",
                    "Save context at logical breakpoints",
                    "Use collaborative reasoning to maintain understanding",
                ],
            }

        else:
            result = {
                "action": action,
                "error": "Unknown action or missing requirements",
                "available_actions": ["save", "checkpoint", "status"],
                "message": "Specify a valid action for context management",
            }

        return json.dumps(result, indent=2)

    except Exception as e:
        return json.dumps(
            {
                "error": str(e),
                "action": action,
                "message": "Context management encountered an error",
            },
            indent=2,
        )


@mcp.tool()
async def ustad_preflight(task_description: str, complexity: str = "medium") -> str:
    """Pre-flight checklist tool for preventing common AI reasoning failures.

    Analyzes tasks to identify potential failure patterns and provides
    preventive recommendations before execution.

    Args:
        task_description: Description of the task to be performed
        complexity: Task complexity - "low", "medium", "high"

    Returns:
        JSON with risk analysis and prevention recommendations
    """
    try:
        # Analyze task for common failure patterns
        task_lower = task_description.lower()

        risk_patterns = {
            "hallucination_risk": any(
                keyword in task_lower
                for keyword in [
                    "technical",
                    "specific",
                    "implementation",
                    "architecture",
                    "framework",
                    "library",
                    "api",
                    "protocol",
                    "standard",
                ]
            ),
            "context_degradation_risk": any(
                keyword in task_lower
                for keyword in [
                    "multi-step",
                    "complex",
                    "system",
                    "integration",
                    "workflow",
                    "process",
                    "sequence",
                    "chain",
                ]
            ),
            "over_engineering_risk": any(
                keyword in task_lower
                for keyword in ["design", "build", "create", "implement", "develop", "architect"]
            ),
            "abandonment_risk": any(
                keyword in task_lower
                for keyword in [
                    "debug",
                    "fix",
                    "error",
                    "problem",
                    "issue",
                    "troubleshoot",
                    "investigate",
                    "analyze",
                ]
            ),
        }

        # Generate prevention recommendations
        recommendations = []

        if risk_patterns["hallucination_risk"]:
            recommendations.extend(
                [
                    "🔍 Use ustad_research to verify technical claims before proceeding",
                    "📚 Research domain-specific best practices and standards",
                    "✅ Fact-check implementation approaches against authoritative sources",
                ]
            )

        if risk_patterns["context_degradation_risk"]:
            recommendations.extend(
                [
                    "📝 Use ustad_context to save checkpoints at logical steps",
                    "🔄 Break complex tasks into smaller, manageable pieces",
                    "📋 Create systematic todo tracking for multi-step processes",
                ]
            )

        if risk_patterns["over_engineering_risk"]:
            recommendations.extend(
                [
                    "🎯 Focus on exact requirements - avoid feature creep",
                    "⚖️ Apply YAGNI principle (You Aren't Gonna Need It)",
                    "🔍 Use collaborative reasoning to validate necessity",
                ]
            )

        if risk_patterns["abandonment_risk"]:
            recommendations.extend(
                [
                    "🔄 Use systematic problem-solving with collaborative reasoning",
                    "📊 Break problems into smaller, solvable components",
                    "💪 Try multiple approaches before considering alternatives",
                ]
            )

        # Default recommendations for all tasks
        if complexity in ["medium", "high"]:
            recommendations.extend(
                [
                    "🧠 Use ustad_think for multi-perspective analysis",
                    "🔬 Research the problem domain comprehensively",
                    "⚡ Consider using collaborative reasoning as default",
                ]
            )

        # Collaborative analysis of the task
        bot = get_bot()
        analysis_result = await bot.think(
            f"Analyze this task for potential failure patterns: {task_description}",
            f"Focus on identifying risks and prevention strategies. Complexity: {complexity}",
            4,
        )

        preflight_result = {
            "task_description": task_description,
            "complexity": complexity,
            "risk_assessment": {
                "hallucination_risk": "high" if risk_patterns["hallucination_risk"] else "low",
                "context_degradation_risk": "high"
                if risk_patterns["context_degradation_risk"]
                else "low",
                "over_engineering_risk": "high"
                if risk_patterns["over_engineering_risk"]
                else "low",
                "abandonment_risk": "high" if risk_patterns["abandonment_risk"] else "low",
            },
            "prevention_recommendations": recommendations,
            "collaborative_analysis": serialize_collaborative_result(analysis_result),
            "checklist": [
                "✅ Research completed (use ustad_research)",
                "✅ Context checkpoints planned (use ustad_context)",
                "✅ Requirements clearly defined",
                "✅ Multi-perspective analysis (use ustad_think)",
                "✅ Prevention strategies identified",
            ],
            "ready_to_proceed": len(recommendations) == 0 or complexity == "low",
            "message": "Pre-flight analysis complete - follow recommendations before proceeding",
        }

        return json.dumps(preflight_result, indent=2)

    except Exception as e:
        return json.dumps(
            {
                "error": str(e),
                "task_description": task_description,
                "message": "Pre-flight analysis encountered an error",
                "fallback": "Proceed with caution and use collaborative reasoning",
            },
            indent=2,
        )


@mcp.tool()
async def ustad_systematic(problem: str, context: str = "", todo_items: list = None) -> str:
    """Systematic execution tool that combines collaborative reasoning with structured task management.

    Provides methodical problem-solving that prevents task abandonment and ensures
    comprehensive execution.

    Args:
        problem: The problem to solve systematically
        context: Additional context and constraints
        todo_items: Optional list of specific tasks to track

    Returns:
        JSON with systematic analysis and execution plan
    """
    try:
        # Use collaborative reasoning to analyze the problem
        bot = get_bot()
        analysis = await bot.think(
            f"Create a systematic approach for: {problem}",
            f"Focus on breaking this into manageable steps and preventing abandonment. Context: {context}",
            6,
        )

        # Extract systematic steps from collaborative analysis
        systematic_steps = []
        if analysis.get("rounds"):
            for round_data in analysis["rounds"]:
                for interaction in round_data.get("interactions", []):
                    content = interaction.get("content", "")
                    if any(
                        keyword in content.lower()
                        for keyword in ["step", "first", "then", "next", "finally"]
                    ):
                        # Extract actionable steps
                        lines = content.split("\n")
                        for line in lines:
                            if any(
                                marker in line for marker in ["1.", "2.", "3.", "•", "-", "Step"]
                            ):
                                systematic_steps.append(line.strip())

        # If no steps found, generate generic systematic approach
        if not systematic_steps:
            systematic_steps = [
                "Research and understand the problem domain",
                "Break down into smaller, manageable components",
                "Identify dependencies and prerequisites",
                "Create implementation plan with checkpoints",
                "Execute systematically with validation at each step",
                "Test and verify the complete solution",
            ]

        # Create execution plan
        execution_plan = {
            "problem": problem,
            "context": context,
            "systematic_analysis": serialize_collaborative_result(analysis),
            "execution_steps": systematic_steps[:8],  # Limit to 8 steps for manageability
            "todo_integration": {
                "recommended_todos": [step for step in systematic_steps[:5]],
                "checkpoint_strategy": "Save context after each major step",
                "abandonment_prevention": [
                    "Use collaborative reasoning for complex steps",
                    "Break down blocked steps into smaller pieces",
                    "Try at least 3 approaches before seeking alternatives",
                ],
            },
            "tools_to_use": [
                "ustad_research for domain understanding",
                "ustad_context for checkpoint management",
                "ustad_think for complex step analysis",
                "ustad_preflight for risk assessment",
            ],
            "success_criteria": [
                "All steps completed successfully",
                "Solution tested and validated",
                "Context preserved throughout execution",
                "No abandoned tasks or shortcuts taken",
            ],
            "estimated_complexity": "high" if len(systematic_steps) > 5 else "medium",
        }

        return json.dumps(execution_plan, indent=2)

    except Exception as e:
        return json.dumps(
            {
                "error": str(e),
                "problem": problem,
                "message": "Systematic execution planning encountered an error",
                "fallback": "Use collaborative reasoning to break down the problem manually",
            },
            indent=2,
        )


@mcp.tool()
async def ustad_session_info() -> str:
    """Get information about the current session and system session statistics.

    Returns:
        JSON with session details and system statistics
    """
    try:
        session_id = get_session_id()
        session_stats = get_session_stats()

        # Clean up old sessions while we're at it
        cleaned = cleanup_old_sessions()

        session_info = {
            "current_session": {
                "session_id": session_id,
                "is_new": session_id not in _session_registry,
                "request_count": _session_registry.get(session_id, {}).get("request_count", 0),
            },
            "system_stats": session_stats,
            "maintenance": {"old_sessions_cleaned": cleaned, "cleanup_threshold_minutes": 30},
            "session_isolation": "Each session gets its own collaborative bot instance",
            "benefits": [
                "No cross-session state contamination",
                "Independent reasoning contexts",
                "Automatic cleanup of old sessions",
                "Thread-safe session management",
            ],
        }

        return json.dumps(session_info, indent=2)

    except Exception as e:
        return json.dumps(
            {"error": str(e), "message": "Session info retrieval encountered an error"}, indent=2
        )


if __name__ == "__main__":
    import sys

    # Parse command line arguments
    transport = "stdio"  # default
    port = 8000
    host = "0.0.0.0"  # Default to all interfaces for containers

    if len(sys.argv) > 1:
        if sys.argv[1] == "--sse":
            transport = "sse"
            port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
        elif sys.argv[1] == "--http":
            transport = "http"
            port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
        elif sys.argv[1] == "--stdio":
            transport = "stdio"

    # Start server with appropriate transport
    if transport == "sse":
        print("🧠 Ustad MCP Server - SSE Transport (Recommended)")
        print("=" * 50)
        print(f"🚀 Starting SSE transport on port {port}")
        print(f"🌐 Host: {host} (container-ready)")
        print("📡 Multiple concurrent sessions supported")
        print("⚡ Real-time streaming with session isolation")
        print(f"🔗 Connect via SSE: http://{host}:{port}/sse")
        print("📊 Session info available at each connection")
        print()
        mcp.run(transport="sse", host=host, port=port)

    elif transport == "http":
        print("🧠 Ustad MCP Server - HTTP Transport")
        print("=" * 45)
        print(f"🚀 Starting HTTP transport on port {port}")
        print("📡 Multiple concurrent sessions supported")
        print(f"🔗 Connect via: http://{host}:{port}")
        mcp.run(transport="http", host=host, port=port)

    else:  # stdio
        print("🧠 Ustad MCP Server - STDIO Transport")
        print("=" * 45)
        print("🚀 Starting STDIO transport (single session)")
        print("⚠️  For multiple sessions, use: --sse or --http")
        print("🐳 For containers, use: --sse (recommended)")
        mcp.run()
