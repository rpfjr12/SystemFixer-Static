import os
import json
from datetime import datetime

DATA_DIR = "data"
REPORTS_DIR = "reports"

# -----------------------------
# STRICT MODE FILTERING LOGIC
# -----------------------------

def is_ui_endpoint(finding):
    """Reject API endpoints, JSON-only endpoints, and anything non-interactive."""
    url = finding.get("target", "").lower()

    # API endpoints are never reportable for clickjacking, CSP, HSTS, etc.
    if "/api" in url or "api." in url:
        return False

    # JSON-only endpoints are not exploitable
    content_type = finding.get("content_type", "").lower()
    if "json" in content_type:
        return False

    return True


def is_reportable_issue(finding):
    """Strict mode: only keep issues that programs actually pay for."""
    issue = finding.get("issue", "").lower()

    # Remove missing header noise
    missing_header_keywords = [
        "missing x-frame-options",
        "missing content-security-policy",
        "missing strict-transport-security",
        "missing x-content-type-options",
        "missing referrer-policy",
    ]
    if any(k in issue for k in missing_header_keywords):
        return False

    # Remove low/no-impact issues
    if "informational" in issue or "low" in issue:
        return False

    # Keep only issues with real impact
    high_value_keywords = [
        "xss",
        "open redirect",
        "cors misconfiguration",
        "sensitive file exposure",
        "directory listing",
        "idOR",
        "authentication bypass",
        "broken access control",
        "csrf",
        "sql injection",
        "rce",
        "ssrf",
        "exposed admin panel",
        "leak",
        "token",
        "credential",
        "misconfiguration with impact",
    ]

    return any(k in issue for k in high_value_keywords)


def strict_filter(finding):
    """Apply ALL strict-mode rules."""
    return is_ui_endpoint(finding) and is_reportable_issue(finding)


# -----------------------------
# REPORT GENERATION
# -----------------------------

def generate_report(program, findings):
    """Generate a strict-mode filtered report."""
    filtered = [f for f in findings if strict_filter(f)]

    if not filtered:
        return None  # No reportable findings

    date_str = datetime.now().strftime("%Y-%m-%d")
    report = f"# {program} – Automated Findings\n\n"
    report += f"**Date:** {date_str}\n"
    report += f"**Total findings:** {len(filtered)}\n\n"

    # Severity summary
    severities = {}
    for f in filtered:
        sev = f.get("severity", "UNKNOWN").upper()
        severities[sev] = severities.get(sev, 0) + 1

    report += "## Summary by severity\n"
    for sev, count in severities.items():
        report += f"- **{sev}:** {count}\n"
    report += "\n## Findings\n\n"

    # Detailed findings
    for i, f in enumerate(filtered, 1):
        report += f"### {i}. {f.get('issue', 'Unknown Issue')} ({f.get('severity', 'UNKNOWN')})\n\n"
        report += f"- **Target:** `{f.get('target', '')}`\n"
        report += f"- **Program:** {program}\n"
        report += f"- **Date detected:** {f.get('date', '')}\n\n"
        report += f"**Description:**\n- {f.get('description', '')}\n\n"
        report += f"**Impact:**\n- {f.get('impact', '')}\n\n"
        report += f"**Suggested remediation:**\n- {f.get('remediation', '')}\n\n"
        report += "---\n\n"

    return report


def main():
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)

    for filename in os.listdir(DATA_DIR):
        if not filename.endswith(".json"):
            continue

        program = filename.split("-")[0].capitalize()
        path = os.path.join(DATA_DIR, filename)

        with open(path, "r") as f:
            findings = json.load(f)

        report = generate_report(program, findings)
        if report:
            report_path = os.path.join(REPORTS_DIR, filename.replace(".json", ".md"))
            with open(report_path, "w") as out:
                out.write(report)


if __name__ == "__main__":
    main()

