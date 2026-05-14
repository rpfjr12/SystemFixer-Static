import os
import json
from system_fixer.report_filter import filter_findings

def generate_filtered_report(program, findings):
    filtered = filter_findings(findings, program)

    if not filtered:
        return None

    report = []
    report.append(f"# {program} – Strict Mode Findings\n")
    report.append(f"Total: {len(filtered)}\n")

    for f in filtered:
        report.append(f"## {f.get('issue','Unknown')}")
        report.append(f"- Target: {f.get('target','')}")
        report.append(f"- Severity: {f.get('severity','')}")
        report.append(f"- Impact: {f.get('impact','')}")
        report.append(f"- Description: {f.get('description','')}")
        report.append("")

    return "\n".join(report)
