"""🧩 Intent Understanding Cognitive Scaffold
==========================================

Supports literal-thinking patterns by helping bridge gaps between explicit requests
and implicit user intentions. Provides scaffolding for understanding context and
subtext that may not be explicitly stated.

Computing Challenge: Literal interpretation without understanding implicit intent
Support Strategy: Intent analysis and context bridging
"""

import re
from typing import Any

from ..anti_patterns.base import CognitiveScaffoldTool, SupportAlert, SupportSeverity


class IntentUnderstandingScaffold(CognitiveScaffoldTool):
    """Scaffolding tool for bridging literal interpretation to intent understanding"""

    def __init__(self):
        super().__init__(
            "intent_understanding",
            "Helps bridge gaps between explicit requests and implicit user intentions",
        )
        self.literal_patterns = [
            r"sometimes it has autistic properties",
            r"doesn't understand your intent",
            r"you're being too literal",
            r"that's not what I meant",
            r"read between the lines",
            r"the real question is",
            r"what I'm really asking",
        ]

        self.intent_indicators = [
            r"I want to understand",
            r"help me figure out",
            r"what should we do about",
            r"how can we improve",
            r"the goal is to",
            r"we need to solve",
        ]

    def analyze(
        self,
        conversation_history: list[dict[str, Any]],
        current_context: dict[str, Any],
        session_id: str,
    ) -> list[SupportAlert]:
        """Analyze conversation for intent understanding support opportunities"""
        if not conversation_history:
            return []

        alerts = []

        # Check for literal interpretation indicators
        literal_signals = self._detect_literal_interpretation_signals(conversation_history)
        if literal_signals:
            alerts.append(
                self._create_literal_interpretation_alert(
                    literal_signals, current_context, session_id
                )
            )

        # Check for implicit intent patterns
        implicit_intent = self._detect_implicit_intent_patterns(conversation_history)
        if implicit_intent:
            alerts.append(
                self._create_implicit_intent_alert(implicit_intent, current_context, session_id)
            )

        # Check for context bridging opportunities
        context_gaps = self._detect_context_bridging_opportunities(conversation_history)
        if context_gaps:
            alerts.append(
                self._create_context_bridging_alert(context_gaps, current_context, session_id)
            )

        return alerts

    def get_scaffolding_suggestions(
        self, alert: SupportAlert, context: dict[str, Any]
    ) -> list[str]:
        """Get specific scaffolding suggestions for intent understanding"""
        if alert.support_type == "literal_interpretation":
            return [
                "Consider using collaborative reasoning to explore deeper user intentions",
                "Ask clarifying questions about the underlying goal",
                "Look for patterns in the user's language that indicate broader context",
                "Use ustad_think to analyze what the user might really be trying to achieve",
            ]

        if alert.support_type == "implicit_intent":
            return [
                "Research the domain to understand common implicit requirements",
                "Use collaborative perspectives to uncover unstated needs",
                "Consider the broader context of what success would look like",
                "Ask about constraints and requirements that haven't been mentioned",
            ]

        if alert.support_type == "context_bridging":
            return [
                "Use LangGraph to create visual intent-mapping workflows",
                "Break down the request into explicit and implicit components",
                "Research similar use cases to identify common unstated requirements",
                "Create a structured intent analysis with collaborative reasoning",
            ]

        return ["Use collaborative reasoning to better understand user intent"]

    def _detect_literal_interpretation_signals(
        self, conversation_history: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        """Detect when user indicates literal interpretation is happening"""
        recent_messages = conversation_history[-5:]  # Last 5 messages

        for message in recent_messages:
            content = message.get("content", "").lower()

            for pattern in self.literal_patterns:
                if re.search(pattern, content):
                    return {
                        "detected_pattern": pattern,
                        "message_content": content,
                        "context": "User indicating literal interpretation without intent understanding",
                    }

        return None

    def _detect_implicit_intent_patterns(
        self, conversation_history: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        """Detect patterns suggesting deeper intent beyond literal request"""
        if len(conversation_history) < 2:
            return None

        user_messages = [msg for msg in conversation_history if msg.get("role") == "user"]

        # Look for evolution in requests that suggests deeper intent
        if len(user_messages) >= 2:
            first_request = user_messages[0].get("content", "").lower()
            latest_request = user_messages[-1].get("content", "").lower()

            # Check for intent indicators in latest messages
            for indicator in self.intent_indicators:
                if re.search(indicator, latest_request):
                    return {
                        "detected_pattern": "implicit_intent_evolution",
                        "first_request": first_request,
                        "latest_request": latest_request,
                        "context": "User requests show evolution suggesting deeper intent",
                    }

        return None

    def _detect_context_bridging_opportunities(
        self, conversation_history: list[dict[str, Any]]
    ) -> dict[str, Any] | None:
        """Detect opportunities where context bridging would help"""
        recent_messages = conversation_history[-3:]

        # Look for short, terse responses that might miss context
        assistant_messages = [msg for msg in recent_messages if msg.get("role") == "assistant"]

        for msg in assistant_messages:
            content = msg.get("content", "")

            # Very short responses might indicate literal interpretation
            if len(content.split()) < 10:
                return {
                    "detected_pattern": "terse_response",
                    "response_content": content,
                    "context": "Short response might indicate missing broader context",
                }

        # Look for user clarifications or corrections
        user_messages = [msg for msg in recent_messages if msg.get("role") == "user"]

        correction_patterns = [
            r"no, what I meant",
            r"that's not quite right",
            r"let me clarify",
            r"I think you misunderstood",
            r"actually, I need",
        ]

        for msg in user_messages:
            content = msg.get("content", "").lower()
            for pattern in correction_patterns:
                if re.search(pattern, content):
                    return {
                        "detected_pattern": "user_clarification",
                        "clarification": content,
                        "context": "User providing clarification suggests intent was initially missed",
                    }

        return None

    def _create_literal_interpretation_alert(
        self, signals: dict[str, Any], context: dict[str, Any], session_id: str
    ) -> SupportAlert:
        """Create alert for literal interpretation support"""
        return self.create_support_alert(
            support_type="literal_interpretation",
            severity=SupportSeverity.MEDIUM,
            confidence=0.8,
            message=f"Literal interpretation detected: {signals['detected_pattern']}",
            recommendations=[
                "Use collaborative reasoning to explore deeper user intentions",
                "Consider implicit requirements and broader context",
                "Ask clarifying questions about the underlying goal",
            ],
            context={
                **context,
                "literal_signals": signals,
                "scaffolding_type": "intent_understanding",
            },
            session_id=session_id,
        )

    def _create_implicit_intent_alert(
        self, implicit_data: dict[str, Any], context: dict[str, Any], session_id: str
    ) -> SupportAlert:
        """Create alert for implicit intent support"""
        return self.create_support_alert(
            support_type="implicit_intent",
            severity=SupportSeverity.MEDIUM,
            confidence=0.75,
            message="Implicit intent patterns detected in user requests",
            recommendations=[
                "Research the domain to understand common implicit requirements",
                "Use collaborative perspectives to uncover unstated needs",
                "Consider the broader context of what success would look like",
            ],
            context={
                **context,
                "implicit_patterns": implicit_data,
                "scaffolding_type": "intent_understanding",
            },
            session_id=session_id,
        )

    def _create_context_bridging_alert(
        self, bridge_data: dict[str, Any], context: dict[str, Any], session_id: str
    ) -> SupportAlert:
        """Create alert for context bridging support"""
        return self.create_support_alert(
            support_type="context_bridging",
            severity=SupportSeverity.HIGH,
            confidence=0.85,
            message="Context bridging opportunity identified",
            recommendations=[
                "Use LangGraph to create visual intent-mapping workflows",
                "Break down the request into explicit and implicit components",
                "Create a structured intent analysis with collaborative reasoning",
            ],
            context={
                **context,
                "bridge_opportunity": bridge_data,
                "scaffolding_type": "intent_understanding",
            },
            session_id=session_id,
        )
