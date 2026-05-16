from system_fixer.severity_scoring import score_severity
from system_fixer.intelligence_enricher import enrich_findings
from system_fixer.rules_engine import apply_rules_to_all

def run_severity_engine(findings):
    print("[severity_engine] Starting severity engine...")

    # Step 1 — Normalize severity labels
    findings = score_severity(findings)
    print("[severity_engine] Severity normalized")

    # Step 2 — Add intelligence metadata
    findings = enrich_findings(findings)
    print("[severity_engine] Intelligence enriched")

    # Step 3 — Apply program-specific rules
    findings = apply_rules_to_all(findings)
    print("[severity_engine] Program rules applied")

    print("[severity_engine] Severity engine complete")
    return findings
