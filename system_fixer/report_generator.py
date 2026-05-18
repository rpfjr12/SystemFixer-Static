import os
import json
from datetime import datetime

OUTPUT_DIR = "reports"

def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def generate_markdown_report(finding):
    title = finding.get("title", "Untitled Finding")
    program = finding.get("program", "Unknown Program")
    target = finding.get("target", "Unknown Target")
    severity = finding.get("severity", "Unrated")
    engine = finding.get("engine", "unknown_engine")
    fingerprint = finding.get("fingerprint", "no-fingerprint")
    money_score = finding.get("money_score", 0)

    # Auto‑generated details from engines
    description = finding.get("description", "Automated engine detected a payout‑worthy vulnerability.")
    reproduction = finding.get("reproduction_steps", "Automated reproduction steps not provided.")
    impact = finding.get("impact", "Automated impact analysis not provided.")
    evidence = finding.get("evidence", "No raw evidence provided.")
    fix = finding.get("fix", "Automated fix recommendation not provided.")

    md = f"""# {title}

**Program:** {program}  
**Target:** {target}  
**Severity:** {severity}  
**Engine:** {engine}  
**Money Score:** {money_score}  
**Fingerprint:** `{fingerprint}`  
**Generated:** {datetime.utcnow().isoformat()} UTC

---

## Summary
{description}

---

## Steps to Reproduce (Auto‑Generated)
{reproduction}

---

## Impact
{impact}

---

## Evidence
