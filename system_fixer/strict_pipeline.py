from system_fixer.findings_loader import load_findings
from system_fixer.findings_normalizer import normalize_findings
from system_fixer.false_positive_filter import filter_false_positives
from system_fixer.severity_engine import run_severity_engine
from system_fixer.intelligence_enricher import enrich_findings
from system_fixer.money_pipeline import run_money_pipeline
from system_fixer.output_writer import write_output

def run_strict_pipeline(min_money_score=40):
    print("[strict_pipeline] Starting STRICT analysis pipeline...")

    # 1. Load raw findings
    findings = load_findings()
    print(f"[strict_pipeline] Loaded {len(findings)} raw findings")

    # 2. Normalize structure
    findings = normalize_findings(findings)
    print("[strict_pipeline] Normalized findings")

    # 3. Remove false positives aggressively
    findings = filter_false_positives(findings)
    print("[strict_pipeline] Filtered false positives")

    # 4. Severity engine (severity + rules)
    findings = run_severity_engine(findings)
    print("[strict_pipeline] Severity engine complete")

    # 5. Intelligence enrichment
    findings = enrich_findings(findings)
    print("[strict_pipeline] Intelligence enrichment complete")

    # 6. Money scoring + ranking with STRICT threshold
    findings = run_money_pipeline(findings, min_score=min_money_score)
    print("[strict_pipeline] Money pipeline complete (STRICT mode)")

    # 7. Write final output
    write_output(findings)
    print("[strict_pipeline] Wrote STRICT processed findings")

    print("[strict_pipeline] STRICT pipeline complete")
    return findings
