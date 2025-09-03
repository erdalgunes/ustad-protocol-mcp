#!/usr/bin/env python3
"""HTTP-based MCP Server for Perfect Collaborative Batch of Thought."""

import logging
import os
import sys

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Add path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from perfect_collaborative_bot import PerfectCollaborativeBatchOfThought
except ImportError as e:
    print(f"Import error: {e}")
    print("Current working directory:", os.getcwd())
    print("Python path:", sys.path)
    sys.exit(1)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("http_mcp_server")

# Initialize FastAPI app
app = FastAPI(
    title="Perfect Collaborative Batch of Thought MCP Server",
    description="Multi-round collaborative AI dialogue with consensus building",
    version="1.0.0",
)

# Initialize bot
bot_instance = None


class ThinkRequest(BaseModel):
    problem: str
    context: str = ""
    num_thoughts: int = 8


class HealthResponse(BaseModel):
    status: str
    version: str
    bot_initialized: bool


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    global bot_instance
    return HealthResponse(
        status="healthy", version="1.0.0", bot_initialized=bot_instance is not None
    )


@app.post("/think")
async def perfect_think(request: ThinkRequest):
    """Multi-round collaborative dialogue where 8 AI perspectives debate,
    challenge each other, and reach consensus through structured discussion.
    """
    global bot_instance

    try:
        # Initialize bot if needed
        if not bot_instance:
            logger.info("Initializing Perfect Collaborative BoT...")
            bot_instance = PerfectCollaborativeBatchOfThought()
            logger.info("Bot initialized successfully")

        # Run collaborative thinking
        logger.info(f"Processing request: {request.problem[:50]}...")
        result = await bot_instance.think(request.problem, request.context)

        logger.info("Collaborative thinking completed successfully")
        return JSONResponse(content=result)

    except Exception as e:
        logger.error(f"Error in perfect_think: {e}")
        raise HTTPException(status_code=500, detail={"error": str(e), "problem": request.problem})


@app.get("/tools")
async def list_tools():
    """List available MCP tools."""
    return {
        "tools": [
            {
                "name": "perfect_think",
                "description": "Multi-round collaborative dialogue where 8 AI perspectives debate, challenge each other, and reach consensus through structured discussion",
                "input_schema": {
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
            }
        ]
    }


@app.get("/")
async def root():
    """Root endpoint with server info."""
    return {
        "name": "Perfect Collaborative Batch of Thought MCP Server",
        "version": "1.0.0",
        "description": "Multi-round collaborative AI dialogue with consensus building",
        "endpoints": {"health": "/health", "think": "/think", "tools": "/tools"},
        "docker": True,
        "collaborative_ai": True,
    }


if __name__ == "__main__":
    # Check if running in container
    in_container = os.path.exists("/.dockerenv")
    host = "0.0.0.0" if in_container else "127.0.0.1"

    logger.info("Starting Perfect Collaborative BoT HTTP MCP Server")
    logger.info(f"Running in container: {in_container}")
    logger.info(f"OpenAI API Key configured: {'OPENAI_API_KEY' in os.environ}")

    # Run the server
    uvicorn.run(app, host=host, port=8080, log_level="info", access_log=True)
