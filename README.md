# 🧠 The Ustad Protocol

> **"Ustad"** (Turkish/Urdu: "Master/Teacher") - Revolutionary AI collaborative reasoning through multi-perspective dialogue

[![MCP Version](https://img.shields.io/badge/MCP-v2.0.0-blue.svg)](https://modelcontextprotocol.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](Dockerfile)

## 🌟 What is the Ustad Protocol?

The Ustad Protocol is a groundbreaking approach to AI reasoning that **overcomes individual AI limitations through collaborative multi-perspective dialogue**. Instead of single AI responses, multiple AI perspectives engage in structured debate, challenge each other's ideas, and reach true consensus.

### Core Innovation: Multi-Round Collaborative Dialogue

```
Problem → 8 AI Perspectives → Challenge & Debate → Consensus → Synthesis → Wisdom
```

- **Challenge Phase**: Ideas are tested through disagreement
- **Consensus Building**: True synthesis emerges from dialogue  
- **Adaptive Reasoning**: Problem complexity determines dialogue depth
- **Session Isolation**: Multiple concurrent users without interference

## 🚀 Key Features

### 🎯 Collaborative Intelligence
- **Multi-Round Dialogue**: 3-8 AI perspectives engage in structured debate
- **Real-Time Streaming**: Watch collaborative reasoning unfold live
- **Custom Perspectives**: Choose analytical, creative, critical, practical, strategic, etc.
- **Meta-Reasoning**: Intelligent tool selection for optimal problem-solving

### 🐳 Production-Ready Deployment
- **Containerized**: Docker + Docker Compose ready
- **Multi-Transport**: STDIO, HTTP, SSE (Server-Sent Events)
- **Session Isolation**: Thread-local storage for concurrent users
- **Health Monitoring**: Built-in health checks and monitoring

### 🛠️ Enhanced Reasoning Tools
- **`ustad_start`**: Initialize collaborative reasoning system
- **`ustad_think`**: Full 3-8 perspective collaborative dialogue
- **`ustad_quick`**: Fast 3-perspective analysis
- **`ustad_research`**: Liberal research with fact-checking
- **`ustad_preflight`**: Risk analysis and failure prevention

## 📦 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/erdalgunes/ustad-protocol.git
cd ustad-protocol

# Set environment variables
export OPENAI_API_KEY="your-openai-api-key"
export TAVILY_API_KEY="your-tavily-api-key"

# Start with Docker Compose (SSE transport for multi-session)
docker-compose up -d

# Server running at: http://localhost:8000/sse
```

### Option 2: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run STDIO transport (single session)
python ustad_fastmcp.py --stdio

# Run SSE transport (multi-session)
python ustad_fastmcp.py --sse --port 8000
```

## 🔧 Claude Code Integration

Add to your `~/.claude.json`:

```json
{
  "mcpServers": {
    "ustad-think": {
      "type": "sse",
      "url": "http://localhost:8000/sse",
      "env": {
        "OPENAI_API_KEY": "${OPENAI_API_KEY}",
        "TAVILY_API_KEY": "${TAVILY_API_KEY}"
      }
    }
  }
}
```

## 🧪 Example Usage

### Multi-Perspective Analysis
```
Use ustad_think to analyze: "How should we architect a scalable microservices system?"
```

**Result**: 8 AI perspectives debate architecture patterns, challenge assumptions, and reach consensus on optimal design.

### Quick Decision Making
```
Use ustad_quick to decide: "Should we use REST or GraphQL for our API?"
```

**Result**: Fast 3-perspective analysis with clear recommendation.

### Research-Backed Solutions
```
Use ustad_research on: "Latest Docker security best practices 2025"
```

**Result**: Web research combined with collaborative analysis.

## 🎪 Architecture

### Transport Options

| Transport | Use Case | Sessions | Performance |
|-----------|----------|----------|-------------|
| **STDIO** | Local development | Single | Fastest |
| **HTTP** | Simple API calls | Multiple | Good |
| **SSE** | Real-time streaming | Multiple | Optimal |

### Session Isolation

```python
from threading import local
_session_storage = local()

def get_session_id():
    if not hasattr(_session_storage, 'session_id'):
        _session_storage.session_id = str(uuid.uuid4())[:8]
    return _session_storage.session_id
```

## 📊 Performance Metrics

- **Cost Optimized**: ~$0.008 per complex analysis (GPT-3.5-turbo)
- **Speed**: Cold start eliminated, session continuity enabled
- **Scalability**: Thread-safe session isolation
- **Reliability**: Containerized with health monitoring

## 🏗️ Project Structure

```
ustad-protocol/
├── ustad_fastmcp.py          # Main MCP server with 15 tools
├── Dockerfile                # Multi-stage container build
├── docker-compose.yml        # SSE deployment configuration
├── requirements.txt          # Python dependencies
├── CONTAINER_DEPLOYMENT.md   # Deployment guide
├── test_enhanced_mcp.py      # Comprehensive tests
└── CLAUDE.md                 # Project-specific instructions
```

## 🔬 Available Tools

| Tool | Purpose | Perspectives | Streaming |
|------|---------|-------------|-----------|
| `ustad_start` | Session initialization | - | ❌ |
| `ustad_think` | Full collaborative reasoning | 3-8 | ✅ |
| `ustad_quick` | Fast analysis | 3 | ❌ |
| `ustad_decide` | Decision making | 4 | ❌ |
| `ustad_research` | Research + analysis | 4 | ❌ |
| `ustad_preflight` | Risk assessment | 4 | ❌ |

## 🚀 Deployment Options

### Local Development
```bash
python ustad_fastmcp.py --stdio
```

### Production (Docker)
```bash
docker-compose up -d
```

### Cloud Run / Kubernetes
See [CONTAINER_DEPLOYMENT.md](CONTAINER_DEPLOYMENT.md) for detailed guides.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Claude Code**: For the excellent MCP integration platform
- **FastMCP**: For the robust MCP framework
- **OpenAI**: For powering the collaborative intelligence
- **Tavily**: For comprehensive web research capabilities

---

**"The apprentice asks, the master guides, wisdom emerges from dialogue."** 🧠✨

[Report Issues](https://github.com/erdalgunes/ustad-protocol/issues) | [Documentation](https://github.com/erdalgunes/ustad-protocol/wiki) | [Discussions](https://github.com/erdalgunes/ustad-protocol/discussions)