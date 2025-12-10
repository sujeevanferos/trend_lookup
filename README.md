# EvolveX - Real-time Signal Intelligence Platform

A comprehensive system that collects, processes, and interprets real-time signals relevant to Sri Lanka's socio-economic and operational environment using advanced Machine Learning models.

## 🎯 Competition Features

This system generates three key indicator types as required:

### 1. National Activity Indicators
Major events, developments, disruptions, or topics gaining traction in the public space.
- **Output**: `output/national_activity_indicators.json`
- Political, economic, and national events
- Government decisions and policy changes
- Weather alerts and disaster warnings

### 2. Operational Environment Indicators
Abstracted signals that reflect conditions affecting business operations or customer behavior.
- **Output**: `output/operational_environment_indicators.json`
- Supply chain disruptions
- Utility issues (power, fuel, water)
- Market fluctuations and price changes
- Consumer behavior shifts

### 3. Risk & Opportunity Insights
Early warnings or emerging positive trends inferred from aggregated, real-time data.
- **Output**: `output/risk_opportunity_insights.json`
- Risk scores with categories (High/Medium/Low)
- Opportunity scores with explanations
- Top affected industries
- Detailed impact analysis

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+ (for UI)
- Git

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd evolveXr2
```

2. **Setup Python environment**
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. **Setup UI**
```bash
cd ui
npm install
npm run build  # Build production bundle
cd ..
```

4. **Download ML models** (Optional - will auto-download on first run)
```bash
python3 download_models.py
```

---

## 🎯 Running the Application

### **Option A: Manual Mode (Recommended for Development)**

**Complete workflow:**

```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Collect fresh data (~30 seconds)
python3 collect_all.py

# 3. Process data with ML pipeline (~5 minutes first run, then cached)
python3 pipeline.py

# 4. Start the backend server
python3 server.py
```

**Access the application:**
- UI: http://localhost:8000
- API: http://localhost:8000/output/

**For UI development (hot reload):**
```bash
# In a separate terminal
cd ui
npm run dev
# Access at: http://localhost:5173
```

**⚡ Performance tip:** After the first run, use `quick_fix_scores.py` instead of full pipeline:
```bash
python3 collect_all.py          # Collect new data
python3 quick_fix_scores.py     # Fast score update (3 min vs 50 min)
```

---

### **Option B: Docker Mode (For Production/Submission)**

> **Note**: Docker setup takes longer to build (~10-15 min) due to building UI and installing dependencies

**Prerequisites:**
- Docker & Docker Compose installed
- UI must be built first: `cd ui && npm run build && cd ..`

**Using Docker Compose:**
```bash
# Build and start
docker-compose up --build

# Or run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

**Access the application:**
- UI: http://localhost:8000
- API: http://localhost:8000/output/

**What Docker does automatically:**
1. ✅ Installs Python dependencies
2. ✅ Builds React UI (if not pre-built)
3. ✅ Starts API server on port 8000
4. ✅ Runs initial data collection
5. ✅ Processes data with ML pipeline

**Optional: Enable hourly auto-updates**
```bash
# The docker-compose.yml includes an optional cron service
docker-compose up -d evolvex-cron
```

---

## 📋 Quick Commands Summary

| Task | Manual Mode | Docker Mode |
|------|-------------|-------------|
| **Install** | `pip install -r requirements.txt` | `docker-compose build` |
| **Start** | `python3 server.py` | `docker-compose up` |
| **Update data** | `python3 collect_all.py && python3 quick_fix_scores.py` | Automatic (cron) |
| **View logs** | Terminal output | `docker-compose logs -f` |
| **Stop** | `Ctrl+C` | `docker-compose down` |
| **Access** | http://localhost:8000 | http://localhost:8000 |

## 📁 Project Structure

