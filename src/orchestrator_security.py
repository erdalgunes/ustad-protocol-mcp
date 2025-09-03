"""Security and practical safeguards for the Sequential Thinking Orchestrator.
Implements API key management, rate limiting, cost tracking, and data sanitization.
"""

import asyncio
import os
import time
from collections import defaultdict
from dataclasses import dataclass
from functools import wraps
from typing import Any


@dataclass
class RateLimitConfig:
    """Configuration for rate limiting"""

    requests_per_minute: int = 20
    requests_per_hour: int = 100
    requests_per_day: int = 1000
    burst_size: int = 5


@dataclass
class CostConfig:
    """Configuration for cost tracking"""

    max_cost_per_request: float = 0.10
    max_cost_per_hour: float = 1.00
    max_cost_per_day: float = 10.00
    warning_threshold: float = 0.80  # Warn at 80% of limit


@dataclass
class ModelCosts:
    """Cost per token for different models"""

    # Costs in USD per 1K tokens
    gpt_5_input: float = 0.015  # Estimated
    gpt_5_output: float = 0.060  # Estimated
    gpt_5_reasoning: float = 0.030  # Estimated reasoning tokens
    gpt_35_input: float = 0.0005
    gpt_35_output: float = 0.0015
    local: float = 0.0  # No cost for local model


class SecureAPIKeyManager:
    """Manages API keys securely without exposing them"""

    def __init__(self):
        self._keys: dict[str, str] = {}
        self._load_from_environment()

    def _load_from_environment(self):
        """Load API keys from environment variables"""
        # Never hardcode keys
        for provider in ["OPENAI", "ANTHROPIC", "DEEPSEEK"]:
            key_name = f"{provider}_API_KEY"
            if key_name in os.environ:
                self._keys[provider.lower()] = os.environ[key_name]

    def get_key(self, provider: str) -> str | None:
        """Get API key for provider (returns None if not configured)"""
        return self._keys.get(provider.lower())

    def has_key(self, provider: str) -> bool:
        """Check if API key is configured for provider"""
        return provider.lower() in self._keys

    def get_masked_key(self, provider: str) -> str:
        """Get masked version of key for logging"""
        key = self._keys.get(provider.lower())
        if not key:
            return "NOT_CONFIGURED"
        # Show first 4 and last 4 characters only
        if len(key) > 12:
            return f"{key[:4]}...{key[-4:]}"
        return "***"


