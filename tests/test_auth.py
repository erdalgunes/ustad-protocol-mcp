"""Test suite for auth.py module.

Following TDD best practices with comprehensive coverage of all code paths.
Tests OAuth 2.1 authentication implementation for FastMCP server.
"""

import os
from unittest.mock import MagicMock, patch

import pytest

from src.auth import create_auth_verifier, get_auth_info, is_auth_enabled


class TestAuthVerifier:
    """Test suite for OAuth 2.1 authentication verifier."""

    def setup_method(self):
        """Clear environment variables before each test for isolation."""
        # Store original env vars
        self.original_env = {}
        for key in ["OAUTH_JWKS_URI", "OAUTH_ISSUER", "OAUTH_AUDIENCE", "OAUTH_REQUIRED_SCOPES"]:
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

    def test_create_auth_verifier_no_jwt_verifier_available(self):
        """Test graceful degradation when JWTVerifier is not available."""
        with patch("src.auth.JWTVerifier", None):
            result = create_auth_verifier()
            assert result is None

    def test_create_auth_verifier_missing_jwks_uri(self):
        """Test auth verifier returns None when JWKS URI is missing."""
        os.environ["OAUTH_ISSUER"] = "https://auth.example.com"
        os.environ["OAUTH_AUDIENCE"] = "test-client"

        with patch("src.auth.JWTVerifier", MagicMock()):
            result = create_auth_verifier()
            assert result is None

    def test_create_auth_verifier_missing_issuer(self):
        """Test auth verifier returns None when issuer is missing."""
        os.environ["OAUTH_JWKS_URI"] = "https://auth.example.com/.well-known/jwks.json"
        os.environ["OAUTH_AUDIENCE"] = "test-client"

        with patch("src.auth.JWTVerifier", MagicMock()):
            result = create_auth_verifier()
            assert result is None

    def test_create_auth_verifier_missing_audience(self):
        """Test auth verifier returns None when audience is missing."""
        os.environ["OAUTH_JWKS_URI"] = "https://auth.example.com/.well-known/jwks.json"
        os.environ["OAUTH_ISSUER"] = "https://auth.example.com"

        with patch("src.auth.JWTVerifier", MagicMock()):
            result = create_auth_verifier()
            assert result is None

    def test_create_auth_verifier_success_with_defaults(self):
        """Test successful auth verifier creation with default scopes."""
        os.environ["OAUTH_JWKS_URI"] = "https://auth.example.com/.well-known/jwks.json"
        os.environ["OAUTH_ISSUER"] = "https://auth.example.com"
        os.environ["OAUTH_AUDIENCE"] = "test-client"

        mock_verifier = MagicMock()
        with patch("src.auth.JWTVerifier", MagicMock(return_value=mock_verifier)) as mock_jwt:
            result = create_auth_verifier()

            assert result == mock_verifier
            mock_jwt.assert_called_once_with(
                jwks_uri="https://auth.example.com/.well-known/jwks.json",
                issuer="https://auth.example.com",
                audience="test-client",
                algorithm="RS256",
                required_scopes=["ustad:access"],
            )

    def test_create_auth_verifier_success_with_custom_scopes(self):
        """Test successful auth verifier creation with custom scopes."""
        os.environ["OAUTH_JWKS_URI"] = "https://auth.example.com/.well-known/jwks.json"
        os.environ["OAUTH_ISSUER"] = "https://auth.example.com"
        os.environ["OAUTH_AUDIENCE"] = "test-client"
        os.environ["OAUTH_REQUIRED_SCOPES"] = "read:data, write:data, admin:all"

        mock_verifier = MagicMock()
        with patch("src.auth.JWTVerifier", MagicMock(return_value=mock_verifier)) as mock_jwt:
            result = create_auth_verifier()

            assert result == mock_verifier
            mock_jwt.assert_called_once_with(
                jwks_uri="https://auth.example.com/.well-known/jwks.json",
                issuer="https://auth.example.com",
                audience="test-client",
                algorithm="RS256",
                required_scopes=["read:data", "write:data", "admin:all"],
            )

    def test_create_auth_verifier_handles_empty_scopes(self):
        """Test auth verifier handles empty scope strings correctly."""
        os.environ["OAUTH_JWKS_URI"] = "https://auth.example.com/.well-known/jwks.json"
        os.environ["OAUTH_ISSUER"] = "https://auth.example.com"
        os.environ["OAUTH_AUDIENCE"] = "test-client"
        os.environ["OAUTH_REQUIRED_SCOPES"] = ",  , ,  "  # Empty/whitespace scopes

        mock_verifier = MagicMock()
        with patch("src.auth.JWTVerifier", MagicMock(return_value=mock_verifier)) as mock_jwt:
            result = create_auth_verifier()

            assert result == mock_verifier
            # Should filter out empty scopes
            mock_jwt.assert_called_once()
            assert mock_jwt.call_args.kwargs["required_scopes"] == []

    def test_create_auth_verifier_exception_handling(self):
        """Test auth verifier handles exceptions during initialization."""
        os.environ["OAUTH_JWKS_URI"] = "https://auth.example.com/.well-known/jwks.json"
        os.environ["OAUTH_ISSUER"] = "https://auth.example.com"
        os.environ["OAUTH_AUDIENCE"] = "test-client"

        with patch("src.auth.JWTVerifier", MagicMock(side_effect=Exception("Connection error"))):
            result = create_auth_verifier()
            assert result is None

    def test_is_auth_enabled_all_vars_present(self):
        """Test auth is enabled when all required environment variables are present."""
        os.environ["OAUTH_JWKS_URI"] = "https://auth.example.com/.well-known/jwks.json"
        os.environ["OAUTH_ISSUER"] = "https://auth.example.com"
        os.environ["OAUTH_AUDIENCE"] = "test-client"

        assert is_auth_enabled() is True

    def test_is_auth_enabled_missing_vars(self):
        """Test auth is disabled when any required environment variable is missing."""
        # Test with no vars
        assert is_auth_enabled() is False

        # Test with partial vars
        os.environ["OAUTH_JWKS_URI"] = "https://auth.example.com/.well-known/jwks.json"
        assert is_auth_enabled() is False

        os.environ["OAUTH_ISSUER"] = "https://auth.example.com"
        assert is_auth_enabled() is False

        # Still missing audience
        assert is_auth_enabled() is False

        # Add final var
        os.environ["OAUTH_AUDIENCE"] = "test-client"
        assert is_auth_enabled() is True

    def test_get_auth_info_no_config(self):
        """Test auth info when no configuration is present."""
        with patch("src.auth.JWTVerifier", MagicMock()):
            info = get_auth_info()

            assert info == {
                "auth_enabled": False,
                "jwks_uri": "not_configured",
                "issuer": "not_configured",
                "audience": "not_configured",
                "required_scopes": "ustad:access",
                "fastmcp_version": "2.0.0+",
            }

    def test_get_auth_info_with_config(self):
        """Test auth info when configuration is present."""
        os.environ["OAUTH_JWKS_URI"] = "https://auth.example.com/.well-known/jwks.json"
        os.environ["OAUTH_ISSUER"] = "https://auth.example.com"
        os.environ["OAUTH_AUDIENCE"] = "test-client"
        os.environ["OAUTH_REQUIRED_SCOPES"] = "custom:scope"

        with patch("src.auth.JWTVerifier", MagicMock()):
            info = get_auth_info()

            assert info == {
                "auth_enabled": True,
                "jwks_uri": "https://auth.example.com/.well-known/jwks.json",
                "issuer": "https://auth.example.com",
                "audience": "test-client",
                "required_scopes": "custom:scope",
                "fastmcp_version": "2.0.0+",
            }

    def test_get_auth_info_no_jwt_verifier(self):
        """Test auth info when JWTVerifier is not available."""
        with patch("src.auth.JWTVerifier", None):
            info = get_auth_info()
            assert info["fastmcp_version"] == "unknown"


@pytest.mark.parametrize(
    ("env_vars", "expected"),
    [
        ({"OAUTH_JWKS_URI": "uri", "OAUTH_ISSUER": "issuer", "OAUTH_AUDIENCE": "audience"}, True),
        ({"OAUTH_JWKS_URI": "uri", "OAUTH_ISSUER": "issuer"}, False),
        ({"OAUTH_JWKS_URI": "uri"}, False),
        ({}, False),
    ],
)
def test_is_auth_enabled_parametrized(env_vars, expected):
    """Parametrized test for auth enabled check with various configurations."""
    # Clear all OAuth env vars first
    for key in ["OAUTH_JWKS_URI", "OAUTH_ISSUER", "OAUTH_AUDIENCE"]:
        if key in os.environ:
            del os.environ[key]

    # Set provided vars
    for key, value in env_vars.items():
        os.environ[key] = value

    try:
        assert is_auth_enabled() == expected
    finally:
        # Cleanup
        for key in env_vars:
            if key in os.environ:
                del os.environ[key]
