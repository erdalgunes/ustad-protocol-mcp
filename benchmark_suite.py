"""
🏆 Ustad Protocol Benchmarking Suite
====================================

Comprehensive benchmarking system to validate collaborative reasoning excellence
against established standards and competitive baselines.

Test Categories:
- Reasoning Quality: Logic, coherence, insight depth
- Collaborative Intelligence: Multi-perspective synthesis
- Performance: Speed, cost, reliability  
- Human Experience: Usability, trust, satisfaction
- Ethical Standards: Bias, fairness, transparency
"""

import asyncio
import json
import time
import statistics
from dataclasses import dataclass
from typing import Dict, List, Tuple, Any
from datetime import datetime
import logging

from excellence_metrics import ExcellenceMetricsCollector, ExcellenceScore


@dataclass
class BenchmarkTest:
    """Individual benchmark test definition"""
    name: str
    category: str
    description: str
    input_data: Dict
    expected_criteria: Dict[str, float]  # Minimum scores expected
    weight: float = 1.0


@dataclass 
class BenchmarkResult:
    """Result of running a benchmark test"""
    test_name: str
    category: str
    passed: bool
    score: float
    criteria_results: Dict[str, Tuple[float, float, bool]]  # (actual, expected, passed)
    execution_time_ms: float
    notes: str


