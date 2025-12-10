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

# Create optimized startup script with model downloading
RUN echo '#!/bin/bash\n\
    set -e\n\
    echo "Starting EvolveX services..."\n\
    \n\
    # Download models if not present (first run)\n\
    if [ ! -f "/app/preprocessing/local_model/config.json" ]; then\n\
    echo "📦 Models not found. Downloading (first run only)..."\n\
    python3 download_models.py || echo "⚠️  Warning: Model download failed"\n\
    fi\n\
    \n\
    # Start API server in background\n\
    python3 server.py &\n\
    SERVER_PID=$!\n\
    \n\
    # Wait for server to start\n\
    sleep 3\n\
    \n\
    # Run initial data collection and processing\n\
    echo "Running initial data collection..."\n\
    python3 collect_all.py || echo "Warning: Data collection had issues"\n\
    \n\
    echo "Processing data with ML pipeline..."\n\
    python3 pipeline.py || echo "Warning: Pipeline had issues"\n\
    \n\
    echo ""\n\
    echo "========================================"\n\
    echo "EvolveX is ready!"\n\
    echo "API Server: http://localhost:8000"\n\
    echo "========================================"\n\
    echo ""\n\
    \n\
    # Keep container running and show server logs\n\
    wait $SERVER_PID\n\
    ' > /app/start.sh && chmod +x /app/start.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/output/live_output.json || exit 1

# Start services
CMD ["/app/start.sh"]
