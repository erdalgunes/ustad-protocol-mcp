"""Test suite for rate_limiting.py module.

Following TDD best practices with comprehensive coverage of all code paths.
Tests rate limiting middleware implementation for FastMCP server.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from src.rate_limiting import (
    create_rate_limiter,
    get_rate_limit_config,
    get_rate_limit_info,
    is_rate_limiting_available,
)


class TestRateLimiting:
    """Test suite for rate limiting middleware."""

    def setup_method(self):
        """Clear environment variables before each test for isolation."""
        self.original_env = {}
        for key in [
            "RATE_LIMIT_ENABLED",
            "RATE_LIMIT_REQUESTS_PER_MINUTE",
            "RATE_LIMIT_BURST_SIZE",
        ]:
            self.original_env[key] = os.environ.get(key)
            if key in os.environ:
                del os.environ[key]

    def teardown_method(self):
        """Restore original environment variables after each test."""
        for key, value in self.original_env.items():
            if value is not None:
                os.environ[key] = value
            elif key in os.environ:
                del os.environ[key]

    def test_create_rate_limiter_not_available(self):
        """Test graceful degradation when FastMCP rate limiting is not available."""
        with patch("src.rate_limiting._FASTMCP_AVAILABLE", False):
            result = create_rate_limiter()
            assert result is None

    def test_create_rate_limiter_disabled_via_env(self):
        """Test rate limiter returns None when explicitly disabled."""
        os.environ["RATE_LIMIT_ENABLED"] = "false"

        with patch("src.rate_limiting._FASTMCP_AVAILABLE", True):
            result = create_rate_limiter()
            assert result is None

        # Test case variations
        os.environ["RATE_LIMIT_ENABLED"] = "FALSE"
        with patch("src.rate_limiting._FASTMCP_AVAILABLE", True):
            result = create_rate_limiter()
            assert result is None

        os.environ["RATE_LIMIT_ENABLED"] = "False"
        with patch("src.rate_limiting._FASTMCP_AVAILABLE", True):
            result = create_rate_limiter()
            assert result is None

    def test_create_rate_limiter_success_with_defaults(self):
        """Test successful rate limiter creation with default values."""
        mock_middleware = MagicMock()

        with (
            patch("src.rate_limiting._FASTMCP_AVAILABLE", True),
            patch(
                "src.rate_limiting.RateLimitingMiddleware", MagicMock(return_value=mock_middleware)
            ) as mock_rl,
        ):
            result = create_rate_limiter()

            assert result == mock_middleware
            mock_rl.assert_called_once_with(
                max_requests_per_second=1.0,  # 60/60
                burst_capacity=10,
                global_limit=True,
            )

    def test_create_rate_limiter_success_with_custom_values(self):
        """Test successful rate limiter creation with custom environment values."""
        os.environ["RATE_LIMIT_REQUESTS_PER_MINUTE"] = "120"
        os.environ["RATE_LIMIT_BURST_SIZE"] = "20"

        mock_middleware = MagicMock()

        with (
            patch("src.rate_limiting._FASTMCP_AVAILABLE", True),
            patch(
                "src.rate_limiting.RateLimitingMiddleware", MagicMock(return_value=mock_middleware)
            ) as mock_rl,
        ):
            result = create_rate_limiter()

            assert result == mock_middleware
            mock_rl.assert_called_once_with(
                max_requests_per_second=2.0,  # 120/60
                burst_capacity=20,
                global_limit=True,
            )

    def test_create_rate_limiter_handles_invalid_env_values(self):
        """Test rate limiter handles invalid environment values gracefully."""
        os.environ["RATE_LIMIT_REQUESTS_PER_MINUTE"] = "not_a_number"
        os.environ["RATE_LIMIT_BURST_SIZE"] = "invalid"

        with (
            patch("src.rate_limiting._FASTMCP_AVAILABLE", True),
            patch("src.rate_limiting.RateLimitingMiddleware", MagicMock()),
        ):
            result = create_rate_limiter()
            # Should return None due to exception
            assert result is None

    def test_create_rate_limiter_exception_handling(self):
        """Test rate limiter handles exceptions during initialization."""
        with (
            patch("src.rate_limiting._FASTMCP_AVAILABLE", True),
            patch(
                "src.rate_limiting.RateLimitingMiddleware",
                MagicMock(side_effect=Exception("Initialization error")),
            ),
        ):
            result = create_rate_limiter()
            assert result is None

    def test_create_rate_limiter_enabled_by_default(self):
        """Test rate limiter is enabled by default when available."""
        # Don't set RATE_LIMIT_ENABLED, should default to enabled
        mock_middleware = MagicMock()

        with (
            patch("src.rate_limiting._FASTMCP_AVAILABLE", True),
            patch(
                "src.rate_limiting.RateLimitingMiddleware", MagicMock(return_value=mock_middleware)
            ),
        ):
            result = create_rate_limiter()
            assert result == mock_middleware

    def test_create_rate_limiter_enabled_explicitly(self):
        """Test rate limiter when explicitly enabled."""
        os.environ["RATE_LIMIT_ENABLED"] = "true"

        mock_middleware = MagicMock()

        with (
            patch("src.rate_limiting._FASTMCP_AVAILABLE", True),
            patch(
                "src.rate_limiting.RateLimitingMiddleware", MagicMock(return_value=mock_middleware)
            ),
        ):
            result = create_rate_limiter()
            assert result == mock_middleware

    def test_is_rate_limiting_available_true(self):
        """Test rate limiting availability check when available."""
        with patch("src.rate_limiting._FASTMCP_AVAILABLE", True):
            assert is_rate_limiting_available() is True

    def test_is_rate_limiting_available_false(self):
        """Test rate limiting availability check when not available."""
        with patch("src.rate_limiting._FASTMCP_AVAILABLE", False):
            assert is_rate_limiting_available() is False

    def test_get_rate_limit_config_defaults(self):
        """Test getting rate limit configuration with defaults."""
        config = get_rate_limit_config()

        assert config == {"requests_per_minute": 60, "burst_size": 10, "enabled": True}

    def test_get_rate_limit_config_custom(self):
        """Test getting rate limit configuration with custom values."""
        os.environ["RATE_LIMIT_REQUESTS_PER_MINUTE"] = "120"
        os.environ["RATE_LIMIT_BURST_SIZE"] = "20"
        os.environ["RATE_LIMIT_ENABLED"] = "false"

        config = get_rate_limit_config()

        assert config == {"requests_per_minute": 120, "burst_size": 20, "enabled": False}

    def test_get_rate_limit_info_available_enabled(self):
        """Test rate limit info when available and enabled."""
        os.environ["RATE_LIMIT_REQUESTS_PER_MINUTE"] = "90"
        os.environ["RATE_LIMIT_BURST_SIZE"] = "15"

        with patch("src.rate_limiting._FASTMCP_AVAILABLE", True):
            info = get_rate_limit_info()

            assert info == {
                "rate_limiting_available": True,
                "rate_limiting_enabled": True,
                "requests_per_minute": 90,
                "burst_size": 15,
                "fastmcp_middleware": True,
            }

    def test_get_rate_limit_info_available_disabled(self):
        """Test rate limit info when available but disabled."""
        os.environ["RATE_LIMIT_ENABLED"] = "false"

        with patch("src.rate_limiting._FASTMCP_AVAILABLE", True):
            info = get_rate_limit_info()

            assert info == {
                "rate_limiting_available": True,
                "rate_limiting_enabled": False,
                "requests_per_minute": 60,
                "burst_size": 10,
                "fastmcp_middleware": True,
            }

    def test_get_rate_limit_info_not_available(self):
        """Test rate limit info when FastMCP not available."""
        with patch("src.rate_limiting._FASTMCP_AVAILABLE", False):
            info = get_rate_limit_info()

            assert info == {
                "rate_limiting_available": False,
                "rate_limiting_enabled": True,  # Config says enabled but not available
                "requests_per_minute": 60,
                "burst_size": 10,
                "fastmcp_middleware": False,
            }


@pytest.mark.parametrize(
    ("rpm", "burst", "expected_rps"),
    [
        ("60", "10", 1.0),
        ("120", "20", 2.0),
        ("30", "5", 0.5),
        ("90", "15", 1.5),
        ("600", "100", 10.0),
    ],
)
def test_rate_limiter_rpm_to_rps_conversion(rpm, burst, expected_rps):
    """Test correct conversion from requests per minute to requests per second."""
    os.environ["RATE_LIMIT_REQUESTS_PER_MINUTE"] = rpm
    os.environ["RATE_LIMIT_BURST_SIZE"] = burst

    mock_middleware = MagicMock()

    with (
        patch("src.rate_limiting._FASTMCP_AVAILABLE", True),
        patch(
            "src.rate_limiting.RateLimitingMiddleware", MagicMock(return_value=mock_middleware)
        ) as mock_rl,
    ):
        result = create_rate_limiter()

        assert result == mock_middleware
        mock_rl.assert_called_once()
        assert mock_rl.call_args.kwargs["max_requests_per_second"] == expected_rps
        assert mock_rl.call_args.kwargs["burst_capacity"] == int(burst)


@pytest.mark.parametrize(
    ("enabled_value", "expected"),
    [
        ("true", True),
        ("TRUE", True),
        ("True", True),
        ("1", True),
        ("yes", True),
        ("false", False),
        ("FALSE", False),
        ("False", False),
        ("0", True),  # Only "false" should disable
        ("no", True),  # Only "false" should disable
        ("", True),  # Empty defaults to enabled
    ],
)
def test_rate_limit_enabled_parsing(enabled_value, expected):
    """Test parsing of RATE_LIMIT_ENABLED environment variable."""
    os.environ["RATE_LIMIT_ENABLED"] = enabled_value

    config = get_rate_limit_config()
    assert config["enabled"] == expected
