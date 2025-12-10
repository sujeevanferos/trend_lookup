# Docker Build Guide

## Problem: "Connection Refused" When Running with Docker

### Root Cause
The UI needs to be built **before** running `docker-compose up`. Docker expects `ui/dist/` to exist.

### Solution

**Before building Docker image:**
```bash
# 1. Build the UI
cd ui
npm install
npm run build
cd ..

# 2. Now Docker will work
docker-compose up --build
```

### Why This Happens
The Dockerfile has a multi-stage build:
1. **Stage 1**: Python dependencies
2. **Stage 2**: Frontend builder (builds UI from source)  
3. **Stage 3**: Copies built UI from Stage 2

If you build locally first, Docker can skip the frontend build stage and use your local build.

### Quick Commands

```bash
# Full Docker build (recommended)
make docker-build    # Builds UI + Docker image
make docker-up       # Starts containers

# Or manually:
cd ui && npm run build && cd ..
docker-compose up --build
```

### Accessing the App

After starting:
- UI: http://localhost:8000/
- API: http://localhost:8000/output/

### Troubleshooting

**"Connection refused"**
- ✓ UI is built (check `ui/dist/` exists)
- ✓ Container is running (`docker ps`)
- ✓ Port 8000 is not in use by another process

**Container exits immediately**
```bash
docker logs evolvex-app
```

**UI loads but shows "Failed to fetch"**
- Wait 30-60 seconds for initial data collection
- Check: `curl http://localhost:8000/output/risk_opportunity_insights.json`
