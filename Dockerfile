# Multi-stage build for EvolveX - Optimized Version
# This reduces image size by ~60-70% compared to the standard build

# Stage 1: Python dependencies builder
FROM python:3.10-slim as python-builder

WORKDIR /app

# Install only build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first for better caching
COPY requirements.txt .

# Install Python packages to a specific location
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Frontend builder
FROM node:18-alpine as frontend-builder

WORKDIR /app/ui

# Copy package files
COPY ui/package*.json ./

# Install dependencies (npm ci is faster and more reliable)
RUN npm ci

# Copy UI source
COPY ui/ ./

# Build UI for production
RUN npm run build

# Stage 3: Final lightweight image
FROM python:3.10-slim

WORKDIR /app

# Install only runtime dependencies (curl for healthcheck)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python packages from builder
COPY --from=python-builder /install /usr/local

# Copy application code (only what's needed)
COPY collect_all.py pipeline.py server.py run_hourly.py download_models.py ./
COPY engine/ ./engine/
COPY preprocessing/*.py ./preprocessing/
COPY preprocessing/*.csv ./preprocessing/
COPY resources/ ./resources/

# Copy built UI from frontend stage
COPY --from=frontend-builder /app/ui/dist /app/ui/dist

# Create necessary directories
RUN mkdir -p jsons output history

# Create volumes for data persistence
VOLUME ["/app/jsons", "/app/output", "/app/history"]

# Expose ports
EXPOSE 8000

# Create optimized startup script - server starts first!
RUN echo '#!/bin/bash\\n\\\nset -e\\n\\\necho \"Starting EvolveX services...\"\\n\\\n\\n\\\n# Start API server immediately\\n\\\necho \"🚀 Starting web server on port 8000...\"\\n\\\npython3 server.py \u0026\\n\\\nSERVER_PID=$!\\n\\\necho \"✓ Server running (PID: $SERVER_PID)\"\\n\\\n\\n\\\n# Download models in background if needed\\n\\\nif [ ! -f \"/app/preprocessing/local_model/config.json\" ]; then\\n\\\n  echo \"📦 Downloading models in background...\"\\n\\\n  (python3 download_models.py || echo \"⚠️  Warning: Model download failed\") \u0026\\n\\\nelse\\n\\\n  echo \"✓ Models already present\"\\n\\\nfi\\n\\\n\\n\\\n# Wait a moment for server to initialize\\n\\\nsleep 2\\n\\\n\\n\\\n# Run initial data collection in background\\n\\\necho \"📊 Running data collection...\"\\n\\\n(python3 collect_all.py \u0026\u0026 python3 pipeline.py || echo \"⚠️  Pipeline issues\") \u0026\\n\\\n\\n\\\necho \"\"\\n\\\necho \"========================================\"\\n\\\necho \"✅ EvolveX is ready!\"\\n\\\necho \"🌐 UI: http://localhost:8000/\"\\n\\\necho \"📡 API: http://localhost:8000/output/\"\\n\\\necho \"========================================\"\\n\\\necho \"\"\\n\\\necho \"ℹ️  Data collection and model download running in background...\"\\n\\\n\\n\\\n# Keep container running\\n\\\nwait $SERVER_PID\\n\\\n' \u003e /app/start.sh \u0026\u0026 chmod +x /app/start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/output/live_output.json || exit 1

# Start services
CMD ["/app/start.sh"]
