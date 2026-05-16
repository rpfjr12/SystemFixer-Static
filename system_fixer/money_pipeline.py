from system_fixer.money_filter import apply_money_filter
from system_fixer.money_ranker import rank_findings_by_money

def run_money_pipeline(findings, min_score=20):
    """
    Full money scoring pipeline:
    1. Apply money filter (dedupe + scoring + threshold)
    2. Rank remaining findings by payout probability
    3. Return clean, sorted list
    """

    print("[money_pipeline] Running money scoring pipeline...")

    filtered = apply_money_filter(findings, min_score=min_score)
    print(f"[money_pipeline] {len(filtered)} findings passed money filter")

    ranked = rank_findings_by_money(filtered)
    print("[money_pipeline] Ranking complete")

    print("[money_pipeline] Money pipeline complete")
    return ranked
