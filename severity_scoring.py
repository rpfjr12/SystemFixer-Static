import json
import os

WEIGHTS_PATH = "system-fixer/severity_weights.json"

def load_weights():
    """
    Load severity weight values from JSON.
    If the file does not exist, return default weights.
    """
    if not os.path.exists(WEIGHTS_PATH):
        return {
            "LOW": 1,
            "MEDIUM": 2,
            "HIGH": 3,
            "CRITICAL": 5
        }
    with open(WEIGHTS_PATH, "r") as f:
        return json.load(f)

def score_finding(finding, weights=None):
    """
    Assign a numeric severity score to a finding based on:
    - Base severity weight
    - Impact multipliers
    """
    if weights is None:
        weights = load_weights()

    severity = finding.get("severity", "LOW").upper()
    base = weights.get(severity, 1)

    impact = finding.get("impact", "").lower()

    # Impact multipliers
    if "account takeover" in impact:
        base += 3
    elif "rce" in impact or "remote code execution" in impact:
        base += 4
    elif "data exposure" in impact:
        base += 2
    elif "csrf" in impact:
        base += 1

    return base

def apply_severity_scores(findings):
    """
    Add a 'score' field to each finding.
    """
    weights = load_weights()
    for f in findings:
        f["score"] = score_finding(f, weights)
    return findings
