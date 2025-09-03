"""OAuth 2.1 Authentication for Ustad Protocol MCP Server

Implements JWT token verification following MCP Authorization Specification (2025-03-26)
and addresses CVE-2025-49596 security vulnerability.

Security Features:
- JWT signature verification with JWKS
- Token expiration validation
- Required scope enforcement
- Audience validation
- Issuer validation per RFC 9728
"""

import logging
import os
from typing import Any

try:
    from fastmcp.server.auth.verifiers import JWTVerifier
except ImportError:
    # Fallback for older FastMCP versions
    JWTVerifier = None

logger = logging.getLogger(__name__)


def create_auth_verifier() -> Any | None:
    """
    Create JWT token verifier for OAuth 2.1 authentication.

    Returns:
        JWTVerifier instance if configured, None if authentication disabled

    Environment Variables:
        OAUTH_JWKS_URI: JWKS endpoint for token verification
        OAUTH_ISSUER: Token issuer URL
        OAUTH_AUDIENCE: Expected audience (typically this server's client ID)
        OAUTH_REQUIRED_SCOPES: Comma-separated list of required scopes
    """
    if JWTVerifier is None:
        logger.warning("JWTVerifier not available. Install FastMCP >=2.11.0 for OAuth support")
        return None

    # Check required environment variables
    jwks_uri = os.getenv("OAUTH_JWKS_URI")
    issuer = os.getenv("OAUTH_ISSUER")
    audience = os.getenv("OAUTH_AUDIENCE")

    if not all([jwks_uri, issuer, audience]):
        logger.info(
            "OAuth not configured. Set OAUTH_JWKS_URI, OAUTH_ISSUER, and OAUTH_AUDIENCE "
            "to enable authentication"
        )
        return None

    # Parse required scopes (default to basic access)
    scopes_str = os.getenv("OAUTH_REQUIRED_SCOPES", "ustad:access")
    required_scopes = [scope.strip() for scope in scopes_str.split(",") if scope.strip()]

    logger.info(
        "Configuring OAuth 2.1 authentication: issuer=%s, audience=%s, scopes=%s",
        issuer,
        audience,
        required_scopes,
    )

    try:
        verifier = JWTVerifier(
            jwks_uri=jwks_uri,
            issuer=issuer,
            audience=audience,
            algorithm="RS256",  # Industry standard for OAuth 2.1
            required_scopes=required_scopes,
        )
        logger.info("OAuth 2.1 authentication enabled successfully")
        return verifier
    except Exception as e:
        logger.exception("Failed to initialize OAuth verifier")
        return None


def is_auth_enabled() -> bool:
    """Check if authentication is enabled and configured."""
    return all(
        [
            os.getenv("OAUTH_JWKS_URI"),
            os.getenv("OAUTH_ISSUER"),
            os.getenv("OAUTH_AUDIENCE"),
        ]
    )


def get_auth_info() -> dict[str, Any]:
    """Get authentication configuration info for debugging."""
    return {
        "auth_enabled": is_auth_enabled(),
        "jwks_uri": os.getenv("OAUTH_JWKS_URI", "not_configured"),
        "issuer": os.getenv("OAUTH_ISSUER", "not_configured"),
        "audience": os.getenv("OAUTH_AUDIENCE", "not_configured"),
        "required_scopes": os.getenv("OAUTH_REQUIRED_SCOPES", "ustad:access"),
        "fastmcp_version": "2.0.0+" if JWTVerifier is not None else "unknown",
    }
