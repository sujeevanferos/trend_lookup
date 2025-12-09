import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_PATH = "./categorization_model"   # FIXED: matches your folder

print("Loading categorization model...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
model.eval()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# --- FIX: Convert string keys ("0","1","2") to int keys (0,1,2) ---
raw_id2label = model.config.id2label
id2label = {int(k): v for k, v in raw_id2label.items()}

label2id = {v: k for k, v in id2label.items()}

print("Model loaded on:", device)
print("Available categories:", id2label)


def predict(text):
    """Predict category of a given text."""
    inputs = tokenizer(
        text,
        truncation=True,
        padding=True,
        max_length=256,
        return_tensors="pt"
    ).to(device)

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=-1)
        best_idx = torch.argmax(probabilities, dim=-1).item()

    # Debugging
    print("\n[DEBUG] Model predicted index:", best_idx)
    print("[DEBUG] id2label keys:", list(id2label.keys()))

    # Safe guard
    if best_idx not in id2label:
        raise ValueError(f"Unknown predicted label ID: {best_idx}")

    return id2label[best_idx]


# --- Quick Test ---
if __name__ == "__main__":
    print("\n--- Quick Model Test ---\n")
    sample_text = "Sri Lanka signs agreement to expand renewable energy capacity."
    print("Text:", sample_text)
    print("Prediction:", predict(sample_text))

