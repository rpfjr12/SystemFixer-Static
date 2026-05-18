def apply_money_filter(findings, min_score=0):
    """
    Filter a list of finding dictionaries based on:
    - trusted source engines
    - minimum money score
    - severity threshold
    """

    TRUSTED_ENGINES = {
        "idor_engine",
        "ssrf_engine",
        "auth_bypass_engine",
        "rate_limit_engine",
        "sensitive_data_engine",
        "jwt_engine",
    }

    SEVERITY_ORDER = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}

    filtered = []

    for f in findings:
        engine = f.get("engine")
        score = f.get("money_score", 0)
        severity = f.get("severity", "").upper()

        # Must come from a trusted engine
        if engine not in TRUSTED_ENGINES:
            continue

        # Must meet minimum score
        if score < min_score:
            continue

        # Must meet severity threshold
        if SEVERITY_ORDER.get(severity, 0) < SEVERITY_ORDER["MEDIUM"]:
            continue

        filtered.append(f)

    return filtered
