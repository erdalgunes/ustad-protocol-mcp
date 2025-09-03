"""Custom exceptions for Ustad Protocol MCP Server.

This module defines a hierarchy of custom exceptions for better error handling
and classification throughout the application.

Exception hierarchy:
    UstadError (base)
    ├── ThinkingError
    │   ├── InvalidThoughtError
    │   ├── ThoughtValidationError
    │   └── BranchingError
    ├── SearchError
    │   ├── APIKeyError
    │   ├── SearchTimeoutError
    │   └── SearchAPIError
    └── ConfigurationError
        ├── AuthConfigError
        └── RateLimitConfigError
"""

from typing import Any


class UstadError(Exception):
    """Base exception for all Ustad Protocol errors.

    This is the base class for all custom exceptions in the application.
    Catching this exception will catch all application-specific errors.
    """

    def __init__(self, message: str, details: dict[str, Any] | None = None) -> None:
        """Initialize the exception with optional details.

        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """Convert exception to dictionary for API responses.

        Returns:
            Dictionary with error information
        """
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
        }


# Thinking-related exceptions
class ThinkingError(UstadError):
    """Base exception for sequential thinking errors."""


class InvalidThoughtError(ThinkingError):
    """Raised when thought data is structurally invalid."""


class ThoughtValidationError(ThinkingError):
    """Raised when thought content fails validation rules."""


class BranchingError(ThinkingError):
    """Raised when branching operations fail."""


# Search-related exceptions
class SearchError(UstadError):
    """Base exception for search-related errors."""


class APIKeyError(SearchError):
    """Raised when API key is missing or invalid."""

    def __init__(self, service: str = "Tavily") -> None:
        """Initialize with service name."""
        super().__init__(
            f"{service} API key not configured",
            {"service": service, "env_var": f"{service.upper()}_API_KEY"},
        )


class SearchTimeoutError(SearchError):
    """Raised when search request times out."""

    def __init__(self, timeout: float, query: str) -> None:
        """Initialize with timeout and query details."""
        super().__init__(
            f"Search timed out after {timeout}s",
            {"timeout": timeout, "query": query[:100]},  # Truncate long queries
        )


class SearchAPIError(SearchError):
    """Raised when search API returns an error."""

    def __init__(self, status_code: int, response_text: str) -> None:
        """Initialize with API error details."""
        super().__init__(
            f"Search API error: {status_code}",
            {"status_code": status_code, "response": response_text[:500]},
        )


# Configuration-related exceptions
class ConfigurationError(UstadError):
    """Base exception for configuration errors."""


class AuthConfigError(ConfigurationError):
    """Raised when authentication configuration is invalid."""

    def __init__(self, missing_vars: list[str]) -> None:
        """Initialize with list of missing variables."""
        super().__init__(
            "Authentication configuration incomplete",
            {
                "missing": missing_vars,
                "required": ["OAUTH_JWKS_URI", "OAUTH_ISSUER", "OAUTH_AUDIENCE"],
            },
        )


class RateLimitConfigError(ConfigurationError):
    """Raised when rate limiting configuration is invalid."""

    def __init__(self, invalid_var: str, value: str) -> None:
        """Initialize with invalid configuration details."""
        super().__init__(
            f"Invalid rate limit configuration: {invalid_var}",
            {"variable": invalid_var, "value": value, "expected": "positive integer"},
        )
