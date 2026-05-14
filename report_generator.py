import os
import json
from collections import defaultdict
from datetime import datetime

DATA_DIR = "data"
REPORTS_DIR = "reports"

# Which severities to keep by default
KEEP_SEVERITIES = {"MEDIUM", "HIGH", "CRITICAL"}

# Titles to drop as too noisy / low value
IGNORE_TITLES = {
    "Server version disclosure",  # often informational
}

def load_all_findings():
    findings = []
    if not os.path.isdir(DATA_DIR):
        return findings

    for file in os.listdir(DATA_DIR):
        if not file.endswith(".json"):
            continue
        path = os.path.join(DATA_DIR, file)
        try:
            with open(path, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    findings.extend(data)
        except Exception:
            # Skip malformed files
            continue
    return findings

def is_worth_reporting(f):
    """
    Decide if a finding is worth keeping.
    You can tune this over time.
    """
    severity = f.get("severity", "").upper().strip()
    title = f.get("title", "").strip()

    if title in IGNORE_TITLES:
        return False

    if severity not in KEEP_SEVERITIES:
        return False

    # You can add more logic here later if you want
    return True

def dedupe_findings(findings):
    """
    Remove duplicates based on (program, target, title).
    """
    seen = set()
    unique = []
    for f in findings:
        key = (
            f.get("program", "").strip(),
            f.get("target", "").strip(),
            f.get("title", "").strip(),
        )
        if key in seen:
            continue
        seen.add(key)
        unique.append(f)
    return unique

def group_by_program(findings):
    grouped = defaultdict(list)
    for f in findings:
        program = f.get("program", "UNKNOWN").strip()
        grouped[program].append(f)
    return grouped

def format_markdown_report(program, findings):
    """
    Build a Markdown report for a single program.
    """
    if not findings:
        return ""

    # Sort by severity then title
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    findings_sorted = sorted(
        findings,
        key=lambda f: (
            severity_order.get(f.get("severity", "").upper(), 99),
            f.get("title", ""),
        ),
    )

    date_str = datetime.utcnow().strftime("%Y-%m-%d")

    lines = []
    lines.append(f"# {program} – Automated Findings")
    lines.append("")
    lines.append(f"**Date:** {date_str}")
    lines.append(f"**Total findings:** {len(findings_sorted)}")
    lines.append("")
    lines.append("## Summary by severity")
    counts = defaultdict(int)
    for f in findings_sorted:
        counts[f.get("severity", "").upper()] += 1
    for sev in sorted(counts.keys(), key=lambda s: severity_order.get(s, 99)):
        lines.append(f"- **{sev}:** {counts[sev]}")
    lines.append("")

    lines.append("## Findings")
    lines.append("")
    for idx, f in enumerate(findings_sorted, start=1):
        sev = f.get("severity", "").upper()
        title = f.get("title", "")
        target = f.get("target", "")
        date = f.get("date", "")
        lines.append(f"### {idx}. {title} ({sev})")
        lines.append("")
        lines.append(f"- **Target:** `{target}`")
        lines.append(f"- **Program:** {program}")
        lines.append(f"- **Date detected:** {date}")
        lines.append("")
        lines.append("**Description:**")
        lines.append(f"- Automated detection of: **{title}**.")
        lines.append("")
        lines.append("**Potential impact (generic):**")
        if "HSTS" in title:
            lines.append("- Without HSTS, users may be exposed to downgrade or MITM attacks if they ever hit HTTP.")
        elif "Content-Security-Policy" in title:
            lines.append("- Without CSP, the application has reduced protection against XSS and content injection.")
        elif "X-Frame-Options" in title:
            lines.append("- Without X-Frame-Options, the application may be vulnerable to clickjacking.")
        elif "Cookie missing HttpOnly" in title:
            lines.append("- Without HttpOnly, cookies may be accessible to client-side scripts, increasing XSS impact.")
        else:
            lines.append("- This issue may increase the attack surface or reduce defense-in-depth.")
        lines.append("")
        lines.append("**Suggested remediation (generic):**")
        if "HSTS" in title:
            lines.append("- Add a Strict-Transport-Security header with an appropriate max-age and includeSubDomains.")
        elif "Content-Security-Policy" in title:
            lines.append("- Define and deploy a Content-Security-Policy that restricts script, frame, and resource sources.")
        elif "X-Frame-Options" in title:
            lines.append("- Add an X-Frame-Options or equivalent CSP frame-ancestors directive to prevent framing.")
        elif "Cookie missing HttpOnly" in title:
            lines.append("- Mark sensitive cookies with the HttpOnly flag to prevent access from client-side scripts.")
        else:
            lines.append("- Apply standard hardening guidance for this class of issue.")
        lines.append("")
        lines.append("---")
        lines.append("")

    return "\n".join(lines)

def write_reports(grouped_findings):
    os.makedirs(REPORTS_DIR, exist_ok=True)
    date_str = datetime.utcnow().strftime("%Y-%m-%d")

    for program, findings in grouped_findings.items():
        if not findings:
            continue
        safe_program = "".join(c for c in program if c.isalnum() or c in ("-", "_")).strip()
        if not safe_program:
            safe_program = "UNKNOWN"
        filename = f"{safe_program}-{date_str}.md"
        path = os.path.join(REPORTS_DIR, filename)
        content = format_markdown_report(program, findings)
        if not content.strip():
            continue
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Wrote report: {path}")

def main():
    all_findings = load_all_findings()
    if not all_findings:
        print("No findings found in data/.")
        return

    # Filter to worth-reporting only
    filtered = [f for f in all_findings if is_worth_reporting(f)]

    if not filtered:
        print("No findings considered worth reporting after filtering.")
        return

    # Deduplicate
    unique = dedupe_findings(filtered)

    # Group by program
    grouped = group_by_program(unique)

    # Write Markdown reports
    write_reports(grouped)

if __name__ == "__main__":
    main()
