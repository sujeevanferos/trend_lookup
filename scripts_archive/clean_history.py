
import json
import hashlib
from pathlib import Path

HISTORY_FILE = Path("history/hourly_history.jsonl")

def get_content_hash(events):
    # Create a signature based on text and source of events
    # Sort to ensure order doesn't matter
    signatures = sorted([f"{e.get('source')}:{e.get('text')}" for e in events])
    return hashlib.md5("".join(signatures).encode('utf-8')).hexdigest()

def clean_history():
    if not HISTORY_FILE.exists():
        print("No history file found.")
        return

    print(f"Reading {HISTORY_FILE}...")
    with open(HISTORY_FILE, 'r') as f:
        lines = f.readlines()

    unique_lines = []
    last_hash = None
    kept_count = 0

    for line in lines:
        if not line.strip():
            continue
        try:
            snapshot = json.loads(line)
            events = snapshot.get('events', [])
            current_hash = get_content_hash(events)

            # If content is different from the last kept snapshot, keep it.
            # OR if it's the very first one.
            if current_hash != last_hash:
                unique_lines.append(line)
                last_hash = current_hash
                kept_count += 1
            else:
                # Duplicate content. 
                # Optional: Check timestamp. If it's > 1 hour apart, maybe keep it?
                # For now, strict deduplication of consecutive identical states.
                pass
        except json.JSONDecodeError:
            print("Skipping invalid JSON line")
            continue

    print(f"Original lines: {len(lines)}")
    print(f"Unique lines: {len(unique_lines)}")

    # Backup
    if len(lines) != len(unique_lines):
        backup_path = HISTORY_FILE.with_suffix('.jsonl.bak')
        with open(backup_path, 'w') as f:
            f.writelines(lines)
        print(f"Backup saved to {backup_path}")

        with open(HISTORY_FILE, 'w') as f:
            f.writelines(unique_lines)
        print("Cleaned history saved.")
    else:
        print("No duplicates found.")

if __name__ == "__main__":
    clean_history()
