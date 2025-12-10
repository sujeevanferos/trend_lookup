
import sys
import json
from pathlib import Path
from transformers import pipeline

# Add project root to path
sys.path.append("/home/ravana/projects/evolveX/evolveXr2")

from engine.taxonomy import ALL_INDUSTRIES, THEMATIC_CATEGORIES

def test_pipeline():
    print("Loading Zero-Shot Model...")
    try:
        classifier = pipeline("zero-shot-classification", model="preprocessing/local_model", device=-1) # Force CPU for testing
    except Exception as e:
        print(f"Failed to load local model: {e}")
        return

    sample_texts = [
        "Central Bank reduces policy interest rate by 50 basis points, making borrowing cheaper.",
        "Cyclone Ditwah causes severe destruction to early-stage Maha season crops.",
        "Vietnam Airlines announces plans to start direct flights to Colombo."
    ]

    print("\n--- Testing Classification ---")
    for text in sample_texts:
        print(f"\nText: {text}")
        
        # Test Industry Relevance
        res = classifier(text, ALL_INDUSTRIES, multi_label=True)
        print("Top 3 Industries:")
        for label, score in zip(res['labels'][:3], res['scores'][:3]):
            print(f"  - {label}: {score:.4f}")

        # Test Thematic Category
        res_theme = classifier(text, THEMATIC_CATEGORIES, multi_label=False)
        print(f"Thematic Category: {res_theme['labels'][0]} ({res_theme['scores'][0]:.4f})")

if __name__ == "__main__":
    test_pipeline()
