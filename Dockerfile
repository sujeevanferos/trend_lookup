# Multi-stage build for EvolveX
FROM python:3.10-slim as backend

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY collect_all.py pipeline.py server.py run_hourly.py ./
COPY engine/ ./engine/
COPY preprocessing/ ./preprocessing/
COPY resources/ ./resources/

# Create necessary directories
RUN mkdir -p jsons output history

# Frontend build stage
FROM node:18-alpine as frontend

WORKDIR /app/ui

# Copy package files
COPY ui/package*.json ./

# Install dependencies
RUN npm ci

# Copy UI source
COPY ui/ ./

# Build UI
RUN npm run build

# Final stage
FROM python:3.10-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from backend stage
COPY --from=backend /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=backend /usr/local/bin /usr/local/bin

# Copy application code from backend stage
COPY --from=backend /app /app

# Copy built UI from frontend stage
COPY --from=frontend /app/ui/dist /app/ui/dist

# Create volumes for data persistence
VOLUME ["/app/jsons", "/app/output", "/app/history"]

# Expose ports
EXPOSE 8000 5173

# Create startup script
RUN echo '#!/bin/bash\n\
echo "Starting EvolveX services..."\n\
\n\
# Start API server in background\n\
python3 server.py &\n\
SERVER_PID=$!\n\
\n\
# Wait for server to start\n\
sleep 2\n\
\n\
# Run initial data collection and processing\n\
echo "Running initial data collection..."\n\
python3 collect_all.py\n\
\n\
echo "Processing data with ML pipeline..."\n\
python3 pipeline.py\n\
\n\
echo ""\n\
echo "========================================"\n\
echo "EvolveX is ready!"\n\
echo "API Server: http://localhost:8000"\n\
echo "========================================"\n\
echo ""\n\
echo "Access outputs:"\n\
echo "  - Live data: http://localhost:8000/output/live_output.json"\n\
echo "  - National Activity: http://localhost:8000/output/national_activity_indicators.json"\n\
echo "  - Operational Environment: http://localhost:8000/output/operational_environment_indicators.json"\n\
echo "  - Risk & Opportunity: http://localhost:8000/output/risk_opportunity_insights.json"\n\
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