class RateLimiter:
    """Token bucket rate limiter with multiple time windows"""

    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.requests: dict[str, list[float]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def check_rate_limit(self, identifier: str = "default") -> bool:
        """Check if request is within rate limits"""
        async with self._lock:
            now = time.time()

            # Clean old requests
            self._clean_old_requests(identifier, now)

            # Check limits
            request_times = self.requests[identifier]

            # Per minute check
            minute_ago = now - 60
            minute_requests = sum(1 for t in request_times if t > minute_ago)
            if minute_requests >= self.config.requests_per_minute:
                return False

            # Per hour check
            hour_ago = now - 3600
            hour_requests = sum(1 for t in request_times if t > hour_ago)
            if hour_requests >= self.config.requests_per_hour:
                return False

            # Per day check
            day_ago = now - 86400
            day_requests = sum(1 for t in request_times if t > day_ago)
            if day_requests >= self.config.requests_per_day:
                return False

            # Add request
            request_times.append(now)
            return True

    def _clean_old_requests(self, identifier: str, now: float):
        """Remove requests older than 24 hours"""
        day_ago = now - 86400
        self.requests[identifier] = [t for t in self.requests[identifier] if t > day_ago]

    async def wait_if_needed(self, identifier: str = "default") -> float:
        """Wait if rate limited and return wait time"""
        if await self.check_rate_limit(identifier):
            return 0.0

        # Calculate wait time
        now = time.time()
        request_times = self.requests[identifier]

        # Find next available slot
        minute_ago = now - 60
        minute_requests = [t for t in request_times if t > minute_ago]

        if len(minute_requests) >= self.config.requests_per_minute:
            # Wait until oldest request in minute window expires
            wait_time = 60 - (now - min(minute_requests))
            await asyncio.sleep(wait_time)
            return wait_time

        return 0.0


class CostTracker:
    """Tracks and limits API costs"""

    def __init__(self, config: CostConfig, model_costs: ModelCosts):
        self.config = config
        self.model_costs = model_costs
        self.costs: dict[str, list[tuple[float, float]]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def track_cost(
        self, model: str, input_tokens: int, output_tokens: int, reasoning_tokens: int = 0
    ) -> dict[str, Any]:
        """Track cost and check limits"""
        async with self._lock:
            # Calculate cost
            cost = self._calculate_cost(model, input_tokens, output_tokens, reasoning_tokens)

            now = time.time()

            # Check if within limits
            if cost > self.config.max_cost_per_request:
                return {
                    "allowed": False,
                    "reason": f"Request cost ${cost:.4f} exceeds limit ${self.config.max_cost_per_request:.2f}",
                    "cost": cost,
                }

            # Check hourly limit
            hour_ago = now - 3600
            hour_costs = [c for t, c in self.costs[model] if t > hour_ago]
            hour_total = sum(hour_costs) + cost

            if hour_total > self.config.max_cost_per_hour:
                return {
                    "allowed": False,
                    "reason": f"Hourly cost ${hour_total:.4f} would exceed limit ${self.config.max_cost_per_hour:.2f}",
                    "cost": cost,
                }

            # Check daily limit
            day_ago = now - 86400
            day_costs = [c for t, c in self.costs[model] if t > day_ago]
            day_total = sum(day_costs) + cost

            if day_total > self.config.max_cost_per_day:
                return {
                    "allowed": False,
                    "reason": f"Daily cost ${day_total:.4f} would exceed limit ${self.config.max_cost_per_day:.2f}",
                    "cost": cost,
                }

            # Track the cost
            self.costs[model].append((now, cost))

            # Check warning threshold
            warning = None
            if hour_total > self.config.max_cost_per_hour * self.config.warning_threshold:
                warning = f"Approaching hourly limit: ${hour_total:.4f} of ${self.config.max_cost_per_hour:.2f}"
            elif day_total > self.config.max_cost_per_day * self.config.warning_threshold:
                warning = f"Approaching daily limit: ${day_total:.4f} of ${self.config.max_cost_per_day:.2f}"

            return {
                "allowed": True,
                "cost": cost,
                "hour_total": hour_total,
                "day_total": day_total,
                "warning": warning,
            }

    def _calculate_cost(
        self, model: str, input_tokens: int, output_tokens: int, reasoning_tokens: int
    ) -> float:
        """Calculate cost based on model and token counts"""
        if model == "local":
            return 0.0

        # Convert to cost per 1K tokens
        input_cost = input_tokens / 1000
        output_cost = output_tokens / 1000
        reasoning_cost = reasoning_tokens / 1000

        if "gpt-5" in model:
            return (
                input_cost * self.model_costs.gpt_5_input
                + output_cost * self.model_costs.gpt_5_output
                + reasoning_cost * self.model_costs.gpt_5_reasoning
            )
        if "gpt-3.5" in model:
            return (
                input_cost * self.model_costs.gpt_35_input
                + output_cost * self.model_costs.gpt_35_output
            )
        # Default to GPT-3.5 costs for unknown models
        return (
            input_cost * self.model_costs.gpt_35_input
            + output_cost * self.model_costs.gpt_35_output
        )

    async def get_cost_report(self) -> dict[str, Any]:
        """Get current cost report"""
        async with self._lock:
            now = time.time()
            hour_ago = now - 3600
            day_ago = now - 86400

            report = {}
            total_hour = 0.0
            total_day = 0.0

            for model, costs in self.costs.items():
                hour_costs = [c for t, c in costs if t > hour_ago]
                day_costs = [c for t, c in costs if t > day_ago]

                model_hour = sum(hour_costs)
                model_day = sum(day_costs)

                total_hour += model_hour
                total_day += model_day

                report[model] = {
                    "hour": model_hour,
                    "day": model_day,
                    "requests_hour": len(hour_costs),
                    "requests_day": len(day_costs),
                }

            report["totals"] = {
                "hour": total_hour,
                "day": total_day,
                "hour_limit": self.config.max_cost_per_hour,
                "day_limit": self.config.max_cost_per_day,
                "hour_remaining": self.config.max_cost_per_hour - total_hour,
                "day_remaining": self.config.max_cost_per_day - total_day,
            }

            return report


class DataSanitizer:
    """Sanitizes data before sending to external APIs"""

    @staticmethod
    def sanitize_for_api(text: str) -> str:
        """Remove sensitive data before API calls"""
        # Remove common sensitive patterns
        import re

        # API keys
        text = re.sub(r"[A-Za-z0-9]{32,}", "[REDACTED_KEY]", text)

        # Email addresses
        text = re.sub(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[REDACTED_EMAIL]", text
        )

        # Phone numbers
        text = re.sub(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", "[REDACTED_PHONE]", text)

        # SSN-like patterns
        text = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED_SSN]", text)

        # Credit card-like patterns
        text = re.sub(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b", "[REDACTED_CC]", text)

        # IP addresses
        text = re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "[REDACTED_IP]", text)

        # Passwords in common formats
        text = re.sub(
            r'(?i)(password|pwd|pass)(["\']?\s*[:=]\s*["\']?|[\s]+is[\s]+)[^\s"\']+',
            r"\1 [REDACTED]",
            text,
        )

        return text

    @staticmethod
    def validate_input(text: str, max_length: int = 10000) -> tuple[bool, str]:
        """Validate input before processing"""
        if not text:
            return False, "Empty input"

        if len(text) > max_length:
            return False, f"Input too long: {len(text)} > {max_length}"

        # Check for injection attempts
        dangerous_patterns = [
            r"<script",
            r"javascript:",
            r"data:text/html",
            r"vbscript:",
            r"onload=",
            r"onerror=",
            r"onclick=",
        ]

        import re

        for pattern in dangerous_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False, "Potentially dangerous content detected"

        return True, "Valid"


class SecureOrchestrator:
    """Wrapper for orchestrator with security features"""

    def __init__(
        self,
        orchestrator,
        rate_limit_config: RateLimitConfig | None = None,
        cost_config: CostConfig | None = None,
    ):
        self.orchestrator = orchestrator
        self.api_keys = SecureAPIKeyManager()
        self.rate_limiter = RateLimiter(rate_limit_config or RateLimitConfig())
        self.cost_tracker = CostTracker(cost_config or CostConfig(), ModelCosts())
        self.sanitizer = DataSanitizer()

    async def think_with_security(
        self, problem: str, effort: str = "medium", preferred_model: str | None = None
    ) -> dict[str, Any]:
        """Secure wrapper for orchestrator.think_with_scaffolding"""
        # Validate input
        valid, message = self.sanitizer.validate_input(problem)
        if not valid:
            return {"error": f"Invalid input: {message}"}

        # Sanitize input
        sanitized_problem = self.sanitizer.sanitize_for_api(problem)

        # Check rate limit
        wait_time = await self.rate_limiter.wait_if_needed()
        if wait_time > 0:
            return {"error": f"Rate limited. Please wait {wait_time:.1f} seconds"}

        # Estimate token count (rough estimate)
        estimated_tokens = len(sanitized_problem.split()) * 2

        # Check cost limits (pre-check with estimates)
        model = preferred_model or "local"
        cost_check = await self.cost_tracker.track_cost(
            model,
            estimated_tokens,
            estimated_tokens * 3,  # Estimate output
            estimated_tokens * 2,  # Estimate reasoning
        )

        if not cost_check["allowed"]:
            return {"error": cost_check["reason"]}

        # Add warning if approaching limits
        result = await self.orchestrator.think_with_scaffolding(
            sanitized_problem, effort, preferred_model
        )

        if cost_check.get("warning"):
            result["cost_warning"] = cost_check["warning"]

        result["cost_info"] = {
            "estimated_cost": cost_check["cost"],
            "hour_total": cost_check["hour_total"],
            "day_total": cost_check["day_total"],
        }

        return result


def secure_api_call(func):
    """Decorator for secure API calls"""

    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            # Add timeout
            return await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=30.0,  # 30 second timeout
            )
        except TimeoutError:
            return {"error": "API call timed out"}
        except Exception:
            # Never expose internal errors to user
            return {"error": "An error occurred processing your request"}

    return wrapper
