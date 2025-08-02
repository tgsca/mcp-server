# Multi-stage build for MCP Text Pseudonymizer
FROM python:3.12-slim AS builder

# Set build arguments
ARG TORCH_VERSION=2.1.0
ARG TORCH_INDEX_URL=https://download.pytorch.org/whl/cpu

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
RUN pip install uv

# Set working directory
WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install dependencies using uv
RUN uv venv /app/venv && \
    . /app/venv/bin/activate && \
    uv pip install torch --index-url ${TORCH_INDEX_URL} && \
    uv pip install -e .

# Pre-download NER models to reduce startup time
RUN . /app/venv/bin/activate && \
    python -c "\
import flair; \
from flair.models import SequenceTagger; \
print('Downloading German NER model...'); \
SequenceTagger.load('flair/ner-german'); \
print('Downloading English NER model...'); \
SequenceTagger.load('flair/ner-english'); \
print('Models downloaded successfully')"

# Runtime stage
FROM python:3.12-slim

# Install system dependencies for runtime
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash mcp-user

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /app/venv /app/venv

# Copy application code
COPY src/ ./src/
COPY main.py ./
COPY .env.template ./

# Create directories for logs and models
RUN mkdir -p /app/logs /app/models && \
    chown -R mcp-user:mcp-user /app

# Switch to non-root user
USER mcp-user

# Set environment variables
ENV PATH="/app/venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV MODEL_CACHE_DIR="/app/models"
ENV LOG_LEVEL="INFO"

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "\
import sys; \
sys.path.append('/app'); \
try: \
    from src.pseudonymizer import TextPseudonymizer; \
    pseudonymizer = TextPseudonymizer(); \
    result = pseudonymizer.detect_language('Hello world'); \
    assert result.language in ['en', 'de']; \
    print('Health check passed'); \
    sys.exit(0); \
except Exception as e: \
    print(f'Health check failed: {e}'); \
    sys.exit(1)"

# Expose port for MCP server
EXPOSE 3000

# Run the MCP server
CMD ["python", "main.py"]