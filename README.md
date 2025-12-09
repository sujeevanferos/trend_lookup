# evolveXr2 – Intelligent News Categorization & Industry Impact Engine

This project processes real‑time Sri Lankan news, government updates, and weather data, categorizes each event, assigns an economic opportunity score, and converts the results into industry‑level impact insights.

It runs automatically every hour, produces a live output for UI dashboards, and stores historical records for long‑term analysis.

---

## 📌 Project Overview

**evolveXr2** includes:

* **Two machine‑learning models**:

  * *Categorization Model* – classifies news into 9 categories.
  * *Opportunity Model* – predicts economic impact (−1.0 to +1.0).
* **A full preprocessing pipeline** for cleaning and standardizing real‑time inputs.
* **A final engine** that reads live JSON data and produces industry impact tables.
* **An hourly scheduler** that refreshes the outputs.
* **History tracking** using append‑only JSONL files.
* **Makefile‑driven training pipeline** with GPU/CPU switching.

---

## 📁 Project Structure

```
evolveXr2/
│
├── preprocessing/            # Training scripts + trained models
│   ├── 1_categorization_train.py
│   ├── 2_opportunity_train.py
│   ├── categorization_model/
│   └── opportunity_model/
│
├── resources/                # Realtime data collectors
│   ├── government_news.json
│   ├── sri_lanka_news.json
│   └── srilanka_weather.json
│
├── engine/                   # Final processing engine
│   ├── pipeline.py           # Processes raw JSON → industry impacts
│   └── run_hourly.py         # One‑shot or hourly scheduled runs
│
├── jsons/                    # Preprocessed files (rewritten hourly)
│
├── output/                   # Final UI‑ready files
│   ├── live_output.json      # Latest snapshot
│   └── industry_map.json     # Category → industry weight mapping
│
├── history/
│   └── hourly_history.jsonl  # Permanent hourly snapshots
│
├── Makefile                  # Training automation
└── README.md
```

---

## 🧠 Machine Learning Models

### 1. Categorization Model

Classifies events into:

* disaster
* economy
* finance
* government
* health
* international
* other
* tourism
* weather

### 2. Opportunity Model

Predicts a continuous **economic impact score**:

```
-1.0 → Strong negative impact
 0.0 → Neutral
+1.0 → Strong positive opportunity
```

Both are trained using DistilBERT.

---

## ⚙️ Training the Models

Makefile includes CPU/GPU switching, logging, and progress bars.

### Train both models

```
make train
```

### Force GPU

```
make train GPU=1
```

### Force CPU

```
make train CPU=1
```

### Enable logs

```
make train LOG=1
```

### Train individually

```
make train-cat
make train-opp
```

---

## 🔄 Hourly Processing Pipeline

The engine reads realtime input JSONs from:

```
resources/
```

Then:

1. Cleans and normalizes text
2. Predicts **category**
3. Predicts **opportunity score**
4. Converts into **industry‑impact values** via `industry_map.json`
5. Writes:

   * `output/live_output.json` (UI uses this)
   * `history/hourly_history.jsonl` (permanent log)

### Run a single refresh

```
python3 engine/run_hourly.py --once
```

### Or activate hourly mode

Handled externally via cron/systemd.

---

## 📊 Output Files

### 1. `live_output.json`

Latest computed snapshot:

* headline
* category
* score
* industry impacts
* timestamp

### 2. `industry_map.json`

Defines how strongly each category affects each industry.
You can tune these weights to improve output accuracy.

### 3. `hourly_history.jsonl`

Append‑only file. Each line is one full snapshot.
Ideal for analytics, time‑series graphs, or dashboards.

---

## 🌐 UI Integration

The UI reads:

* `output/live_output.json` → Live dashboard
* `history/hourly_history.jsonl` → Trend graphs

Graphs recommended:

* Category distribution
* Industry impact over time
* Opportunity score heatmaps

---

## 🧹 Cleanup

Remove all generated models:

```
make clean-models
```

Full cleanup:

```
make clean
```