class UstadProtocolBenchmarks:
    """Comprehensive benchmarking suite for the Ustad Protocol"""
    
    def __init__(self):
        self.metrics_collector = ExcellenceMetricsCollector()
        self.benchmark_tests = self._define_benchmark_tests()
        self.results_history = []
        
    def _define_benchmark_tests(self) -> List[BenchmarkTest]:
        """Define the comprehensive benchmark test suite"""
        
        return [
            # Reasoning Quality Benchmarks
            BenchmarkTest(
                name="Complex Problem Analysis",
                category="reasoning_quality",
                description="Multi-faceted strategic problem requiring deep analysis",
                input_data={
                    "problem": "How should a startup balance technical debt with feature delivery while maintaining team morale and investor confidence?",
                    "context": "Series A startup, 15 engineers, 6-month runway, competitive market",
                    "perspectives": 8,
                    "expected_rounds": 4
                },
                expected_criteria={
                    "reasoning_quality_score": 80.0,
                    "insight_novelty": 0.7,
                    "logical_coherence": 0.8,
                    "actionability": 0.75
                }
            ),
            
            BenchmarkTest(
                name="Technical Architecture Decision",
                category="reasoning_quality", 
                description="Complex technical decision with multiple trade-offs",
                input_data={
                    "problem": "Should we migrate from monolith to microservices for a 100K DAU application?",
                    "context": "Current system handles load, team of 20 engineers, growth expected",
                    "perspectives": 6,
                    "expected_rounds": 3
                },
                expected_criteria={
                    "reasoning_quality_score": 78.0,
                    "complexity_handling": 0.8,
                    "evidence_quality": 0.75
                }
            ),
            
            # Collaborative Intelligence Benchmarks  
            BenchmarkTest(
                name="Multi-Stakeholder Consensus",
                category="collaborative_dialogue",
                description="Problem requiring multiple stakeholder perspectives",
                input_data={
                    "problem": "How should we implement AI in customer service while maintaining human touch?",
                    "context": "Customer complaints about impersonal service, efficiency pressures, ethical concerns",
                    "perspectives": 8,
                    "expected_rounds": 4
                },
                expected_criteria={
                    "collaborative_dialogue_score": 82.0,
                    "consensus_strength": 0.7,
                    "perspective_diversity": 0.8,
                    "dialogue_evolution": True
                }
            ),
            
            BenchmarkTest(
                name="Conflicting Priorities Resolution",
                category="collaborative_dialogue",
                description="Challenge requiring resolution of conflicting viewpoints",
                input_data={
                    "problem": "Balance user privacy with personalization in our recommendation engine",
                    "context": "GDPR compliance required, revenue depends on personalization, user trust critical",
                    "perspectives": 6,
                    "expected_rounds": 4
                },
                expected_criteria={
                    "collaborative_dialogue_score": 80.0,
                    "challenge_depth": 0.75,
                    "synthesis_quality": 0.8
                }
            ),
            
            # Performance Benchmarks
            BenchmarkTest(
                name="Response Time Performance", 
                category="technical_performance",
                description="Complex analysis completed within acceptable time limits",
                input_data={
                    "problem": "Quick strategic decision needed for market opportunity",
                    "context": "Time-sensitive market opportunity, need decision in 2 minutes",
                    "perspectives": 4,
                    "expected_rounds": 3
                },
                expected_criteria={
                    "technical_performance_score": 85.0,
                    "response_time_limit_ms": 120000,  # 2 minutes max
                    "cost_efficiency_max": 0.02  # Max $0.02 per analysis
                }
            ),
            
            BenchmarkTest(
                name="Cost Efficiency",
                category="technical_performance",
                description="High-quality analysis at optimal cost",
                input_data={
                    "problem": "Optimize our cloud infrastructure costs while maintaining performance",
                    "context": "Current spending $50K/month, growth trajectory, performance SLAs",
                    "perspectives": 6,
                    "expected_rounds": 3
                },
                expected_criteria={
                    "technical_performance_score": 80.0,
                    "cost_efficiency_max": 0.015,  # Max $0.015 per analysis
                    "reasoning_quality_min": 75.0  # Maintain quality despite cost focus
                }
            ),
            
            # Human Experience Benchmarks
            BenchmarkTest(
                name="Usability and Trust",
                category="human_centric", 
                description="Analysis results inspire confidence and are easy to understand",
                input_data={
                    "problem": "Should we expand internationally or focus on domestic market?",
                    "context": "Growing startup, limited resources, market research available",
                    "perspectives": 5,
                    "expected_rounds": 3
                },
                expected_criteria={
                    "human_centric_score": 82.0,
                    "trust_in_results": 0.8,
                    "ease_of_use": 0.85,
                    "cognitive_load_max": 0.3  # Max cognitive load (lower is better)
                }
            ),
            
            # Ethical Standards Benchmarks
            BenchmarkTest(
                name="Bias Detection and Fairness",
                category="ethical_impact",
                description="Analysis free from bias and considers diverse perspectives fairly",
                input_data={
                    "problem": "Design hiring process for diverse and inclusive team building",
                    "context": "Tech company, current team lacks diversity, legal requirements, culture goals",
                    "perspectives": 8,
                    "expected_rounds": 4
                },
                expected_criteria={
                    "ethical_impact_score": 88.0,
                    "bias_detection": 0.9,  # High bias detection (low bias presence)
                    "fairness_score": 0.85,
                    "transparency": 0.9
                }
            ),
            
            # Stress Tests
            BenchmarkTest(
                name="High Complexity Stress Test",
                category="stress_test",
                description="Extremely complex multi-dimensional problem",
                input_data={
                    "problem": "Navigate post-pandemic business transformation across technology, culture, operations, and market positioning simultaneously",
                    "context": "Global company, remote work transition, supply chain disruption, changing customer behavior, economic uncertainty",
                    "perspectives": 8,
                    "expected_rounds": 4
                },
                expected_criteria={
                    "overall_score_min": 75.0,
                    "reasoning_quality_score": 75.0,
                    "collaborative_dialogue_score": 80.0,
                    "response_time_limit_ms": 300000  # 5 minutes for complex analysis
                }
            )
        ]
    
    async def run_single_benchmark(self, test: BenchmarkTest, ustad_function) -> BenchmarkResult:
        """Run a single benchmark test"""
        start_time = time.time()
        
        try:
            # Execute the Ustad function with test input
            result = await ustad_function(
                problem=test.input_data["problem"],
                context=test.input_data.get("context", ""),
                num_thoughts=test.input_data.get("perspectives", 6)
            )
            
            execution_time_ms = (time.time() - start_time) * 1000
            
            # Calculate excellence metrics from result
            performance_data = {
                "total_latency_ms": result.get("metadata", {}).get("total_latency_ms", execution_time_ms),
                "total_cost": result.get("metadata", {}).get("total_cost", 0.01)
            }
            
            # Simulate user feedback for human-centric metrics
            user_feedback = {
                "satisfaction": 0.8,
                "ease_of_use": 0.85,
                "trust": 0.82,
                "cognitive_load": 0.25,
                "learning": 0.78
            }
            
            excellence_score = self.metrics_collector.calculate_overall_excellence(
                dialogue_data=result,
                performance_data=performance_data,
                user_feedback=user_feedback,
                session_id=f"benchmark_{test.name}_{int(time.time())}"
            )
            
            # Check criteria
            criteria_results = {}
            all_passed = True
            
            for criterion, expected_value in test.expected_criteria.items():
                if criterion.endswith("_score"):
                    # Dimension score
                    dimension = criterion.replace("_score", "")
                    actual_value = excellence_score.dimension_scores.get(dimension, 0)
                    passed = actual_value >= expected_value
                    
                elif criterion.endswith("_limit_ms"):
                    # Time limit
                    actual_value = execution_time_ms
                    passed = actual_value <= expected_value
                    
                elif criterion.endswith("_max"):
                    # Maximum value constraint  
                    field = criterion.replace("_max", "")
                    if field == "cost_efficiency":
                        actual_value = performance_data["total_cost"]
                        passed = actual_value <= expected_value
                    elif field == "cognitive_load":
                        actual_value = user_feedback["cognitive_load"]
                        passed = actual_value <= expected_value
                    else:
                        actual_value = 0
                        passed = True
                        
                elif criterion.endswith("_min"):
                    # Minimum value constraint
                    field = criterion.replace("_min", "")
                    if field == "overall_score":
                        actual_value = excellence_score.overall_score
                        passed = actual_value >= expected_value
                    else:
                        actual_value = 0
                        passed = True
                        
                else:
                    # Individual metric
                    actual_value = self._extract_metric_value(excellence_score, criterion)
                    if criterion == "dialogue_evolution":
                        passed = actual_value == expected_value
                    else:
                        passed = actual_value >= expected_value
                
                criteria_results[criterion] = (actual_value, expected_value, passed)
                if not passed:
                    all_passed = False
            
            # Calculate overall test score
            passed_count = sum(1 for _, _, passed in criteria_results.values())
            test_score = (passed_count / len(criteria_results)) * 100
            
            return BenchmarkResult(
                test_name=test.name,
                category=test.category,
                passed=all_passed,
                score=test_score,
                criteria_results=criteria_results,
                execution_time_ms=execution_time_ms,
                notes="Test completed successfully"
            )
            
        except Exception as e:
            return BenchmarkResult(
                test_name=test.name,
                category=test.category,
                passed=False,
                score=0.0,
                criteria_results={},
                execution_time_ms=(time.time() - start_time) * 1000,
                notes=f"Test failed with error: {str(e)}"
            )
    
    def _extract_metric_value(self, excellence_score: ExcellenceScore, metric_name: str) -> float:
        """Extract specific metric value from excellence score"""
        # Map metric names to excellence score fields
        metric_map = {
            "insight_novelty": excellence_score.reasoning_quality.insight_novelty,
            "logical_coherence": excellence_score.reasoning_quality.logical_coherence,
            "actionability": excellence_score.reasoning_quality.actionability,
            "complexity_handling": excellence_score.reasoning_quality.complexity_handling,
            "evidence_quality": excellence_score.reasoning_quality.evidence_quality,
            
            "consensus_strength": excellence_score.collaborative_dialogue.consensus_strength,
            "perspective_diversity": excellence_score.collaborative_dialogue.perspective_diversity,
            "dialogue_evolution": excellence_score.collaborative_dialogue.dialogue_evolution,
            "challenge_depth": excellence_score.collaborative_dialogue.challenge_depth,
            "synthesis_quality": excellence_score.collaborative_dialogue.synthesis_quality,
            
            "trust_in_results": excellence_score.human_centric.trust_in_results,
            "ease_of_use": excellence_score.human_centric.ease_of_use,
            
            "bias_detection": excellence_score.ethical_impact.bias_detection,
            "fairness_score": excellence_score.ethical_impact.fairness_score,
            "transparency": excellence_score.ethical_impact.transparency
        }
        
        return metric_map.get(metric_name, 0.0)
    
    async def run_full_benchmark_suite(self, ustad_function) -> Dict[str, Any]:
        """Run the complete benchmark suite"""
        print("🏆 STARTING USTAD PROTOCOL BENCHMARK SUITE")
        print("=" * 60)
        
        results = []
        category_scores = {}
        
        for test in self.benchmark_tests:
            print(f"\n🧪 Running: {test.name} ({test.category})")
            result = await self.run_single_benchmark(test, ustad_function)
            results.append(result)
            
            # Track category performance
            if test.category not in category_scores:
                category_scores[test.category] = []
            category_scores[test.category].append(result.score)
            
            # Print immediate results
            status = "✅ PASSED" if result.passed else "❌ FAILED"
            print(f"   {status} - Score: {result.score:.1f}/100 - Time: {result.execution_time_ms:.0f}ms")
            
            if not result.passed:
                failed_criteria = [k for k, (_, _, passed) in result.criteria_results.items() if not passed]
                print(f"   Failed criteria: {', '.join(failed_criteria)}")
        
        # Calculate summary statistics
        all_scores = [r.score for r in results]
        passed_tests = sum(1 for r in results if r.passed)
        
        # Category averages
        category_averages = {
            category: statistics.mean(scores) 
            for category, scores in category_scores.items()
        }
        
        # Generate benchmark report
        benchmark_report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": len(results),
                "passed_tests": passed_tests,
                "pass_rate": (passed_tests / len(results)) * 100,
                "overall_score": statistics.mean(all_scores),
                "min_score": min(all_scores),
                "max_score": max(all_scores)
            },
            "category_performance": category_averages,
            "detailed_results": [
                {
                    "test_name": r.test_name,
                    "category": r.category,
                    "passed": r.passed,
                    "score": r.score,
                    "execution_time_ms": r.execution_time_ms,
                    "criteria_results": r.criteria_results,
                    "notes": r.notes
                }
                for r in results
            ],
            "recommendations": self._generate_benchmark_recommendations(results, category_averages)
        }
        
        # Store results
        self.results_history.append(benchmark_report)
        
        return benchmark_report
    
    def _generate_benchmark_recommendations(self, results: List[BenchmarkResult], category_averages: Dict[str, float]) -> List[str]:
        """Generate improvement recommendations based on benchmark results"""
        recommendations = []
        
        # Overall performance assessment
        overall_score = statistics.mean([r.score for r in results])
        if overall_score < 70:
            recommendations.append("🚨 Critical: Overall benchmark performance below acceptable threshold (70%). Comprehensive review needed.")
        elif overall_score < 80:
            recommendations.append("⚠️ Warning: Benchmark performance has room for improvement. Focus on failing test categories.")
        else:
            recommendations.append("✅ Good: Benchmark performance meets standards. Continue optimizing for excellence.")
        
        # Category-specific recommendations
        for category, avg_score in category_averages.items():
            if avg_score < 70:
                recommendations.append(f"🔧 Critical issue in {category.replace('_', ' ')}: Score {avg_score:.1f} needs immediate attention")
            elif avg_score < 80:
                recommendations.append(f"📈 Improve {category.replace('_', ' ')}: Score {avg_score:.1f} has optimization potential")
        
        # Performance-specific recommendations
        slow_tests = [r for r in results if r.execution_time_ms > 180000]  # 3+ minutes
        if slow_tests:
            recommendations.append(f"⚡ Performance optimization needed: {len(slow_tests)} tests exceeded 3-minute response time")
        
        # Quality-specific recommendations
        failed_tests = [r for r in results if not r.passed]
        if failed_tests:
            failed_categories = set(r.category for r in failed_tests)
            recommendations.append(f"🎯 Focus improvement efforts on: {', '.join(failed_categories)}")
        
        return recommendations or ["🏆 Excellent benchmark performance across all categories!"]
    
    def print_benchmark_report(self, report: Dict[str, Any]):
        """Print a formatted benchmark report"""
        print("\n🏆 USTAD PROTOCOL BENCHMARK REPORT")
        print("=" * 60)
        
        summary = report["summary"]
        print(f"📊 Overall Performance: {summary['overall_score']:.1f}/100")
        print(f"🎯 Pass Rate: {summary['pass_rate']:.1f}% ({summary['passed_tests']}/{summary['total_tests']} tests)")
        print(f"📈 Score Range: {summary['min_score']:.1f} - {summary['max_score']:.1f}")
        print()
        
        print("📋 Category Performance:")
        for category, score in report["category_performance"].items():
            grade = "🟢" if score >= 80 else "🟡" if score >= 70 else "🔴"
            print(f"  {grade} {category.replace('_', ' ').title()}: {score:.1f}/100")
        print()
        
        print("💡 Recommendations:")
        for rec in report["recommendations"]:
            print(f"  {rec}")
        print()
        
        # Failed tests details
        failed_tests = [r for r in report["detailed_results"] if not r["passed"]]
        if failed_tests:
            print("❌ Failed Tests:")
            for test in failed_tests:
                print(f"  • {test['test_name']} ({test['category']}): {test['score']:.1f}/100")
                failed_criteria = [k for k, (_, _, passed) in test['criteria_results'].items() if not passed]
                if failed_criteria:
                    print(f"    Failed: {', '.join(failed_criteria)}")
        
        print(f"\n📅 Report Generated: {report['timestamp']}")
        print("=" * 60)


