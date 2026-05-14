import os
import json
from system_fixer.report_filter import filter_findings

def load_findings(path):
    with open(path, "r") as f:
        return json.load(f)

def generate_strict_report(program, input_path, output_path):
    findings = load_findings(input_path)
    filtered = filter_findings(findings, program)

    if not filtered:
        return None

    lines = []
    lines.append(f"# {program} – Strict Mode Report\n")
    lines.append(f"Total Findings: {len(filtered)}\n")

    for f in filtered:
        lines.append(f"## {f.get('issue','Unknown')}")
        lines.append(f"- Target: {f.get('target','')}")
        lines.append(f"- Severity: {f.get('severity','')}")
        lines.append(f"- Impact: {f.get('impact','')}")
        lines.append(f"- Description: {f.get('description','')}")
        lines.append("")

    with open(output_path, "w") as out:
        out.write("\n".join(lines))

    return True
