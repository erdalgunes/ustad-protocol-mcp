"""
Test suite for enhanced sequential thinking features.
Following TDD - write tests for new features first.
"""

import pytest
from datetime import datetime
from typing import Dict, List


class TestEnhancedSequentialThinking:
    """Test enhanced sequential thinking features"""
    
    def test_confidence_scoring(self):
        """Test that thoughts can have confidence scores"""
        from src.sequential_thinking_v2 import EnhancedSequentialThinkingServer
        
        server = EnhancedSequentialThinkingServer()
        
        thought_data = {
            "thought": "Initial analysis with high confidence",
            "thoughtNumber": 1,
            "totalThoughts": 3,
            "nextThoughtNeeded": True,
            "confidence": 0.95  # High confidence
        }
        
        result = server.process_thought(thought_data)
        
        assert "confidence" in result
        assert result["confidence"] == 0.95
        
        # Test default confidence
        thought_data2 = {
            "thought": "Another thought without explicit confidence",
            "thoughtNumber": 2,
            "totalThoughts": 3,
            "nextThoughtNeeded": True
        }
        
        result2 = server.process_thought(thought_data2)
        assert "confidence" in result2
        assert 0 <= result2["confidence"] <= 1  # Should have default value
        
    def test_thought_relationships(self):
        """Test tracking relationships between thoughts"""
        from src.sequential_thinking_v2 import EnhancedSequentialThinkingServer
        
        server = EnhancedSequentialThinkingServer()
        
        # First thought
        thought1 = {
            "thought": "Define the problem",
            "thoughtNumber": 1,
            "totalThoughts": 3,
            "nextThoughtNeeded": True
        }
        server.process_thought(thought1)
        
        # Second thought that builds on first
        thought2 = {
            "thought": "Analyze problem components",
            "thoughtNumber": 2,
            "totalThoughts": 3,
            "nextThoughtNeeded": True,
            "relatedThoughts": [1],  # Relates to thought 1
            "relationshipType": "builds_on"
        }
        result = server.process_thought(thought2)
        
        assert "relatedThoughts" in result
        assert 1 in result["relatedThoughts"]
        assert result["relationshipType"] == "builds_on"
        
        # Get relationship graph
        graph = server.get_thought_relationships()
        assert len(graph) > 0
        assert any(rel["from"] == 2 and rel["to"] == 1 for rel in graph)
        
    def test_metadata_support(self):
        """Test that thoughts include metadata like timestamps"""
        from src.sequential_thinking_v2 import EnhancedSequentialThinkingServer
        
        server = EnhancedSequentialThinkingServer()
        
        thought_data = {
            "thought": "Thought with metadata",
            "thoughtNumber": 1,
            "totalThoughts": 2,
            "nextThoughtNeeded": True,
            "context": {"user": "test_user", "session": "abc123"}
        }
        
        result = server.process_thought(thought_data)
        
        # Should have timestamp
        assert "timestamp" in result
        timestamp = datetime.fromisoformat(result["timestamp"])
        assert isinstance(timestamp, datetime)
        
        # Should preserve context
        assert "context" in result
        assert result["context"]["user"] == "test_user"
        
    def test_thought_categories(self):
        """Test categorization of thoughts"""
        from src.sequential_thinking_v2 import EnhancedSequentialThinkingServer
        
        server = EnhancedSequentialThinkingServer()
        
        thought_data = {
            "thought": "Analyzing the data structure",
            "thoughtNumber": 1,
            "totalThoughts": 3,
            "nextThoughtNeeded": True,
            "category": "analysis"
        }
        
        result = server.process_thought(thought_data)
        
        assert "category" in result
        assert result["category"] == "analysis"
        
        # Test auto-categorization
        thought_data2 = {
            "thought": "Conclusion: The approach is viable",
            "thoughtNumber": 2,
            "totalThoughts": 3,
            "nextThoughtNeeded": False
        }
        
        result2 = server.process_thought(thought_data2)
        assert "category" in result2
        # Should auto-detect as conclusion
        assert result2["category"] == "conclusion"
        
    def test_coherence_validation(self):
        """Test logical coherence validation between thoughts"""
        from src.sequential_thinking_v2 import EnhancedSequentialThinkingServer
        
        server = EnhancedSequentialThinkingServer()
        
        # Add coherent thoughts
        thought1 = {
            "thought": "The system has three main components",
            "thoughtNumber": 1,
            "totalThoughts": 3,
            "nextThoughtNeeded": True
        }
        server.process_thought(thought1)
        
        thought2 = {
            "thought": "Let's analyze the first component in detail",
            "thoughtNumber": 2,
            "totalThoughts": 3,
            "nextThoughtNeeded": True,
            "relatedThoughts": [1]
        }
        result = server.process_thought(thought2)
        
        # Should have coherence score
        coherence = server.calculate_coherence()
        assert "overall_coherence" in coherence
        assert coherence["overall_coherence"] > 0.5  # Should be reasonably coherent
        
    def test_performance_metrics(self):
        """Test tracking of performance metrics"""
        from src.sequential_thinking_v2 import EnhancedSequentialThinkingServer
        import time
        
        server = EnhancedSequentialThinkingServer()
        
        start_time = time.time()
        
        # Process multiple thoughts
        for i in range(1, 4):
            thought = {
                "thought": f"Processing step {i}",
                "thoughtNumber": i,
                "totalThoughts": 3,
                "nextThoughtNeeded": i < 3
            }
            server.process_thought(thought)
        
        metrics = server.get_performance_metrics()
        
        assert "total_thinking_time" in metrics
        assert "average_thought_time" in metrics
        assert "thoughts_per_minute" in metrics
        assert metrics["total_thoughts"] == 3
        
    def test_export_import_session(self):
        """Test exporting and importing thinking sessions"""
        from src.sequential_thinking_v2 import EnhancedSequentialThinkingServer
        
        server1 = EnhancedSequentialThinkingServer()
        
        # Create a session
        thought = {
            "thought": "Test thought for export",
            "thoughtNumber": 1,
            "totalThoughts": 1,
            "nextThoughtNeeded": False,
            "confidence": 0.9
        }
        server1.process_thought(thought)
        
        # Export session
        exported = server1.export_session()
        assert "thoughts" in exported
        assert "metadata" in exported
        assert len(exported["thoughts"]) == 1
        
        # Import into new server
        server2 = EnhancedSequentialThinkingServer()
        server2.import_session(exported)
        
        # Verify import
        history = server2.get_thought_history()
        assert len(history) == 1
        assert history[0]["thought"] == "Test thought for export"
        assert history[0]["confidence"] == 0.9
        
    def test_thought_validation_rules(self):
        """Test validation rules for thought quality"""
        from src.sequential_thinking_v2 import EnhancedSequentialThinkingServer
        
        server = EnhancedSequentialThinkingServer()
        
        # Test thought too short
        short_thought = {
            "thought": "OK",  # Too short
            "thoughtNumber": 1,
            "totalThoughts": 2,
            "nextThoughtNeeded": True
        }
        
        result = server.process_thought(short_thought)
        assert "warnings" in result
        assert any("short" in w.lower() for w in result["warnings"])
        
        # Test thought too long
        long_thought = {
            "thought": "x" * 1001,  # Too long
            "thoughtNumber": 2,
            "totalThoughts": 2,
            "nextThoughtNeeded": False
        }
        
        result = server.process_thought(long_thought)
        assert "warnings" in result
        assert any("long" in w.lower() for w in result["warnings"])