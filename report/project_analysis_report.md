# EvolveX Project Analysis Report

**Date**: 2025-12-12
**Project**: EvolveX - Real-time Signal Intelligence Platform

## 1. Executive Summary
EvolveX is a sophisticated real-time signal intelligence platform designed to monitor and analyze socio-economic and operational signals in Sri Lanka. It leverages a Python-based machine learning pipeline to process news and data from various sources, classifying them into actionable insights (National Activity, Operational Environment, Risk & Opportunity). The system presents this data through a modern React-based user interface.

## 2. Project Architecture
The project follows a decoupled client-server architecture, containerized with Docker.

### Backend (Python)
- **Framework**: Flask (for API serving).
- **Core Logic**: Custom ETL pipeline (`collect_all.py`, `pipeline.py`).
- **ML Models**: 
    - Zero-Shot Classification (`valhalla/distilbart-mnli-12-3`).
    - Opportunity Regression Model.
- **Data Storage**: JSON files and JSONL for history (NoSQL-style flat file storage).

### Frontend (React)
- **Framework**: React 18 with Vite.
- **Styling**: TailwindCSS.
- **Visualization**: Recharts, Chart.js.
- **Routing**: React Router.

### Infrastructure
- **Containerization**: Docker & Docker Compose.
- **Automation**: Cron-based scheduling for hourly updates.

## 3. Code Statistics
| Language | Files | Lines of Code (Approx) |
|----------|-------|------------------------|
| Python   | ~20   | 4,289                  |
| JSX      | ~15   | 1,532                  |
| JavaScript| ~5    | 49                     |
| **Total**|       | **~5,870**             |

*Note: Counts exclude dependencies (`node_modules`, `.venv`) and build artifacts.*

## 4. Key Components Analysis

### 4.1 Data Collection Layer
- **Scripts**: `collect_all.py` orchestrates collection from `resources/`.
- **Sources**: 
    - News (RSS, Google, YouTube, GDELT).
    - Government announcements.
    - Weather data (OpenWeather).
- **Observation**: Modular design allows easy addition of new sources.

### 4.2 Machine Learning Pipeline (`pipeline.py`)
- **Workflow**: Load JSONs -> Zero-Shot Classification -> Opportunity Scoring -> Aggregation -> Output.
- **Optimization**: Implements caching for classification results to reduce processing time from ~50 mins to ~5 mins.
- **Models**: Uses local Hugging Face models for privacy and offline capability.

### 4.3 API Server (`server.py`)
- **Role**: Simple HTTP server to expose the `output/` directory as a JSON API.
- **Features**: CORS enabled for frontend access.

### 4.4 User Interface (`ui/`)
- **Pages**:
    - **Home**: Real-time dashboard.
    - **Analysis**: Historical trends.
    - **Competition Pages**: National Activity, Operational Environment, Risk/Opportunity.
- **Design**: Modern, responsive UI with dark/light mode support.

## 5. Dependencies & Configuration

### Python (`requirements.txt`)
- **Core**: `torch` (CPU), `transformers`, `scikit-learn`, `numpy`, `pandas`.
- **Web**: `flask`, `flask-cors`, `requests`, `beautifulsoup4`.
- **Optimization**: Explicitly uses CPU-only PyTorch to reduce image size.

### Node.js (`ui/package.json`)
- **Build Tool**: Vite (fast build times).
- **UI Libs**: `lucide-react` (icons), `clsx`, `tailwind-merge`.

## 6. Observations & Recommendations
1.  **Data Persistence**: Currently relies on flat JSON files. As history grows (`hourly_history.jsonl`), performance might degrade. Consider migrating to a lightweight database like SQLite or PostgreSQL for long-term scalability.
2.  **Error Handling**: Ensure robust error handling in data collectors (e.g., if an RSS feed changes format) to prevent pipeline failures.
3.  **Docker Optimization**: The Docker build includes a multi-stage process (implied). Ensure `.dockerignore` effectively excludes heavy local models if they are downloaded at build time, or mount them as volumes to keep image size down.
4.  **Testing**: The `tests/` directory exists, which is good practice. Ensure critical pipeline components have unit tests.

## 7. Conclusion
EvolveX is a well-structured, functional application that effectively combines data engineering, machine learning, and modern web development. The architecture is suitable for its current scope and allows for future expansion.
