import json
import os
from system_fixer.report_generator import generate_reports

OUTPUT_FILE = "processed_findings.json"

def write_output(findings):
    # Write JSON output for debugging / dashboard use
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(findings, f, indent=4)
    print(f"[output_writer] Wrote JSON output to {OUTPUT_FILE}")

    # Generate payout-ready Markdown reports
    generate_reports(findings)
    print("[output_writer] Generated payout-ready Markdown reports")
