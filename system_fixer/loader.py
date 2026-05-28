import json
import os

def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

def load_programs(path=None):
    """Load programs from programs.json."""
    if path is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = os.path.join(base_dir, "programs.json")
    
    if not os.path.exists(path):
        return []
    
    with open(path, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []
