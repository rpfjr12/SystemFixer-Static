"""ROI optimizer to prioritize scanning based on historical payouts."""

import json
from pathlib import Path
from typing import Dict, List, Tuple, Any

from system_fixer.revenue_tracker import revenue_tracker
from system_fixer.scope_manager import scope_manager


class ROIOptimizer:
    """Optimizes scanning strategy based on payout history and ROI metrics."""

    def __init__(self):
        self.revenue_tracker = revenue_tracker

    def get_scan_priority_order(self, programs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Return programs ranked by expected ROI (payout per day)."""
        # Get 30-day ROI rankings
        rankings = self.revenue_tracker.rank_programs_by_roi(days=30)
        ranking_map = {prog: idx for idx, (prog, _) in enumerate(rankings)}

        # Build result with ROI scoring
        result = []
        for program in programs:
            prog_id = (program.get("id") or program.get("name") or "").lower()
            rank = ranking_map.get(prog_id, len(rankings) + 1)
            roi_value = (
                rankings[rank][1] if rank < len(rankings) else 0
            )

            program_copy = program.copy()
            program_copy["roi_ranking"] = rank + 1
            program_copy["estimated_daily_roi"] = roi_value
            program_copy["scan_priority_score"] = self._compute_priority_score(
                program, rank, roi_value
            )
            result.append(program_copy)

        # Sort by priority score descending
        return sorted(result, key=lambda p: p["scan_priority_score"], reverse=True)

    def _compute_priority_score(
        self, program: Dict[str, Any], roi_rank: int, roi_value: float
    ) -> float:
        """Compute a priority score for scanning this program."""
        # Higher ROI = higher priority
        roi_score = max(0, 100 - (roi_rank * 5))  # Rank 1 = 95, Rank 2 = 90, etc.

        # Factor in active status
        active_score = 50 if program.get("active") else 0

        # Factor in notes/potential upside (if "high payout" mentioned)
        notes = (program.get("notes") or "").lower()
        upside_score = 0
        if "high" in notes or "elite" in notes or "extreme" in notes:
            upside_score = 30
        elif "crypto" in notes or "fintech" in notes:
            upside_score = 20

        # Combine scores
        total_score = roi_score + active_score + upside_score + (roi_value / 10)
        return total_score

    def filter_by_roi_threshold(
        self, programs: List[Dict[str, Any]], min_daily_roi: float = 10.0
    ) -> List[Dict[str, Any]]:
        """Filter programs that have shown ROI above threshold in last 30 days."""
        ranked = self.get_scan_priority_order(programs)
        filtered = [p for p in ranked if p.get("estimated_daily_roi", 0) >= min_daily_roi]
        return filtered

    def get_recommended_scan_order(self, programs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get recommended scan order for maximum ROI."""
        # Start with active programs
        active = [p for p in programs if p.get("active")]

        # Rank by ROI
        ranked = self.get_scan_priority_order(active)

        # Return with recommended scan intervals based on ROI
        for program in ranked:
            roi_value = program.get("estimated_daily_roi", 0)
            if roi_value > 100:
                program["recommended_scan_interval_hours"] = 6  # High ROI: scan often
            elif roi_value > 50:
                program["recommended_scan_interval_hours"] = 12
            elif roi_value > 20:
                program["recommended_scan_interval_hours"] = 24
            else:
                program["recommended_scan_interval_hours"] = 72  # Scan weekly

        return ranked

    def estimate_expected_revenue(self, programs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Estimate expected revenue from scanning these programs."""
        ranked = self.get_scan_priority_order(programs)
        active_count = len([p for p in ranked if p.get("active")])

        daily_roi = sum(p.get("estimated_daily_roi", 0) for p in ranked)
        weekly_roi = daily_roi * 7
        monthly_roi = daily_roi * 30

        return {
            "active_programs": active_count,
            "estimated_daily_revenue": daily_roi,
            "estimated_weekly_revenue": weekly_roi,
            "estimated_monthly_revenue": monthly_roi,
            "ranked_programs": ranked,
        }

    def should_focus_on_vulnerability_type(self, vuln_type: str, days: int = 30) -> bool:
        """Determine if a vulnerability type should be prioritized based on ROI."""
        vuln_rankings = self.revenue_tracker.rank_vulnerabilities_by_roi(days)

        # Get top 3 vulnerability types
        top_vulns = vuln_rankings[:3] if len(vuln_rankings) > 0 else []
        top_vuln_names = [v[0] for v in top_vulns]

        return vuln_type in top_vuln_names

    def get_top_opportunity_areas(self) -> Dict[str, Any]:
        """Identify the best opportunities for revenue based on historical data."""
        program_roi = self.revenue_tracker.get_program_roi(30)
        vuln_roi = self.revenue_tracker.get_vulnerability_roi(30)

        top_programs = list(program_roi.items())[:3]
        top_vulns = list(vuln_roi.items())[:3]

        return {
            "top_revenue_programs": [
                {
                    "program": name,
                    "daily_roi": metrics.get("payout_per_day"),
                    "avg_payout": metrics.get("avg_payout"),
                    "count": metrics.get("count"),
                }
                for name, metrics in top_programs
            ],
            "top_vulnerability_types": [
                {
                    "vulnerability": name,
                    "daily_roi": metrics.get("payout_per_day"),
                    "avg_payout": metrics.get("avg_payout"),
                    "count": metrics.get("count"),
                }
                for name, metrics in top_vulns
            ],
        }


roi_optimizer = ROIOptimizer()
