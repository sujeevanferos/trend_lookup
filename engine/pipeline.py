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
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
JSONS_DIR = ROOT / "jsons"
OUTPUT_DIR = ROOT / "output"
HISTORY_DIR = ROOT / "history"
PREPROC_DIR = ROOT / "preprocessing"

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
INDUSTRY_MAP_PATH = OUTPUT_DIR / "industry_map.json"
HISTORY_FILE = HISTORY_DIR / "hourly_history.jsonl"

# timestamp helper
def now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

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

# ---- industry map defaults (auto-created if missing) ----
DEFAULT_INDUSTRY_MAP = {
  "disaster": { "agriculture":1.0, "fisheries":1.0, "mining":1.0, "forestry":1.0,
                "manufacturing":1.0, "construction":1.0, "apparel_textiles":1.0, "energy":1.0,
                "chemicals":1.0, "food_beverages":1.0, "tourism":1.0, "retail":1.0,
                "real_estate":1.0, "healthcare":1.0, "education":1.0, "banking_finance":1.0,
                "insurance":1.0, "transportation":1.0, "logistics":1.0, "ict_tech":1.0,
                "media_communications":1.0, "government_services":1.0, "pharmaceuticals":1.0,
                "exports":1.0, "import_trade":1.0 },
  "weather": { "agriculture":0.9,"tourism":0.6,"energy":0.5,"logistics":0.6,"transportation":0.6,"fisheries":0.7,
               "retail":0.3,"manufacturing":0.2,"apparel_textiles":0.1,"chemicals":0.1,"food_beverages":0.1,"real_estate":0.1,
               "healthcare":0.1,"education":0.1,"banking_finance":0.1,"insurance":0.1,"ict_tech":0.1,"media_communications":0.1,
               "government_services":0.1,"pharmaceuticals":0.1,"exports":0.1,"import_trade":0.1 },
  "economy": {}, "finance": {}, "government": {}, "health": {}, "international": {}, "tourism": {}, "other": {}
}

# fill generic 0.5/0.3/0.1 patterns for missing categories
_generic_list = ["agriculture","fisheries","mining","forestry","manufacturing","construction","apparel_textiles","energy",
                 "chemicals","food_beverages","tourism","retail","real_estate","healthcare","education","banking_finance",
                 "insurance","transportation","logistics","ict_tech","media_communications","government_services","pharmaceuticals",
                 "exports","import_trade"]
if not DEFAULT_INDUSTRY_MAP.get("economy"):
    DEFAULT_INDUSTRY_MAP["economy"] = {k:0.5 for k in _generic_list}
if not DEFAULT_INDUSTRY_MAP.get("finance"):
    DEFAULT_INDUSTRY_MAP["finance"] = {k:(1.0 if k=="banking_finance" else 0.1) for k in _generic_list}
if not DEFAULT_INDUSTRY_MAP.get("government"):
    DEFAULT_INDUSTRY_MAP["government"] = {k:0.3 for k in _generic_list}
if not DEFAULT_INDUSTRY_MAP.get("health"):
    DEFAULT_INDUSTRY_MAP["health"] = {"healthcare":1.0, **{k:0.05 for k in _generic_list if k!="healthcare"}}
if not DEFAULT_INDUSTRY_MAP.get("international"):
    DEFAULT_INDUSTRY_MAP["international"] = {"exports":0.9,"import_trade":0.9, **{k:0.1 for k in _generic_list if k not in ("exports","import_trade")}}
if not DEFAULT_INDUSTRY_MAP.get("tourism"):
    DEFAULT_INDUSTRY_MAP["tourism"] = {"tourism":1.0,"retail":0.6,"transportation":0.5,"real_estate":0.2,"logistics":0.2,"media_communications":0.1}
if not DEFAULT_INDUSTRY_MAP.get("other"):
    DEFAULT_INDUSTRY_MAP["other"] = {k:0.1 for k in _generic_list}

# ensure industry_map exists
if not INDUSTRY_MAP_PATH.exists():
    INDUSTRY_MAP_PATH.write_text(json.dumps(DEFAULT_INDUSTRY_MAP, indent=2), encoding="utf-8")

try:
    INDUSTRY_MAP = json.loads(INDUSTRY_MAP_PATH.read_text(encoding="utf-8"))
except Exception:
    INDUSTRY_MAP = DEFAULT_INDUSTRY_MAP

