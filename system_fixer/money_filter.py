from system_fixer.severity_weights import SEVERITY_WEIGHTS if False else None  # placeholder to show dependency

import json
import os

WEIGHTS_FILE = "system_fixer/severity_weights.json"

def load_severity_weights():
    if not os.path.exists(WEIGHTS_FILE):
        print(f"[money_filter] No weights file found at {WEIGHTS_FILE}, using defaults")
        return {
            "CRITICAL": 5,
            "HIGH": 4,
            "MEDIUM": 3,
            "LOW": 1,
            "UNRATED": 0
        }

    try:
        with open(WEIGHTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"[money_filter] Loaded severity weights from {WEIGHTS_FILE}")
            return data
    except Exception as e:
        print(f"[money_filter] Error loading weights: {e}, using defaults")
        return {
            "CRITICAL": 5,
            "HIGH": 4,
            "MEDIUM": 3,
            "LOW": 1,
            "UNRATED": 0
        }

def compute_money_score(finding, weights):
    severity = finding.get("severity", "UNRATED")
    sev_weight = weights.get(severity, 0)

    intel = finding.get("intelligence", {})
    tag_count = intel.get("tag_count", 0)
    has_exploit = "exploit" in (intel.get("tags") or [])
    has_chain = "chain" in (intel.get("tags") or [])

    base = sev_weight * 10
    bonus = 0

    if tag_count > 0:
        bonus += min(tag_count * 2, 20)

    if has_exploit:
        bonus += 15

    if has_chain:
        bonus += 10

    money_score = base + bonus
    finding["money_score"] = money_score
    return finding

def apply_money_filter(findings, min_score=20):
    print("[money_filter] Applying money scoring and filtering...")
    weights = load_severity_weights()

    scored = []
    seen_fingerprints = set()

    for f in findings:
        # Skip if no fingerprint (cannot dedupe or track)
        fp = f.get("fingerprint")
        if not fp:
            continue

        # Deduplicate by fingerprint
        if fp in seen_fingerprints:
            continue
        seen_fingerprints.add(fp)

        f = compute_money_score(f, weights)

        if f.get("money_score", 0) >= min_score:
            scored.append(f)

    scored.sort(key=lambda x: x.get("money_score", 0), reverse=True)

    print(f"[money_filter] {len(scored)} findings passed money filter (min_score={min_score})")
    return scored
