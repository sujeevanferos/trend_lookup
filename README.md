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
- Virtual environment (recommended)

### Installation

1. **Clone and setup Python environment**
```bash
git clone <repository-url>
cd evolveXr2
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. **Install UI dependencies**
```bash
cd ui
npm install
cd ..
```

### Option A: Docker Deployment (Recommended for Production)

**Using Docker Compose (easiest):**
```bash
# Build and start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Using Docker directly:**
```bash
# Build image
docker build -t evolvex .

# Run container
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/jsons:/app/jsons \
  -v $(pwd)/output:/app/output \
  -v $(pwd)/history:/app/history \
  --name evolvex-app \
  evolvex

# View logs
docker logs -f evolvex-app

# Stop container
docker stop evolvex-app
```

**What Docker does automatically:**
1. ✅ Installs all Python dependencies
2. ✅ Builds the React UI
3. ✅ Starts the API server (port 8000)
4. ✅ Runs initial data collection
5. ✅ Processes data with ML pipeline
6. ✅ Serves all JSON outputs

**Access the API:**
- API Server: http://localhost:8000
- Live Output: http://localhost:8000/output/live_output.json
- National Activity: http://localhost:8000/output/national_activity_indicators.json
- Operational Environment: http://localhost:8000/output/operational_environment_indicators.json
- Risk & Opportunity: http://localhost:8000/output/risk_opportunity_insights.json

**Optional: Enable hourly auto-updates**
```bash
# The docker-compose.yml includes an optional cron service
# Uncomment the evolvex-cron service to enable hourly pipeline runs
docker-compose up -d evolvex-cron
```

### Option B: Manual Setup (Development)

**Complete Workflow (Recommended):**
```bash
# 1. Collect data from all sources
python3 collect_all.py

# 2. Process with ML models and generate all outputs
python3 pipeline.py

# 3. Start the API server (separate terminal)
python3 server.py

# 4. Start the UI (separate terminal)
cd ui && npm run dev
```

**Access the dashboard**: http://localhost:5173

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

**Caching System:**
- MD5-based deduplication prevents redundant ML inference
- First run: ~6 minutes (processes all items)
- Subsequent runs: ~9 seconds (skips cached items)
- **97% CPU reduction** on repeat runs

Cache file: `output/processed_cache.json`

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

## 📄 License

[Add your license here]

## 👥 Contributors

[Add contributors]

---

**Built for IEEE Competition** - Real-time Signal Intelligence for Sri Lanka
