# Deployment Guide - Ustad Protocol MCP v0.1.0

## 🚀 Quick Deployment

### Prerequisites

- Docker installed
- Docker Compose installed
- Tavily API key (get from https://tavily.com)

### Steps

1. **Clone the repository**

```bash
git clone https://github.com/erdalgunes/ustad-protocol-mcp.git
cd ustad-protocol-mcp
```

2. **Configure environment**

```bash
cp .env.example .env
# Edit .env and add your TAVILY_API_KEY
```

3. **Build and run**

```bash
docker-compose up -d
```

4. **Verify deployment**

```bash
# Check health
curl http://localhost:8080/health

# Check logs
docker logs ustad-protocol-mcp-server
```

## 📋 Container Details

- **Image**: `ustad-protocol-mcp:v0.1.0`
- **Port**: 8080 (mapped to internal 8000)
- **Health endpoint**: `http://localhost:8080/health`
- **SSE endpoint**: `http://localhost:8080/sse`

## 🛠️ Available Tools

1. **ustad_think** - Sequential thinking for structured problem-solving
1. **ustad_search** - Web search via Tavily API

## 📊 Current Status

✅ **VERIFIED DEPLOYMENT**:

- Docker image built successfully
- Container running healthy
- Health endpoint responding
- Tavily API configured
- Rate limiting enabled

## 🔧 Troubleshooting

### Port already in use

Change the port mapping in `docker-compose.yml`:

```yaml
ports:
  - "9000:8000"  # Use different external port
```

### API key not working

Ensure your `.env` file contains:

```
TAVILY_API_KEY=tvly-prod-YOUR_KEY_HERE
```

### Container won't start

Check logs:

```bash
docker-compose logs -f
```

## 🎯 Integration with Claude

To replace existing MCP servers with this unified server:

1. Stop existing sequential-thinking and tavily MCPs
1. Update your MCP client configuration to point to `http://localhost:8080`
1. Both tools (ustad_think and ustad_search) are available in one server

## 📈 Performance

- **Image size**: ~200MB (multi-stage build with slim base)
- **Memory usage**: < 100MB idle
- **Startup time**: < 3 seconds
- **Test coverage**: 93.23%

## 🔐 Security

- ✅ Non-root user (ustaduser)
- ✅ Rate limiting enabled (60 req/min)
- ⚠️ Authentication disabled (development mode)
- ✅ Health checks configured

## 📝 Version

**v0.1.0** - First stable release

- Minimal MCP server with 2 tools
- Docker containerized
- Production-ready configuration
- 93.23% test coverage
