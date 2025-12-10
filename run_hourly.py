import subprocess
import sys
from datetime import datetime
import argparse
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

RESOURCES_DIR = BASE_DIR / "resources"
PIPELINE_SCRIPT = BASE_DIR / "pipeline.py"
HISTORY_DIR = BASE_DIR / "history"

def run_resource_scripts():
    print("Running resource scripts...")

    scripts = [
        RESOURCES_DIR / "gov/gov.py",
        RESOURCES_DIR / "headlines/headline_ocean.py",
        RESOURCES_DIR / "weather/weather.py",
    ]

    for script in scripts:
        print(f" → Running {script.name}")
        result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[ERROR] {script.name} failed:")
            print(result.stderr)
        else:
            print(f"[OK] {script.name} completed.")

def run_pipeline():
    print("Running pipeline to generate live_output.json ...")
    result = subprocess.run([sys.executable, str(PIPELINE_SCRIPT)], capture_output=True, text=True)

    if result.returncode != 0:
        print("[ERROR] Pipeline failed:")
        print(result.stderr)
        return False
    else:
        print("[OK] Pipeline completed.")
        return True

def append_to_history():
    print("Appending snapshot to history...")
    HISTORY_DIR.mkdir(exist_ok=True)
    history_file = HISTORY_DIR / "hourly_history.jsonl"
    live_file = BASE_DIR / "output/live_output.json"

    if live_file.exists():
        line = live_file.read_text().strip()
        with open(history_file, "a") as f:
            f.write(line + "\n")
        print("[OK] Snapshot appended.")
    else:
        print("[ERROR] live_output.json not found!")

def run_once():
    print("==========================")
    print("Running hourly job ONCE")
    print("==========================")

    run_resource_scripts()
    if run_pipeline():
        append_to_history()

def run_every_hour():
    while True:
        run_once()
        print("Waiting 1 hour...")
        time.sleep(3600)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run one cycle only")
    args = parser.parse_args()

    if args.once:
        run_once()
    else:
        run_every_hour()