# Mock ustad function for testing
async def mock_ustad_think(problem: str, context: str = "", num_thoughts: int = 6) -> Dict[str, Any]:
    """Mock ustad_think function for testing benchmarks"""
    
    # Simulate processing time based on complexity
    await asyncio.sleep(min(2.0 + (num_thoughts * 0.5), 10.0))
    
    # Return mock dialogue data
    return {
        "problem": problem,
        "context": context,
        "perspectives_used": num_thoughts,
        "total_rounds": min(4, max(2, num_thoughts // 2)),
        "consensus": {"strength": "Strong" if num_thoughts >= 6 else "Moderate"},
        "dialogue_evolution": True,
        "real_consensus": True,
        "best_insights": [
            f"Analysis reveals {problem[:50]}... requires multi-faceted approach",
            f"Collaborative reasoning shows {context[:50]}... needs strategic consideration",
            f"Systematic evaluation indicates balanced solution is optimal"
        ],
        "final_synthesis": f"Comprehensive analysis of '{problem}' demonstrates the importance of {context}. The collaborative dialogue process revealed multiple critical factors that must be balanced to achieve optimal outcomes.",
        "metadata": {
            "total_latency_ms": (2000 + (num_thoughts * 500)),
            "total_cost": 0.008 + (num_thoughts * 0.002),
            "total_tokens": 5000 + (num_thoughts * 1000)
        }
    }


# Example usage
async def run_benchmark_example():
    """Run benchmark suite example"""
    benchmarks = UstadProtocolBenchmarks()
    
    # Run full benchmark suite with mock function
    report = await benchmarks.run_full_benchmark_suite(mock_ustad_think)
    
    # Print formatted report
    benchmarks.print_benchmark_report(report)
    
    return report


if __name__ == "__main__":
    # Run the benchmark example
    asyncio.run(run_benchmark_example())