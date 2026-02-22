FROM python:3.11-slim

WORKDIR /app

# Install system dependencies needed by some Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the fastembed/ONNX model at build time
# This avoids a slow cold-start download on first request
RUN python -c "from fastembed import TextEmbedding; TextEmbedding(model_name='BAAI/bge-small-en-v1.5')"

# Copy application code
COPY . .

# Render injects PORT at runtime (default 10000)
EXPOSE 10000

# Use shell form so ${PORT} is expanded at runtime
CMD gunicorn wsgi:app --workers 1 --bind "0.0.0.0:${PORT:-10000}" --timeout 300 --keep-alive 5
