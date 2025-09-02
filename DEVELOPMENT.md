# 🛠️ Development Workflow - Ustad Protocol Anti-Pattern Detection

## 🎯 Overview

This document outlines the parallel development workflow for building anti-pattern detection tools. Each tool can be developed independently using git worktrees while maintaining rigorous testing standards.

## 📁 Project Structure

```
ustad-protocol/
├── src/ustad/anti_patterns/          # Core framework
│   ├── __init__.py                   # Framework exports
│   ├── base.py                       # Base classes and utilities
│   ├── context_degradation.py        # Context degradation detector
│   ├── impulsivity.py                # Impulsivity detector  
│   ├── task_abandonment.py           # Task abandonment detector
│   ├── over_engineering.py           # Over-engineering detector
│   └── hallucination.py              # Hallucination detector
├── tests/                            # Comprehensive test suite
│   ├── conftest.py                   # Test configuration
│   ├── test_framework.py             # Testing framework
│   └── test_*.py                     # Individual tool tests
├── scripts/                          # Development utilities
│   └── run_tests.py                  # Test runner
└── ../ustad-worktrees/               # Parallel development
    ├── context-degradation/          # Issue #1 worktree
    ├── impulsivity-detection/         # Issue #2 worktree
    ├── task-abandonment/              # Issue #3 worktree
    ├── over-engineering/              # Issue #4 worktree
    ├── hallucination-detection/       # Issue #5 worktree
    └── integration/                   # Issue #6 worktree
```

## 🚀 Getting Started

### 1. Choose Your Issue

Pick an anti-pattern detection tool to work on:
- **Issue #1**: 🧠 Context Degradation Prevention Tool
- **Issue #2**: ⚡ Impulsivity Detection and Prevention Tool  
- **Issue #3**: 💪 Task Abandonment Prevention Tool
- **Issue #4**: 🏗️ Over-Engineering Detection Tool
- **Issue #5**: 🔍 Hallucination Detection Tool

### 2. Navigate to Your Worktree

```bash
# For context degradation tool (Issue #1)
cd ../ustad-worktrees/context-degradation

# For impulsivity detection tool (Issue #2)  
cd ../ustad-worktrees/impulsivity-detection

# etc...
```

### 3. Set Up Development Environment

```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-test.txt

# Verify setup
python -m pytest tests/ --collect-only
```

## 🧪 Testing Requirements

**Every tool MUST pass rigorous testing before integration:**

### Accuracy Requirements
- **Context Degradation**: >80% accuracy
- **Impulsivity Detection**: >75% accuracy  
- **Task Abandonment**: >70% accuracy
- **Over-Engineering**: >75% accuracy
- **Hallucination Detection**: >70% accuracy

### Performance Requirements
- **Response Time**: <2000ms for analysis
- **Memory Usage**: <100MB
- **Error Handling**: >90% graceful handling rate

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: Framework integration
- **Accuracy Tests**: Detection accuracy validation  
- **Performance Tests**: Speed and resource benchmarks
- **Edge Case Tests**: Error handling and robustness

## 🔧 Development Process

### 1. Implement Your Detector

Create your detector class inheriting from `AntiPatternDetector`:

```python
from src.ustad.anti_patterns.base import AntiPatternDetector, PatternAlert, PatternSeverity

class YourPatternDetector(AntiPatternDetector):
    def __init__(self):
        super().__init__("your_pattern", "Description of your pattern")
        
    def analyze(self, conversation_history, current_context, session_id):
        # Implement pattern detection logic
        alerts = []
        
        if self._detect_pattern(conversation_history, current_context):
            alert = self.create_alert(
                pattern_type="your_pattern",
                severity=PatternSeverity.MEDIUM,
                confidence=0.85,
                message="Pattern detected",
                recommendations=["Specific action to take"],
                context=current_context,
                session_id=session_id
            )
            alerts.append(alert)
            
        return alerts
        
    def get_prevention_suggestions(self, alert, context):
        return ["Actionable prevention suggestions"]
        
    def _detect_pattern(self, conversation, context):
        # Your detection logic here
        return False
```

### 2. Write Comprehensive Tests

