def apply_money_filter(findings, min_score=0):
    """Filter findings by money_score threshold."""
    filtered = []
    for f in findings:
        score = f.get("money_score", 0)
        if score >= min_score:
            filtered.append(f)
    return filtered
