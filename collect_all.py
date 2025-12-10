#!/usr/bin/env python3
"""
collect_all.py - Master Data Collection Script

Runs all resource collection scripts in sequence:
1. Headlines (RSS, Google News, YouTube, GDELT)
2. Government news
3. Weather data

Saves all outputs to jsons/ folder ready for pipeline.py to process.
"""

import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RESOURCES = ROOT / "resources"

# Scripts to run (in order)
COLLECTION_SCRIPTS = [
    RESOURCES / "headlines" / "headline_ocean.py",
    RESOURCES / "gov" / "gov.py",
    RESOURCES / "weather" / "weather.py",
]

def run_script(script_path):
    """Run a Python script and return success status."""
    print(f"\n{'='*60}")
    print(f"Running: {script_path.name}")
    print('='*60)
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=script_path.parent,
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✓ {script_path.name} completed successfully")
            return True
        else:
            print(f"✗ {script_path.name} failed with code {result.returncode}")
            return False
            
    except Exception as e:
        print(f"✗ Error running {script_path.name}: {e}")
        return False

def main():
    print("\n" + "="*60)
    print(" DATA COLLECTION - Master Script")
    print("="*60)
    
    success_count = 0
    
    for script in COLLECTION_SCRIPTS:
        if not script.exists():
            print(f"⚠ Script not found: {script}")
            continue
            
        if run_script(script):
            success_count += 1
    
    print("\n" + "="*60)
    print(f" COLLECTION COMPLETE: {success_count}/{len(COLLECTION_SCRIPTS)} successful")
    print("="*60)
    
    if success_count == len(COLLECTION_SCRIPTS):
        print("\n✓ All data collected. Ready to run pipeline.py")
        return 0
    else:
        print("\n⚠ Some collection scripts failed. Check outputs above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
