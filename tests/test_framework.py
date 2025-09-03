"""
🧪 Rigorous Testing Framework for Anti-Pattern Detection
=======================================================

Comprehensive testing infrastructure to ensure reliable detection of AI failure patterns.
This framework provides:
- Test data generation for realistic scenarios
- Accuracy measurement and validation
- Performance benchmarking
- Edge case handling verification
- Regression testing capabilities
"""

import statistics
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pytest

from src.ustad.anti_patterns.base import AntiPatternDetector, PatternSeverity


@dataclass
class TestScenario:
    """Test scenario for anti-pattern detection"""

    name: str  # Descriptive name
    conversation_history: list[dict[str, Any]]  # Input conversation
    context: dict[str, Any]  # Additional context
    expected_pattern: str | None  # Expected pattern type (None if no pattern)
    expected_severity: PatternSeverity | None  # Expected severity
    expected_confidence_min: float  # Minimum expected confidence
    description: str  # What this scenario tests
    tags: list[str]  # Test categories (e.g., ["edge_case", "regression"])


class AntiPatternTestSuite:
    """Comprehensive test suite for anti-pattern detectors"""

    def __init__(self):
        self.test_scenarios: list[TestScenario] = []
        self.performance_benchmarks: dict[str, float] = {}
        self.accuracy_requirements = {
            "context_degradation": 0.80,
            "impulsivity": 0.75,
            "task_abandonment": 0.70,
            "over_engineering": 0.75,
            "hallucination": 0.70,
        }

    def add_scenario(self, scenario: TestScenario):
        """Add a test scenario to the suite"""
        self.test_scenarios.append(scenario)

    def test_detector_accuracy(self, detector: AntiPatternDetector) -> dict[str, Any]:
        """Test detector accuracy against all scenarios"""
        results = {
            "total_tests": len(self.test_scenarios),
            "correct_detections": 0,
            "false_positives": 0,
            "false_negatives": 0,
            "accuracy": 0.0,
            "precision": 0.0,
            "recall": 0.0,
            "detailed_results": [],
        }

        for scenario in self.test_scenarios:
            try:
                start_time = time.time()
                alerts = detector.analyze(
                    scenario.conversation_history, scenario.context, f"test_session_{scenario.name}"
                )
                response_time = (time.time() - start_time) * 1000  # ms

                # Evaluate result
                detected_pattern = alerts[0].pattern_type if alerts else None
                detected_severity = alerts[0].severity if alerts else None
                detected_confidence = alerts[0].confidence if alerts else 0.0

                # Check correctness
                correct = self._evaluate_detection(
                    scenario, detected_pattern, detected_severity, detected_confidence
                )

                if correct:
                    results["correct_detections"] += 1
                elif scenario.expected_pattern and not detected_pattern:
                    results["false_negatives"] += 1
                elif not scenario.expected_pattern and detected_pattern:
                    results["false_positives"] += 1

                # Store detailed result
                results["detailed_results"].append(
                    {
                        "scenario": scenario.name,
                        "expected_pattern": scenario.expected_pattern,
                        "detected_pattern": detected_pattern,
                        "expected_severity": scenario.expected_severity.value
                        if scenario.expected_severity
                        else None,
                        "detected_severity": detected_severity.value if detected_severity else None,
                        "confidence": detected_confidence,
                        "response_time_ms": response_time,
                        "correct": correct,
                        "description": scenario.description,
                    }
                )

            except Exception as e:
                results["detailed_results"].append(
                    {"scenario": scenario.name, "error": str(e), "correct": False}
                )

        # Calculate metrics
        total = results["total_tests"]
        correct = results["correct_detections"]
        fp = results["false_positives"]
        fn = results["false_negatives"]

        results["accuracy"] = correct / total if total > 0 else 0.0
        results["precision"] = correct / (correct + fp) if (correct + fp) > 0 else 0.0
        results["recall"] = correct / (correct + fn) if (correct + fn) > 0 else 0.0
        results["f1_score"] = (
            2
            * (results["precision"] * results["recall"])
            / (results["precision"] + results["recall"])
            if (results["precision"] + results["recall"]) > 0
            else 0.0
        )

        return results

    def test_performance_benchmarks(self, detector: AntiPatternDetector) -> dict[str, Any]:
        """Test detector performance against benchmarks"""
        response_times = []
        memory_usage = []

        # Test with various input sizes
        test_sizes = [1, 5, 10, 25, 50]  # Number of conversation exchanges

        performance_results = {
            "detector_name": detector.name,
            "response_times": {},
            "memory_usage": {},
            "meets_requirements": True,
            "requirements": {
                "max_response_time_ms": 2000,  # 2 seconds max
                "max_memory_mb": 100,  # 100MB max
            },
        }

        for size in test_sizes:
            # Create test conversation of specified size
            test_conversation = self._generate_test_conversation(size)
            test_context = {"complexity": "medium", "session_length": size}

            # Measure response time
            start_time = time.time()
            detector.analyze(test_conversation, test_context, f"perf_test_{size}")
            response_time = (time.time() - start_time) * 1000  # Convert to ms

            performance_results["response_times"][f"size_{size}"] = response_time

            # Check against requirements
            if response_time > performance_results["requirements"]["max_response_time_ms"]:
                performance_results["meets_requirements"] = False

        return performance_results

    def test_edge_cases(self, detector: AntiPatternDetector) -> dict[str, Any]:
        """Test detector handling of edge cases"""
        edge_cases = [
            # Empty inputs
            {"conversation": [], "context": {}, "name": "empty_conversation"},
            {
                "conversation": [{"role": "user", "content": ""}],
                "context": {},
                "name": "empty_content",
            },
            # Large inputs
            {
                "conversation": [{"role": "user", "content": "x" * 10000}],
                "context": {},
                "name": "very_long_message",
            },
            # Malformed inputs
            {
                "conversation": [{"invalid": "structure"}],
                "context": {},
                "name": "malformed_structure",
            },
            {"conversation": None, "context": {}, "name": "null_conversation"},
        ]

        results = {
            "total_edge_cases": len(edge_cases),
            "handled_gracefully": 0,
            "errors": [],
            "details": [],
        }

        for edge_case in edge_cases:
            try:
                alerts = detector.analyze(
                    edge_case["conversation"] or [],
                    edge_case["context"],
                    f"edge_test_{edge_case['name']}",
                )
                # If no exception, it was handled gracefully
                results["handled_gracefully"] += 1
                results["details"].append(
                    {"case": edge_case["name"], "handled": True, "alerts_count": len(alerts)}
                )

            except Exception as e:
                results["errors"].append({"case": edge_case["name"], "error": str(e)})
                results["details"].append(
                    {"case": edge_case["name"], "handled": False, "error": str(e)}
                )

        results["graceful_handling_rate"] = (
            results["handled_gracefully"] / results["total_edge_cases"]
        )

        return results

    def run_comprehensive_test(self, detector: AntiPatternDetector) -> dict[str, Any]:
        """Run all tests and generate comprehensive report"""
        print(f"\n🧪 Running comprehensive test suite for {detector.name}")
        print("=" * 60)

        # Run all test categories
        accuracy_results = self.test_detector_accuracy(detector)
        performance_results = self.test_performance_benchmarks(detector)
        edge_case_results = self.test_edge_cases(detector)

        # Generate summary
        overall_results = {
            "detector_name": detector.name,
            "test_timestamp": datetime.now().isoformat(),
            "overall_status": "PASS",
            "accuracy": accuracy_results,
            "performance": performance_results,
            "edge_cases": edge_case_results,
            "summary": {
                "accuracy_score": accuracy_results["accuracy"],
                "meets_performance_req": performance_results["meets_requirements"],
                "edge_case_handling": edge_case_results["graceful_handling_rate"],
                "total_scenarios_tested": len(self.test_scenarios),
            },
        }

        # Determine overall status
        required_accuracy = self.accuracy_requirements.get(detector.name.lower(), 0.70)

        if (
            accuracy_results["accuracy"] < required_accuracy
            or not performance_results["meets_requirements"]
            or edge_case_results["graceful_handling_rate"] < 0.90
        ):
            overall_results["overall_status"] = "FAIL"

        return overall_results

    def _evaluate_detection(
        self,
        scenario: TestScenario,
        detected_pattern: str | None,
        detected_severity: PatternSeverity | None,
        detected_confidence: float,
    ) -> bool:
        """Evaluate if detection matches expected result"""

        # Check pattern detection
        if scenario.expected_pattern != detected_pattern:
            return False

        # If pattern expected, check other criteria
        if scenario.expected_pattern:
            # Check severity (allow some flexibility)
            if scenario.expected_severity and detected_severity:
                severity_levels = {
                    PatternSeverity.LOW: 1,
                    PatternSeverity.MEDIUM: 2,
                    PatternSeverity.HIGH: 3,
                    PatternSeverity.CRITICAL: 4,
                }
                expected_level = severity_levels[scenario.expected_severity]
                detected_level = severity_levels[detected_severity]

                # Allow ±1 level difference
                if abs(expected_level - detected_level) > 1:
                    return False

            # Check minimum confidence
            if detected_confidence < scenario.expected_confidence_min:
                return False

        return True

    def _generate_test_conversation(self, size: int) -> list[dict[str, Any]]:
        """Generate test conversation of specified size"""
        conversation = []
        for i in range(size):
            conversation.append(
                {
                    "role": "user" if i % 2 == 0 else "assistant",
                    "content": f"Test message {i + 1} with some content to analyze.",
                    "timestamp": datetime.now().isoformat(),
                }
            )
        return conversation

    def generate_test_report(self, results: dict[str, Any]) -> str:
        """Generate human-readable test report"""
        report = f"""
🧪 ANTI-PATTERN DETECTOR TEST REPORT
====================================

Detector: {results['detector_name']}
Status: {results['overall_status']}
Test Date: {results['test_timestamp']}

📊 ACCURACY METRICS
- Overall Accuracy: {results['accuracy']['accuracy']:.1%}
- Precision: {results['accuracy']['precision']:.1%}
- Recall: {results['accuracy']['recall']:.1%}
- F1 Score: {results['accuracy']['f1_score']:.1%}
- Scenarios Tested: {results['accuracy']['total_tests']}
- False Positives: {results['accuracy']['false_positives']}
- False Negatives: {results['accuracy']['false_negatives']}

⚡ PERFORMANCE METRICS
- Meets Requirements: {results['performance']['meets_requirements']}
- Max Response Time: {max(results['performance']['response_times'].values()):.1f}ms
- Avg Response Time: {statistics.mean(results['performance']['response_times'].values()):.1f}ms

🛡️ EDGE CASE HANDLING
- Graceful Handling Rate: {results['edge_cases']['graceful_handling_rate']:.1%}
- Edge Cases Tested: {results['edge_cases']['total_edge_cases']}
- Errors: {len(results['edge_cases']['errors'])}

{'✅ ALL TESTS PASSED' if results['overall_status'] == 'PASS' else '❌ TESTS FAILED'}
"""
        return report


