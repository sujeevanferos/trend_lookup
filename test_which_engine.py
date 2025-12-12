#!/usr/bin/env python3
"""Quick test to see which engine is being used"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT))

# Mimic pipeline loading
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

# Fallback dummy
if opp_engine is None:
    class OppDummy:
        @staticmethod
        def predict(text): return 0.0, 0.5
    opp_engine = OppDummy()
    print("[INFO] Using OppDummy fallback")
else:
    print(f"[INFO] Using real engine: {opp_engine}")

# Test it
test_text = "Sri Lanka stocks close up, pushed by Colombo Dockyard"
score, conf = opp_engine.predict(test_text)
print(f"Test: {test_text}")
print(f"Score: {score}, Confidence: {conf}")
