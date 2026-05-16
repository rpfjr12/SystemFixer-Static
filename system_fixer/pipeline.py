def run_pipeline():
    print("[pipeline] Starting unified analysis pipeline...")

    findings = load_findings()
    print(f"[pipeline] Loaded {len(findings)} raw findings")

    findings = normalize_findings(findings)
    print("[pipeline] Normalized findings")

    findings = filter_false_positives(findings)
    print("[pipeline] Filtered false positives")

    findings = score_severity(findings)
    print("[pipeline] Scored severity")

    findings = enrich_findings(findings)
    print("[pipeline] Enriched findings with intelligence")

    write_output(findings)
    print("[pipeline] Wrote processed findings")

    print("[pipeline] Pipeline complete")