# Pre-built test scenarios for common patterns
def create_default_test_scenarios() -> list[TestScenario]:
    """Create default test scenarios for anti-pattern detection"""

    scenarios = [
        # Context degradation scenarios
        TestScenario(
            name="context_drift_basic",
            conversation_history=[
                {"role": "user", "content": "Help me design a REST API for user management"},
                {"role": "assistant", "content": "I'll help you design a user management API..."},
                {"role": "user", "content": "What about database schema?"},
                {
                    "role": "assistant",
                    "content": "Here's a great recipe for chocolate cake...",
                },  # Clear context loss
            ],
            context={"topic": "API design", "session_length": 4},
            expected_pattern="context_degradation",
            expected_severity=PatternSeverity.HIGH,
            expected_confidence_min=0.8,
            description="Clear topic drift from API design to cooking",
            tags=["context", "basic"],
        ),
        # Impulsivity scenarios
        TestScenario(
            name="impulsive_implementation",
            conversation_history=[
                {
                    "role": "user",
                    "content": "I need to build a scalable microservices architecture",
                },
                {
                    "role": "assistant",
                    "content": "Let me immediately start coding the services...",
                },  # No planning
            ],
            context={"complexity": "high", "planning_present": False},
            expected_pattern="impulsivity",
            expected_severity=PatternSeverity.MEDIUM,
            expected_confidence_min=0.7,
            description="Jumping to implementation without planning complex system",
            tags=["impulsivity", "planning"],
        ),
        # Task abandonment scenarios
        TestScenario(
            name="quick_workaround",
            conversation_history=[
                {"role": "user", "content": "The authentication is failing with a complex error"},
                {
                    "role": "assistant",
                    "content": "This looks complicated. Let me just disable authentication for now...",
                },
            ],
            context={"error_present": True, "complexity": "high"},
            expected_pattern="task_abandonment",
            expected_severity=PatternSeverity.HIGH,
            expected_confidence_min=0.8,
            description="Giving up on proper fix and using dangerous workaround",
            tags=["abandonment", "workaround"],
        ),
        # Over-engineering scenarios
        TestScenario(
            name="unnecessary_complexity",
            conversation_history=[
                {"role": "user", "content": "I need a simple function to add two numbers"},
                {
                    "role": "assistant",
                    "content": "Let's build an abstract NumberProcessor factory with dependency injection, strategy patterns, and configuration management...",
                },
            ],
            context={"requirement_complexity": "low", "solution_complexity": "high"},
            expected_pattern="over_engineering",
            expected_severity=PatternSeverity.MEDIUM,
            expected_confidence_min=0.7,
            description="Complex solution for simple requirement",
            tags=["over_engineering", "complexity"],
        ),
        # Hallucination scenarios
        TestScenario(
            name="unverified_technical_claim",
            conversation_history=[
                {"role": "user", "content": "What's the latest Python version?"},
                {
                    "role": "assistant",
                    "content": "Python 3.15 was released last month with amazing new features...",
                },  # Likely false
            ],
            context={"contains_specific_claims": True, "research_used": False},
            expected_pattern="hallucination",
            expected_severity=PatternSeverity.HIGH,
            expected_confidence_min=0.75,
            description="Specific version claim without verification",
            tags=["hallucination", "facts"],
        ),
        # No pattern scenarios (negative tests)
        TestScenario(
            name="healthy_conversation",
            conversation_history=[
                {"role": "user", "content": "Can you help me understand React hooks?"},
                {
                    "role": "assistant",
                    "content": "I'd be happy to explain React hooks. Let me start with the basics...",
                },
            ],
            context={"topic": "React", "appropriate_response": True},
            expected_pattern=None,
            expected_severity=None,
            expected_confidence_min=0.0,
            description="Normal, healthy conversation - should not trigger patterns",
            tags=["negative", "baseline"],
        ),
    ]

    return scenarios


