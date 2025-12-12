#!/usr/bin/env python3
"""Test opportunity model predictions"""
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

model_dir = Path("engine/opportunity_model")
print(f"Loading model from: {model_dir}")

tokenizer = AutoTokenizer.from_pretrained(str(model_dir))
model = AutoModelForSequenceClassification.from_pretrained(str(model_dir))

# Test texts
test_texts = [
    "Sri Lanka stocks close up, pushed by Colombo Dockyard",
    "Demand for vegetables in Sri Lanka slump in Cyclone Ditwah aftermath",
    "Sri Lanka egg output down 30-pct after Ditwah kills 500,000 layers : industry"
]

print(f"Model config: {model.config}")
print(f"Num labels: {model.config.num_labels}")
print()

for text in test_texts:
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        
    print(f"Text: {text[:100]}")
    print(f"  Logits shape: {logits.shape}")
    print(f"  Logits: {logits}")
    
    if logits.shape[-1] == 1:
        score = float(logits.item())
        print(f"  Single output (regression): {score}")
    else:
        probs = torch.softmax(logits, dim=-1)[0]
        print(f"  Probabilities: {probs}")
        
        # Try the pipeline's logic
        labels = torch.arange(logits.shape[-1], dtype=torch.float32)
        expected = float((labels * probs).sum().item())
        score = (expected / (logits.shape[-1]-1)) * 2.0 - 1.0
        print(f"  Calculated score: {score}")
    print()
