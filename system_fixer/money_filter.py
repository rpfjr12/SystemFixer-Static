import json
import os

SUBMISSIONS_FILE = "bounty_data/submissions.json"

def load_submitted_fingerprints():
    if not os.path.exists(SUBMISSIONS_FILE):
        return set()
    with open(SUBMISSIONS_FILE, "r") as f:
        data = json.load(f)
    return {item["fingerprint"] for item in data if "fingerprint" in item}

def fingerprint_finding(f):
    # stable ID: program + target + title
    return f"{f.get('program','')}|{f.get('target','')}|{f.get('title','')}"

def money_score(f):
    sev = f.get("severity", "").upper()
    base = {"CRITICAL": 5, "HIGH": 4, "MEDIUM": 3, "LOW": 2}.get(sev, 1)
    exploit = f.get("exploitability_score", 1)
    return base * exploit

def filter_money_findings(findings):
    submitted = load_submitted_fingerprints()
    candidates = []

    for f in findings:
        fp = fingerprint_finding(f)
        if fp in submitted:
            continue  # already submitted before

        f["fingerprint"] = fp
        f["money_score"] = money_score(f)
        candidates.append(f)

    # highest money_score first
    candidates.sort(key=lambda x: x.get("money_score", 0), reverse=True)
    return candidates
