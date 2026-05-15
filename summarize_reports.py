import os
import re

REPORT_DIR = "reports"

def extract_findings(text):
    findings = []
    lines = text.splitlines()
    for line in lines:
        if line.lower().startswith("severity"):
            findings.append(line.strip())
        if "finding" in line.lower():
            findings.append(line.strip())
    return findings

def summarize_reports():
    summary = []

    for filename in os.listdir(REPORT_DIR):
        if filename.endswith(".md"):
            path = os.path.join(REPORT_DIR, filename)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            findings = extract_findings(content)

            summary.append({
                "file": filename,
                "findings": findings
            })

    return summary

def write_summary(summary):
    with open("SUMMARY.md", "w", encoding="utf-8") as f:
        f.write("# Report Summary\n\n")
        for item in summary:
            f.write(f"## {item['file']}\n")
            if item["findings"]:
                for finding in item["findings"]:
                    f.write(f"- {finding}\n")
            else:
                f.write("- No findings detected\n")
            f.write("\n")

if __name__ == "__main__":
    summary = summarize_reports()
    write_summary(summary)
    print("SUMMARY.md created.")
