#!/usr/bin/env python3
"""Docker health check script for ustad-protocol-mcp server."""

import sys

import httpx


def main() -> None:
    """Check server health by testing both /health and /capabilities endpoints."""
    base_url = "http://localhost:8000"

    endpoints = ["/health", "/capabilities"]

    try:
        for endpoint in endpoints:
            url = f"{base_url}{endpoint}"
            response = httpx.get(url, timeout=3.0)
            response.raise_for_status()
            print(f"✓ {endpoint} endpoint is healthy")

        print("✓ All health checks passed")
        sys.exit(0)

    except httpx.HTTPStatusError as e:
        print(f"✗ HTTP error {e.response.status_code} for {e.request.url}")
        sys.exit(1)
    except httpx.RequestError as e:
        print(f"✗ Connection error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
