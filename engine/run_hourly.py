#!/usr/bin/env python3
"""
engine/run_hourly.py

Scheduler to run pipeline every hour.

Usage:
    python3 engine/run_hourly.py        # runs forever, invoking pipeline each hour
    python3 engine/run_hourly.py --once # run pipeline once and exit
"""

import time
from pathlib import Path
from datetime import datetime
import signal
import sys

ROOT = Path(__file__).resolve().parent.parent
PIPELINE = ROOT / "engine" / "pipeline.py"

# import pipeline function as module
import importlib.util
import types

def load_pipeline():
    spec = importlib.util.spec_from_file_location("engine.pipeline", str(PIPELINE))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def format_now():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def main(run_once=False):
    mod = load_pipeline()
    print(f"[{format_now()}] Pipeline loaded. run_once={run_once}")
    if run_once:
        snapshot = mod.run_pipeline()
        print(f"[{format_now()}] Completed one run. snapshot_id={snapshot.get('snapshot_id')}")
        return

    # graceful shutdown support
    stop = False
    def _handler(signum, frame):
        nonlocal stop
        print(f"[{format_now()}] Received shutdown signal. Exiting after current run.")
        stop = True
    signal.signal(signal.SIGINT, _handler)
    signal.signal(signal.SIGTERM, _handler)

    while not stop:
        try:
            snapshot = mod.run_pipeline()
            print(f"[{format_now()}] Run complete. snapshot_id={snapshot.get('snapshot_id')} events={snapshot.get('events_count')}")
        except Exception as e:
            print(f"[{format_now()}] Pipeline run failed:", e)
        # sleep for 3600 seconds (1 hour)
        for _ in range(3600):
            if stop:
                break
            time.sleep(1)
    print(f"[{format_now()}] Scheduler stopped. Bye.")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--once", action="store_true", help="Run only once then exit")
    args = p.parse_args()
    main(run_once=args.once)