# Pytest fixtures and test functions
@pytest.fixture
def test_suite():
    """Create test suite with default scenarios"""
    suite = AntiPatternTestSuite()
    for scenario in create_default_test_scenarios():
        suite.add_scenario(scenario)
    return suite


class MockDetector(AntiPatternDetector):
    """Mock detector for testing the framework itself"""

    def __init__(self):
        super().__init__("mock_detector", "Test detector for framework validation")

    def analyze(self, conversation_history, current_context, session_id):
        # Simple mock logic - detect pattern if "error" in last message
        if conversation_history and "error" in conversation_history[-1].get("content", "").lower():
            return [
                self.create_alert(
                    "mock_pattern",
                    PatternSeverity.MEDIUM,
                    0.8,
                    "Mock pattern detected",
                    ["Fix the error"],
                    current_context,
                    session_id,
                )
            ]
        return []

    def get_prevention_suggestions(self, alert, context):
        return ["This is a mock suggestion"]


def test_framework_functionality(test_suite):
    """Test the testing framework itself"""
    detector = MockDetector()
    results = test_suite.run_comprehensive_test(detector)

    assert "detector_name" in results
    assert "accuracy" in results
    assert "performance" in results
    assert "edge_cases" in results
    assert results["overall_status"] in ["PASS", "FAIL"]


if __name__ == "__main__":
    # Demo the testing framework
    suite = AntiPatternTestSuite()
    for scenario in create_default_test_scenarios():
        suite.add_scenario(scenario)

    # Test with mock detector
    detector = MockDetector()
    results = suite.run_comprehensive_test(detector)

    print(suite.generate_test_report(results))
