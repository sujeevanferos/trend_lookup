"""
train_opportunity_model.py
Trains DistilBERT to predict a continuous opportunity score (-1 to +1)
"""

import os
import pandas as pd
import numpy as np
import torch

from datasets import Dataset
from sklearn.model_selection import train_test_split
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding,
)

# -----------------------------------------------------------
# CONFIG
# -----------------------------------------------------------
CSV_PATH = "opportunity_training.csv"
OUT_DIR = "opportunity_model"
MODEL_NAME = "distilbert-base-uncased"

EPOCHS = 4
BATCH_SIZE = 8
LR = 4e-5
SEED = 42

torch.manual_seed(SEED)
np.random.seed(SEED)

# -----------------------------------------------------------
# LOAD DATA
# -----------------------------------------------------------
if not os.path.exists(CSV_PATH):
    raise FileNotFoundError("Run generate_opportunity_dataset.py first!")

df = pd.read_csv(CSV_PATH)
df = df.dropna(subset=["text", "score"])
df["text"] = df["text"].astype(str).str.strip()
df = df[df["text"].str.len() > 10].reset_index(drop=True)

print("Loaded samples:", len(df))

# Ensure values stay in valid range
df["score"] = df["score"].clip(-1.0, 1.0)

# Train/Val split
train_df, val_df = train_test_split(df, test_size=0.15, random_state=SEED)

train_ds = Dataset.from_pandas(train_df)
val_ds = Dataset.from_pandas(val_df)

# -----------------------------------------------------------
# TOKENIZER
# -----------------------------------------------------------
tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_NAME)

def tokenize(batch):
    return tokenizer(batch["text"], truncation=True, max_length=256)

train_ds = train_ds.map(tokenize, batched=True)
val_ds   = val_ds.map(tokenize, batched=True)

# -----------------------------------------------------------
# FIX: Rename "score" to "labels" (REQUIRED by HuggingFace)
# -----------------------------------------------------------
train_ds = train_ds.rename_column("score", "labels")
val_ds   = val_ds.rename_column("score", "labels")

# Format for PyTorch
cols = ["input_ids", "attention_mask", "labels"]
train_ds.set_format("torch", columns=cols)
val_ds.set_format("torch", columns=cols)

# -----------------------------------------------------------
# REGRESSION MODEL
# -----------------------------------------------------------
model = DistilBertForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=1,            # Regression: SINGLE OUTPUT
    problem_type="regression"
)

# -----------------------------------------------------------
# METRICS
# -----------------------------------------------------------
def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = logits.reshape(-1)
    labels = labels.reshape(-1)
    mse = np.mean((preds - labels) ** 2)
    mae = np.mean(np.abs(preds - labels))
    return {"mse": mse, "mae": mae}

# -----------------------------------------------------------
# TRAINING ARGUMENTS (OLD TRANSFORMERS COMPATIBLE)
# -----------------------------------------------------------
training_args = TrainingArguments(
    output_dir=OUT_DIR,
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    learning_rate=LR,
    logging_steps=50,
    save_steps=300,
    eval_steps=200,
    do_eval=True,
    fp16=torch.cuda.is_available()
)

data_collator = DataCollatorWithPadding(tokenizer)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_ds,
    eval_dataset=val_ds,
    data_collator=data_collator,
    tokenizer=tokenizer,
    compute_metrics=compute_metrics,
)

# -----------------------------------------------------------
# TRAIN
# -----------------------------------------------------------
trainer.train()

# -----------------------------------------------------------
# SAVE MODEL
# -----------------------------------------------------------
trainer.save_model(OUT_DIR)
tokenizer.save_pretrained(OUT_DIR)

print("Model-2 (Opportunity Regression) saved to:", OUT_DIR)

