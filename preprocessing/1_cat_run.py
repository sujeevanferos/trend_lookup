import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification

MODEL_PATH = "categorization_model"   # same folder where training saved

def load_model():
    print("Loading model from:", MODEL_PATH)
    tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_PATH)
    model = DistilBertForSequenceClassification.from_pretrained(MODEL_PATH)

    # Some old Transformer versions store id2label keys as strings → fix
    id2label_raw = model.config.id2label
    id2label = {int(k): v for k, v in id2label_raw.items()}

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    model.eval()

    print("Loaded categories:", id2label)
    return tokenizer, model, id2label, device


def predict(text, tokenizer, model, id2label, device):
    inputs = tokenizer(
        text,
        truncation=True,
        max_length=256,
        padding=True,
        return_tensors="pt"
    )

    inputs = {k: v.to(device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        pred_idx = torch.argmax(logits, dim=-1).item()

    label = id2label[pred_idx]
    confidence = torch.softmax(logits, dim=-1)[0][pred_idx].item()

    return {
        "text": text,
        "predicted_category": label,
        "category_id": pred_idx,
        "confidence": round(float(confidence), 4)
    }

def predict_top3(text, tokenizer, model, id2label, device):
    inputs = tokenizer(
        text,
        truncation=True,
        max_length=256,
        padding=True,
        return_tensors="pt"
    ).to(device)

    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probs = torch.softmax(logits, dim=-1)[0]

    top = torch.topk(probs, 3)
    results = []
    for score, idx in zip(top.values, top.indices):
        results.append({
            "category": id2label[int(idx)],
            "confidence": round(float(score), 4)
        })
    return results


"""if __name__ == "__main__":
    tokenizer, model, id2label, device = load_model()

    sample = "Sri Lanka signs agreement to expand renewable energy capacity."

    result = predict(sample, tokenizer, model, id2label, device)

    print("\n--- Prediction ---")
    print("Text:", result["text"])
    print("Category:", result["predicted_category"])
    print("Category ID:", result["category_id"])
    print("Confidence:", result["confidence"])
"""

if __name__ == "__main__":
    tokenizer, model, id2label, device = load_model()

    sample = "Central bank blocked transactions"

    print("\n--- Top 3 Predictions ---")
    top3 = predict_top3(sample, tokenizer, model, id2label, device)
    for i, item in enumerate(top3):
        print(f"{i+1}. {item['category']}  (confidence: {item['confidence']})")




