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

---

## 🚀 Manual Implementation

Follow these steps to set up and run the system manually.

### 1. Train Models

First, you need to train the machine learning models. The system supports both GPU (CUDA) and CPU training.

**If you have a GPU (NVIDIA CUDA):**
```bash
make train GPU=1
```

**If you do not have a GPU (CPU only):**
```bash
make train
```

This will train both the categorization and opportunity models and save them to the `engine/` directory.

### 2. Collect Data

Gather fresh data from various sources (News, Government, Weather).
```bash
python3 collect_all.py
```
This script runs approximately 30 seconds to fetch the latest information.

### 3. Run ML Pipeline

Process the collected data through the machine learning pipeline to generate indicators and insights.
```bash
python3 pipeline.py
```
*Note: The first run may take longer (~5 minutes) to build the cache. Subsequent runs are much faster.*

### 4. Start Backend Server

Start the API server to serve the processed data.
```bash
python3 server.py
```
The server will start on `http://localhost:8000`.

### 5. Start User Interface (UI)

In a separate terminal, start the React frontend.

```bash
cd ui
npm install  # Install dependencies (first time only)
npm run dev
```
Access the application at `http://localhost:5173`.

### 6. Automated Updates (Cron Job)

To keep the system updated automatically, use `run_hourly.py`. This script handles data collection and pipeline processing in one go.

**Setup Cron Job:**
```bash
# Open crontab
crontab -e

# Add line to run hourly (adjust paths accordingly)
0 * * * * cd /path/to/evolveXr2 && /path/to/.venv/bin/python3 run_hourly.py
```

---

## 🐳 Docker Implementation

For production or submission, you can run the entire system using Docker.

**Prerequisites:**
- Docker & Docker Compose installed
- UI must be built first: `cd ui && npm run build && cd ..`

**Run with Docker Compose:**
```bash
# Build and start
docker-compose up --build

# Or run in background
docker-compose up -d
```

**What Docker does:**
1. Installs all dependencies
2. Starts the API server
3. Runs initial data collection and processing
4. Serves the application at `http://localhost:8000`

---

## 👥 Contributors

1. F.R.SUJEEVAN
2. L.SHARMILAN
3. J.J.K.POOJA
4. S.JUTHTHIS
