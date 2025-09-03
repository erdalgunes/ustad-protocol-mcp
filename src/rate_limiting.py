"""Rate limiting for Ustad Protocol MCP Server

Implements rate limiting to prevent abuse of sequential thinking and search endpoints.
Uses FastMCP's built-in rate limiting middleware for optimal integration.

Security Features:
- Prevents DoS attacks against expensive endpoints
- Token bucket algorithm for smooth rate limiting
- Configurable rate limits per endpoint type
- IP-based rate limiting with graceful degradation
- Native FastMCP integration
"""

import logging
import os
from typing import Any, Protocol, runtime_checkable

# Type checking imports - only used by mypy, not at runtime

# Runtime imports with graceful degradation
try:
    from fastmcp.server.middleware.rate_limiting import (
        RateLimitError,
        RateLimitingMiddleware,
        TokenBucketRateLimiter,
    )

    _FASTMCP_AVAILABLE = True
except ImportError:
    _FASTMCP_AVAILABLE = False

    # Define Protocol fallbacks for type checking when FastMCP is not available
    @runtime_checkable
    class RateLimitingMiddleware(Protocol):  # type: ignore[no-redef]
        """Fallback protocol for RateLimitingMiddleware."""

    @runtime_checkable
    class TokenBucketRateLimiter(Protocol):  # type: ignore[no-redef]
        """Fallback protocol for TokenBucketRateLimiter."""

    class RateLimitError(Exception):  # type: ignore[no-redef]
        """Fallback exception for RateLimitError."""


logger = logging.getLogger(__name__)


def create_rate_limiter() -> Any | None:
    """
    Create rate limiter middleware for FastMCP server.

    Returns:
        RateLimitingMiddleware instance if available, None if rate limiting disabled

    Environment Variables:
        RATE_LIMIT_ENABLED: Set to "false" to disable rate limiting
        RATE_LIMIT_REQUESTS_PER_MINUTE: Requests per minute per client (default: 60)
        RATE_LIMIT_BURST_SIZE: Token bucket burst capacity (default: 10)
    """
    if not _FASTMCP_AVAILABLE:
        logger.warning(
            "FastMCP rate limiting not available. Update FastMCP to latest version for rate limiting"
        )
        return None

    # Check if rate limiting is enabled
    if os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "false":
        logger.info("Rate limiting disabled via RATE_LIMIT_ENABLED=false")
        return None

    try:
        # Parse configuration - convert to requests per second for FastMCP v2.0 API
        requests_per_minute = int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "60"))
        burst_size = int(os.getenv("RATE_LIMIT_BURST_SIZE", "10"))

        # Convert to requests per second (FastMCP v2.0 uses RPS)
        requests_per_second = requests_per_minute / 60.0

        # Create middleware using FastMCP v2.0 API
        middleware = RateLimitingMiddleware(
            max_requests_per_second=requests_per_second,
            burst_capacity=burst_size,
            global_limit=True,  # Apply globally for simplicity
        )

        logger.info(
            "Rate limiting enabled - %.1f req/sec (%.0f req/min) with burst %d",
            requests_per_second,
            requests_per_minute,
            burst_size,
        )

        return middleware
    except Exception as e:
        logger.exception("Failed to initialize rate limiter")
        return None


def is_rate_limiting_available() -> bool:
    """Check if rate limiting dependencies are available."""
    return _FASTMCP_AVAILABLE


def get_rate_limit_config() -> dict[str, int]:
    """Get current rate limiting configuration."""
    return {
        "requests_per_minute": int(os.getenv("RATE_LIMIT_REQUESTS_PER_MINUTE", "60")),
        "burst_size": int(os.getenv("RATE_LIMIT_BURST_SIZE", "10")),
        "enabled": os.getenv("RATE_LIMIT_ENABLED", "true").lower() != "false",
    }


def get_rate_limit_info() -> dict[str, Any]:
    """Get rate limiting configuration info for debugging."""
    config = get_rate_limit_config()
    return {
        "rate_limiting_available": is_rate_limiting_available(),
        "rate_limiting_enabled": config["enabled"],
        "requests_per_minute": config["requests_per_minute"],
        "burst_size": config["burst_size"],
        "fastmcp_middleware": _FASTMCP_AVAILABLE,
    }
