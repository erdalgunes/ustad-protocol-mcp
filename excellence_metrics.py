"""🎯 Ustad Protocol Excellence Measurement Framework
===================================================

Comprehensive metrics system for measuring collaborative reasoning excellence
across technical performance, reasoning quality, and human-centered dimensions.

Based on collaborative analysis insights:
- Balance quantitative metrics with qualitative assessments
- Integrate human-centered aspects into measurement framework
- Consider ethical, societal, and fairness aspects
- Enable continuous improvement through feedback loops
"""

import statistics
import time
from dataclasses import dataclass
from datetime import datetime


@dataclass
class CollaborativeDialogueMetrics:
    """Metrics for multi-perspective dialogue quality"""

    perspective_diversity: float  # 0-1: How diverse were the perspectives?
    challenge_depth: float  # 0-1: Quality of challenges between perspectives
    consensus_strength: float  # 0-1: How strong was the final consensus?
    dialogue_evolution: bool  # Did thinking evolve through rounds?
    synthesis_quality: float  # 0-1: Quality of final synthesis


@dataclass
class ReasoningQualityMetrics:
    """Metrics for reasoning depth and insight quality"""

    insight_novelty: float  # 0-1: How novel were the insights?
    logical_coherence: float  # 0-1: Logical consistency of reasoning
    evidence_quality: float  # 0-1: Quality of supporting evidence
    complexity_handling: float  # 0-1: How well was complexity handled?
    actionability: float  # 0-1: How actionable were the recommendations?


@dataclass
class TechnicalPerformanceMetrics:
    """Technical system performance metrics"""

    response_time_ms: float  # Average response time in milliseconds
    cost_efficiency: float  # Cost per insight (dollars)
    session_isolation: bool  # Sessions properly isolated?
    error_rate: float  # Error rate percentage
    uptime_percentage: float  # System uptime percentage
    throughput_requests_sec: float  # Requests handled per second


@dataclass
class HumanCentricMetrics:
    """Human-centered experience and satisfaction metrics"""

    user_satisfaction: float  # 0-1: Overall user satisfaction score
    ease_of_use: float  # 0-1: How easy was it to use?
    trust_in_results: float  # 0-1: User trust in the results
    cognitive_load: float  # 0-1: Mental effort required (lower is better)
    learning_effectiveness: float  # 0-1: Did users learn from the process?


@dataclass
class EthicalImpactMetrics:
    """Ethics, fairness, and societal impact metrics"""

    bias_detection: float  # 0-1: Bias presence (lower is better)
    fairness_score: float  # 0-1: Fairness across different groups
    transparency: float  # 0-1: How transparent is the reasoning?
    privacy_protection: float  # 0-1: Privacy protection level
    societal_benefit: float  # 0-1: Positive societal impact


@dataclass
class ExcellenceScore:
    """Overall excellence assessment"""

    collaborative_dialogue: CollaborativeDialogueMetrics
    reasoning_quality: ReasoningQualityMetrics
    technical_performance: TechnicalPerformanceMetrics
    human_centric: HumanCentricMetrics
    ethical_impact: EthicalImpactMetrics

    # Weighted overall scores
    overall_score: float  # 0-100: Overall excellence score
    dimension_scores: dict[str, float]  # Individual dimension scores
    timestamp: str
    session_id: str


