#!/usr/bin/env python3
"""Direct test of the exact code path the pipeline uses"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT))

# Mimic pipeline exactly
cat_engine = None
opp_engine = None

def try_load_preproc_engines():
    global cat_engine, opp_engine
    try:
        from preprocessing.opportunity_engine import load as load_opp
        opp_engine = load_opp()
        print("[INFO] Opportunity engine loaded successfully")
    except Exception as e:
        print(f"[WARN] Opportunity engine failed to load: {e}")
        import traceback
        traceback.print_exc()
        opp_engine = None

try_load_preproc_engines()

# Check if fallback is needed
if opp_engine is None:
    print("ERROR: Opportunity engine is None, will use dummy!")
    class OppDummy:
        @staticmethod
        def predict(text): return 0.0, 0.5
    opp_engine = OppDummy()
else:
    print(f"SUCCESS: Real opportunity engine loaded: {opp_engine}")

# Test prediction like the pipeline does
test_texts = [
    "Sri Lanka stocks close up, pushed by Colombo Dockyard", 
    "Demand for vegetables in Sri Lanka slump in Cyclone Ditwah aftermath"
]

for text in test_texts:
    opp_score, opp_conf = opp_engine.predict(text)
    print(f"\nText: {text[:60]}")
    print(f"  opp_score: {opp_score}")
    print(f"  rounded: {round(float(opp_score), 4)}")
