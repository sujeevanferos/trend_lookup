import os
import json
import random
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.utils.class_weight import compute_class_weight

import torch
from datasets import Dataset, DatasetDict
from transformers import (
    DistilBertTokenizerFast,
    DistilBertForSequenceClassification,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments
)
import evaluate

# ---------------------------
# CONFIG
# ---------------------------
CSV_PATH = os.path.join(os.path.dirname(__file__), "training_data.csv")
OUT_DIR = os.path.join(os.path.dirname(__file__), "../engine/categorization_model")
MODEL_NAME = "distilbert-base-uncased"

EPOCHS = 4
BATCH_SIZE = 8
LR = 5e-5
WEIGHT_DECAY = 0.01
SEED = 42
TEST_SIZE = 0.15
MAX_LENGTH = 256

# ---------------------------
# SEED
# ---------------------------
def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
set_seed(SEED)

# ---------------------------
# LOAD AND CLEAN DATA
# ---------------------------
df = pd.read_csv(CSV_PATH)
df = df.dropna(subset=["text", "category"])
df["text"] = df["text"].astype(str).str.strip()
df = df[df["text"].str.len() > 5].reset_index(drop=True)

print("Loaded", len(df), "samples")

# Encode labels
le = LabelEncoder()
df["label"] = le.fit_transform(df["category"])
label_map = {i: label for i, label in enumerate(le.classes_)}

os.makedirs(OUT_DIR, exist_ok=True)
with open(os.path.join(OUT_DIR, "label_map.json"), "w") as f:
    json.dump(label_map, f, indent=2)

print("\nLabel map:", label_map, "\n")

# ---------------------------
# STRATIFIED SPLIT
# ---------------------------
sss = StratifiedShuffleSplit(n_splits=1, test_size=TEST_SIZE, random_state=SEED)
train_idx, test_idx = next(sss.split(df["text"], df["label"]))

train_df = df.iloc[train_idx].reset_index(drop=True)
test_df = df.iloc[test_idx].reset_index(drop=True)

hf_train = Dataset.from_pandas(train_df[["text", "label"]])
hf_eval  = Dataset.from_pandas(test_df[["text", "label"]])

dataset = DatasetDict({"train": hf_train, "validation": hf_eval})
print("Train:", len(hf_train), "Eval:", len(hf_eval))

# ---------------------------
# TOKENIZER
# ---------------------------
tokenizer = DistilBertTokenizerFast.from_pretrained(MODEL_NAME)

def preprocess(batch):
    return tokenizer(batch["text"], truncation=True, max_length=MAX_LENGTH)

dataset = dataset.map(preprocess, batched=True)
dataset.set_format(type="torch", columns=["input_ids", "attention_mask", "label"])

data_collator = DataCollatorWithPadding(tokenizer)

# ---------------------------
# CLASS WEIGHTS
# ---------------------------
num_labels = len(label_map)
y_train = train_df["label"].to_numpy()

class_weights = compute_class_weight("balanced", classes=np.arange(num_labels), y=y_train)
class_weights = torch.tensor(class_weights, dtype=torch.float)

print("\nClass weights:", class_weights.tolist(), "\n")

# ---------------------------
# MODEL
# ---------------------------
id2label = {i: label for i, label in label_map.items()}
label2id = {label: i for i, label in label_map.items()}

model = DistilBertForSequenceClassification.from_pretrained(
    MODEL_NAME,
    num_labels=num_labels
)

# Inject label mapping manually (old Transformers needs this)
model.config.id2label = id2label
model.config.label2id = label2id

# ---------------------------
# Custom Trainer with Weighted Loss
# ---------------------------
class WeightedTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs["labels"]
        outputs = model(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"]
        )
        logits = outputs.logits
        loss_fct = torch.nn.CrossEntropyLoss(weight=class_weights.to(logits.device))
        loss = loss_fct(logits, labels)
        return (loss, outputs) if return_outputs else loss

# ---------------------------
# TRAINING ARGS (No new API)
# ---------------------------
training_args = TrainingArguments(
    output_dir=OUT_DIR,
    num_train_epochs=EPOCHS,
    per_device_train_batch_size=BATCH_SIZE,
    per_device_eval_batch_size=BATCH_SIZE,
    learning_rate=LR,
    weight_decay=WEIGHT_DECAY,
    logging_steps=50,
    do_train=True,
    do_eval=True
)

# ---------------------------
# METRICS
# ---------------------------
accuracy = evaluate.load("accuracy")
f1 = evaluate.load("f1")

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {
        "accuracy": accuracy.compute(predictions=preds, references=labels)["accuracy"],
        "f1_macro": f1.compute(predictions=preds, references=labels, average="macro")["f1"]
    }

# ---------------------------
# TRAINER
# ---------------------------
trainer = WeightedTrainer(
    model=model,
    args=training_args,
    train_dataset=dataset["train"],
    eval_dataset=dataset["validation"],
    tokenizer=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
)

# ---------------------------
# TRAIN MODEL
# ---------------------------
trainer.train()

# ---------------------------
# SAVE MODEL
# ---------------------------
trainer.save_model(OUT_DIR)
tokenizer.save_pretrained(OUT_DIR)

# Save config with labels
model.config.id2label = id2label
model.config.label2id = label2id
model.save_pretrained(OUT_DIR)

print("\nTraining complete! Model saved to:", OUT_DIR)

