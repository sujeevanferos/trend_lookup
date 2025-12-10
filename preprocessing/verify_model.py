import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification

MODEL_DIR = "../engine/opportunity_model"

def verify():
    print(f"Loading model from {MODEL_DIR}...")
    try:
        tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_DIR)
        model = DistilBertForSequenceClassification.from_pretrained(MODEL_DIR)
    except Exception as e:
        print(f"Failed to load model: {e}")
        return

    test_sentences = [
        "President is taking action against corruption",
        "Police arrest scammers",
        "Government cracks down on illegal mining",
        "Corruption scandal exposed",
        "Vegetable prices are increased",
        "Heavy rain is expected"
    ]

    print("\n--- Verification Results ---")
    for text in test_sentences:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            logits = model(**inputs).logits
            score = logits.item()
            # Clip to -1 to 1
            score = max(-1.0, min(1.0, score))
            
        print(f"Text: {text}")
        print(f"Score: {score:.4f}\n")

if __name__ == "__main__":
    verify()
