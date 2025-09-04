# Multi-stage build for minimal image size
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install poetry and build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Copy poetry files first for better caching
COPY pyproject.toml poetry.lock* ./
# Install dependencies (no dev deps, no root package yet)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --only main

# Production stage
FROM python:3.11-slim

# Create non-root user for security
RUN useradd -m -u 1000 ustaduser

# Set working directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy application code
COPY --chown=ustaduser:ustaduser ustad_mcp_server.py .
COPY --chown=ustaduser:ustaduser src/sequential_thinking.py ./src/
COPY --chown=ustaduser:ustaduser src/constants.py ./src/
COPY --chown=ustaduser:ustaduser scripts/health_check.py ./scripts/

# Set environment variables
ENV PATH=/home/ustaduser/.local/bin:$PATH \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DOCKER_CONTAINER=true \
    PORT=8080

# Switch to non-root user
USER ustaduser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python scripts/health_check.py || exit 1

# Expose port
EXPOSE 8080

# Run the server
CMD ["python", "ustad_mcp_server.py"]
