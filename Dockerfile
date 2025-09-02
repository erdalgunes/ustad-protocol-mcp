# Ustad - The Master Teacher MCP Server
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY .env.example ./

# Set Python path
ENV PYTHONPATH="/app/src"

# Expose port for HTTP mode (if needed)
EXPOSE 8080

# Run HTTP server for Cloud Run
CMD ["python", "-m", "src.ustad.http_mcp_server"]