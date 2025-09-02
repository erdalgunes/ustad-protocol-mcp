#!/usr/bin/env python3
"""Test the enhanced MCP server tools."""

import asyncio
import sys
sys.path.append('.')

from ustad_fastmcp import mcp

async def test_tools():
    """Test that all tools are properly registered."""
    print("🧠 Ustad MCP Enhanced Tools Test")
    print("=" * 50)
    
    # Get all registered tools  
    tools_dict = await mcp.get_tools()
    tools = list(tools_dict.keys())
    print(f"📊 Total tools registered: {len(tools)}")
    
    expected_tools = [
        "ustad_start", "ustad_think", "ustad_think_stream", 
        "ustad_quick", "ustad_decide", "ustad_meta",
        "ustad_research", "ustad_context", "ustad_preflight", "ustad_systematic",
        "get_protocol_guide", "get_usage_examples", "get_protocol_status", "version"
    ]
    
    print("\n🔧 Available tools:")
    for tool in sorted(tools):
        status = "✅" if tool in expected_tools else "❓"
        print(f"  {status} {tool}")
    
    print(f"\n📈 Expected: {len(expected_tools)}, Found: {len(tools)}")
    
    # Test that key enhanced tools are present
    enhanced_tools = ["ustad_research", "ustad_context", "ustad_preflight", "ustad_systematic"]
    missing = [tool for tool in enhanced_tools if tool not in tools]
    
    if missing:
        print(f"❌ Missing enhanced tools: {missing}")
        return False
    else:
        print("✅ All enhanced tools are properly registered!")
        return True

if __name__ == "__main__":
    success = asyncio.run(test_tools())
    sys.exit(0 if success else 1)