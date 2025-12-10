#!/usr/bin/env python3
"""Download zero-shot model for faster pipeline runs"""
from transformers import pipeline
from pathlib import Path

output_dir = Path("preprocessing/zero_shot_model")
output_dir.mkdir(parents=True, exist_ok=True)

print("Downloading zero-shot model...")
print("This may take a few minutes...")

classifier = pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-3")

print(f"\nSaving to {output_dir}...")
classifier.save_pretrained(str(output_dir))

print("✓ Zero-shot model downloaded successfully!")
print(f"✓ Saved to {output_dir}")
