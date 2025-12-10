import json
from pathlib import Path

# Read backup file (old format)
backup_path = Path("history/hourly_history.jsonl.bak")
output_path = Path("history/hourly_history.jsonl")

converted_lines = []

with open(backup_path, 'r') as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        
        try:
            snapshot = json.loads(line)
            
            # Convert old format events to new format
            if 'events' in snapshot:
                new_events = []
                for event in snapshot['events']:
                    # Skip if already in new format
                    if 'impacts' in event:
                        new_events.append(event)
                        continue
                    
                    # Convert from industry_impact dict to impacts list
                    impacts = []
                    if 'industry_impact' in event and isinstance(event['industry_impact'], dict):
                        for industry, score in event['industry_impact'].items():
                            # Determine impact type based on score
                            if score > 0.1:
                                impact_type = "Opportunity"
                            elif score < -0.1:
                                impact_type = "Threat"
                            else:
                                impact_type = "Neutral"
                            
                            impacts.append({
                                "industry": industry.replace("_", " ").title(),
                                "score": round(score, 4),
                                "impact_type": impact_type,
                                "relevance": 0.5  # Default relevance
                            })
                    
                    # Create new event with impacts
                    new_event = {
                        "id": event.get("id"),
                        "timestamp": event.get("timestamp"),
                        "source": event.get("source"),
                        "text": event.get("text"),
                        "thematic_category": event.get("category", "General"),
                        "impacts": impacts if impacts else [{
                            "industry": "Other",
                            "score": event.get("opportunity_score", 0),
                            "impact_type": "Neutral",
                            "relevance": 0.5
                        }]
                    }
                    new_events.append(new_event)
                
                snapshot['events'] = new_events
            
            converted_lines.append(json.dumps(snapshot) + '\n')
            
        except json.JSONDecodeError:
            print(f"Skipping invalid line")
            continue

# Write converted data
with open(output_path, 'w') as f:
    f.writelines(converted_lines)

print(f"Converted {len(converted_lines)} snapshots from old to new format")
