import json
import os

BASE_DIR = os.path.dirname(__file__)
RULES_PATH = os.path.join(BASE_DIR, "program_rules.json")

def load_program_rules():
    if not os.path.exists(RULES_PATH):
        return {}
    with open(RULES_PATH, "r") as f:
        return json.load(f)

def severity_value(sev):
    sev = sev.upper()
    mapping = {
        "CRITICAL": 4,
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
        "INFO": 0
    }
    return mapping.get(sev, 0)

def meets_severity_threshold(program, severity):
    rules = load_program_rules()
    program_key = program.lower() if isinstance(program, str) else (program.get("id") or program.get("name") or "").lower()

    if program_key not in rules:
        # default strict mode: MEDIUM+
        return severity_value(severity) >= severity_value("MEDIUM")

    min_required = rules[program_key].get("min_severity", "MEDIUM")
    return severity_value(severity) >= severity_value(min_required)
