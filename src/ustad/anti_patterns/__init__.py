"""
🧠 Ustad Protocol Cognitive Scaffolding Framework
===============================================

Support tools and utilities for providing cognitive assistance with common computing challenges:
- Memory fragmentation / Context switching overhead
- Race conditions / Premature optimization  
- Process termination / Resource cleanup issues
- Memory bloat / Unnecessary complexity
- Cache misses / Unverified data confidence

This framework provides cognitive scaffolding tools that integrate with the Ustad Protocol MCP server
to support effective reasoning and execution patterns.
"""

from .base import CognitiveScaffoldTool, SupportAlert, SupportSeverity
from .context import ContextTracker
from .utils import analyze_conversation, extract_patterns, generate_recommendations

__version__ = "0.4.0"
__all__ = [
    "CognitiveScaffoldTool",
    "SupportAlert", 
    "SupportSeverity",
    "ContextTracker",
    "analyze_conversation",
    "extract_patterns",
    "generate_recommendations"
]