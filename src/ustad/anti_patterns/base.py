"""Base classes and utilities for cognitive scaffolding and support tools."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any


class SupportSeverity(Enum):
    """Support intensity levels for cognitive scaffolding"""

    LOW = "low"  # Light guidance, gentle suggestion
    MEDIUM = "medium"  # Clear assistance, helpful recommendation
    HIGH = "high"  # Strong support, important scaffolding needed
    CRITICAL = "critical"  # Intensive support, immediate assistance required


@dataclass
class SupportAlert:
    """Alert generated when cognitive scaffolding support is recommended"""

    support_type: str  # Type of cognitive support needed
    severity: SupportSeverity  # How much assistance is recommended
    confidence: float  # Confidence in recommendation (0-1)
    message: str  # Human-readable description
    recommendations: list[str]  # Actionable support suggestions
    context: dict[str, Any]  # Additional context data
    timestamp: datetime  # When support was recommended
    session_id: str  # Which session this relates to

    def to_dict(self) -> dict[str, Any]:
        """Convert support alert to dictionary for JSON serialization"""
        return {
            "support_type": self.support_type,
            "severity": self.severity.value,
            "confidence": self.confidence,
            "message": self.message,
            "recommendations": self.recommendations,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SupportAlert":
        """Create support alert from dictionary"""
        return cls(
            support_type=data["support_type"],
            severity=SupportSeverity(data["severity"]),
            confidence=data["confidence"],
            message=data["message"],
            recommendations=data["recommendations"],
            context=data["context"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            session_id=data["session_id"],
        )


class CognitiveScaffoldTool(ABC):
    """Base class for all cognitive scaffolding support tools"""

    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.enabled = True
        self.support_count = 0
        self.last_support = None

    @abstractmethod
    def analyze(
        self,
        conversation_history: list[dict[str, Any]],
        current_context: dict[str, Any],
        session_id: str,
    ) -> list[SupportAlert]:
        """Analyze conversation for cognitive support opportunities.

        Args:
            conversation_history: List of previous messages/exchanges
            current_context: Current conversation state and metadata
            session_id: Unique identifier for this session

        Returns:
            List of cognitive support recommendations
        """

    @abstractmethod
    def get_scaffolding_suggestions(
        self, alert: SupportAlert, context: dict[str, Any]
    ) -> list[str]:
        """Get specific scaffolding suggestions for cognitive support.

        Args:
            alert: The support alert that was recommended
            context: Additional context for generating suggestions

        Returns:
            List of actionable scaffolding recommendations
        """

    def is_support_needed(
        self, conversation_history: list[dict[str, Any]], context: dict[str, Any]
    ) -> tuple[bool, float]:
        """Quick check if cognitive support is needed without full analysis.

        Returns:
            (support_needed, confidence_score)
        """
        alerts = self.analyze(conversation_history, context, "quick_check")
        if alerts:
            max_confidence = max(alert.confidence for alert in alerts)
            return True, max_confidence
        return False, 0.0

    def create_support_alert(
        self,
        support_type: str,
        severity: SupportSeverity,
        confidence: float,
        message: str,
        recommendations: list[str],
        context: dict[str, Any],
        session_id: str,
    ) -> SupportAlert:
        """Helper method to create standardized support alerts"""
        alert = SupportAlert(
            support_type=support_type,
            severity=severity,
            confidence=confidence,
            message=message,
            recommendations=recommendations,
            context=context,
            timestamp=datetime.now(),
            session_id=session_id,
        )

        self.support_count += 1
        self.last_support = alert.timestamp

        return alert

    def get_statistics(self) -> dict[str, Any]:
        """Get support statistics for this tool"""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "support_count": self.support_count,
            "last_support": self.last_support.isoformat() if self.last_support else None,
        }


class CognitiveScaffoldingEngine:
    """Coordinates multiple cognitive scaffolding support tools"""

    def __init__(self):
        self.scaffold_tools: dict[str, CognitiveScaffoldTool] = {}
        self.support_history: list[SupportAlert] = []
        self.enabled = True

    def register_scaffold_tool(self, tool: CognitiveScaffoldTool):
        """Register a new cognitive scaffolding tool"""
        self.scaffold_tools[tool.name] = tool

    def unregister_scaffold_tool(self, name: str):
        """Remove a scaffolding tool"""
        if name in self.scaffold_tools:
            del self.scaffold_tools[name]

    def analyze_all(
        self,
        conversation_history: list[dict[str, Any]],
        current_context: dict[str, Any],
        session_id: str,
    ) -> list[SupportAlert]:
        """Run all enabled scaffolding tools and return consolidated support recommendations"""
        if not self.enabled:
            return []

        all_alerts = []

        for tool in self.scaffold_tools.values():
            if tool.enabled:
                try:
                    alerts = tool.analyze(conversation_history, current_context, session_id)
                    all_alerts.extend(alerts)
                except Exception as e:
                    # Log error but don't fail entire scaffolding analysis
                    print(f"Error in scaffolding tool {tool.name}: {e}")

        # Sort by severity and confidence
        all_alerts.sort(key=lambda x: (x.severity.value, x.confidence), reverse=True)

        # Store in history
        self.support_history.extend(all_alerts)

        return all_alerts

    def get_active_support(self, session_id: str) -> list[SupportAlert]:
        """Get recent support recommendations for a specific session"""
        recent_alerts = [
            alert
            for alert in self.support_history[-50:]  # Last 50 alerts
            if alert.session_id == session_id
        ]
        return recent_alerts

    def get_summary_report(self) -> dict[str, Any]:
        """Get summary of all scaffolding tool activity"""
        return {
            "enabled": self.enabled,
            "total_scaffold_tools": len(self.scaffold_tools),
            "active_scaffold_tools": sum(1 for t in self.scaffold_tools.values() if t.enabled),
            "total_support_recommendations": len(self.support_history),
            "scaffold_tool_stats": [t.get_statistics() for t in self.scaffold_tools.values()],
            "recent_support": len([a for a in self.support_history[-100:]]),  # Last 100
        }


# Global cognitive scaffolding engine instance
scaffolding_engine = CognitiveScaffoldingEngine()
