#!/usr/bin/env python3
"""
Download and cache ML models for EvolveX
This should be run on container startup if models are not present
"""
import os
from pathlib import Path
from transformers import AutoModel, AutoTokenizer

# Model configuration
BASE_MODEL = "distilbert-base-uncased"
LOCAL_MODEL_DIR = Path("./preprocessing/local_model")

def download_models():
    """Download and cache the base model"""
    print(f"📦 Downloading model: {BASE_MODEL}")
    print(f"📂 Saving to: {LOCAL_MODEL_DIR}")
    
    # Create directory if it doesn't exist
    LOCAL_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    
    # Check if model already exists
    if (LOCAL_MODEL_DIR / "config.json").exists():
        print("✅ Base model already exists, checking zero-shot model...")
    else:
        print("📦 Base model missing, proceeding to download...")
    
    try:
        # 1. Download Base Model (for training/custom models)
        print(f"📦 Downloading Base Model: {BASE_MODEL}")
        if not (LOCAL_MODEL_DIR / "config.json").exists():
            tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
            tokenizer.save_pretrained(LOCAL_MODEL_DIR)
            model = AutoModel.from_pretrained(BASE_MODEL)
            model.save_pretrained(LOCAL_MODEL_DIR)
            print("✅ Base model downloaded")
        else:
            print("✅ Base model already exists")

        # 2. Download Zero-Shot Model (for pipeline fallback)
        ZERO_SHOT_MODEL = "valhalla/distilbart-mnli-12-3"
        ZERO_SHOT_DIR = Path("./preprocessing/zero_shot_model")
        
        print(f"📦 Downloading Zero-Shot Model: {ZERO_SHOT_MODEL}")
        if not (ZERO_SHOT_DIR / "config.json").exists():
            from transformers import pipeline
            # Use pipeline to download and save - ensures compatibility
            classifier = pipeline("zero-shot-classification", model=ZERO_SHOT_MODEL)
            classifier.save_pretrained(ZERO_SHOT_DIR)
            print("✅ Zero-shot model downloaded")
        else:
            print("✅ Zero-shot model already exists")
        
        print("✅ All models downloaded successfully!")
        
        # Verify download
        size_mb = sum(f.stat().st_size for f in LOCAL_MODEL_DIR.rglob('*') if f.is_file()) / 1024 / 1024
        z_size_mb = sum(f.stat().st_size for f in ZERO_SHOT_DIR.rglob('*') if f.is_file()) / 1024 / 1024
        print(f"📊 Base Model size: {size_mb:.1f} MB")
        print(f"📊 Zero-Shot Model size: {z_size_mb:.1f} MB")
        
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        raise

if __name__ == "__main__":
    download_models()