```
evolveXr2/
├── collect_all.py              # Master data collection script
├── pipeline.py                 # Main ML processing pipeline
├── server.py                   # CORS-enabled HTTP server (port 8000)
├── run_hourly.py              # Cron job for automated runs
│
├── Dockerfile                  # 🐳 Docker container definition
├── docker-compose.yml         # 🐳 Docker Compose orchestration
├── .dockerignore              # Docker build exclusions
│
├── resources/                  # Data collection scripts
│   ├── headlines/             # News scrapers (RSS, Google, YouTube, GDELT)
│   ├── gov/                   # Government sources
│   └── weather/               # Weather API integration
│
├── jsons/                     # Raw collected data
│   ├── sri_lanka_news.json
│   ├── government_news.json
│   └── srilanka_weather.json
│
├── preprocessing/             # ML models
│   ├── local_model/          # Zero-Shot classifier
│   └── opp_reg_model/        # Opportunity regression model
│
├── engine/                    # Classification engine
│   └── taxonomy.py           # Industry & category definitions
│
├── output/                    # Generated outputs
│   ├── live_output.json                        # Real-time events
│   ├── national_activity_indicators.json       # Competition output 1
│   ├── operational_environment_indicators.json # Competition output 2
│   ├── risk_opportunity_insights.json          # Competition output 3
│   └── processed_cache.json                    # Performance cache
│
├── history/                   # Historical data
│   └── hourly_history.jsonl  # Time-series snapshots
│
└── ui/                        # React frontend
    ├── src/
    │   ├── pages/
    │   │   ├── Home.jsx                    # Dashboard overview
    │   │   ├── Analysis.jsx                # Historical trends
    │   │   ├── NationalActivity.jsx        # National indicators
    │   │   ├── OperationalEnvironment.jsx  # Operational signals
    │   │   └── RiskOpportunity.jsx         # Risk/Opp insights
    │   └── components/
    └── ...
```

## 🔄 Data Flow

```
1. Data Collection (collect_all.py)
   ├── resources/headlines/headline_ocean.py → jsons/sri_lanka_news.json
   ├── resources/gov/gov.py → jsons/government_news.json
   └── resources/weather/weather.py → jsons/srilanka_weather.json

2. ML Processing (pipeline.py)
   ├── Load jsons/*.json
   ├── Run Zero-Shot classification (thematic categories)
   ├── Run Opportunity scoring (positive/negative impact)
   ├── Calculate industry-specific impacts
   ├── Classify into 3 indicator types
   └── Generate outputs:
       ├── output/live_output.json
       ├── output/national_activity_indicators.json
       ├── output/operational_environment_indicators.json
       ├── output/risk_opportunity_insights.json
       └── history/hourly_history.jsonl (append)

3. Serving (server.py + UI)
   ├── server.py serves JSON files via HTTP (port 8000)
   └── React UI fetches and displays (port 5173)
```

## ⚡ Performance Optimization

### Classification Cache System
The pipeline now includes intelligent caching for zero-shot classification results:

```bash
# First run: Builds cache (50-60 minutes)
python3 pipeline.py

# Subsequent runs: Uses cache (~5 minutes)
python3 pipeline.py
```

**How it works:**
- Caches thematic categories and industry classifications by text hash
- Stores results in `output/classification_cache.json`
- Shows cache hit/miss statistics during processing
- **10-20x faster** on re-runs with same data

**Quick Score Updates:**
```bash
python3 collect_all.py          # Collect new data
python3 quick_fix_scores.py     # Fast score update (3 min vs 50 min)
```

This script:
- ✅ Uses existing classifications
- ✅ Only recalculates opportunity scores  
- ✅ Completes in 2-3 minutes
- ✅ Perfect for regular updates

### Why the Pipeline is Slow

The bottleneck is **zero-shot classification**:
- Opportunity scoring: **0.01s/article** (fast)
- Thematic classification: **2-3s/article** (slow)
- Industry classification: **2-3s/article** (slow)

With 580+ articles:
- Total: ~5-6 seconds × 580 = **50-60 minutes**
- After caching: **~5 minutes** ⚡

## 🐳 Docker Troubleshooting

### Before Docker Build
**Important:** Build the UI first!
```bash
cd ui && npm run build && cd ..
```

### Common Issues

**"Connection refused" when accessing UI**  
✓ Check container is running: `docker ps`  
✓ Verify port 8000 is not in use: `lsof -i:8000`  
✓ Wait 30-60s for initial data collection

**Build takes forever**  
➜ Check build context size (should be \u003c100MB)  
➜ `.dockerignore` excludes large model files  
➜ First build downloads dependencies (~10-15 min)

**Port 8000 already in use**  
```bash
# Stop local server first
pkill -f "python3 server.py"

# Or change Docker port in docker-compose.yml:
# ports: - "8080:8000"
```

**UI not loading**  
➜ Ensure `ui/dist/` exists before Docker build  
➜ Run `cd ui && npm run build && cd ..`

**Container exits immediately**  
```bash
# Check logs for errors
docker logs evolvex-app

# Rebuild without cache
docker-compose build --no-cache
```

## ⏱️ Automated Runs

**Hourly Cron Job:**
```bash
# Add to crontab
0 * * * * cd /path/to/evolveXr2 && /path/to/.venv/bin/python3 run_hourly.py
```

Or use the provided script:
```bash
python3 run_hourly.py
```

