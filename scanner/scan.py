import json
import requests
import os
from datetime import datetime

def load_programs():
    with open("programs.json", "r") as f:
        return json.load(f)

def scan_target(url):
    findings = []
    try:
        r = requests.get(url, timeout=10)
        headers = r.headers

        # Missing HSTS
        if "Strict-Transport-Security" not in headers:
            findings.append(("MEDIUM", "Missing Strict-Transport-Security (HSTS)"))

        # Missing CSP
        if "Content-Security-Policy" not in headers:
            findings.append(("MEDIUM", "Missing Content-Security-Policy (CSP)"))

        # Missing X-Frame-Options
        if "X-Frame-Options" not in headers:
            findings.append(("MEDIUM", "Missing X-Frame-Options"))

        # Cookie HttpOnly check
        cookies = r.cookies
        for c in cookies:
            if not c.has_nonstandard_attr("HttpOnly"):
                findings.append(("MEDIUM", "Cookie missing HttpOnly flag"))

        # Server version disclosure
        if "Server" in headers:
            findings.append(("LOW", "Server version disclosure"))

    except Exception:
        findings.append(("LOW", "Target unreachable"))

    return findings

def save_findings(program, target, findings):
    os.makedirs("data", exist_ok=True)
    date = datetime.utcnow().strftime("%Y-%m-%d")
    filename = f"data/{program['id']}-{date}.json"

    output = []
    for sev, title in findings:
        output.append({
            "severity": sev,
            "title": title,
            "target": target,
            "program": program["name"],
            "date": date
        })

    with open(filename, "w") as f:
        json.dump(output, f, indent=2)

def main():
    programs = load_programs()
    for program in programs:
        for target in program["scope"]:
            findings = scan_target(target)
            save_findings(program, target, findings)

if __name__ == "__main__":
    main()
