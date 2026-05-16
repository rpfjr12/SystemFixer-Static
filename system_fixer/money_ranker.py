def rank_findings_by_money(findings):
    """
    Sorts findings by:
    1. money_score (descending)
    2. severity (fallback)
    3. title (stable tie-breaker)
    """

    def sort_key(f):
        return (
            f.get("money_score", 0) * -1,
            f.get("severity", ""),
            f.get("title", "").lower()
        )

    ranked = sorted(findings, key=sort_key)
    print(f"[money_ranker] Ranked {len(ranked)} findings by payout probability")
    return ranked
