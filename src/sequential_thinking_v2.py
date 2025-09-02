"""
Enhanced Sequential Thinking Server - Production-ready improvements.
Adds confidence scoring, relationships, and metadata while maintaining YAGNI.
"""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass, field
from datetime import datetime
import time
import json
import re


@dataclass
class EnhancedThoughtData:
    """Enhanced data class with confidence and metadata"""
    thought: str
    thought_number: int
    total_thoughts: int
    next_thought_needed: bool
    is_revision: bool = False
    revises_thought: Optional[int] = None
    branch_from_thought: Optional[int] = None
    branch_id: Optional[str] = None
    needs_more_thoughts: bool = False
    # New fields
    confidence: float = 0.7  # Default confidence
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    category: Optional[str] = None
    related_thoughts: List[int] = field(default_factory=list)
    relationship_type: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)


class EnhancedSequentialThinkingServer:
    """
    Enhanced sequential thinking with production-ready features.
    Maintains YAGNI principle - only essential improvements.
    """
    
    # Thought categories
    CATEGORIES = {
        "analysis": ["analyzing", "examine", "investigate", "study"],
        "conclusion": ["conclusion", "therefore", "thus", "finally"],
        "hypothesis": ["hypothesis", "assume", "suppose", "if"],
        "observation": ["observe", "notice", "see", "find"],
        "question": ["?", "why", "how", "what", "when"],
        "action": ["will", "should", "must", "need to", "going to"]
    }
    
    def __init__(self):
        """Initialize enhanced server with metrics"""
        self.thought_history: List[EnhancedThoughtData] = []
        self.branches: Dict[str, List[EnhancedThoughtData]] = {}
        self._is_complete = False
        self.relationships: List[Dict[str, Any]] = []
        self.start_time = time.time()
        self.thought_times: List[float] = []
        
    def process_thought(self, thought_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process thought with enhanced validation and features.
        """
        thought_start = time.time()
        
        # Validate required fields
        required_fields = ["thought", "thoughtNumber", "totalThoughts", "nextThoughtNeeded"]
        for field in required_fields:
            if field not in thought_data:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate thought number
        thought_number = thought_data["thoughtNumber"]
        if thought_number < 1:
            raise ValueError(f"Invalid thought number: {thought_number}, must be >= 1")
        
        # Validate thought content
        warnings = self._validate_thought_content(thought_data["thought"])
        
        # Auto-categorize if not provided
        category = thought_data.get("category")
        if not category:
            category = self._auto_categorize(thought_data["thought"])
        
        # Set confidence with bounds
        confidence = thought_data.get("confidence", 0.7)
        confidence = max(0.0, min(1.0, confidence))  # Clamp to [0, 1]
        
        # Create enhanced thought
        thought = EnhancedThoughtData(
            thought=thought_data["thought"],
            thought_number=thought_number,
            total_thoughts=thought_data["totalThoughts"],
            next_thought_needed=thought_data["nextThoughtNeeded"],
            is_revision=thought_data.get("isRevision", False),
            revises_thought=thought_data.get("revisesThought"),
            branch_from_thought=thought_data.get("branchFromThought"),
            branch_id=thought_data.get("branchId"),
            needs_more_thoughts=thought_data.get("needsMoreThoughts", False),
            confidence=confidence,
            category=category,
            related_thoughts=thought_data.get("relatedThoughts", []),
            relationship_type=thought_data.get("relationshipType"),
            context=thought_data.get("context", {}),
            warnings=warnings
        )
        
        # Add to history
        self.thought_history.append(thought)
        
        # Track relationships
        if thought.related_thoughts:
            for related in thought.related_thoughts:
                self.relationships.append({
                    "from": thought.thought_number,
                    "to": related,
                    "type": thought.relationship_type or "related"
                })
        
        # Handle branching
        if thought.branch_id:
            if thought.branch_id not in self.branches:
                self.branches[thought.branch_id] = []
            self.branches[thought.branch_id].append(thought)
        
        # Check completion
        if not thought.next_thought_needed:
            self._is_complete = True
        
        # Track timing
        thought_time = time.time() - thought_start
        self.thought_times.append(thought_time)
        
        # Return response
        return self._thought_to_dict(thought)
    
    def _validate_thought_content(self, thought: str) -> List[str]:
        """Validate thought content and return warnings"""
        warnings = []
        
        # Check length
        if len(thought) < 10:
            warnings.append("Thought is very short (< 10 chars)")
        elif len(thought) > 1000:
            warnings.append("Thought is very long (> 1000 chars)")
        
        # Check for empty/whitespace
        if not thought.strip():
            warnings.append("Thought is empty or only whitespace")
        
        return warnings
    
    def _auto_categorize(self, thought: str) -> str:
        """Auto-categorize thought based on content"""
        thought_lower = thought.lower()
        
        for category, keywords in self.CATEGORIES.items():
            if any(keyword in thought_lower for keyword in keywords):
                return category
        
        return "general"
    
    def _thought_to_dict(self, thought: EnhancedThoughtData) -> Dict[str, Any]:
        """Convert thought to dictionary"""
        return {
            "thought": thought.thought,
            "thoughtNumber": thought.thought_number,
            "totalThoughts": thought.total_thoughts,
            "nextThoughtNeeded": thought.next_thought_needed,
            "isRevision": thought.is_revision,
            "revisesThought": thought.revises_thought,
            "branchFromThought": thought.branch_from_thought,
            "branchId": thought.branch_id,
            "needsMoreThoughts": thought.needs_more_thoughts,
            "confidence": thought.confidence,
            "timestamp": thought.timestamp,
            "category": thought.category,
            "relatedThoughts": thought.related_thoughts,
            "relationshipType": thought.relationship_type,
            "context": thought.context,
            "warnings": thought.warnings
        }
    
    def get_thought_relationships(self) -> List[Dict[str, Any]]:
        """Get the relationship graph between thoughts"""
        return self.relationships.copy()
    
    def calculate_coherence(self) -> Dict[str, float]:
        """Calculate coherence metrics for the thought sequence"""
        if len(self.thought_history) < 2:
            return {"overall_coherence": 1.0, "details": "Not enough thoughts"}
        
        # Simple coherence based on relationships and confidence
        total_confidence = sum(t.confidence for t in self.thought_history)
        avg_confidence = total_confidence / len(self.thought_history)
        
        # Relationship density (how connected thoughts are)
        possible_relationships = len(self.thought_history) * (len(self.thought_history) - 1) / 2
        actual_relationships = len(self.relationships)
        relationship_density = actual_relationships / possible_relationships if possible_relationships > 0 else 0
        
        # Overall coherence score
        overall = (avg_confidence * 0.6) + (relationship_density * 0.4)
        
        return {
            "overall_coherence": min(overall, 1.0),
            "average_confidence": avg_confidence,
            "relationship_density": relationship_density,
            "total_thoughts": len(self.thought_history),
            "total_relationships": len(self.relationships)
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for the thinking session"""
        if not self.thought_history:
            return {
                "total_thoughts": 0,
                "total_thinking_time": 0,
                "average_thought_time": 0,
                "thoughts_per_minute": 0
            }
        
        total_time = time.time() - self.start_time
        avg_thought_time = sum(self.thought_times) / len(self.thought_times) if self.thought_times else 0
        thoughts_per_minute = (len(self.thought_history) / total_time) * 60 if total_time > 0 else 0
        
        return {
            "total_thoughts": len(self.thought_history),
            "total_thinking_time": total_time,
            "average_thought_time": avg_thought_time,
            "thoughts_per_minute": thoughts_per_minute,
            "confidence_trend": [t.confidence for t in self.thought_history],
            "categories_used": list(set(t.category for t in self.thought_history if t.category))
        }
    
    def export_session(self) -> Dict[str, Any]:
        """Export the current session for persistence"""
        return {
            "thoughts": [self._thought_to_dict(t) for t in self.thought_history],
            "relationships": self.relationships,
            "branches": {
                branch_id: [self._thought_to_dict(t) for t in thoughts]
                for branch_id, thoughts in self.branches.items()
            },
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "is_complete": self._is_complete,
                "total_thoughts": len(self.thought_history),
                "coherence": self.calculate_coherence(),
                "performance": self.get_performance_metrics()
            }
        }
    
    def import_session(self, session_data: Dict[str, Any]):
        """Import a saved session"""
        self.reset()
        
        # Import thoughts
        for thought_dict in session_data.get("thoughts", []):
            # Convert back to our format
            self.thought_history.append(EnhancedThoughtData(
                thought=thought_dict["thought"],
                thought_number=thought_dict["thoughtNumber"],
                total_thoughts=thought_dict["totalThoughts"],
                next_thought_needed=thought_dict["nextThoughtNeeded"],
                confidence=thought_dict.get("confidence", 0.7),
                timestamp=thought_dict.get("timestamp", datetime.now().isoformat()),
                category=thought_dict.get("category"),
                related_thoughts=thought_dict.get("relatedThoughts", []),
                relationship_type=thought_dict.get("relationshipType"),
                context=thought_dict.get("context", {}),
                warnings=thought_dict.get("warnings", [])
            ))
        
        # Import relationships
        self.relationships = session_data.get("relationships", [])
        
        # Import metadata
        metadata = session_data.get("metadata", {})
        self._is_complete = metadata.get("is_complete", False)
    
    def get_thought_history(self) -> List[Dict[str, Any]]:
        """Get complete thought history"""
        return [self._thought_to_dict(t) for t in self.thought_history]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get enhanced summary with metrics"""
        base_summary = {
            "total_thoughts": len(self.thought_history),
            "branches_created": len(self.branches),
            "is_complete": self._is_complete,
            "relationships": len(self.relationships)
        }
        
        if self.thought_history:
            base_summary.update({
                "final_thought": self.thought_history[-1].thought,
                "average_confidence": sum(t.confidence for t in self.thought_history) / len(self.thought_history),
                "coherence": self.calculate_coherence()["overall_coherence"]
            })
        
        return base_summary
    
    def reset(self):
        """Reset the server"""
        self.thought_history.clear()
        self.branches.clear()
        self.relationships.clear()
        self._is_complete = False
        self.start_time = time.time()
        self.thought_times.clear()
    
    def is_complete(self) -> bool:
        """Check if thinking is complete"""
        return self._is_complete