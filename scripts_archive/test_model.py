import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
import os
import sys

# Path to the trained model
MODEL_DIR = "engine/opportunity_model"

def main():
    if not os.path.exists(MODEL_DIR):
        print(f"Error: Model directory not found at {MODEL_DIR}")
        return

    print(f"Loading model from {MODEL_DIR}...")
    try:
        tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_DIR)
        model = DistilBertForSequenceClassification.from_pretrained(MODEL_DIR)
    except Exception as e:
        print(f"Failed to load model: {e}")
        return

    print("\n" + "="*50)
    print("Opportunity Model Interactive Test")
    print("Enter a news headline or text to get its score (-1.0 to 1.0)")
    print("Type 'q' or 'exit' to quit.")
    print("="*50 + "\n")

    while True:
        try:
            text = input("Enter text: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break

        if text.lower() in ('q', 'exit', 'quit'):
            break
        
        if not text:
            continue

        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=256)
        
        with torch.no_grad():
            logits = model(**inputs).logits
            score = logits.item()
            # Clip to -1 to 1
            score = max(-1.0, min(1.0, score))

        # Colorize output
        # Green for Opportunity, Red for Risk, Yellow for Neutral
        if score > 0.2:
            color = "\033[92m" # Green
            interp = "Opportunity"
        elif score < -0.2:
            color = "\033[91m" # Red
            interp = "Risk/Negative"
        else:
            color = "\033[93m" # Yellow
            interp = "Neutral"
            
        reset = "\033[0m"
        
        print(f"Score: {color}{score:.4f}{reset}  [{interp}]")
        print("-" * 30)

if __name__ == "__main__":
    main()
