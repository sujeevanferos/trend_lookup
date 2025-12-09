"""
categorization_engine.py

Loads the trained DistilBERT model (categorization_model/)
and provides classification functions.

Functions:
    - load_engine()
    - predict(text)
    - predict_batch(text_list)
    - categorize_json_file(path)

Outputs:
    - category (string)
    - confidence (0 → 1)
    - opportunity_score (-1 → +1)
"""

import json
import torch
import numpy as np
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification

MODEL_DIR = "categorization_model"
LABEL_MAP_PATH = "label_map.json"

# ---------------------------------------------------------------------
# Load label map
# ---------------------------------------------------------------------
with open(LABEL_MAP_PATH, "r") as f:
    label_map = json.load(f)
# Reverse map: label_id -> category name
id_to_label = {int(k): v for k, v in label_map.items()}

# ---------------------------------------------------------------------
# Load model + tokenizer once (singleton)
# ---------------------------------------------------------------------
print("Loading categorization model...")

tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_DIR)
model = DistilBertForSequenceClassification.from_pretrained(MODEL_DIR)
model.eval()

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

print("Model loaded on:", device)

# ---------------------------------------------------------------------
# Utility: softmax
# ---------------------------------------------------------------------
def softmax(x):
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum()


# ---------------------------------------------------------------------
# BUSINESS OPPORTUNITY SCORE MAPPING
# ---------------------------------------------------------------------
# You can change the scores depending on your business logic
BUSINESS_SCORE = {
    "disaster": -0.8,
    "threat": -0.6,
    "weather": -0.2,
    "politics": -0.1,
    "international": 0.0,
    "environment": 0.1,
    "health": 0.2,
    "tourism": 0.4,
    "economy": 0.5,
    "finance": 0.6,
    "development": 0.7,
    "opportunity": 0.8,
}

DEFAULT_SCORE = 0.0


# ---------------------------------------------------------------------
# Main predict() function
# ---------------------------------------------------------------------
def predict(text: str):
    """
    Predicts a category for a single text input.
    Returns:
        {
            "category": "...",
            "confidence": float,
            "opportunity_score": float
        }
    """
    if not text or len(text.strip()) < 3:
        return {
            "category": "unknown",
            "confidence": 0.0,
            "opportunity_score": 0.0
        }

    encoded = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
    encoded = {k: v.to(device) for k, v in encoded.items()}

    with torch.no_grad():
        output = model(**encoded)
        logits = output.logits.cpu().numpy()[0]

    probs = softmax(logits)
    label_id = int(np.argmax(probs))
    category = id_to_label[label_id]
    confidence = float(probs[label_id])

    # map category → -1 to +1 score
    opportunity_score = BUSINESS_SCORE.get(category, DEFAULT_SCORE)

    return {
        "category": category,
        "confidence": round(confidence, 4),
        "opportunity_score": round(opportunity_score, 3)
    }


# ---------------------------------------------------------------------
# Batch prediction for speed
# ---------------------------------------------------------------------
def predict_batch(texts):
    """
    Input: list of strings
    Output: list of prediction dicts
    """

    results = []

    encoded = tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=256,
        return_tensors="pt"
    )

    encoded = {k: v.to(device) for k, v in encoded.items()}

    with torch.no_grad():
        logits = model(**encoded).logits.cpu().numpy()

    for i, logit in enumerate(logits):
        probs = softmax(logit)
        label_id = int(np.argmax(probs))
        category = id_to_label[label_id]
        confidence = float(probs[label_id])
        opportunity_score = BUSINESS_SCORE.get(category, DEFAULT_SCORE)

        results.append({
            "text": texts[i],
            "category": category,
            "confidence": round(confidence, 4),
            "opportunity_score": round(opportunity_score, 3)
        })

    return results


# ---------------------------------------------------------------------
# Categorize an entire JSON file
# ---------------------------------------------------------------------
def categorize_json_file(path):
    """
    Loads a JSON file and applies classification to every item.
    Returns list of results.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    outputs = []

    for item in data:
        # support strings or objects
        if isinstance(item, dict):
            text = item.get("title", "") + " " + item.get("summary", "")
        elif isinstance(item, str):
            text = item
        else:
            continue

        result = predict(text)
        outputs.append(result)

    return outputs


# ---------------------------------------------------------------------
# Demo
# ---------------------------------------------------------------------
if __name__ == "__main__":
    sample = "There will be no tax from tomorrow"
    print("Test:", predict(sample))

