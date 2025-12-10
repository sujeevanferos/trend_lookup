#!/usr/bin/env python3
"""
engine/pipeline.py

Strict ingestion pipeline:
 - Loads ONLY the 3 approved realtime JSON files in jsons/
 - Uses preprocessing engines (categorization + opportunity) if available
 - Falls back to transformers-based wrappers if not
 - Produces output/live_output.json (overwrite)
 - Appends a single hourly snapshot (Option 2) to history/hourly_history.jsonl
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
import sys
import hashlib

ROOT = Path(__file__).resolve().parent
JSONS_DIR = ROOT / "jsons"
OUTPUT_DIR = ROOT / "output"
HISTORY_DIR = ROOT / "history"
PREPROC_DIR = ROOT / "engine"

sys.path.append(str(ROOT))

# Import Taxonomy
try:
    from engine.taxonomy import TAXONOMY, ALL_INDUSTRIES, THEMATIC_CATEGORIES
except ImportError:
    # Fallback if running from wrong dir
    sys.path.append(str(ROOT / "engine"))
    from taxonomy import TAXONOMY, ALL_INDUSTRIES, THEMATIC_CATEGORIES

# Approved files (strict) — nothing else will ever be loaded
APPROVED_SOURCES = {
    "sri_lanka_news": JSONS_DIR / "sri_lanka_news.json",
    "government_news": JSONS_DIR / "government_news.json",
    "weather": JSONS_DIR / "srilanka_weather.json",
}

# outputs
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
HISTORY_DIR.mkdir(parents=True, exist_ok=True)
LIVE_OUTPUT = OUTPUT_DIR / "live_output.json"
HISTORY_FILE = HISTORY_DIR / "hourly_history.jsonl"
CACHE_FILE = OUTPUT_DIR / "processed_cache.json"

# Cache helpers
def load_cache() -> Set[str]:
    """Load set of already-processed news item hashes."""
    if not CACHE_FILE.exists():
        return set()
    try:
        with open(CACHE_FILE, 'r') as f:
            data = json.load(f)
            return set(data.get('processed', []))
    except Exception:
        return set()

def save_cache(cache: Set[str]):
    """Save processed news hashes to cache file."""
    try:
        with open(CACHE_FILE, 'w') as f:
            json.dump({'processed': list(cache)}, f)
    except Exception as e:
        print(f"[WARN] Failed to save cache: {e}")

def get_text_hash(text: str) -> str:
    """Generate a hash for a news text to identify duplicates."""
    return hashlib.md5(text.encode('utf-8')).hexdigest()

# timestamp helper
def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

# ========================================
# COMPETITION FEATURES: Classification Keywords
# ========================================

# National Activity Indicators - Major national events
NATIONAL_ACTIVITY_KEYWORDS = {
    'political': ['election', 'government', 'parliament', 'minister', 'president', 'policy', 
                  'law', 'legislation', 'vote', 'political', 'coalition', 'cabinet'],
    'economic': ['economy', 'gdp', 'inflation', 'trade', 'export', 'import', 'debt', 'imf',
                 'budget', 'fiscal', 'economic growth', 'recession'],
    'disasters': ['cyclone', 'flood', 'landslide', 'drought', 'disaster', 'emergency',
                  'warning', 'alert', 'evacuation', 'storm', 'earthquake'],
    'public': ['protest', 'strike', 'demonstration', 'rally', 'public', 'nationwide',
               'crisis', 'unrest', 'movement']
}

# Operational Environment Indicators - Business/operational signals
OPERATIONAL_KEYWORDS = {
    'supply_chain': ['supply', 'shortage', 'stock', 'inventory', 'logistics', 'transport',
                     'delivery', 'distribution', 'import restriction'],
    'utilities': ['power cut', 'electricity', 'fuel', 'gas', 'water', 'blackout', 'outage',
                  'energy crisis', 'power failure'],
    'market': ['price', 'cost', 'inflation', 'market', 'consumer', 'retail', 'sale',
               'demand', 'spending', 'purchasing'],
    'business': ['business', 'company', 'sector', 'operations', 'productivity']
}

def classify_national_activity(text: str, thematic_category: str) -> bool:
    """
    Determine if news qualifies as a National Activity Indicator.
    Uses keyword matching on text and thematic category analysis.
    """
    text_lower = text.lower()
    
    # Check thematic categories that are clearly national
    national_categories = [
        'Social/Political Issues', 'Security & Defense', 'Regulatory & Governance',
        'Extreme Weather Events', 'Infrastructure & Development'
    ]
    if thematic_category in national_categories:
        return True
    
    # Keyword matching
    keyword_count = 0
    for category_keywords in NATIONAL_ACTIVITY_KEYWORDS.values():
        for keyword in category_keywords:
            if keyword in text_lower:
                keyword_count += 1
                if keyword_count >= 2:  # At least 2 keywords for confidence
                    return True
    
    return keyword_count >= 1  # Allow 1 strong keyword

def classify_operational_environment(text: str, impacts: List[Dict]) -> bool:
    """
    Determine if news qualifies as an Operational Environment Indicator.
    Checks for business/operational impact signals.
    """
    text_lower = text.lower()
    
    # Check if it affects multiple industries (broad operational impact)
    if len(impacts) >= 3:
        return True
    
    # Keyword matching
    for category_keywords in OPERATIONAL_KEYWORDS.values():
        for keyword in category_keywords:
            if keyword in text_lower:
                return True
    
    return False

def calculate_risk_score(opp_score: float, text: str, impacts: List[Dict]) -> Dict:
    """
    Calculate risk score, category, and explanation.
    Risk is inverse of opportunity - negative opp_score = high risk.
    """
    # Risk score is absolute value of negative opportunity
    risk_score = -opp_score if opp_score < 0 else 0.0
    opp_score_positive = opp_score if opp_score > 0 else 0.0
    
    # Determine risk category
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
    
    # Determine opportunity category
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
    
    # Get most impacted industries
    top_industries = sorted(impacts, key=lambda x: abs(x['score']), reverse=True)[:3]
    affected_industries = [imp['industry'] for imp in top_industries]
    
    return {
        "risk_score": round(risk_score, 4),
        "risk_category": risk_category,
        "risk_explanation": risk_explanation,
        "opportunity_score": round(opp_score_positive, 4),
        "opportunity_category": opp_category,
        "opportunity_explanation": opp_explanation,
        "top_affected_industries": affected_industries
    }

# safe json reader
def safe_load_json(path: Path) -> Optional[Any]:
    if not path.exists():
        return None
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[WARN] Failed to parse JSON {path}: {e}")
        return None

# minimal text extractor for a news/gov item
def extract_text_from_item(item: Any) -> str:
    if not item:
        return ""
    if isinstance(item, str):
        return item.strip()
    if isinstance(item, dict):
        candidates = []
        for k in ("title", "headline", "summary", "description", "content", "text"):
            v = item.get(k) or item.get(k.lower())
            if v:
                candidates.append(str(v).strip())
        # sometimes item stores nested 'article' or 'fields'
        if not candidates:
            # flatten all string-like values up to a small depth
            for v in item.values():
                if isinstance(v, str) and len(v.strip()) > 5:
                    candidates.append(v.strip())
                    if len(candidates) >= 2:
                        break
        return " ".join(candidates).strip()
    # fallback
    return str(item).strip()

# ---- load engines: try user-provided preprocessing engines first ----
cat_engine = None
opp_engine = None
zero_shot_engine = None

def try_load_preproc_engines():
    global cat_engine, opp_engine
    try:
        from preprocessing.categorization_engine import load as load_cat
        cat_engine = load_cat()
    except Exception:
        cat_engine = None
    try:
        from preprocessing.opportunity_engine import load as load_opp
        opp_engine = load_opp()
    except Exception:
        opp_engine = None

# ---- fallback wrappers using transformers (if user didn't expose load functions) ----
def build_transformers_fallbacks():
    global cat_engine, opp_engine, zero_shot_engine
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification, pipeline
        import torch
    except Exception:
        return

    device = 0 if torch.cuda.is_available() else -1

    # Opportunity Model (Sentiment/Opportunity)
    opp_model_dir = PREPROC_DIR / "opportunity_model"
    if opp_engine is None and opp_model_dir.exists():
        try:
            tok2 = AutoTokenizer.from_pretrained(str(opp_model_dir))
            model2 = AutoModelForSequenceClassification.from_pretrained(str(opp_model_dir))
            if device == 0:
                model2.to("cuda")
            
            def opp_predict(text: str):
                inputs = tok2(text, return_tensors="pt", truncation=True, padding=True)
                if device == 0:
                    inputs = {k: v.to("cuda") for k, v in inputs.items()}
                with torch.no_grad():
                    logits = model2(**inputs).logits
                    if logits.shape[-1] == 1:
                        score = max(-1.0, min(1.0, float(logits.item())))
                        conf = 1.0
                    else:
                        probs = torch.softmax(logits, dim=-1)[0]
                        # Assuming 3 classes: [Negative, Neutral, Positive] or similar mapping
                        # For simplicity, let's assume class 0 is neg, 1 neutral, 2 pos
                        # Or if it's regression trained as classification
                        # Let's stick to the previous logic if it worked, or simplify
                        # Previous logic was complex. Let's assume the model outputs a single score or we map it.
                        # If we don't know the mapping, let's use a simple heuristic or the previous code's logic
                        # Re-using previous logic:
                        labels = torch.arange(logits.shape[-1], dtype=torch.float32)
                        if device == 0: labels = labels.to("cuda")
                        expected = float((labels * probs).sum().item())
                        score = (expected / (logits.shape[-1]-1)) * 2.0 - 1.0
                        conf = float(probs.max().item())
                return float(score), float(conf)
            
            opp_engine = type("OppEngine", (), {"predict": staticmethod(opp_predict)})
        except Exception as e:
            print("[WARN] Opp fallback failed:", e)

    # Zero-Shot Model (for Thematic Category & Industry Relevance)
    # We use the same model for both
    # Try local model first, then standard
    if Path("preprocessing/zero_shot_model").exists():
        model_path = "preprocessing/zero_shot_model"
    elif Path("./preprocessing/zero_shot_model").exists():
        model_path = "./preprocessing/zero_shot_model"
    else:
        model_path = "valhalla/distilbart-mnli-12-3"
    try:
        zero_shot_engine = pipeline("zero-shot-classification", model=model_path, device=device)
    except Exception as e:
        print(f"[WARN] Zero-Shot engine failed to load: {e}")

# attempt to load engines
try_load_preproc_engines()
build_transformers_fallbacks()

# final safety dummies
if opp_engine is None:
    class OppDummy:
        @staticmethod
        def predict(text): return 0.0, 0.5
    opp_engine = OppDummy()

if zero_shot_engine is None:
    class ZeroShotDummy:
        def __call__(self, text, candidate_labels, multi_label=False):
            return {"labels": candidate_labels, "scores": [1.0/len(candidate_labels)]*len(candidate_labels)}
    zero_shot_engine = ZeroShotDummy()


# ---- main processing steps (strict sources only) ----
def process_news_list(raw_list: List[Any], source_name: str, cache: Set[str]) -> List[Dict[str, Any]]:
    events = []
    if not isinstance(raw_list, list):
        return events
    
    cache_hits = 0
    new_items = 0
    
    for item in raw_list:
        text = extract_text_from_item(item)
        if not text or len(text) < 5:
            continue

        # FILTER: Skip unwanted text
        if "Downloads" in text:
            continue
        
        # CACHE CHECK: Skip if already processed
        text_hash = get_text_hash(text)
        if text_hash in cache:
            cache_hits += 1
            continue
        
        # Mark as processed
        cache.add(text_hash)
        new_items += 1

        # 1. Global Opportunity Score
        opp_score, opp_conf = opp_engine.predict(text)

        # 2. Thematic Category (Tier 2)
        # Single label classification
        thematic_res = zero_shot_engine(text, THEMATIC_CATEGORIES, multi_label=False)
        thematic_category = thematic_res["labels"][0]
        
        # 3. Industry Relevance & Scoring
        # Multi-label classification to find all relevant industries
        industry_res = zero_shot_engine(text, ALL_INDUSTRIES, multi_label=True)
        
        impacts = []
        for label, relevance in zip(industry_res["labels"], industry_res["scores"]):
            # Threshold for relevance
            # LOWERED THRESHOLD: 0.1 to capture more industries
            if relevance > 0.1: 
                # Calculate Industry Score
                # If opp_score is positive, we want positive impact.
                # If opp_score is negative, we want negative impact (threat).
                # Relevance scales the magnitude.
                
                ind_score = opp_score * relevance
                
                # Determine Impact Type
                # LOWERED THRESHOLD: 0.05 for impact type
                if ind_score > 0.05:
                    impact_type = "Opportunity"
                elif ind_score < -0.05:
                    impact_type = "Threat"
                else:
                    impact_type = "Neutral"

                impacts.append({
                    "industry": label,
                    "score": round(ind_score, 4),
                    "impact_type": impact_type,
                    "relevance": round(relevance, 4)
                })
        
        # If no industry is relevant, assign to "Other"
        if not impacts:
             impacts.append({
                    "industry": "Other",
                    "score": round(opp_score * 0.5, 4), # Lower confidence
                    "impact_type": "Neutral",
                    "relevance": 0.5
                })

        # Sort impacts by absolute score magnitude
        impacts.sort(key=lambda x: abs(x["score"]), reverse=True)

        ev = {
            "id": str(uuid.uuid4()),
            "timestamp": item.get("published") if isinstance(item, dict) and item.get("published") else now_iso(),
            "source": source_name,
            "text": text,
            "thematic_category": thematic_category,
            "opportunity_score": round(float(opp_score), 4), # Keep global score for reference
            "opportunity_confidence": round(float(opp_conf), 4),
            "impacts": impacts
        }
        events.append(ev)
    
    if cache_hits > 0 or new_items > 0:
        print(f"[{source_name}] Processed: {new_items} new, {cache_hits} cached (skipped)")
    return events

def process_weather_dict(weather_obj: Dict[str, Any]) -> List[Dict[str, Any]]:
    events = []
    if not isinstance(weather_obj, dict):
        return events
    for place, rec in weather_obj.items():
        desc = ""
        if isinstance(rec, dict):
            desc = rec.get("weather_description") or rec.get("weather_main") or ""
            temp = rec.get("temperature")
            hum = rec.get("humidity")
            extras = []
            if temp is not None:
                extras.append(f"Temp {temp}°C")
            if hum is not None:
                extras.append(f"Humidity {hum}%")
            if rec.get("warnings"):
                extras.append("Warnings present")
            text = f"{place}: {desc}. " + " ".join(extras)
        else:
            text = f"{place}: {str(rec)}"
        
        if not text or len(text) < 5:
            continue

        # Weather gets special treatment - no ML inference needed
        # Set thematic_category to "Weather" and industry to "Weather"
        thematic_category = "Weather"
        
        # Simple negative score for weather (weather reports are typically neutral to negative for business)
        # We can use a simple heuristic based on warnings
        if isinstance(rec, dict) and rec.get("warnings"):
            opp_score = -0.5  # Weather warnings are negative
        else:
            opp_score = 0.0   # Normal weather is neutral
        
        # Weather impacts all industries but we'll just label it as "Weather"
        impacts = [{
            "industry": "Weather",
            "score": round(opp_score, 4),
            "impact_type": "Weather Report",
            "relevance": 1.0
        }]
        
        # No fallback needed - weather always has one
        impacts.sort(key=lambda x: abs(x["score"]), reverse=True)

        ev = {
            "id": str(uuid.uuid4()),
            "timestamp": now_iso(),
            "source": "weather",
            "place": place,
            "text": text,
            "thematic_category": thematic_category,
            "opportunity_score": round(float(opp_score), 4),
            "impacts": impacts
        }
        events.append(ev)
    return events

# ========================================
# COMPETITION FEATURES: Indicator Generation
# ========================================

def generate_national_indicators(events: List[Dict]) -> List[Dict]:
    """
    Filter and format National Activity Indicators.
    Returns events that qualify as major national events.
    """
    national_events = []
    
    for event in events:
        # Skip weather - not national activity unless disaster
        if event.get('source') == 'weather':
            continue
            
        text = event.get('text', '')
        thematic_category = event.get('thematic_category', '')
        
        if classify_national_activity(text, thematic_category):
            national_events.append({
                "id": event.get('id'),
                "timestamp": event.get('timestamp'),
                "source": event.get('source'),
                "headline": text[:200],  # Truncated for readability
                "thematic_category": thematic_category,
                "top_industries_affected": [imp['industry'] for imp in event.get('impacts', [])[:3]],
                "impact_score": event.get('opportunity_score', 0)
            })
    
    # Sort by absolute impact
    national_events.sort(key=lambda x: abs(x.get('impact_score', 0)), reverse=True)
    
    return national_events

def generate_operational_indicators(events: List[Dict]) -> List[Dict]:
    """
    Filter and format Operational Environment Indicators.
    Returns events with business/operational signals.
    """
    operational_events = []
    
    for event in events:
        # Skip weather unless it affects operations
        if event.get('source') == 'weather':
            continue
            
        text = event.get('text', '')
        impacts = event.get('impacts', [])
        
        if classify_operational_environment(text, impacts):
            # Calculate breadth of impact
            affected_count = len([imp for imp in impacts if abs(imp.get('score', 0)) > 0.1])
            
            operational_events.append({
                "id": event.get('id'),
                "timestamp": event.get('timestamp'),
                "source": event.get('source'),
                "signal": text[:200],
                "thematic_category": event.get('thematic_category', ''),
                "affected_industries_count": affected_count,
                "top_affected_industries": [imp['industry'] for imp in impacts[:5]],
                "overall_impact": event.get('opportunity_score', 0)
            })
    
    # Sort by breadth of impact
    operational_events.sort(key=lambda x: x.get('affected_industries_count', 0), reverse=True)
    
    return operational_events

def generate_risk_opportunity_insights(events: List[Dict]) -> List[Dict]:
    """
    Generate enhanced risk/opportunity insights with explanations.
    Returns all events with detailed risk and opportunity analysis.
    """
    insights = []
    
    for event in events:
        text = event.get('text', '')
        opp_score = event.get('opportunity_score', 0)
        impacts = event.get('impacts', [])
        
        # Calculate detailed risk/opportunity
        risk_data = calculate_risk_score(opp_score, text, impacts)
        
        insights.append({
            "id": event.get('id'),
            "timestamp": event.get('timestamp'),
            "source": event.get('source'),
            "headline": text[:200],
            "thematic_category": event.get('thematic_category', ''),
            "risk_score": risk_data['risk_score'],
            "risk_category": risk_data['risk_category'],
            "risk_explanation": risk_data['risk_explanation'],
            "opportunity_score": risk_data['opportunity_score'],
            "opportunity_category": risk_data['opportunity_category'],
            "opportunity_explanation": risk_data['opportunity_explanation'],
            "top_affected_industries": risk_data['top_affected_industries']
        })
    
    # Sort by highest risk OR opportunity (whichever is greater)
    insights.sort(
        key=lambda x: max(x.get('risk_score', 0), x.get('opportunity_score', 0)), 
        reverse=True
    )
    
    return insights

# ---- run pipeline (single snapshot) ----
def run_pipeline(save_history: bool = True):
    print(f"[{now_iso()}] Starting pipeline run...")
    
    # Load cache
    cache = load_cache()
    initial_cache_size = len(cache)
    
    all_events: List[Dict[str, Any]] = []

    # strictly load each approved source; warn when missing
    for src_name, src_path in APPROVED_SOURCES.items():
        if not src_path.exists():
            print(f"[WARN] {src_path} not found, skipping {src_name}")
            continue
        raw_data = safe_load_json(src_path)
        if raw_data is None:
            print(f"[INFO] Approved source missing or unreadable: {src_path}")
            continue
        if src_name == "weather":
            events = process_weather_dict(raw_data)
        else:
            events = process_news_list(raw_data, src_name, cache)
        all_events.extend(events)

    # Calculate overall score (average of opportunity scores)
    if all_events:
        avg_score = sum(e.get("opportunity_score", 0) for e in all_events) / len(all_events)
    else:
        avg_score = 0.0

    snapshot = {
        "snapshot_id": str(uuid.uuid4()),
        "run_timestamp": now_iso(),
        "overall_score": round(avg_score, 4),
        "events_count": len(all_events),
        "events": all_events
    }

    # Save cache (only if we processed new items)
    if len(cache) > initial_cache_size:
        save_cache(cache)
        print(f"[CACHE] Stored {len(cache) - initial_cache_size} new items (total: {len(cache)})")
    
    # live output (overwrite)
    try:
        with LIVE_OUTPUT.open("w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[ERROR] Failed to write live output {LIVE_OUTPUT}: {e}")
    
    # ========================================
    # Generate Competition Indicator Outputs
    # ========================================
    
    # 1. National Activity Indicators
    national_indicators = generate_national_indicators(all_events)
    national_output = {
        "generated_at": now_iso(),
        "total_indicators": len(national_indicators),
        "indicators": national_indicators
    }
    national_file = OUTPUT_DIR / "national_activity_indicators.json"
    try:
        with national_file.open("w", encoding="utf-8") as f:
            json.dump(national_output, f, indent=2, ensure_ascii=False)
        print(f"[COMP] National Activity Indicators: {len(national_indicators)} events → {national_file}")
    except Exception as e:
        print(f"[ERROR] Failed to write national indicators: {e}")
    
    # 2. Operational Environment Indicators
    operational_indicators = generate_operational_indicators(all_events)
    operational_output = {
        "generated_at": now_iso(),
        "total_indicators": len(operational_indicators),
        "indicators": operational_indicators
    }
    operational_file = OUTPUT_DIR / "operational_environment_indicators.json"
    try:
        with operational_file.open("w", encoding="utf-8") as f:
            json.dump(operational_output, f, indent=2, ensure_ascii=False)
        print(f"[COMP] Operational Environment Indicators: {len(operational_indicators)} events → {operational_file}")
    except Exception as e:
        print(f"[ERROR] Failed to write operational indicators: {e}")
    
    # 3. Risk & Opportunity Insights
    risk_opp_insights = generate_risk_opportunity_insights(all_events)
    risk_opp_output = {
        "generated_at": now_iso(),
        "total_insights": len(risk_opp_insights),
        "insights": risk_opp_insights
    }
    risk_opp_file = OUTPUT_DIR / "risk_opportunity_insights.json"
    try:
        with risk_opp_file.open("w", encoding="utf-8") as f:
            json.dump(risk_opp_output, f, indent=2, ensure_ascii=False)
        print(f"[COMP] Risk \u0026 Opportunity Insights: {len(risk_opp_insights)} events → {risk_opp_file}")
    except Exception as e:
        print(f"[ERROR] Failed to write risk/opportunity insights: {e}")

    # append hourly snapshot (Option 2: one object per line)
    if save_history:
        try:
            with HISTORY_FILE.open("a", encoding="utf-8") as f:
                f.write(json.dumps(snapshot, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"[ERROR] Failed to append history {HISTORY_FILE}: {e}")

    return snapshot

# CLI
if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--no-history", action="store_true", help="Don't append to hourly history")
    args = p.parse_args()
    snap = run_pipeline(save_history=(not args.no_history))
    print(f"[{now_iso()}] Completed snapshot {snap['snapshot_id']} with {snap['events_count']} events. Live written to {LIVE_OUTPUT}")

