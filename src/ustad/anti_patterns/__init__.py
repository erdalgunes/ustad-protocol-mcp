"""
🛡️ Ustad Protocol Anti-Pattern Detection Framework
==================================================

Common utilities and base classes for detecting and preventing AI failure patterns:
- Context degradation
- Impulsiveness  
- Task abandonment
- Over-engineering
- Hallucinations

This framework provides the foundation for building real-time pattern detection
and intervention tools that integrate with the Ustad Protocol MCP server.
"""

from .base import AntiPatternDetector, PatternAlert, PatternSeverity
from .context import ContextTracker
from .utils import analyze_conversation, extract_patterns, generate_recommendations

__version__ = "0.3.0"
__all__ = [
    "AntiPatternDetector",
    "PatternAlert", 
    "PatternSeverity",
    "ContextTracker",
    "analyze_conversation",
    "extract_patterns",
    "generate_recommendations"
]