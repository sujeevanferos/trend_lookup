import json
import pandas as pd
from transformers import pipeline
from tqdm import tqdm
import os

# CONFIG
# ---------------------------
# Using a smaller but capable model for speed/quality balance. 
# 'valhalla/distilbart-mnli-12-3' is a good distilled version of bart-large-mnli
MODEL_NAME = "./local_model" 
OUTPUT_CSV = "opportunity_training.csv"
JSON_FILES = [
    "../jsons/sri_lanka_news.json",
    "../jsons/government_news.json",
    "../jsons/srilanka_weather.json"
]

CANDIDATE_LABELS = [
    "economic opportunity", 
    "business growth",
    "economic crisis", 
    "natural disaster", 
    "inflation", 
    "rising costs", 
    "business threat",
    "neutral news"
]

def extract_text(item):
    if isinstance(item, dict):
        # Combine title and summary if available
        t = (item.get("title", "") + " " + item.get("summary", "")).strip()
        return t
    if isinstance(item, str):
        return item.strip()
    return ""

def apply_keyword_rules(text, current_score):
    text_lower = text.lower()
    
    # Positive context modifiers (fighting the bad stuff)
    positive_modifiers = [
        "action against", "fight", "combat", "crackdown", "arrest", "seize", 
        "stop", "prevent", "reduce", "control", "tackle", "eliminate", "eradicate",
        "investigate", "probe", "caught", "busted", "raid"
    ]
    
    # Strong negative keywords
    negatives = [
        "price increase", "prices increased", "prices are increased", "cost rise", "inflation",
        "flood", "heavy rain", "landslide", "disaster", "cyclone", "storm",
        "crisis", "shortage", "scam", "fraud", "unauthorized", "corruption", "bribe"
    ]
    
    # Check for negatives
    for kw in negatives:
        if kw in text_lower:
            # Check if it's being fought
            is_being_fought = any(mod in text_lower for mod in positive_modifiers)
            
            if is_being_fought:
                # If fighting bad things, it's GOOD (or at least not bad)
                # e.g. "Action against corruption" -> Positive
                if current_score < 0.2:
                    return 0.4 # Force positive
                return current_score + 0.2
            else:
                # If just the bad thing, it's BAD
                if current_score > 0:
                    return -0.5  # Force negative
                else:
                    return current_score - 0.3 # Make it more negative
                
    return current_score

def get_synthetic_data():
    # Explicitly teach the model about negative "increases" AND positive "fighting"
    data = [
        # NEGATIVES
        ("Vegetable prices are increased", -0.6),
        ("Raw materials prices are increased", -0.5),
        ("Fuel costs are rising", -0.6),
        ("Inflation is increasing", -0.8),
        ("Cost of living is going up", -0.7),
        ("Price of rice has increased", -0.5),
        ("Electricity bill rates increased", -0.6),
        ("Tax rates have increased", -0.4),
        ("Interest rates are rising", -0.3),
        ("Heavy rain is expected", -0.5),
        ("Floods are predicted", -0.7),
        ("Landslide warning issued", -0.8),
        ("Storm surge warning", -0.7),
        ("Cyclone alert", -0.9),
        ("Drought conditions worsening", -0.6),
        ("Water scarcity reported", -0.5),
        ("Power cuts announced", -0.6),
        ("Shortage of medicine", -0.8),
        ("Food shortage expected", -0.8),
        ("Unemployment rate is increasing", -0.7),
        ("Job losses reported", -0.7),
        ("Company declares bankruptcy", -0.9),
        ("Stock market crash", -0.8),
        ("Currency devaluation", -0.7),
        ("Scam alert issued", -0.5),
        ("Fraudulent activities detected", -0.6),
        ("Corruption scandal exposed", -0.8),
        ("Bribery charges filed", -0.7),
        ("Government increases taxes on small businesses", -0.5),
        ("Import restrictions imposed", -0.4),
        ("Export ban on tea", -0.6),
        ("Tourism arrivals dropped", -0.7),
        ("Hotel bookings cancelled", -0.6),
        ("Flight cancellations due to weather", -0.5),
        ("Roads blocked by protesters", -0.6),
        ("Political instability continues", -0.7),
        ("Strike action paralyzes transport", -0.6),
        ("Hospital staff on strike", -0.7),
        ("Schools closed due to flu", -0.4),
        ("Dengue cases on the rise", -0.5),

        # POSITIVES (Fighting the bad)
        ("President takes action against corruption", 0.6),
        ("Government cracks down on scams", 0.5),
        ("Police arrest fraudsters", 0.5),
        ("Authorities seize unauthorized goods", 0.4),
        ("New laws to combat inflation", 0.5),
        ("Measures to control rising costs", 0.4),
        ("Steps taken to prevent floods", 0.5),
        ("Disaster relief teams deployed", 0.6),
        ("Aid reaches flood victims", 0.7),
        ("Government investigates bribery", 0.5),
        ("Illegal mining stopped by police", 0.4),
        ("Drug trafficking ring busted", 0.5),
        ("Action taken to reduce unemployment", 0.6),
        ("Plan to tackle cost of living crisis", 0.5),
        ("Efforts to eliminate poverty", 0.7)
    ]
    # Duplicate them to give them more weight during training
    return [{"text": t, "score": s} for t, s in data] * 5

def generate_dataset():
    print(f"Loading Zero-Shot Classifier: {MODEL_NAME}...")
    classifier = pipeline("zero-shot-classification", model=MODEL_NAME, device=-1) # device=-1 for CPU

    all_data = []
    
    # Load all JSONs
    for json_file in JSON_FILES:
        if not os.path.exists(json_file):
            print(f"[WARN] File not found: {json_file}")
            continue
            
        with open(json_file, "r") as f:
            try:
                data = json.load(f)
                all_data.extend(data)
            except Exception as e:
                print(f"[ERR] Failed to load {json_file}: {e}")

    print(f"Total raw items: {len(all_data)}")
    
    samples = []
    seen_texts = set()

    for item in tqdm(all_data, desc="Labeling"):
        text = extract_text(item)
        
        # Basic filtering
        if len(text) < 20 or text in seen_texts:
            continue
        seen_texts.add(text)

        # Zero-Shot Classification
        try:
            result = classifier(text, CANDIDATE_LABELS, multi_label=True)
            
            scores = dict(zip(result['labels'], result['scores']))
            
            # Positive factors
            opp_score = max(scores.get("economic opportunity", 0.0), scores.get("business growth", 0.0))
            
            # Negative factors (take the max of any negative trait)
            neg_score = max(
                scores.get("economic crisis", 0.0),
                scores.get("natural disaster", 0.0),
                scores.get("inflation", 0.0),
                scores.get("rising costs", 0.0),
                scores.get("business threat", 0.0)
            )
            
            # Calculate final score
            final_score = opp_score - neg_score
            
            # Apply Keyword Rules (Heuristic Override)
            final_score = apply_keyword_rules(text, final_score)
            
            # Clip to [-1, 1]
            final_score = max(-1.0, min(1.0, final_score))
            
            samples.append({
                "text": text,
                "score": round(final_score, 4)
            })
            
        except Exception as e:
            print(f"[WARN] Failed to process text: {text[:30]}... {e}")

    # Inject Synthetic Data
    synthetic = get_synthetic_data()
    samples.extend(synthetic)
    print(f"Injected {len(synthetic)} synthetic samples.")

    # Save to CSV
    df = pd.DataFrame(samples)
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved {len(df)} labeled samples to {OUTPUT_CSV}")

if __name__ == "__main__":
    generate_dataset()
