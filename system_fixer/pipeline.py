from system_fixer.findings_loader import load_findings
from system_fixer.findings_normalizer import normalize_findings
from system_fixer.false_positive_filter import filter_false_positives
from system_fixer.severity_engine import run_severity_engine
from system_fixer.intelligence_enricher import enrich_findings
from system_fixer.money_pipeline import run_money_pipeline
from system_fixer.output_writer import write_output

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

    # 4. Severity engine (severity + rules)
    findings = run_severity_engine(findings)
    print("[pipeline] Severity engine complete")

    # 5. Intelligence enrichment
    findings = enrich_findings(findings)
    print("[pipeline] Intelligence enrichment complete")

    # 6. Money scoring + ranking (dedupe + score + sort)
    findings = run_money_pipeline(findings)
    print("[pipeline] Money pipeline complete")

    # 7. Write final output
    write_output(findings)
    print("[pipeline] Wrote processed findings")

    print("[pipeline] Pipeline complete")
    return findings
