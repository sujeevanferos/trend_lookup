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
        print("✅ Model already exists, skipping download")
        return
    
    try:
        # Download tokenizer
        print("  → Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
        tokenizer.save_pretrained(LOCAL_MODEL_DIR)
        
        # Download model
        print("  → Downloading model weights...")
        model = AutoModel.from_pretrained(BASE_MODEL)
        model.save_pretrained(LOCAL_MODEL_DIR)
        
        print("✅ Model downloaded successfully!")
        
        # Verify download
        size_mb = sum(f.stat().st_size for f in LOCAL_MODEL_DIR.rglob('*') if f.is_file()) / 1024 / 1024
        print(f"📊 Model size: {size_mb:.1f} MB")
        
    except Exception as e:
        print(f"❌ Error downloading model: {e}")
        raise

if __name__ == "__main__":
    download_models()
