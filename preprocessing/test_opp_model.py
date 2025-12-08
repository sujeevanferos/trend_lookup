import torch
import numpy as np
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification

MODEL_DIR = "opportunity_model"

# Load tokenizer + model
tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_DIR)
model = DistilBertForSequenceClassification.from_pretrained(MODEL_DIR)
model.eval()

device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

def predict_score(text):
    encoded = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
    encoded = {k: v.to(device) for k, v in encoded.items()}

    with torch.no_grad():
        output = model(**encoded)
        score = output.logits.cpu().numpy()[0][0]

    # Clamp to -1…+1
    score = float(max(-1.0, min(1.0, score)))
    return round(score, 4)

# -----------------------
# Test your model
# -----------------------
sample = "Tourism arrivals have increased significantly this month"
print("Input:", sample)
print("Predicted Opportunity Score:", predict_score(sample))

