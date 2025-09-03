# Ustad Protocol MCP Server

> **"Ustad"** (Turkish/Urdu: "Master/Teacher") - Minimal MCP server with sequential thinking and search

[![MCP Version](https://img.shields.io/badge/MCP-v1.0.0-blue.svg)](https://modelcontextprotocol.io/)
[![FastMCP](https://img.shields.io/badge/FastMCP-v2.0.0-orange.svg)](https://github.com/jlowin/fastmcp)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](Dockerfile)

## ✨ Features

- 🧠 **Sequential Thinking**: Structured problem-solving with chain-of-thought reasoning
- 🔍 **Web Search**: Tavily-powered search for fact-checking and research
- 🐳 **Containerized**: Production-ready Docker setup with health checks
- 📡 **SSE Protocol**: Real-time Server-Sent Events communication
- 🚀 **FastMCP**: Built on FastMCP for optimal performance
- 🔒 **Secure**: Non-root container user, intelligent host detection (0.0.0.0 in containers, localhost in dev)

## 🚀 Quick Start

### Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd ustad-protocol

# Configure environment
cp .env.example .env
# Edit .env and add your TAVILY_API_KEY

# Build and run
docker-compose up --build
```

Server will be available at `http://localhost:8000`

### Local Development

```bash
# Install dependencies
poetry install

# Set environment
export TAVILY_API_KEY=your_api_key_here

# Run server
poetry run python ustad_mcp_server.py
```

## 🛠️ Tools

### ustad_think

Sequential thinking for structured problem-solving:

```json
{
  "thought": "Analyzing the problem step by step",
  "thought_number": 1,
  "total_thoughts": 5,
  "next_thought_needed": true
}
```

### ustad_search

Web search using Tavily API:

```json
{
  "query": "Python best practices 2024",
  "max_results": 5,
  "search_type": "general"
}
```

## 📝 Configuration

Set in `.env` file or environment:

| Variable         | Description               | Default                            |
| ---------------- | ------------------------- | ---------------------------------- |
| `TAVILY_API_KEY` | Tavily API key for search | Required                           |
| `PORT`           | Server port               | 8000                               |
| `HOST`           | Server host               | Auto-detected based on environment |

## 🏗️ Architecture

```
.
├── ustad_mcp_server.py        # Main MCP server
├── src/
│   └── sequential_thinking.py # Sequential thinking logic
├── Dockerfile                 # Multi-stage Docker build
├── docker-compose.yml         # Docker Compose config
└── pyproject.toml            # Poetry dependencies
```

## 📄 License

MIT