## 🤖 ML Models

### Zero-Shot Classifier
- **Model**: `valhalla/distilbart-mnli-12-3` (local)
- **Purpose**: Classify news into thematic categories and industries
- **Categories**: 9 thematic (Politics, Economy, Weather, etc.)
- **Industries**: 15 sectors (Financial Services, Tourism, Agriculture, etc.)

### Opportunity Regression Model
- **Purpose**: Score news items for positive/negative impact
- **Range**: -1.0 (high risk) to +1.0 (high opportunity)
- **Output**: Combined with relevance for industry-specific scores

## 🎨 UI Features

### Dashboard Pages
1. **Home** - Real-time overview with market sentiment
2. **Analysis** - Historical trends and industry impact
3. **National Activity** - Major national events (competition feature)
4. **Operational Environment** - Business signals (competition feature)
5. **Risk & Opportunity** - Detailed insights (competition feature)

### Features
- Dark/Light mode toggle
- Real-time data updates (60s intervals)
- Responsive design
- Industry filtering
- Time-series charts

## 🔧 API Endpoints

All served via `server.py` on port 8000:

```
http://localhost:8000/output/live_output.json
http://localhost:8000/output/national_activity_indicators.json
http://localhost:8000/output/operational_environment_indicators.json
http://localhost:8000/output/risk_opportunity_insights.json
http://localhost:8000/history/hourly_history.jsonl
```

## ⏱️ Automated Runs

**Hourly Cron Job:**
```bash
# Add to crontab
0 * * * * cd /path/to/evolveXr2 && /path/to/.venv/bin/python3 run_hourly.py
```

Or use the provided script:
```bash
python3 run_hourly.py
```

## 📊 Sample Output

**National Activity Indicator:**
```json
{
  "id": "uuid",
  "timestamp": "2025-12-10T08:00:00Z",
  "headline": "Parliament passes new economic reform bill",
  "thematic_category": "Regulatory & Governance",
  "top_industries_affected": ["Financial Services", "Real Estate"],
  "impact_score": 0.4521
}
```

**Risk & Opportunity Insight:**
```json
{
  "id": "uuid",
  "headline": "IMF approves next tranche of funding",
  "risk_score": 0.0,
  "risk_category": "No Significant Risk",
  "opportunity_score": 0.7234,
  "opportunity_category": "High Opportunity",
  "opportunity_explanation": "Strong positive signals indicating significant growth potential.",
  "top_affected_industries": ["Financial Services", "Tourism", "Real Estate"]
}
```

## 🛠️ Development

**Train ML Models:**
```bash
make train          # Train both models
make train-cat      # Train categorization only
make train-opp      # Train opportunity model only
```

**Clean Up:**
```bash
# Remove old model directories
make clean-models

# Full cleanup
make clean
```

## 📝 Configuration

**API Keys Required:**
- `resources/headlines/yt_key.py` - YouTube API key
- `resources/weather/weather_key.py` - OpenWeather API key

## 🐛 Troubleshooting

**UI shows "Failed to fetch":**
- Ensure `server.py` is running on port 8000
- Check CORS settings in browser console

**No data in competition pages:**
- Run `pipeline.py` to generate JSON files
- Verify files exist in `output/` directory

**Cache issues:**
- Delete `output/processed_cache.json` to rebuild cache
- Run `pipeline.py --no-history` for testing

**Docker-specific issues:**

**Container won't start:**
```bash
# Check logs
docker-compose logs evolvex

# Rebuild image
docker-compose build --no-cache
docker-compose up -d
```

**Permission errors with volumes:**
```bash
# Fix volume permissions (Linux)
sudo chown -R $USER:$USER jsons/ output/ history/
```

**API keys not working in Docker:**
```bash
# Make sure API key files are mounted correctly
# Check docker-compose.yml volumes section
docker-compose exec evolvex ls -la resources/headlines/
docker-compose exec evolvex ls -la resources/weather/
```

**Port 8000 already in use:**
```bash
# Find and kill process using port 8000
sudo lsof -i :8000
# Or change port in docker-compose.yml:
#   ports:
#     - "8080:8000"  # Use port 8080 instead
```

**Hourly cron not running:**
```bash
# Check cron service logs
docker-compose logs -f evolvex-cron

# Manually trigger pipeline in container
docker-compose exec evolvex python3 run_hourly.py
```


## 👥 Contributors

F.R.Sujeevan
L.Sharmilan
J.J.K.Pooja
S.Juththis


**Built for IEEE Competition** - Real-time Signal Intelligence for Sri Lanka
