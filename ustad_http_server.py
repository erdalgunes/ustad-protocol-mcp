#!/usr/bin/env python3
"""
Ustad MCP HTTP Server - Multi-session capable version

This version uses HTTP transport to support multiple concurrent Claude Code sessions.
Perfect for team environments or when running multiple instances.

Usage:
    python ustad_http_server.py [port]

Example:
    python ustad_http_server.py 8000
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from ustad_fastmcp import mcp

def main():
    port = 8000
    
    # Check for custom port
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"❌ Invalid port: {sys.argv[1]}")
            print("Usage: python ustad_http_server.py [port]")
            sys.exit(1)
    
    print("🧠 Ustad MCP HTTP Server - Multi-Session Edition")
    print("=" * 55)
    print(f"🚀 Starting HTTP transport on port {port}")
    print(f"📡 Multiple concurrent sessions supported")
    print(f"🔗 Connect via: http://localhost:{port}")
    print(f"⚡ Session isolation: Each connection gets independent context")
    print()
    print("Available tools: 15 enhanced reasoning tools")
    print("- ustad_start, ustad_think, ustad_research, ustad_preflight")
    print("- ustad_context, ustad_systematic, ustad_session_info, and more!")
    print()
    
    try:
        mcp.run(transport="http", host="127.0.0.1", port=port)
    except KeyboardInterrupt:
        print("\n👋 Shutting down Ustad MCP Server")
    except Exception as e:
        print(f"❌ Server error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()