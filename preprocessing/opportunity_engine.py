"""
opportunity_engine.py

This engine combines:
 - Model-1: Categorization (classification)
 - Model-2: Opportunity Impact (regression)

Functions:
    analyze(text)
    analyze_batch(list_of_texts)
    analyze_json(path)
"""

import json
import torch
import numpy as np

# === Load Categorization Model (Model-1) ===
from categorization_engine import predict as classify

# === Load Opportunity Regression Model (Model-2) ===
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification

REG_MODEL_DIR = "opportunity_model"

print("Loading Opportunity Regression Model...")

reg_tokenizer = DistilBertTokenizerFast.from_pretrained(REG_MODEL_DIR)
reg_model = DistilBertForSequenceClassification.from_pretrained(REG_MODEL_DIR)
reg_model.eval()

device = "cuda" if torch.cuda.is_available() else "cpu"
reg_model.to(device)

print("Regression model loaded on:", device)


# ---------------------------------------------------------
# UTILS
# ---------------------------------------------------------
def clamp(x, lo=-1.0, hi=1.0):
    return float(max(lo, min(hi, x)))


def regression_score(text):
    """Run Model-2 and return -1 → +1 score"""
    enc = reg_tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
    enc = {k: v.to(device) for k, v in enc.items()}

    with torch.no_grad():
        out = reg_model(**enc).logits.cpu().numpy()[0][0]

    return clamp(out)


# ---------------------------------------------------------
# MAIN ANALYZER
# ---------------------------------------------------------
def analyze(text: str):
    """
    Full analysis pipeline:
        - Categorization model
        - Opportunity regression model
        - Final combined index
    """

    if not text or len(text.strip()) < 5:
        return {
            "category": "unknown",
            "category_confidence": 0.0,
            "opportunity_score": 0.0,
            "final_index": 0.0
        }

    # Step 1: Categorization (Model-1)
    cat = classify(text)
    category = cat["category"]
    cat_conf = cat["confidence"]

    # Step 2: Regression model (Model-2)
    reg = regression_score(text)

    # Step 3: Combined final score
    # Weighting: regression is stronger, category-confidence fine-tunes
    final_index = clamp(reg * 0.8 + cat_conf * 0.2)

    return {
        "category": category,
        "category_confidence": round(cat_conf, 4),
        "opportunity_score": round(reg, 4),
        "final_index": round(final_index, 4)
    }


# ---------------------------------------------------------
# BATCH MODE
# ---------------------------------------------------------
def analyze_batch(texts):
    results = []
    for t in texts:
        results.append(analyze(t))
    return results


# ---------------------------------------------------------
# JSON FILE MODE
# ---------------------------------------------------------
def extract_text(item):
    if isinstance(item, dict):
        return (item.get("title", "") + " " + item.get("summary", "")).strip()
    if isinstance(item, str):
        return item.strip()
    return ""


def analyze_json(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    outputs = []
    for item in data:
        text = extract_text(item)
        if len(text) < 5:
            continue
        outputs.append(analyze(text))

    return outputs


# ---------------------------------------------------------
# DEMO (run directly)
# ---------------------------------------------------------
if __name__ == "__main__":
    test_text = "It will rain from tomorrow."
    print(analyze(test_text))

