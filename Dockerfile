# Ustad MCP Server - Multi-session SSE Container
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy requirements first, then source code
COPY src/ ./src/
COPY ustad_fastmcp.py .
COPY *.md .
COPY docker-compose.yml .

# Set environment variables for container  
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Expose port for SSE transport (default 8000)
EXPOSE 8000

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Create a non-root user for security
RUN useradd --create-home --shell /bin/bash ustad
RUN chown -R ustad:ustad /app
USER ustad

# Default to SSE transport for multi-session support
CMD ["python", "ustad_fastmcp.py", "--sse", "8000"]

# Usage examples:
# docker build -t ustad-mcp .
# docker run -p 8000:8000 ustad-mcp                          # SSE (default)
# docker run -p 8000:8000 ustad-mcp python ustad_fastmcp.py --http 8000  # HTTP
# docker run -p 8001:8001 ustad-mcp python ustad_fastmcp.py --sse 8001   # SSE on different port