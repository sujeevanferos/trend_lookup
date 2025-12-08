import json
import random
import pandas as pd
from transformers import pipeline
from categorization_engine import predict as classify

# Initialize sentiment analyzer
sentiment = pipeline("sentiment-analysis")

# Category base scores
CATEGORY_BASE_SCORE = {
    "disaster": -0.8,
    "weather": -0.3,
    "threat": -0.6,
    "politics": -0.1,
    "government": 0.0,
    "international": 0.0,
    "environment": 0.2,
    "health": 0.2,
    "tourism": 0.4,
    "economy": 0.5,
    "finance": 0.6,
    "development": 0.7
}

def compute_final_score(category, sentiment_label, sentiment_score):
    base = CATEGORY_BASE_SCORE.get(category, 0.0)

    if sentiment_label == "POSITIVE":
        impact = sentiment_score * 0.5
    elif sentiment_label == "NEGATIVE":
        impact = -sentiment_score * 0.5
    else:
        impact = 0.0

    final = base + impact
    return max(-1.0, min(1.0, final))

def extract_text(item):
    if isinstance(item, dict):
        t = (item.get("title", "") + " " + item.get("summary", "")).strip()
        return t
    if isinstance(item, str):
        return item.strip()
    return ""

def process_file(path):
    print("Processing:", path)

    with open(path, "r") as f:
        data = json.load(f)

    samples = []
    for item in data:
        text = extract_text(item)

        if len(text) < 15:
            continue

        # Category model
        cat_info = classify(text)
        category = cat_info["category"]

        # Sentiment
        s = sentiment(text[:512])[0]  # safe truncate
        sentiment_label = s["label"]
        sentiment_score = s["score"]

        # Combined score
        final_score = compute_final_score(category, sentiment_label, sentiment_score)

        samples.append({
            "text": text,
            "score": round(final_score, 4)
        })

    print(" -> Added", len(samples), "samples")
    return samples

if __name__ == "__main__":

    files = [
        "../jsons/sri_lanka_news.json",
        "../jsons/government_news.json",
        "../jsons/srilanka_weather.json"
    ]

    all_rows = []

    for file in files:
        rows = process_file(file)
        all_rows.extend(rows)

    random.shuffle(all_rows)

    df = pd.DataFrame(all_rows)
    df.to_csv("opportunity_training.csv", index=False)

    print("Saved opportunity_training.csv with", len(df), "rows")

