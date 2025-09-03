# Multi-stage build for minimal image size with uv
FROM python:3.11-slim as builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Copy dependency files first for better caching
COPY pyproject.toml uv.lock README.md ./

# Install dependencies (removed cache mount for compatibility)
RUN uv sync --frozen --no-dev --no-install-project

# Copy all source files
COPY ustad_mcp_server.py .
COPY src/ ./src/

# Install the project itself
RUN uv sync --frozen --no-dev

# Production stage
FROM python:3.11-slim

# Create non-root user for security
RUN useradd -m -u 1000 ustaduser

# Set working directory
WORKDIR /app

# Copy the virtual environment and application from builder
COPY --from=builder --chown=ustaduser:ustaduser /app /app

# Set environment variables
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DOCKER_CONTAINER=true \
    HOST=0.0.0.0 \
    PORT=8000

# Switch to non-root user
USER ustaduser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health').raise_for_status()" || exit 1

# Expose port
EXPOSE 8000

# Run the server
CMD ["python", "ustad_mcp_server.py"]
