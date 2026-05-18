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

def load_programs():
    with open("programs.json", "r") as f:
        return json.load(f)

def scan_target(url):
    findings = []

    # ONLY payout‑worthy checks
    findings += check_idor(url)
    findings += check_ssrf(url)
    findings += check_auth_bypass(url)
    findings += check_rate_limit(url)
    findings += check_sensitive_data(url)
    findings += check_jwt(url)

    return findings

def save_findings(program, target, findings):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    date = datetime.utcnow().strftime("%Y-%m-%d")
    filename = f"{program['id']}-{date}.json"
    path = os.path.join(OUTPUT_DIR, filename)

    output = []
    for f in findings:
        output.append({
            "severity": f.get("severity", "HIGH"),
            "title": f.get("title", "Unknown finding"),
            "target": target,
            "program": program["name"],
            "date": date,
            "details": f.get("details", {}),
        })

    with open(path, "w") as f:
        json.dump(output, f, indent=4)

    print(f"[scanner] Saved: {path}")

def main():
    programs = load_programs()
    for program in programs:
        for target in program["scope"]:
            findings = scan_target(target)
            save_findings(program, target, findings)

if __name__ == "__main__":
    main()
