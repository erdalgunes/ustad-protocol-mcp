#!/usr/bin/env python3
"""Working MCP Server for Perfect Collaborative Batch of Thought."""

import asyncio
import json
import logging
import os
import sys

# Add the current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Try to import MCP - this should work with proper installation
    import mcp.types as mcp_types
    from mcp import stdio_server
    from mcp.server import NotificationOptions, Server

    # Import our collaborative bot
    from perfect_collaborative_bot import PerfectCollaborativeBatchOfThought

    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("working_mcp_server")

    # Create server
    server = Server("perfect-collaborative-bot")

    # Initialize bot
    bot_instance = None

    @server.list_tools()
    async def handle_list_tools() -> list[mcp_types.Tool]:
        """List available tools."""
        return [
            mcp_types.Tool(
                name="perfect_think",
                description="Multi-round collaborative dialogue where 8 AI perspectives debate, challenge each other, and reach consensus through structured discussion",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "problem": {
                            "type": "string",
                            "description": "The problem or question to analyze collaboratively",
                        },
                        "context": {
                            "type": "string",
                            "description": "Additional context, constraints, or requirements",
                            "default": "",
                        },
                        "num_thoughts": {
                            "type": "integer",
                            "description": "Number of perspectives (max 8 for optimal dialogue)",
                            "default": 8,
                        },
                    },
                    "required": ["problem"],
                },
            )
        ]

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict | None
    ) -> list[mcp_types.TextContent | mcp_types.ImageContent | mcp_types.EmbeddedResource]:
        """Handle tool calls."""
        global bot_instance

        if name != "perfect_think":
            raise ValueError(f"Unknown tool: {name}")

        if not arguments:
            raise ValueError("Arguments required for perfect_think")

        problem = arguments.get("problem")
        if not problem:
            raise ValueError("'problem' argument is required")

        context = arguments.get("context", "")
        num_thoughts = arguments.get("num_thoughts", 8)

        # Initialize bot if not done
        if not bot_instance:
            try:
                bot_instance = PerfectCollaborativeBatchOfThought()
                logger.info("Perfect Collaborative BoT initialized")
            except Exception as e:
                logger.error(f"Failed to initialize bot: {e}")
                return [
                    mcp_types.TextContent(
                        type="text", text=json.dumps({"error": f"Bot initialization failed: {e!s}"})
                    )
                ]

        try:
            # Run the collaborative thinking
            result = await bot_instance.think(problem, context)

            # Return as text content
            return [mcp_types.TextContent(type="text", text=json.dumps(result, indent=2))]

        except Exception as e:
            logger.error(f"Error in perfect_think: {e}")
            return [
                mcp_types.TextContent(
                    type="text", text=json.dumps({"error": str(e), "problem": problem})
                )
            ]

    async def main():
        """Run the server."""
        logger.info("Starting Perfect Collaborative BoT MCP Server")

        # Use stdio transport
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())

    if __name__ == "__main__":
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
            sys.exit(1)

except ImportError as e:
    print(f"MCP import failed: {e}")
    print("This suggests the MCP package is not properly installed.")
    print("Try: pip install mcp")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    print("Check that all dependencies are installed correctly.")
    sys.exit(1)
