"""
Base classes and utilities for anti-pattern detection.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json


class PatternSeverity(Enum):
    """Severity levels for detected anti-patterns"""
    LOW = "low"           # Minor issue, gentle suggestion
    MEDIUM = "medium"     # Notable issue, clear recommendation  
    HIGH = "high"         # Critical issue, strong intervention needed
    CRITICAL = "critical" # Severe issue, immediate action required


@dataclass
class PatternAlert:
    """Alert generated when an anti-pattern is detected"""
    pattern_type: str                    # Type of pattern detected
    severity: PatternSeverity           # How severe the issue is
    confidence: float                   # Confidence in detection (0-1)
    message: str                        # Human-readable description
    recommendations: List[str]          # Actionable suggestions
    context: Dict[str, Any]            # Additional context data
    timestamp: datetime                 # When detected
    session_id: str                    # Which session this relates to
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary for JSON serialization"""
        return {
            "pattern_type": self.pattern_type,
            "severity": self.severity.value,
            "confidence": self.confidence,
            "message": self.message,
            "recommendations": self.recommendations,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PatternAlert":
        """Create alert from dictionary"""
        return cls(
            pattern_type=data["pattern_type"],
            severity=PatternSeverity(data["severity"]),
            confidence=data["confidence"],
            message=data["message"],
            recommendations=data["recommendations"],
            context=data["context"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            session_id=data["session_id"]
        )


class AntiPatternDetector(ABC):
    """Base class for all anti-pattern detection tools"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.enabled = True
        self.detection_count = 0
        self.last_detection = None
        
    @abstractmethod
    def analyze(self, 
                conversation_history: List[Dict[str, Any]], 
                current_context: Dict[str, Any],
                session_id: str) -> List[PatternAlert]:
        """
        Analyze conversation for anti-patterns.
        
        Args:
            conversation_history: List of previous messages/exchanges
            current_context: Current conversation state and metadata
            session_id: Unique identifier for this session
            
        Returns:
            List of detected pattern alerts
        """
        pass
    
    @abstractmethod
    def get_prevention_suggestions(self, 
                                 alert: PatternAlert,
                                 context: Dict[str, Any]) -> List[str]:
        """
        Get specific prevention suggestions for a detected pattern.
        
        Args:
            alert: The pattern alert that was detected
            context: Additional context for generating suggestions
            
        Returns:
            List of actionable prevention recommendations
        """
        pass
    
    def is_pattern_present(self, 
                          conversation_history: List[Dict[str, Any]], 
                          context: Dict[str, Any]) -> Tuple[bool, float]:
        """
        Quick check if pattern is present without full analysis.
        
        Returns:
            (is_present, confidence_score)
        """
        alerts = self.analyze(conversation_history, context, "quick_check")
        if alerts:
            max_confidence = max(alert.confidence for alert in alerts)
            return True, max_confidence
        return False, 0.0
    
    def create_alert(self,
                    pattern_type: str,
                    severity: PatternSeverity,
                    confidence: float,
                    message: str,
                    recommendations: List[str],
                    context: Dict[str, Any],
                    session_id: str) -> PatternAlert:
        """Helper method to create standardized alerts"""
        alert = PatternAlert(
            pattern_type=pattern_type,
            severity=severity,
            confidence=confidence,
            message=message,
            recommendations=recommendations,
            context=context,
            timestamp=datetime.now(),
            session_id=session_id
        )
        
        self.detection_count += 1
        self.last_detection = alert.timestamp
        
        return alert
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get detection statistics for this tool"""
        return {
            "name": self.name,
            "enabled": self.enabled,
            "detection_count": self.detection_count,
            "last_detection": self.last_detection.isoformat() if self.last_detection else None
        }


class PatternDetectionEngine:
    """Coordinates multiple anti-pattern detectors"""
    
    def __init__(self):
        self.detectors: Dict[str, AntiPatternDetector] = {}
        self.alert_history: List[PatternAlert] = []
        self.enabled = True
        
    def register_detector(self, detector: AntiPatternDetector):
        """Register a new anti-pattern detector"""
        self.detectors[detector.name] = detector
        
    def unregister_detector(self, name: str):
        """Remove a detector"""
        if name in self.detectors:
            del self.detectors[name]
    
    def analyze_all(self, 
                   conversation_history: List[Dict[str, Any]], 
                   current_context: Dict[str, Any],
                   session_id: str) -> List[PatternAlert]:
        """Run all enabled detectors and return consolidated alerts"""
        if not self.enabled:
            return []
            
        all_alerts = []
        
        for detector in self.detectors.values():
            if detector.enabled:
                try:
                    alerts = detector.analyze(conversation_history, current_context, session_id)
                    all_alerts.extend(alerts)
                except Exception as e:
                    # Log error but don't fail entire detection
                    print(f"Error in detector {detector.name}: {e}")
                    
        # Sort by severity and confidence
        all_alerts.sort(key=lambda x: (x.severity.value, x.confidence), reverse=True)
        
        # Store in history
        self.alert_history.extend(all_alerts)
        
        return all_alerts
    
    def get_active_patterns(self, session_id: str) -> List[PatternAlert]:
        """Get recent alerts for a specific session"""
        recent_alerts = [
            alert for alert in self.alert_history[-50:]  # Last 50 alerts
            if alert.session_id == session_id
        ]
        return recent_alerts
    
    def get_summary_report(self) -> Dict[str, Any]:
        """Get summary of all detector activity"""
        return {
            "enabled": self.enabled,
            "total_detectors": len(self.detectors),
            "active_detectors": sum(1 for d in self.detectors.values() if d.enabled),
            "total_alerts": len(self.alert_history),
            "detector_stats": [d.get_statistics() for d in self.detectors.values()],
            "recent_alerts": len([a for a in self.alert_history[-100:]])  # Last 100
        }


# Global detection engine instance
detection_engine = PatternDetectionEngine()