def apply_money_filter(findings, min_score=0):
    """Keep ONLY auto-verifiable, payout-worthy findings."""

    AUTO_ENGINES = {
        "idor_engine",
        "ssrf_engine",
        "auth_bypass_engine",
        "rate_limit_engine",
        "sensitive_data_engine",
        "jwt_engine"
    }

    filtered = []

    for f in findings:
        engine = f.get("engine")
        score = f.get("money_score", 0)
        severity = f.get("severity", "").upper()

        # Must come from an auto-verifiable engine
        if engine not in AUTO_ENGINES:
            continue

        # Must meet minimum money score
        if score < min_score:
            continue

        # Must be MEDIUM/HIGH/CRITICAL
        if severity not in ["MEDIUM", "HIGH", "CRITICAL"]:
            continue

        filtered.append(f)

    return filtered