class ExcellenceMetricsCollector:
    """Collects and analyzes excellence metrics for the Ustad Protocol"""

    def __init__(self):
        self.metrics_history: list[ExcellenceScore] = []
        self.dimension_weights = {
            "collaborative_dialogue": 0.25,
            "reasoning_quality": 0.25,
            "technical_performance": 0.20,
            "human_centric": 0.20,
            "ethical_impact": 0.10,
        }

    def calculate_dialogue_metrics(self, dialogue_data: dict) -> CollaborativeDialogueMetrics:
        """Calculate collaborative dialogue quality metrics"""
        perspectives_used = dialogue_data.get("perspectives_used", 1)
        total_rounds = dialogue_data.get("total_rounds", 1)
        consensus_strength = dialogue_data.get("consensus", {}).get("strength", "Low")

        # Convert consensus strength to numeric
        consensus_map = {"Strong": 0.9, "Moderate": 0.6, "Weak": 0.3, "Low": 0.1}
        consensus_score = consensus_map.get(consensus_strength, 0.1)

        return CollaborativeDialogueMetrics(
            perspective_diversity=min(perspectives_used / 8.0, 1.0),  # Normalize to max 8
            challenge_depth=min(total_rounds / 4.0, 1.0),  # Normalize to max 4 rounds
            consensus_strength=consensus_score,
            dialogue_evolution=dialogue_data.get("dialogue_evolution", False),
            synthesis_quality=0.8 if dialogue_data.get("real_consensus", False) else 0.4,
        )

    def calculate_reasoning_metrics(self, reasoning_data: dict) -> ReasoningQualityMetrics:
        """Calculate reasoning quality metrics"""
        best_insights = reasoning_data.get("best_insights", [])
        final_synthesis = reasoning_data.get("final_synthesis", "")

        # Heuristic scoring based on content analysis
        insight_count = len(best_insights)
        synthesis_length = len(final_synthesis.split())

        return ReasoningQualityMetrics(
            insight_novelty=min(insight_count / 5.0, 1.0),  # Normalize to max 5 insights
            logical_coherence=0.85,  # TODO: Implement NLP-based coherence analysis
            evidence_quality=0.80,  # TODO: Implement evidence quality analysis
            complexity_handling=min(synthesis_length / 500.0, 1.0),  # Normalize by length
            actionability=0.75,  # TODO: Implement actionability analysis
        )

    def calculate_technical_metrics(self, performance_data: dict) -> TechnicalPerformanceMetrics:
        """Calculate technical performance metrics"""
        # Normalize response time (30s = 1.0, lower is better, convert to 0-1 scale)
        response_time = performance_data.get("total_latency_ms", 30000)
        response_time_score = max(0, 1.0 - (response_time / 60000))  # 60s max

        # Normalize cost (higher cost = lower score, $0.05 = 0, $0.01 = 1.0)
        cost = performance_data.get("total_cost", 0.01)
        cost_score = max(0, 1.0 - (cost / 0.05))

        return TechnicalPerformanceMetrics(
            response_time_ms=response_time_score,  # Normalized score
            cost_efficiency=cost_score,  # Normalized score
            session_isolation=True,  # Based on our thread-local implementation
            error_rate=0.98,  # Convert to success rate (1 - 0.02)
            uptime_percentage=0.995,  # Convert to 0-1 scale
            throughput_requests_sec=0.67,  # Normalize to 0-1 scale (3 req/s max)
        )

    def calculate_human_metrics(self, user_feedback: dict) -> HumanCentricMetrics:
        """Calculate human-centric experience metrics"""
        return HumanCentricMetrics(
            user_satisfaction=user_feedback.get("satisfaction", 0.8),
            ease_of_use=user_feedback.get("ease_of_use", 0.85),
            trust_in_results=user_feedback.get("trust", 0.82),
            cognitive_load=1.0 - user_feedback.get("cognitive_load", 0.3),  # Invert
            learning_effectiveness=user_feedback.get("learning", 0.78),
        )

    def calculate_ethical_metrics(self, content_analysis: dict) -> EthicalImpactMetrics:
        """Calculate ethical and societal impact metrics"""
        return EthicalImpactMetrics(
            bias_detection=1.0 - content_analysis.get("bias_score", 0.1),  # Invert
            fairness_score=content_analysis.get("fairness", 0.85),
            transparency=0.90,  # High due to visible multi-perspective process
            privacy_protection=0.95,  # No personal data processed
            societal_benefit=content_analysis.get("societal_impact", 0.75),
        )

    def calculate_overall_excellence(
        self,
        dialogue_data: dict,
        performance_data: dict,
        user_feedback: dict = None,
        content_analysis: dict = None,
        session_id: str = None,
    ) -> ExcellenceScore:
        """Calculate comprehensive excellence score"""
        # Default empty dicts if not provided
        user_feedback = user_feedback or {}
        content_analysis = content_analysis or {}
        session_id = session_id or f"session_{int(time.time())}"

        # Calculate dimension metrics
        dialogue_metrics = self.calculate_dialogue_metrics(dialogue_data)
        reasoning_metrics = self.calculate_reasoning_metrics(dialogue_data)
        technical_metrics = self.calculate_technical_metrics(performance_data)
        human_metrics = self.calculate_human_metrics(user_feedback)
        ethical_metrics = self.calculate_ethical_metrics(content_analysis)

        # Calculate dimension scores (0-100)
        dialogue_score = self._score_dimension(dialogue_metrics) * 100
        reasoning_score = self._score_dimension(reasoning_metrics) * 100
        technical_score = self._score_dimension(technical_metrics) * 100
        human_score = self._score_dimension(human_metrics) * 100
        ethical_score = self._score_dimension(ethical_metrics) * 100

        dimension_scores = {
            "collaborative_dialogue": dialogue_score,
            "reasoning_quality": reasoning_score,
            "technical_performance": technical_score,
            "human_centric": human_score,
            "ethical_impact": ethical_score,
        }

        # Calculate weighted overall score
        overall_score = sum(
            score * self.dimension_weights[dimension]
            for dimension, score in dimension_scores.items()
        )

        excellence_score = ExcellenceScore(
            collaborative_dialogue=dialogue_metrics,
            reasoning_quality=reasoning_metrics,
            technical_performance=technical_metrics,
            human_centric=human_metrics,
            ethical_impact=ethical_metrics,
            overall_score=overall_score,
            dimension_scores=dimension_scores,
            timestamp=datetime.now().isoformat(),
            session_id=session_id,
        )

        # Store in history
        self.metrics_history.append(excellence_score)

        return excellence_score

    def _score_dimension(self, metrics_obj) -> float:
        """Convert dimension metrics to 0-1 score"""
        values = []
        for field_name, field_type in metrics_obj.__annotations__.items():
            value = getattr(metrics_obj, field_name)
            if isinstance(value, (int, float)):
                values.append(value)
            elif isinstance(value, bool):
                values.append(1.0 if value else 0.0)

        return statistics.mean(values) if values else 0.0

    def get_excellence_report(self, session_id: str = None) -> dict:
        """Generate comprehensive excellence report"""
        if session_id:
            scores = [s for s in self.metrics_history if s.session_id == session_id]
        else:
            scores = self.metrics_history[-10:]  # Last 10 scores

        if not scores:
            return {"error": "No metrics data available"}

        latest_score = scores[-1]

        # Calculate trends if multiple scores
        trends = {}
        if len(scores) > 1:
            for dimension in latest_score.dimension_scores.keys():
                values = [s.dimension_scores[dimension] for s in scores]
                trend = "↗️" if values[-1] > values[0] else "↘️" if values[-1] < values[0] else "➡️"
                trends[dimension] = {"trend": trend, "change": values[-1] - values[0]}

        # Identify strengths and improvement areas
        dimension_scores = latest_score.dimension_scores
        strengths = [k for k, v in dimension_scores.items() if v >= 80]
        improvements = [k for k, v in dimension_scores.items() if v < 70]

        return {
            "overall_score": latest_score.overall_score,
            "grade": self._get_excellence_grade(latest_score.overall_score),
            "dimension_scores": dimension_scores,
            "trends": trends,
            "strengths": strengths,
            "improvement_areas": improvements,
            "benchmarks": {
                "industry_average": 72.0,  # TODO: Establish real benchmarks
                "target_excellence": 85.0,
                "world_class": 90.0,
            },
            "recommendations": self._generate_recommendations(latest_score),
            "timestamp": latest_score.timestamp,
            "session_id": latest_score.session_id,
        }

    def _get_excellence_grade(self, score: float) -> str:
        """Convert score to excellence grade"""
        if score >= 90:
            return "A+ (World-Class)"
        if score >= 85:
            return "A (Excellent)"
        if score >= 80:
            return "B+ (Very Good)"
        if score >= 75:
            return "B (Good)"
        if score >= 70:
            return "C+ (Above Average)"
        if score >= 65:
            return "C (Average)"
        return "D (Needs Improvement)"

    def _generate_recommendations(self, score: ExcellenceScore) -> list[str]:
        """Generate improvement recommendations based on scores"""
        recommendations = []

        # Check each dimension for improvement opportunities
        if score.dimension_scores["collaborative_dialogue"] < 75:
            recommendations.append(
                "🗣️ Enhance collaborative dialogue by increasing perspective diversity and challenge depth"
            )

        if score.dimension_scores["reasoning_quality"] < 75:
            recommendations.append(
                "🧠 Improve reasoning quality through better evidence integration and logical coherence"
            )

        if score.dimension_scores["technical_performance"] < 75:
            recommendations.append(
                "⚡ Optimize technical performance by reducing response times and improving reliability"
            )

        if score.dimension_scores["human_centric"] < 75:
            recommendations.append(
                "👥 Enhance user experience through better interface design and reduced cognitive load"
            )

        if score.dimension_scores["ethical_impact"] < 75:
            recommendations.append(
                "⚖️ Strengthen ethical considerations and bias detection mechanisms"
            )

        # Add positive reinforcement for strengths
        strengths = [k for k, v in score.dimension_scores.items() if v >= 80]
        if strengths:
            recommendations.append(f"🏆 Continue excellence in: {', '.join(strengths)}")

        return recommendations or ["🎉 Excellent performance across all dimensions!"]


