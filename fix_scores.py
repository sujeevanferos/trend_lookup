#!/usr/bin/env python3
"""
Quick fix: Regenerate risk_opportunity_insights.json from the existing live_output.json
The live_output.json was generated with opportunity_score = 0.0 due to the dummy fallback.
We'll recalculate using the real opportunity engine.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT))

OUTPUT_DIR = ROOT / "output"
LIVE_OUTPUT = OUTPUT_DIR / "live_output.json"

# Load existing live output
print("Loading existing live_output.json...")
with open(LIVE_OUTPUT, 'r') as f:
    live_data = json.load(f)

events = live_data.get('events', [])
print(f"Found {len(events)} events")

# Load opportunity engine
print("Loading opportunity engine...")
from preprocessing.opportunity_engine import load as load_opp
opp_engine = load_opp()
print("Opportunity engine loaded successfully!")

# Import the calculate_risk_score function from pipeline
exec(open('pipeline.py').read(), globals())

# Process each event and recalculate scores
print("Recalculating scores...")
for i, event in enumerate(events):
    text = event.get('text', '')
    
    # Get new opportunity score from the real model
    opp_score, opp_conf = opp_engine.predict(text)
    
    # Update the event
    event['opportunity_score'] = round(float(opp_score), 4)
    event['opportunity_confidence'] = round(float(opp_conf), 4)
    
    if i < 5:  # Debug first 5
        print(f"  Event {i}: '{text[:60]}...' → score={opp_score:.4f}")

# Save updated live_output
print("\nSaving updated live_output.json...")
with open(LIVE_OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(live_data, f, indent=2, ensure_ascii=False)

# Regenerate risk_opportunity_insights.json
print("Generating risk_opportunity_insights.json...")
insights = generate_risk_opportunity_insights(events)

risk_opp_output = {
    "generated_at": live_data.get('run_timestamp'),
    "total_insights": len(insights),
    "insights": insights
}

risk_opp_file = OUTPUT_DIR / "risk_opportunity_insights.json"
with open(risk_opp_file, 'w', encoding='utf-8') as f:
    json.dump(risk_opp_output, f, indent=2, ensure_ascii=False)

print(f"\n✓ Generated {len(insights)} insights")
print(f"✓ Written to {risk_opp_file}")

# Show some stats
print("\nScore statistics:")
all_scores = [abs(e.get('opportunity_score', 0)) for e in events]
non_zero = [s for s in all_scores if s > 0]
print(f"  Non-zero scores: {len(non_zero)}/{len(all_scores)}")
if non_zero:
    print(f"  Average non-zero: {sum(non_zero)/len(non_zero):.4f}")
    print(f"  Max score: {max(non_zero):.4f}")
