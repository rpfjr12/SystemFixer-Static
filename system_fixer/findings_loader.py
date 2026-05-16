import json
import os

INPUT_FILE = "raw_findings.json"

def load_findings():
    if not os.path.exists(INPUT_FILE):
        print(f"[findings_loader] No {INPUT_FILE} found, returning empty list")
        return []

    try:
        with open(INPUT_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"[findings_loader] Loaded {len(data)} findings from {INPUT_FILE}")
            return data
    except Exception as e:
        print(f"[findings_loader] Error loading findings: {e}")
        return []
