"""
Tests for orchestrator security features.
Verifies API key management, rate limiting, cost tracking, and data sanitization.
"""

import pytest
import asyncio
import os
from unittest.mock import patch, MagicMock
import time

from src.orchestrator_security import (
    SecureAPIKeyManager,
    RateLimiter,
    RateLimitConfig,
    CostTracker,
    CostConfig,
    ModelCosts,
    DataSanitizer,
    SecureOrchestrator
)


class TestSecureAPIKeyManager:
    """Test API key management"""
    
    def test_load_from_environment(self):
        """Test loading API keys from environment"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key-123"}):
            manager = SecureAPIKeyManager()
            assert manager.has_key("openai")
            assert manager.get_key("openai") == "test-key-123"
    
    def test_missing_key_returns_none(self):
        """Test missing keys return None"""
        manager = SecureAPIKeyManager()
        assert manager.get_key("nonexistent") is None
        assert not manager.has_key("nonexistent")
    
    def test_masked_key_display(self):
        """Test key masking for logs"""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "sk-1234567890abcdef"}):
            manager = SecureAPIKeyManager()
            masked = manager.get_masked_key("openai")
            assert masked == "sk-1...cdef"
            assert "567890" not in masked  # Middle part hidden
    
    def test_no_key_configured(self):
        """Test masking when no key configured"""
        with patch.dict(os.environ, {}, clear=True):  # Clear all env vars
            manager = SecureAPIKeyManager()
            assert manager.get_masked_key("openai") == "NOT_CONFIGURED"


class TestRateLimiter:
    """Test rate limiting functionality"""
    
    @pytest.mark.asyncio
    async def test_allows_requests_within_limit(self):
        """Test requests allowed within limits"""
        config = RateLimitConfig(requests_per_minute=5)
        limiter = RateLimiter(config)
        
        # Should allow 5 requests
        for _ in range(5):
            assert await limiter.check_rate_limit()
    
    @pytest.mark.asyncio
    async def test_blocks_requests_over_limit(self):
        """Test requests blocked when over limit"""
        config = RateLimitConfig(requests_per_minute=2)
        limiter = RateLimiter(config)
        
        # First 2 should pass
        assert await limiter.check_rate_limit()
        assert await limiter.check_rate_limit()
        
        # Third should fail
        assert not await limiter.check_rate_limit()
    
    @pytest.mark.asyncio
    async def test_wait_if_needed(self):
        """Test waiting when rate limited"""
        config = RateLimitConfig(requests_per_minute=1)
        limiter = RateLimiter(config)
        
        # First request passes
        assert await limiter.check_rate_limit()
        
        # Second request should require wait
        wait_time = await limiter.wait_if_needed()
        assert wait_time > 0
    
    @pytest.mark.asyncio
    async def test_multiple_identifiers(self):
        """Test rate limiting with multiple identifiers"""
        config = RateLimitConfig(requests_per_minute=2)
        limiter = RateLimiter(config)
        
        # User 1 makes 2 requests
        assert await limiter.check_rate_limit("user1")
        assert await limiter.check_rate_limit("user1")
        assert not await limiter.check_rate_limit("user1")
        
        # User 2 should still be able to make requests
        assert await limiter.check_rate_limit("user2")
        assert await limiter.check_rate_limit("user2")


class TestCostTracker:
    """Test cost tracking and limits"""
    
    @pytest.mark.asyncio
    async def test_tracks_costs_correctly(self):
        """Test cost calculation and tracking"""
        config = CostConfig(max_cost_per_request=1.0)
        costs = ModelCosts()
        tracker = CostTracker(config, costs)
        
        # Track a GPT-5 request
        result = await tracker.track_cost("gpt-5", 1000, 500, 200)
        
        assert result["allowed"]
        assert result["cost"] > 0
        # GPT-5: 1K input * 0.015 + 0.5K output * 0.060 + 0.2K reasoning * 0.030
        expected = 0.015 + 0.030 + 0.006
        assert abs(result["cost"] - expected) < 0.001
    
    @pytest.mark.asyncio
    async def test_blocks_expensive_requests(self):
        """Test blocking requests over cost limit"""
        config = CostConfig(max_cost_per_request=0.01)
        costs = ModelCosts()
        tracker = CostTracker(config, costs)
        
        # Try expensive request
        result = await tracker.track_cost("gpt-5", 10000, 10000, 5000)
        
        assert not result["allowed"]
        assert "exceeds limit" in result["reason"]
    
    @pytest.mark.asyncio
    async def test_hourly_limit(self):
        """Test hourly cost limits"""
        config = CostConfig(
            max_cost_per_request=0.50,  # Increased to allow individual requests
            max_cost_per_hour=0.10  # Low hourly limit to test
        )
        costs = ModelCosts()
        tracker = CostTracker(config, costs)
        
        # Make requests that total over hourly limit
        # Each request: 2K * 0.015 + 1K * 0.060 + 0.5K * 0.030 = 0.030 + 0.060 + 0.015 = 0.105
        result1 = await tracker.track_cost("gpt-5", 1000, 500, 200)
        assert result1["allowed"]
        
        # Second request should exceed hourly limit of 0.10
        result2 = await tracker.track_cost("gpt-5", 1000, 500, 200)
        assert not result2["allowed"]
        assert "Hourly cost" in result2["reason"]
    
    @pytest.mark.asyncio
    async def test_warning_threshold(self):
        """Test cost warning threshold"""
        config = CostConfig(
            max_cost_per_request=0.10,
            max_cost_per_hour=0.10,
            warning_threshold=0.80
        )
        costs = ModelCosts()
        tracker = CostTracker(config, costs)
        
        # Make request that approaches limit (80% of 0.10 = 0.08)
        # 5K * 0.015 + 1K * 0.060 + 0.5K * 0.030 = 0.075 + 0.060 + 0.015 = 0.150 - too much
        # Let's use smaller amounts: 2K * 0.015 + 1K * 0.060 + 0 = 0.030 + 0.060 = 0.090
        result = await tracker.track_cost("gpt-5", 2000, 1000, 0)
        
        assert result["allowed"]
        assert result.get("warning") is not None
        assert "Approaching" in result["warning"]
    
    @pytest.mark.asyncio
    async def test_cost_report(self):
        """Test cost reporting"""
        config = CostConfig()
        costs = ModelCosts()
        tracker = CostTracker(config, costs)
        
        # Track some costs
        await tracker.track_cost("gpt-5", 1000, 500, 200)
        await tracker.track_cost("local", 1000, 500, 0)  # Should be free
        
        report = await tracker.get_cost_report()
        
        assert "gpt-5" in report
        assert "local" in report
        assert report["local"]["hour"] == 0  # Local is free
        assert report["totals"]["hour"] > 0
        assert report["totals"]["day_remaining"] > 0


class TestDataSanitizer:
    """Test data sanitization"""
    
    def test_sanitizes_api_keys(self):
        """Test API key redaction"""
        text = "My API key is sk-1234567890abcdefghijklmnopqrstuv"
        sanitized = DataSanitizer.sanitize_for_api(text)
        assert "sk-1234567890" not in sanitized
        assert "[REDACTED_KEY]" in sanitized
    
    def test_sanitizes_emails(self):
        """Test email redaction"""
        text = "Contact me at user@example.com for details"
        sanitized = DataSanitizer.sanitize_for_api(text)
        assert "user@example.com" not in sanitized
        assert "[REDACTED_EMAIL]" in sanitized
    
    def test_sanitizes_phone_numbers(self):
        """Test phone number redaction"""
        text = "Call me at 555-123-4567"
        sanitized = DataSanitizer.sanitize_for_api(text)
        assert "555-123-4567" not in sanitized
        assert "[REDACTED_PHONE]" in sanitized
    
    def test_sanitizes_ssn(self):
        """Test SSN redaction"""
        text = "SSN: 123-45-6789"
        sanitized = DataSanitizer.sanitize_for_api(text)
        assert "123-45-6789" not in sanitized
        assert "[REDACTED_SSN]" in sanitized
    
    def test_sanitizes_credit_cards(self):
        """Test credit card redaction"""
        text = "Card: 4111 1111 1111 1111"
        sanitized = DataSanitizer.sanitize_for_api(text)
        assert "4111 1111 1111 1111" not in sanitized
        assert "[REDACTED_CC]" in sanitized
    
    def test_sanitizes_passwords(self):
        """Test password redaction"""
        text = 'password: "secretpass123"'
        sanitized = DataSanitizer.sanitize_for_api(text)
        assert "secretpass123" not in sanitized
        assert "[REDACTED]" in sanitized
    
    def test_validates_input_length(self):
        """Test input length validation"""
        valid, message = DataSanitizer.validate_input("x" * 100)
        assert valid
        
        valid, message = DataSanitizer.validate_input("x" * 20000)
        assert not valid
        assert "too long" in message
    
    def test_detects_injection_attempts(self):
        """Test injection detection"""
        malicious = "<script>alert('xss')</script>"
        valid, message = DataSanitizer.validate_input(malicious)
        assert not valid
        assert "dangerous" in message.lower()


class TestSecureOrchestrator:
    """Test secure orchestrator wrapper"""
    
    @pytest.mark.asyncio
    async def test_validates_input(self):
        """Test input validation"""
        mock_orchestrator = MagicMock()
        secure = SecureOrchestrator(mock_orchestrator)
        
        # Test empty input
        result = await secure.think_with_security("")
        assert "error" in result
        assert "Empty input" in result["error"]
    
    @pytest.mark.asyncio
    async def test_sanitizes_before_api_call(self):
        """Test sanitization before API calls"""
        mock_orchestrator = MagicMock()
        
        # Track the actual argument passed
        actual_arg = None
        async def capture_arg(problem, effort, model):
            nonlocal actual_arg
            actual_arg = problem
            return {"result": "success"}
        
        mock_orchestrator.think_with_scaffolding = capture_arg
        
        secure = SecureOrchestrator(mock_orchestrator)
        
        sensitive = "My password is secret123"
        result = await secure.think_with_security(sensitive)
        
        # Check that sanitized version was passed
        assert actual_arg is not None
        assert "secret123" not in actual_arg
        assert "password" in actual_arg.lower()  # Word password should remain
        assert "[REDACTED]" in actual_arg
    
    @pytest.mark.asyncio
    async def test_respects_rate_limits(self):
        """Test rate limiting enforcement"""
        mock_orchestrator = MagicMock()
        mock_orchestrator.think_with_scaffolding = AsyncMock(
            return_value={"result": "success"}
        )
        config = RateLimitConfig(requests_per_minute=1)
        secure = SecureOrchestrator(mock_orchestrator, rate_limit_config=config)
        
        # First request should work
        secure.rate_limiter.check_rate_limit = AsyncMock(return_value=True)
        secure.rate_limiter.wait_if_needed = AsyncMock(return_value=0.0)
        result = await secure.think_with_security("Test")
        assert "error" not in result or "Rate limited" not in result.get("error", "")
        
        # Second request should be rate limited
        secure.rate_limiter.check_rate_limit = AsyncMock(return_value=False)
        secure.rate_limiter.wait_if_needed = AsyncMock(return_value=1.0)
        result = await secure.think_with_security("Test")
        assert "error" in result
        assert "Rate limited" in result["error"]
    
    @pytest.mark.asyncio
    async def test_tracks_costs(self):
        """Test cost tracking integration"""
        mock_orchestrator = MagicMock()
        mock_orchestrator.think_with_scaffolding = AsyncMock(
            return_value={"result": "success"}
        )
        
        cost_config = CostConfig(max_cost_per_request=0.01)
        secure = SecureOrchestrator(
            mock_orchestrator,
            cost_config=cost_config
        )
        
        # Mock cost check to add warning
        secure.cost_tracker.track_cost = AsyncMock(
            return_value={
                "allowed": True,
                "cost": 0.008,
                "hour_total": 0.008,
                "day_total": 0.008,
                "warning": "Approaching limit"
            }
        )
        
        result = await secure.think_with_security("Test")
        
        # Should include cost info and warning
        assert "cost_info" in result
        assert "cost_warning" in result
        assert result["cost_warning"] == "Approaching limit"


# Helper async mock
class AsyncMock(MagicMock):
    async def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)