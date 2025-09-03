"""Tests for /capabilities endpoint."""

import os
import sys

import pytest
from fastapi.testclient import TestClient

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.constants import CAPABILITIES_DATA


class TestCapabilitiesEndpoint:
    """Test suite for /capabilities endpoint."""

    @pytest.fixture
    def client(self):
        """Create test client for the FastAPI app."""
        # Import here to avoid circular imports

        # Create the app from the server module
        from starlette.applications import Starlette
        from starlette.responses import JSONResponse
        from starlette.routing import Route

        # Use actual server constants for testing
        async def capabilities_endpoint(request):
            """Return capabilities information using actual server constants."""
            return JSONResponse(CAPABILITIES_DATA)

        # Create test app
        test_app = Starlette(
            routes=[
                Route("/capabilities", capabilities_endpoint, methods=["GET"]),
            ]
        )

        return TestClient(test_app)

    def test_capabilities_endpoint_exists(self, client):
        """Test that /capabilities endpoint exists and returns 200."""
        response = client.get("/capabilities")
        assert response.status_code == 200

    def test_capabilities_response_structure(self, client):
        """Test that response has correct JSON structure."""
        response = client.get("/capabilities")
        data = response.json()

        # Check required fields exist
        assert "version" in data
        assert "features" in data
        assert "tools" in data

    def test_capabilities_version_format(self, client):
        """Test that version follows semantic versioning."""
        response = client.get("/capabilities")
        data = response.json()

        version = data["version"]
        # Check semantic versioning format (X.Y.Z)
        assert isinstance(version, str)
        parts = version.split(".")
        assert len(parts) == 3
        for part in parts:
            assert part.isdigit()

    def test_capabilities_features_structure(self, client):
        """Test that features object has correct structure and types."""
        response = client.get("/capabilities")
        data = response.json()

        features = data["features"]
        assert isinstance(features, dict)

        # Check expected feature flags
        expected_features = [
            "intent_analysis",
            "auto_fact_check",
            "guided_thinking",
            "min_thinking_steps",
        ]

        for feature in expected_features:
            assert feature in features
            # All features should be boolean except min_thinking_steps
            if feature == "min_thinking_steps":
                assert isinstance(features[feature], int)
                assert features[feature] >= 0
            else:
                assert isinstance(features[feature], bool)

    def test_capabilities_tools_list(self, client):
        """Test that tools is a list of strings."""
        response = client.get("/capabilities")
        data = response.json()

        tools = data["tools"]
        assert isinstance(tools, list)
        assert len(tools) > 0

        # Check all tools are strings
        for tool in tools:
            assert isinstance(tool, str)
            assert len(tool) > 0

        # Check expected tools are present
        expected_tools = ["ustad_think", "ustad_search"]
        for tool in expected_tools:
            assert tool in tools

    def test_capabilities_response_content_type(self, client):
        """Test that response has correct content type."""
        response = client.get("/capabilities")
        assert response.headers["content-type"] == "application/json"
