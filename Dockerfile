FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and corpus
COPY . .

# Build arg to skip heavy steps in CI
ARG SKIP_MODEL_DOWNLOAD=false

# Pre-build the ChromaDB vector index AND download the embedding model
# during Docker build (build env has no memory limit).
# At runtime the app finds a pre-built index and loads the model
# lazily on first query only — startup stays under 200MB.
RUN if [ "$SKIP_MODEL_DOWNLOAD" != "true" ]; then \
      python -c "\
from config import Config; \
from app.rag.ingest import build_index, get_collection; \
config = {k: getattr(Config, k) for k in dir(Config) if not k.startswith('_')}; \
print('Pre-building ChromaDB index...'); \
count = build_index(config); \
print(f'Indexed {count} chunks into ChromaDB') \
"; \
    fi

# Render injects PORT at runtime (default 10000)
EXPOSE 10000

# Use shell form so ${PORT} is expanded at runtime
CMD gunicorn wsgi:app --workers 1 --bind "0.0.0.0:${PORT:-10000}" --timeout 300 --keep-alive 5
