# 🐳 Ustad MCP Containerized Deployment Guide

## 🌟 SSE Transport - Multi-Session Ready

Our enhanced Ustad MCP server now supports **SSE (Server-Sent Events)** transport, making it perfect for containerized deployments with multiple concurrent sessions.

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)
```bash
# Clone and navigate to the project
cd ustad

# Create environment file
cp .env.example .env
# Edit .env with your API keys:
# OPENAI_API_KEY=your_key_here
# TAVILY_API_KEY=your_key_here

# Start the container
docker-compose up -d

# Check logs
docker-compose logs -f ustad-mcp
```

### Option 2: Direct Docker
```bash
# Build the image
docker build -t ustad-mcp .

# Run with SSE transport (recommended)
docker run -d \
  --name ustad-mcp-server \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e TAVILY_API_KEY=your_key \
  ustad-mcp

# Run with HTTP transport (alternative)
docker run -d \
  --name ustad-mcp-http \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  ustad-mcp python ustad_fastmcp.py --http 8000
```

## 🔧 Transport Options

### SSE Transport (Default - Recommended)
```bash
# Container startup
python ustad_fastmcp.py --sse 8000

# Features:
✅ Multiple concurrent sessions
✅ Real-time streaming updates  
✅ Persistent connections
✅ Automatic session isolation
✅ Perfect for collaborative reasoning
```

### HTTP Transport (Alternative)
```bash
# Container startup  
python ustad_fastmcp.py --http 8000

# Features:
✅ Multiple concurrent sessions
✅ Request/response pattern
✅ RESTful interface
✅ Stateless connections
```

### STDIO Transport (Local Only)
```bash
# Direct execution (not containerized)
python ustad_fastmcp.py --stdio

# Features:
✅ Single session only
✅ Lowest latency
✅ Perfect for local development
```

## 📡 Connecting to Containerized MCP

### From Claude Code:
```json
{
  "mcpServers": {
    "ustad-think": {
      "command": "docker",
      "args": ["exec", "ustad-mcp-server", "python", "ustad_fastmcp.py", "--stdio"],
      "env": {
        "OPENAI_API_KEY": "your_key",
        "TAVILY_API_KEY": "your_key"
      }
    }
  }
}
```

### Via SSE URL:
```
http://localhost:8000/sse
```

## 🛠️ Available Tools

All 15 enhanced reasoning tools:
- **ustad_start** - Session initialization
- **ustad_think** - Multi-perspective collaborative reasoning  
- **ustad_research** - Liberal fact-checking with Tavily
- **ustad_preflight** - Pre-flight risk analysis
- **ustad_context** - Context continuity management
- **ustad_systematic** - Systematic execution planning
- **ustad_session_info** - Session isolation statistics
- Plus: ustad_quick, ustad_decide, ustad_meta, etc.

## 🏥 Health Monitoring

```bash
# Check container health
docker ps
docker logs ustad-mcp-server

# Health endpoint
curl http://localhost:8000/health

# Session info
curl -X POST http://localhost:8000 \
  -H "Content-Type: application/json" \
  -d '{"method": "tools/call", "params": {"name": "ustad_session_info"}}'
```

## 🔄 Scaling Options

### Multiple Instances
```yaml
# docker-compose.override.yml
services:
  ustad-mcp-2:
    extends: ustad-mcp
    container_name: ustad-mcp-server-2
    ports:
      - "8001:8000"
      
  ustad-mcp-3:
    extends: ustad-mcp
    container_name: ustad-mcp-server-3
    ports:
      - "8002:8000"
```

### Load Balancing
```yaml
nginx:
  image: nginx:alpine
  ports:
    - "80:80"
  volumes:
    - ./nginx.conf:/etc/nginx/nginx.conf
  depends_on:
    - ustad-mcp
```

## 🛡️ Security Features

- **Non-root user** - Container runs as `ustad` user
- **No privileged mode** required
- **Environment variable isolation**
- **Session-based authentication** (when configured)
- **Network isolation** via Docker networks

## 📊 Production Deployment

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ustad-mcp
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ustad-mcp
  template:
    spec:
      containers:
      - name: ustad-mcp
        image: ustad-mcp:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: api-keys
              key: openai
```

### Cloud Run / Container Apps
```yaml
# Cloud Run deployment
gcloud run deploy ustad-mcp \
  --image gcr.io/project/ustad-mcp \
  --port 8000 \
  --set-env-vars OPENAI_API_KEY=key \
  --allow-unauthenticated
```

---

## 🎯 Why SSE for Containers?

1. **Perfect Multi-Session Support** - Each connection is naturally isolated
2. **Real-time Streaming** - Ideal for `ustad_think_stream` and collaborative reasoning
3. **Resource Efficiency** - Persistent connections reduce overhead
4. **Container-Native** - Works seamlessly with orchestration platforms
5. **Session Lifecycle** - Connection lifecycle matches session lifecycle

**Result**: Robust, scalable, multi-session MCP server ready for production! 🚀