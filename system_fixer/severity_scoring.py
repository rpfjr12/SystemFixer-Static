def score_severity(findings):
    scored = []

    for f in findings:
        sev = f.get("severity", "").lower()

        # Normalize severity labels
        if sev in ["critical", "crit", "p1", "sev1"]:
            f["severity"] = "CRITICAL"
        elif sev in ["high", "p2", "sev2"]:
            f["severity"] = "HIGH"
        elif sev in ["medium", "med", "p3", "sev3"]:
            f["severity"] = "MEDIUM"
        elif sev in ["low", "p4", "sev4"]:
            f["severity"] = "LOW"
        else:
            f["severity"] = "UNRATED"

        scored.append(f)

    print(f"[severity_scorer] Assigned normalized severity to {len(scored)} findings")
    return scored
