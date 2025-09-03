"""Server constants and configuration."""

from typing import Any

# Server version - single source of truth
SERVER_VERSION = "0.2.0"

# Server capabilities configuration
CAPABILITIES_DATA: dict[str, Any] = {
    "version": SERVER_VERSION,
    "features": {
        "intent_analysis": False,
        "auto_fact_check": False,
        "guided_thinking": True,
        "min_thinking_steps": 10,
    },
    "tools": ["ustad_think", "ustad_search"],
}

# Health check data
HEALTH_DATA: dict[str, Any] = {
    "status": "healthy",
    "server": "ustad-protocol-mcp",
    "version": SERVER_VERSION,
    "tools": CAPABILITIES_DATA["tools"],
}
