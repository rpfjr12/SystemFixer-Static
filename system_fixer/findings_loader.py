import json
import os

def load_findings(path):
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)
