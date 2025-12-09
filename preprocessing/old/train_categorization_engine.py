import os
import json
import random
import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from datasets import Dataset
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments
)
import evaluate
import torch

# ---------------------------
# SETTINGS
# ---------------------------
CSV_PATH = "training_data.csv"
OUT_DIR = "categorization_model"
MODEL_NAME = "distilbert-base-uncased"

EPOCHS = 4
BATCH_SIZE = 8
LR = 5e-5
WEIGHT_DECAY = 0.01
SEED = 42
TEST_SIZE = 0.15

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

set_seed(SEED)

# ---------------------------
# LOAD CSV
# ---------------------------
df = pd.read_csv(CSV_PATH)
df = df.dropna(subset=["text", "category"])
df["text"] = df["text"].astype(str).str.strip()
df = df[df["text"].str.len() > 5].reset_index(drop=True)

print(f"Loaded {len(df)} labeled samples.")

# Encode labels
label_encoder = LabelEncoder()
df["label"] = label_encoder.fit_transform(df["category"])

# Save label map
label_map = {int(i): label for i, label in enumerate(label_encoder.classes_)}
with open("label_map.json", "w") as f:
    json.dump(label_map, f, indent=2)
print(f"Saved label_map.json with {len(label_map)} classes.")

# ---------------------------
# BUILD DATASET
# ---------------------------
dataset = Dataset.from_pandas(df[["text", "label"]])
dataset = dataset.shuffle(seed=SEED)
split = dataset.train_test_split(test_size=TEST_SIZE, seed=SEED)

train_ds = split["train"]
eval_ds  = split["test"]

print(f"Train: {len(train_ds)}, Eval: {len(eval_ds)}")

# ---------------------------
# TOKENIZER
# ---------------------------
tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_NAME)

def preprocess(batch):
    return tokenizer(batch["text"], truncation=True, max_length=256)

train_ds = train_ds.map(preprocess, batched=True)
eval_ds  = eval_ds.map(preprocess, batched=True)

train_ds.set_format(type="torch", columns=["input_ids", "attention_mask", "label"])
eval_ds.set_format(type="torch", columns=["input_ids", "attention_mask", "label"])

# ---------------------------
# MODEL
# ---------------------------
num_labels = len(label_map)
model = DistilBertForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=num_labels
)

# ---------------------------
# METRICS
# ---------------------------
accuracy = evaluate.load("accuracy")
f1 = evaluate.load("f1")

def compute_metrics(pred):
    logits, labels = pred
    preds = np.argmax(logits, axis=-1)
    return {
        "accuracy": accuracy.compute(predictions=preds, references=labels)["accuracy"],
        "f1_macro": f1.compute(predictions=preds, references=labels, average="macro")["f1"]
    }

# ---------------------------
# TRAINING ARGUMENTS (OLD-VERSION SAFE)
# ---------------------------
training_args = TrainingArguments(
    output_dir=OUT_DIR,
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    learning_rate=LR,
    weight_decay=WEIGHT_DECAY,
    logging_steps=50,
    save_steps=500,
    eval_steps=200,
    do_eval=True,
    fp16=torch.cuda.is_available()
)

# ---------------------------
# TRAINER
# ---------------------------
data_collator = DataCollatorWithPadding(tokenizer)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_ds,
    eval_dataset=eval_ds,
    tokenizer=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics
)

# ---------------------------
# TRAIN
# ---------------------------
trainer.train()

# ---------------------------
# SAVE MODEL
# ---------------------------
trainer.save_model(OUT_DIR)
tokenizer.save_pretrained(OUT_DIR)

print(f"\nTraining complete. Model saved in: {OUT_DIR}")

