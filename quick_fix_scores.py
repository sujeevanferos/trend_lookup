#!/usr/bin/env python3
"""
Fast fix: Regenerate risk_opportunity_insights.json from existing live_output.json
Only recalculate opportunity scores, don't reprocess industries/categories
"""
import json
import uuid
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
OUTPUT_DIR = ROOT / "output"

# Load live output
print("Loading existing live_output.json...")
with open(OUTPUT_DIR / "live_output.json", 'r') as f:
    live_data = json.load(f)

events = live_data.get('events', [])
print(f"Found {len(events)} events")

# Load opportunity engine
print("Loading opportunity engine...")
import sys
sys.path.append(str(ROOT))
from preprocessing.opportunity_engine import load as load_opp
opp_engine = load_opp()
print("✓ Opportunity engine loaded")

# Calculate risk/opportunity for each event
def calculate_risk_score(opp_score, impacts):
    """Calculate risk and opportunity categories"""
    risk_score = -opp_score if opp_score < 0 else 0.0
    opp_score_positive = opp_score if opp_score > 0 else 0.0
    
    if risk_score > 0.5:
        risk_category = "High Risk"
        risk_explanation = "Significant negative impact detected across multiple sectors."
    elif risk_score > 0.2:
        risk_category = "Medium Risk"
        risk_explanation = "Moderate negative impact with potential operational challenges."
    elif risk_score > 0:
        risk_category = "Low Risk"
        risk_explanation = "Minor negative signals, monitoring recommended."
    else:
        risk_category = "No Significant Risk"
        risk_explanation = "No immediate risk indicators detected."
    
    if opp_score_positive > 0.5:
        opp_category = "High Opportunity"
        opp_explanation = "Strong positive signals indicating significant growth potential."
    elif opp_score_positive > 0.2:
        opp_category = "Medium Opportunity"  
        opp_explanation = "Moderate positive indicators suggesting favorable conditions."
    elif opp_score_positive > 0:
        opp_category = "Low Opportunity"
        opp_explanation = "Minor positive signals, potential for small gains."
    else:
        opp_category = "No Significant Opportunity"
        opp_explanation = "No immediate opportunity indicators detected."
    
    top_industries = sorted(impacts, key=lambda x: abs(x.get('score', 0)), reverse=True)[:3]
    affected_industries = [imp.get('industry', 'Unknown') for imp in top_industries]
    
    return {
        "risk_score": round(risk_score, 4),
        "risk_category": risk_category,
        "risk_explanation": risk_explanation,
        "opportunity_score": round(opp_score_positive, 4),
        "opportunity_category": opp_category,
        "opportunity_explanation": opp_explanation,
        "top_affected_industries": affected_industries
    }

# Process events
print("Recalculating scores...")
insights = []
count_updated = 0

for i, event in enumerate(events):
    text = event.get('text', '')
    
    # Get NEW opportunity score from real model
    opp_score, opp_conf = opp_engine.predict(text)
    
    # Update event with new score
    event['opportunity_score'] = round(float(opp_score), 4)
    event['opportunity_confidence'] = round(float(opp_conf), 4)
    
    if abs(opp_score) > 0.001:  # Count non-zero scores
        count_updated += 1
    
    # Calculate risk/opportunity insight
    impacts = event.get('impacts', [])
    risk_data = calculate_risk_score(opp_score, impacts)
    
    insights.append({
        "id": event.get('id'),
        "timestamp": event.get('timestamp'),
        "source": event.get('source'),
        "headline": text[:200],
        "thematic_category": event.get('thematic_category', ''),
        **risk_data
    })
    
    if (i + 1) % 100 == 0:
        print(f"  Processed {i + 1}/{len(events)} events...")

# Sort insights by highest risk OR opportunity
insights.sort(
    key=lambda x: max(x.get('risk_score', 0), x.get('opportunity_score', 0)), 
    reverse=True
)

# Save updated live_output
print("\nSaving updated live_output.json...")
with open(OUTPUT_DIR / "live_output.json", 'w', encoding='utf-8') as f:
    json.dump(live_data, f, indent=2, ensure_ascii=False)

# Save risk_opportunity_insights
print("Saving risk_opportunity_insights.json...")
risk_opp_output = {
    "generated_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
    "total_insights": len(insights),
    "insights": insights
}

with open(OUTPUT_DIR / "risk_opportunity_insights.json", 'w', encoding='utf-8') as f:
    json.dump(risk_opp_output, f, indent=2, ensure_ascii=False)

print(f"\n✓ Generated {len(insights)} risk/opportunity insights")
print(f"✓ Updated {count_updated} events with non-zero scores")

# Stats
high_risks = len([i for i in insights if i['risk_category'] == 'High Risk'])
high_opps = len([i for i in insights if i['opportunity_category'] == 'High Opportunity'])
print(f"\nStats:")
print(f"  High Risks: {high_risks}")
print(f"  High Opportunities: {high_opps}")
print(f"  Events with non-zero scores: {count_updated}/{len(events)}")

print("\n✓ Done! UI should now show proper scores.")