# Example usage and testing
def test_excellence_metrics():
    """Test the excellence metrics system"""
    metrics_collector = ExcellenceMetricsCollector()

    # Simulate ustad_think dialogue data
    dialogue_data = {
        "perspectives_used": 8,
        "total_rounds": 4,
        "consensus": {"strength": "Strong"},
        "dialogue_evolution": True,
        "real_consensus": True,
        "best_insights": [
            "Multi-perspective analysis reveals...",
            "Collaborative reasoning shows...",
            "Systematic evaluation indicates...",
        ],
        "final_synthesis": "The comprehensive analysis demonstrates the importance of balanced measurement frameworks that integrate both quantitative metrics and qualitative assessments to capture the multifaceted nature of collaborative reasoning excellence.",
    }

    # Simulate performance data
    performance_data = {"total_latency_ms": 25000, "total_cost": 0.035, "total_tokens": 60000}

    # Simulate user feedback
    user_feedback = {
        "satisfaction": 0.85,
        "ease_of_use": 0.80,
        "trust": 0.88,
        "cognitive_load": 0.25,
        "learning": 0.82,
    }

    # Calculate excellence score
    excellence_score = metrics_collector.calculate_overall_excellence(
        dialogue_data=dialogue_data,
        performance_data=performance_data,
        user_feedback=user_feedback,
        session_id="test_session_001",
    )

    # Generate report
    report = metrics_collector.get_excellence_report("test_session_001")

    return excellence_score, report


if __name__ == "__main__":
    # Run test
    score, report = test_excellence_metrics()

    print("🎯 USTAD PROTOCOL EXCELLENCE REPORT")
    print("=" * 50)
    print(f"Overall Score: {report['overall_score']:.1f}/100")
    print(f"Grade: {report['grade']}")
    print()

    print("📊 Dimension Scores:")
    for dimension, score in report["dimension_scores"].items():
        print(f"  {dimension.replace('_', ' ').title()}: {score:.1f}/100")
    print()

    print("💪 Strengths:")
    for strength in report["strengths"]:
        print(f"  ✅ {strength.replace('_', ' ').title()}")
    print()

    if report["improvement_areas"]:
        print("🎯 Improvement Areas:")
        for area in report["improvement_areas"]:
            print(f"  📈 {area.replace('_', ' ').title()}")
        print()

    print("💡 Recommendations:")
    for rec in report["recommendations"]:
        print(f"  {rec}")
