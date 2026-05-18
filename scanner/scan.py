# scanner.py
# High-value automated scanner for normalized targets.

import json
import os
from datetime import datetime

# HIGH‑VALUE ENGINES ONLY
from idor_engine import check_idor
from ssrf_engine import check_ssrf
from auth_bypass_engine import check_auth_bypass
from rate_limit_engine import check_rate_limit
from sensitive_data_engine import check_sensitive_data
from jwt_engine import check_jwt

OUTPUT_DIR = "data"

def scan_target(url):
    """Run only payout-worthy checks on a single target."""
    findings = []

    engines = [
        check_idor,
        check_ssrf,
        check_auth_bypass,
        check_rate_limit,
        check_sensitive_data,
        check_jwt,
    ]

    for engine in engines:
        try:
            findings.extend(engine(url))
        except Exception as e:
            print(f"[scanner] Engine error on {url}: {e}")

    return findings


def save_findings(program, findings):
    """Save findings for a program into a clean JSON file."""
    if not findings:
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    date = datetime.utcnow().strftime("%Y-%m-%d")

    program_id = program.get("id", program.get("name", "unknown")).replace(" ", "_")
    filename = f"{program_id}-{date}.json"
    path = os.path.join(OUTPUT_DIR, filename)

    output = []
    for f in findings:
        output.append({
            "severity": f.get("severity", "HIGH"),
            "title": f.get("title", "Unknown finding"),
            "target": f.get("target"),
            "program": program.get("name", "Unknown Program"),
            "date": date,
            "details": f.get("details", {}),
        })

    with open(path, "w") as fp:
        json.dump(output, fp, indent=4)

    print(f"[scanner] Saved: {path}")


def scan_program(program):
    """Scan all normalized targets for a single program."""
    targets = program.get("normalized_scope", [])
    all_findings = []

    for target in targets:
        print(f"[scanner] Scanning target: {target}")
        findings = scan_target(target)

        # Attach target to each finding
        for f in findings:
            f["target"] = target

        all_findings.extend(findings)

    return all_findings