```python
import pytest
from tests.test_framework import AntiPatternTestSuite, TestScenario
from your_detector import YourPatternDetector

class TestYourPatternDetector:
    
    def test_basic_detection(self):
        detector = YourPatternDetector()
        conversation = [...]  # Test conversation
        context = {...}       # Test context
        
        alerts = detector.analyze(conversation, context, "test_session")
        
        assert len(alerts) > 0
        assert alerts[0].pattern_type == "your_pattern"
        assert alerts[0].confidence >= 0.7
    
    def test_accuracy_requirements(self):
        suite = AntiPatternTestSuite()
        suite.add_scenario(TestScenario(...))  # Add test scenarios
        
        detector = YourPatternDetector()
        results = suite.test_detector_accuracy(detector)
        
        assert results["accuracy"] >= 0.75  # Your accuracy requirement
    
    def test_performance_benchmarks(self):
        suite = AntiPatternTestSuite()
        detector = YourPatternDetector()
        
        results = suite.test_performance_benchmarks(detector)
        assert results["meets_requirements"] == True
```

### 3. Run Tests Frequently

```bash
# Run all tests for your detector
python scripts/run_tests.py --test-type all --verbose

# Run only accuracy tests  
python scripts/run_tests.py --test-type accuracy --validate-accuracy

# Run with coverage
python scripts/run_tests.py --coverage

# Quick test during development
python -m pytest tests/test_your_detector.py -v
```

### 4. Validate Before Committing

```bash
# Comprehensive validation
python scripts/run_tests.py --test-type all --validate-accuracy --coverage

# Must show:
# - All tests passed ✅
# - Accuracy requirements met ✅  
# - Performance requirements met ✅
# - Coverage >80% ✅
```

## 📋 Quality Gates

**Before merging your branch, ensure:**

- [ ] **All tests pass** with required accuracy levels
- [ ] **Performance benchmarks** met (<2s response time)  
- [ ] **Code coverage** >80%
- [ ] **Edge cases** handled gracefully (>90% rate)
- [ ] **Documentation** updated with usage examples
- [ ] **Integration tests** pass with existing framework
- [ ] **GitHub issue** requirements fully addressed

## 🔄 Integration Process

Once your detector is complete:

### 1. Create Pull Request
```bash
git add .
git commit -m "feat: implement [pattern-name] detection tool

- Achieves [X]% accuracy on test scenarios
- Meets <2s performance requirements  
- Handles edge cases gracefully
- Integrates with MCP framework

Resolves #[issue-number]"

git push origin feature/your-branch-name
```

### 2. Integration Testing
The integration team (Issue #6) will:
- Add your detector to main MCP server
- Test SSE transport compatibility
- Validate real-time monitoring
- Performance test with all detectors

### 3. Final Validation
```bash
# Integration tests
cd ../ustad-worktrees/integration
python scripts/run_tests.py --test-type integration --verbose
```

## 🐛 Debugging and Troubleshooting

### Common Issues

**Low Accuracy**
```bash
# Debug with detailed test results
python scripts/run_tests.py --test-type accuracy --verbose
# Review failed scenarios in test output
# Adjust detection logic and thresholds
```

**Performance Issues**
```bash
# Profile your detector
python -m pytest tests/ --benchmark-only
# Optimize expensive operations
# Consider caching or preprocessing
```

**Integration Problems**
```bash
# Test framework compatibility
python -m pytest tests/test_framework.py -v
# Verify base class implementation
# Check method signatures match interface
```

## 📊 Monitoring and Metrics

### Development Metrics
- Detection accuracy per pattern type
- False positive/negative rates  
- Response time distribution
- Memory usage patterns
- Error handling coverage

### Success Criteria
- **Accuracy**: Meets minimum thresholds
- **Performance**: <2s response time consistently
- **Reliability**: >99% uptime in testing
- **Usability**: Clear, actionable recommendations

## 🤝 Collaboration

### Communication
- Use GitHub issues for feature discussions
- Tag relevant team members in PRs
- Update issue status regularly
- Share test results and benchmarks

### Code Review Checklist
- [ ] Follows `AntiPatternDetector` interface
- [ ] Comprehensive test coverage
- [ ] Performance requirements met
- [ ] Clear documentation and examples
- [ ] Error handling implemented
- [ ] Integration compatibility verified

## 🎯 Success Definition

**A successful anti-pattern detection tool:**
1. **Accurately detects** the target failure pattern
2. **Provides actionable** prevention recommendations  
3. **Integrates seamlessly** with the Ustad Protocol MCP
4. **Performs efficiently** in real-time scenarios
5. **Handles errors gracefully** without breaking the system
6. **Improves user outcomes** through proactive guidance

---

**Ready to build better AI through collaborative reasoning!** 🚀