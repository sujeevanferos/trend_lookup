#!/usr/bin/env python3
"""Test if opportunity engine loads correctly"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT))

print("Attempting to load opportunity engine...")

try:
    from preprocessing.opportunity_engine import load as load_opp
    opp_engine = load_opp()
    print(f"✓ Successfully loaded opportunity engine: {opp_engine}")
    
    # Test it
    test_texts = [
        "Sri Lanka stocks close up, pushed by Colombo Dockyard",
        "Demand for vegetables in Sri Lanka slump in Cyclone Ditwah aftermath"
    ]
    
    for text in test_texts:
        score, conf = opp_engine.predict(text)
        print(f"Text: {text[:60]}")
        print(f"  Score: {score}, Confidence: {conf}")
        print()
        
except Exception as e:
    print(f"✗ Failed to load opportunity engine: {e}")
    import traceback
    traceback.print_exc()