# ---- load engines: try user-provided preprocessing engines first ----
cat_engine = None
opp_engine = None

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
    global cat_engine, opp_engine
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        import torch
    except Exception:
        return

    # categorization fallback
    cat_model_dir = PREPROC_DIR / "categorization_model"
    if cat_engine is None and cat_model_dir.exists():
        try:
            tok = AutoTokenizer.from_pretrained(str(cat_model_dir))
            model = AutoModelForSequenceClassification.from_pretrained(str(cat_model_dir))
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            model.to(device); model.eval()
            raw = getattr(model.config, "id2label", {}) or {}
            id2label = {int(k): v for k, v in raw.items()} if raw else {}

            def cat_predict(text: str):
                enc = tok(text, truncation=True, padding=True, return_tensors="pt").to(device)
                with torch.no_grad():
                    out = model(**enc)
                    logits = out.logits
                    probs = torch.softmax(logits, dim=-1)[0]
                    idx = int(probs.argmax().item())
                    conf = float(probs[idx].item())
                    label = id2label.get(idx, str(idx))
                return label, conf
            cat_engine = type("CatEngine", (), {"predict": staticmethod(cat_predict)})
        except Exception as e:
            print("[WARN] Cat fallback failed:", e)

    # opportunity fallback
    opp_model_dir = PREPROC_DIR / "opportunity_model"
    if opp_engine is None and opp_model_dir.exists():
        try:
            tok2 = AutoTokenizer.from_pretrained(str(opp_model_dir))
            model2 = AutoModelForSequenceClassification.from_pretrained(str(opp_model_dir))
            device2 = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            model2.to(device2); model2.eval()

            def opp_predict(text: str):
                enc = tok2(text, truncation=True, padding=True, return_tensors="pt").to(device2)
                with torch.no_grad():
                    out = model2(**enc)
                    logits = out.logits
                    import torch as _t
                    if logits.shape[-1] == 1:
                        raw = float(logits.squeeze().item())
                        score = float(_t.tanh(_t.tensor(raw)).item())
                        conf = 1.0
                    else:
                        probs = _t.softmax(logits, dim=-1)[0]
                        labels = _t.arange(logits.shape[-1], dtype=_t.float32).to(device2)
                        expected = float((labels * probs).sum().item())
                        score = (expected / (logits.shape[-1]-1)) * 2.0 - 1.0
                        conf = float(probs.max().item())
                return float(score), float(conf)
            opp_engine = type("OppEngine", (), {"predict": staticmethod(opp_predict)})
        except Exception as e:
            print("[WARN] Opp fallback failed:", e)

# attempt to load engines
try_load_preproc_engines()
build_transformers_fallbacks()

# final safety dummies (should rarely be used)
if cat_engine is None:
    class CatDummy:
        @staticmethod
        def predict(text): return "other", 0.5
    cat_engine = CatDummy()
if opp_engine is None:
    class OppDummy:
        @staticmethod
        def predict(text): return 0.0, 0.5
    opp_engine = OppDummy()

# ---- compute impacts using industry map (value range -1..1) ----
def compute_industry_impact(category: str, opp_score: float) -> Dict[str, float]:
    cat = str(category).lower()
    weights = INDUSTRY_MAP.get(cat) or INDUSTRY_MAP.get(cat.lower()) or INDUSTRY_MAP.get("other", {})
    impacts: Dict[str, float] = {}
    for ind, w in weights.items():
        try:
            val = float(w) * float(opp_score)
        except Exception:
            val = 0.0
        impacts[ind] = round(val, 4)
    return impacts

# ---- main processing steps (strict sources only) ----
def process_news_list(raw_list: List[Any], source_name: str) -> List[Dict[str, Any]]:
    events = []
    if not isinstance(raw_list, list):
        return events
    for item in raw_list:
        text = extract_text_from_item(item)
        if not text or len(text) < 5:
            continue
        category, cat_conf = cat_engine.predict(text)
        opp_score, opp_conf = opp_engine.predict(text)
        impacts = compute_industry_impact(category, opp_score)
        ev = {
            "id": str(uuid.uuid4()),
            "timestamp": item.get("published") if isinstance(item, dict) and item.get("published") else now_iso(),
            "source": source_name,
            "text": text,
            "category": category,
            "category_confidence": float(cat_conf),
            "opportunity_score": round(float(opp_score), 4),
            "opportunity_confidence": round(float(opp_conf), 4),
            "industry_impact": impacts
        }
        events.append(ev)
    return events

def process_weather_dict(weather_obj: Dict[str, Any]) -> List[Dict[str, Any]]:
    events = []
    if not isinstance(weather_obj, dict):
        return events
    for place, rec in weather_obj.items():
        # rec expected as dict with keys like weather_description, temperature, humidity, warnings
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
        category, cat_conf = cat_engine.predict(text)
        opp_score, opp_conf = opp_engine.predict(text)
        impacts = compute_industry_impact(category, opp_score)
        ev = {
            "id": str(uuid.uuid4()),
            "timestamp": now_iso(),
            "source": "weather",
            "place": place,
            "text": text,
            "category": category,
            "category_confidence": float(cat_conf),
            "opportunity_score": round(float(opp_score), 4),
            "opportunity_confidence": round(float(opp_conf), 4),
            "industry_impact": impacts
        }
        events.append(ev)
    return events

# ---- run pipeline (single snapshot) ----
def run_pipeline(save_history: bool = True) -> Dict[str, Any]:
    all_events: List[Dict[str, Any]] = []

    # strictly load each approved source; warn when missing
    for source_name, path in APPROVED_SOURCES.items():
        raw = safe_load_json(path)
        if raw is None:
            print(f"[INFO] Approved source missing or unreadable: {path}")
            continue
        if source_name == "weather":
            events = process_weather_dict(raw)
        else:
            events = process_news_list(raw, source_name)
        all_events.extend(events)

    snapshot = {
        "snapshot_id": str(uuid.uuid4()),
        "run_timestamp": now_iso(),
        "events_count": len(all_events),
        "events": all_events
    }

    # overwrite live output
    try:
        with LIVE_OUTPUT.open("w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[ERROR] Failed to write live output {LIVE_OUTPUT}: {e}")

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

