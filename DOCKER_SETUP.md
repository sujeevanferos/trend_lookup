# 🚀 EvolveX - Quick Setup Guide

## Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- Git installed
- 4GB+ RAM available
- Internet connection (for first run - model download)

---

## 📥 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/sujeevanferos/trend_lookup.git
cd trend_lookup
```

### 2. Create API Key Files

Create your API key files (these are gitignored for security):

```bash
# YouTube API Key
cat > resources/headlines/yt_key.py << 'EOF'
YOUTUBE_API_KEY = "your-youtube-api-key-here"
EOF

# Weather API Key  
cat > resources/weather/weather_key.py << 'EOF'
WEATHER_API_KEY = "your-weather-api-key-here"
EOF
```

> **Note:** Get API keys from:
> - YouTube: [Google Cloud Console](https://console.cloud.google.com/)
> - Weather: [OpenWeatherMap](https://openweathermap.org/api) or similar

### 3. Build the Docker Image

```bash
docker build -t evolvex:latest .
```

**Expected build time:** ~15-20 minutes (first time only)

### 4. Run the Container

```bash
docker run -d \
  --name evolvex \
  -p 8000:8000 \
  -v $(pwd)/jsons:/app/jsons \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/history:/app/history \
  -v $(pwd)/preprocessing/local_model:/app/preprocessing/local_model \
  -v $(pwd)/resources/headlines/yt_key.py:/app/resources/headlines/yt_key.py \
  -v $(pwd)/resources/weather/weather_key.py:/app/resources/weather/weather_key.py \
  evolvex:latest
```

### 5. Watch Startup Logs

```bash
docker logs -f evolvex
```

**First run:** ML models will download (~256MB, 2-3 minutes)
**Subsequent runs:** Models are cached, starts immediately

### 6. Test the API

Once you see "EvolveX is ready!" in the logs:

```bash
# Test main output
curl http://localhost:8000/output/live_output.json

# Test other endpoints
curl http://localhost:8000/output/national_activity_indicators.json
curl http://localhost:8000/output/operational_environment_indicators.json
curl http://localhost:8000/output/risk_opportunity_insights.json
```

---

## 🎯 Alternative: Using Docker Compose (Recommended)

**Simpler approach for managing containers:**

### 1. Start Services

```bash
docker-compose up -d
```

### 2. View Logs

```bash
docker-compose logs -f
```

### 3. Stop Services

```bash
docker-compose down
```

---

## 📊 What Happens on First Run?

1. ✅ Container starts
2. 📦 Downloads DistilBERT model (~256MB) - **one-time only**
3. 🌐 Fetches initial data (news, weather, etc.)
4. 🤖 Runs ML pipeline for analysis
5. ✅ API server ready on `http://localhost:8000`

**Total first run time:** ~5-7 minutes  
**Subsequent runs:** ~1-2 minutes

---

## 🛠️ Common Commands

### Container Management

```bash
# Start container
docker start evolvex

# Stop container
docker stop evolvex

# Restart container
docker restart evolvex

# View logs
docker logs -f evolvex

# Execute command in container
docker exec -it evolvex /bin/bash
```

### Cleanup

```bash
# Remove container
docker stop evolvex && docker rm evolvex

# Remove image
docker rmi evolvex:latest

# Clean everything (careful!)
docker system prune -a
```

---

## 📁 Directory Structure

```
trend_lookup/
├── Dockerfile              # Docker build instructions
├── docker-compose.yml      # Compose configuration
├── requirements.txt        # Python dependencies
├── server.py              # API server
├── pipeline.py            # ML processing pipeline
├── collect_all.py         # Data collection
├── download_models.py     # Model downloader
├── engine/                # Core processing logic
├── preprocessing/         # ML models & training
├── resources/            # Data sources configuration
├── ui/                   # Frontend (built into Docker)
├── jsons/                # Raw data cache (volume)
├── output/               # Processed outputs (volume)
└── history/              # Historical data (volume)
```

---

## 🐛 Troubleshooting

### Container won't start

```bash
# Check logs for errors
docker logs evolvex

# Check if port 8000 is already in use
lsof -i :8000
```

### Models not downloading

```bash
# Check internet connection
docker exec evolvex curl -I https://huggingface.co

# Manually trigger download
docker exec evolvex python3 download_models.py
```

### API returns errors

```bash
# Check if all services are running
docker exec evolvex ps aux

# Restart container
docker restart evolvex
```

### Out of disk space during build

```bash
# Clean up Docker cache
docker system prune -a -f
docker builder prune -f
```

---

## 🔒 Security Notes

- ⚠️ **Never commit API keys** - they are in `.gitignore`
- ⚠️ **Don't share your keys** publicly
- ✅ Use environment variables for production deployment
- ✅ API keys should be mounted as volumes (as shown above)

---

## 📡 API Endpoints

Once running, access these endpoints at `http://localhost:8000/`:

| Endpoint | Description |
|----------|-------------|
| `/output/live_output.json` | Latest processed data |
| `/output/national_activity_indicators.json` | National activity metrics |
| `/output/operational_environment_indicators.json` | Environmental indicators |
| `/output/risk_opportunity_insights.json` | Risk & opportunity analysis |

---

## 🎓 Development Setup

For development (without Docker):

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download models
python download_models.py

# Run server
python server.py
```

---

## 📞 Support

If you encounter issues:

1. Check the logs: `docker logs evolvex`
2. Ensure Docker daemon is running
3. Verify API keys are set correctly
4. Check available disk space (need ~3GB)
5. Ensure ports 8000 is available

---

## 📝 System Requirements

- **Docker:** 20.10+
- **RAM:** 4GB minimum, 8GB recommended
- **Disk:** 3GB for Docker image + data
- **Network:** Required for initial model download
- **OS:** Linux, macOS, or Windows with WSL2

---

**🎉 You're all set!** The API will be available at `http://localhost:8000` once the container is running.
