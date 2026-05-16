from system_fixer.findings_loader import load_findings
from system_fixer.findings_normalizer import normalize_findings
from system_fixer.false_positive_filter import filter_false_positives
from system_fixer.severity_scorer import score_severity
from system_fixer.intelligence_enricher import enrich_findings
from system_fixer.output_writer import write_output
from system_fixer.money_filter import filter_money_findings

def run_pipeline():
    print("[pipeline] Starting unified analysis pipeline...")

    # 1. Load raw findings
    findings = load_findings()
    print(f"[pipeline] Loaded {len(findings)} raw findings")

    # 2. Normalize structure
    findings = normalize_findings(findings)
    print("[pipeline] Normalized findings")

    # 3. Remove false positives
    findings = filter_false_positives(findings)
    print("[pipeline] Filtered false positives")

    # 4. Score severity
    findings = score_severity(findings)
    print("[pipeline] Scored severity")

    # 5. Add intelligence metadata
    findings = enrich_findings(findings)
    print("[pipeline] Enriched findings with intelligence")

    # 6. Filter to ONLY high‑money, non‑duplicate findings
    findings = filter_money_findings(findings)
    print(f"[pipeline] Filtered to {len(findings)} high‑money, non‑duplicate candidates")

    # 7. Write final output
    write_output(findings)
    print("[pipeline] Wrote processed findings")

    print("[pipeline] Pipeline complete")
