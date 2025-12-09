"""
This script will label the news as politics, international, weather, economy, etc...
"""
import json
import csv
import re
import os
import random

# ----------------------------------------
# 1. PATH SETTINGS
# ----------------------------------------

# JSON folder location (relative to this script in resources/)
JSON_DIR = "../jsons/"

JSON_FILES = [
    "government_news.json",
    "sri_lanka_news.json",
    "srilanka_weather.json"
]

MIN_SAMPLES = 1000      # Minimum samples per category
MAX_SAMPLES = 2000      # Maximum samples per category


# ----------------------------------------
# 2. CATEGORY KEYWORD RULES (expand later)
# ----------------------------------------

RULES = {
    "disaster": [
        "flood", "flooded", "flooding", "cyclone", "landslide", "heavy rain",
        "missing", "storm", "weather alert", "damaged", "evacuate",
        "strong winds", "winds", "wind gusts", "monsoon", "torrential",
        "inundated", "impact", "disaster"
    ],
    "weather": [
        "rain", "wind", "cloud", "temperature", "humidity", "sunny",
        "low pressure", "showers", "forecast", "climate", "conditions",
        "weather", "heat", "warm", "cold"
    ],
    "economy": [
        "inflation", "price index", "ccpi", "market", "trade",
        "exports", "imports", "gdp", "economy", "production",
        "industrial", "jobs", "employment"
    ],
    "government": [
        "president", "ministry", "government", "cabinet",
        "prime minister", "policy", "announcement", "state",
        "authority", "official", "secretary"
    ],
    "international": [
        "india", "china", "foreign", "global", "maldives", "japan",
        "united states", "uk", "donation", "aid", "embassy",
        "international", "foreign minister", "diplomatic"
    ],
    "finance": [
        "tax", "interest rate", "loan", "central bank",
        "monetary policy", "customs", "revenue", "budget",
        "fiscal", "financial", "bank", "interest"
    ],
    "health": [
        "hospital", "health", "disease", "virus", "medical", "infection",
        "doctor", "clinic", "medicine", "patients"
    ],
    "tourism": [
        "tourists", "travelers", "hotel", "tourism",
        "visitors", "travel", "airlines", "airport", "tourist"
    ]
}

DEFAULT_CAT = "other"



# ----------------------------------------
# 3. CLEANING FUNCTIONS
# ----------------------------------------

def clean_text(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text



# ----------------------------------------
# 4. AUTO-LABEL FUNCTION
# ----------------------------------------

def auto_label(text):
    text_c = clean_text(text)
    for category, keywords in RULES.items():
        if any(k in text_c for k in keywords):
            return category
    return DEFAULT_CAT



# ----------------------------------------
# 5. TEXT EXTRACTION FROM JSON ITEM
# ----------------------------------------

def extract_text(item):
    """Safely extract text regardless of structure."""
    if isinstance(item, dict):
        title = item.get("title", "")
        summary = item.get("summary", "")
        return clean_text(f"{title} {summary}")
    elif isinstance(item, str):
        return clean_text(item)
    else:
        return ""  # unsupported type



# ----------------------------------------
# 6. LOAD JSON FILE SAFELY
# ----------------------------------------

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception as e:
        print(f"[ERROR] Failed to load {path}: {e}")
        return []



# ----------------------------------------
# 7. BUILD RAW SAMPLES (before balancing)
# ----------------------------------------

def build_raw_samples():
    rows_by_category = {}

    for file in JSON_FILES:
        full_path = os.path.join(JSON_DIR, file)
        data = load_json(full_path)

        print(f"Loaded {len(data)} items from {file}")

        for item in data:

            # Skip invalid items
            if not isinstance(item, (dict, str)):
                continue

            text = extract_text(item)

            if len(text) < 5:
                continue

            category = auto_label(text)

            if category not in rows_by_category:
                rows_by_category[category] = []

            rows_by_category[category].append(text)

    return rows_by_category



# ----------------------------------------
# 8. BALANCE DATASET
# ----------------------------------------

def balance_dataset(rows_by_category):
    final_rows = []

    for category, samples in rows_by_category.items():
        count = len(samples)

        if count == 0:
            continue

        # Oversample to reach MIN_SAMPLES
        if count < MIN_SAMPLES:
            repeated = samples.copy()
            while len(repeated) < MIN_SAMPLES:
                repeated.append(random.choice(samples))
            samples = repeated[:MIN_SAMPLES]

        # Undersample large categories
        elif count > MAX_SAMPLES:
            samples = random.sample(samples, MAX_SAMPLES)

        # Store results
        for text in samples:
            final_rows.append([text, category])

    return final_rows



# ----------------------------------------
# 9. WRITE CSV OUTPUT
# ----------------------------------------

def write_csv(rows):
    with open("training_data.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text", "category"])
        writer.writerows(rows)

    print("\ntraining_data.csv created!")
    print(f"Total samples: {len(rows)}\n")



# ----------------------------------------
# MAIN EXECUTION
# ----------------------------------------

if __name__ == "__main__":
    print("Loading and labeling data...")
    raw_samples = build_raw_samples()

    print("\nBalancing dataset...")
    balanced_rows = balance_dataset(raw_samples)

    print("Writing dataset...")
    write_csv(balanced_rows)

