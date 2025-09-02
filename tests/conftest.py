"""
Pytest configuration and shared fixtures for Ustad Protocol testing.
"""

import pytest
import asyncio
from typing import Dict, List, Any
from datetime import datetime
import tempfile
import json

from src.ustad.anti_patterns.base import PatternDetectionEngine, PatternAlert, PatternSeverity
from tests.test_framework import AntiPatternTestSuite, create_default_test_scenarios


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def detection_engine():
    """Create a fresh detection engine for each test."""
    return PatternDetectionEngine()


@pytest.fixture  
def test_suite():
    """Create test suite with default scenarios."""
    suite = AntiPatternTestSuite()
    for scenario in create_default_test_scenarios():
        suite.add_scenario(scenario)
    return suite


@pytest.fixture
def sample_conversation():
    """Generate sample conversation history for testing."""
    return [
        {
            "role": "user",
            "content": "Help me build a REST API for user management",
            "timestamp": "2025-01-01T10:00:00Z"
        },
        {
            "role": "assistant", 
            "content": "I'll help you design a user management API. Let's start with the endpoints...",
            "timestamp": "2025-01-01T10:00:30Z"
        },
        {
            "role": "user",
            "content": "What about authentication?",
            "timestamp": "2025-01-01T10:01:00Z"
        }
    ]


@pytest.fixture
def sample_context():
    """Generate sample context for testing."""
    return {
        "session_id": "test_session_123",
        "topic": "API development",
        "complexity": "medium",
        "user_experience": "intermediate",
        "session_start": "2025-01-01T10:00:00Z",
        "message_count": 3
    }


@pytest.fixture
def sample_alert():
    """Generate sample pattern alert for testing."""
    return PatternAlert(
        pattern_type="test_pattern",
        severity=PatternSeverity.MEDIUM,
        confidence=0.85,
        message="Test pattern detected in conversation",
        recommendations=[
            "Consider using collaborative reasoning",
            "Verify technical claims with research"
        ],
        context={"test": True},
        timestamp=datetime.now(),
        session_id="test_session_123"
    )


@pytest.fixture
def temp_test_data():
    """Create temporary directory with test data files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create sample test data files
        test_data = {
            "conversations": [
                {
                    "id": "conv_1",
                    "messages": [
                        {"role": "user", "content": "Test message 1"},
                        {"role": "assistant", "content": "Test response 1"}
                    ]
                }
            ],
            "patterns": [
                {
                    "pattern_type": "context_degradation",
                    "examples": ["Topic drift", "Context loss"]
                }
            ]
        }
        
        test_file = f"{temp_dir}/test_data.json"
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
            
        yield temp_dir


@pytest.fixture(autouse=True)
def reset_detection_counts():
    """Reset detection counts before each test."""
    # This ensures test isolation
    yield
    # Cleanup after test if needed


# Pytest markers for test organization
pytestmark = [
    pytest.mark.filterwarnings("ignore::DeprecationWarning"),
    pytest.mark.asyncio
]


# Custom assertion helpers
def assert_pattern_detected(alerts: List[PatternAlert], expected_pattern: str):
    """Assert that a specific pattern was detected."""
    pattern_types = [alert.pattern_type for alert in alerts]
    assert expected_pattern in pattern_types, f"Expected pattern '{expected_pattern}' not found in {pattern_types}"


def assert_confidence_above(alerts: List[PatternAlert], min_confidence: float):
    """Assert that alerts have confidence above threshold."""
    for alert in alerts:
        assert alert.confidence >= min_confidence, f"Alert confidence {alert.confidence} below minimum {min_confidence}"


def assert_performance_within_limits(execution_time_ms: float, max_time_ms: float = 2000):
    """Assert that execution time is within performance limits."""
    assert execution_time_ms <= max_time_ms, f"Execution time {execution_time_ms}ms exceeds limit {max_time_ms}ms"


# Test data generators
class ConversationGenerator:
    """Generate realistic conversation data for testing."""
    
    @staticmethod
    def generate_context_drift_conversation(length: int = 5) -> List[Dict[str, Any]]:
        """Generate conversation that exhibits context drift."""
        topics = ["API design", "database schema", "cooking recipes", "space travel", "music theory"]
        conversation = []
        
        for i in range(length):
            topic = topics[min(i, len(topics) - 1)]
            conversation.append({
                "role": "user" if i % 2 == 0 else "assistant",
                "content": f"Let's discuss {topic} and related concepts...",
                "timestamp": f"2025-01-01T10:{i:02d}:00Z"
            })
        
        return conversation
    
    @staticmethod
    def generate_impulsive_conversation() -> List[Dict[str, Any]]:
        """Generate conversation showing impulsive behavior."""
        return [
            {
                "role": "user",
                "content": "I need to build a complex distributed system with high availability",
                "timestamp": "2025-01-01T10:00:00Z"
            },
            {
                "role": "assistant", 
                "content": "Sure! Let me immediately start coding the microservices without any planning or architecture discussion...",
                "timestamp": "2025-01-01T10:00:05Z"  # Very fast response
            }
        ]
    
    @staticmethod
    def generate_abandonment_conversation() -> List[Dict[str, Any]]:
        """Generate conversation showing task abandonment."""
        return [
            {
                "role": "user",
                "content": "The authentication system is throwing complex JWT validation errors",
                "timestamp": "2025-01-01T10:00:00Z"
            },
            {
                "role": "assistant",
                "content": "This looks complicated. Let me just remove authentication entirely for now...",
                "timestamp": "2025-01-01T10:00:30Z"
            }
        ]