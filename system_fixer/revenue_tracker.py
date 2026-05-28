"""Revenue and ROI tracker for autonomous payout optimization."""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta

BASE_DIR = Path(__file__).resolve().parent.parent
REVENUE_DIR = BASE_DIR / "revenue_data"
REVENUE_DIR.mkdir(exist_ok=True)

PAYOUT_HISTORY = REVENUE_DIR / "payout_history.jsonl"
PROGRAM_ROI = REVENUE_DIR / "program_roi.json"
VULNERABILITY_ROI = REVENUE_DIR / "vulnerability_roi.json"


class RevenueTracker:
    """Track payouts and compute ROI for autonomous revenue optimization."""

    def __init__(self):
        self.payout_history = []
        self._load_history()

    def _load_history(self):
        """Load payout history from disk."""
        if PAYOUT_HISTORY.exists():
            with open(PAYOUT_HISTORY, "r") as f:
                for line in f:
                    if line.strip():
                        self.payout_history.append(json.loads(line))

    def record_payout(
        self,
        program_id: str,
        vulnerability_type: str,
        payout_amount: float,
        severity: str,
        time_to_acceptance_hours: float,
        submission_id: str = None,
    ):
        """Record a confirmed payout."""
        entry = {
            "timestamp": int(time.time()),
            "iso_date": datetime.utcnow().isoformat(),
            "program_id": program_id,
            "vulnerability_type": vulnerability_type,
            "payout": float(payout_amount),
            "severity": severity,
            "time_to_acceptance_hours": float(time_to_acceptance_hours),
            "submission_id": submission_id,
        }
        self.payout_history.append(entry)

        # Append to history file
        with open(PAYOUT_HISTORY, "a") as f:
            f.write(json.dumps(entry) + "\n")

        return entry

    def get_program_roi(self, days: int = 30) -> Dict[str, Dict[str, Any]]:
        """Compute ROI metrics per program over the last N days."""
        cutoff = int(time.time()) - (days * 86400)
        recent = [h for h in self.payout_history if h["timestamp"] >= cutoff]

        roi_map = {}
        for entry in recent:
            prog = entry["program_id"]
            if prog not in roi_map:
                roi_map[prog] = {
                    "count": 0,
                    "total_payout": 0,
                    "avg_payout": 0,
                    "avg_hours_to_accept": 0,
                    "payout_per_day": 0,
                    "severity_breakdown": {},
                }
            roi_map[prog]["count"] += 1
            roi_map[prog]["total_payout"] += entry["payout"]
            roi_map[prog]["avg_hours_to_accept"] += entry["time_to_acceptance_hours"]

            sev = entry.get("severity", "UNKNOWN")
            if sev not in roi_map[prog]["severity_breakdown"]:
                roi_map[prog]["severity_breakdown"][sev] = {"count": 0, "total": 0}
            roi_map[prog]["severity_breakdown"][sev]["count"] += 1
            roi_map[prog]["severity_breakdown"][sev]["total"] += entry["payout"]

        # Finalize calculations
        for prog, metrics in roi_map.items():
            if metrics["count"] > 0:
                metrics["avg_payout"] = metrics["total_payout"] / metrics["count"]
                metrics["avg_hours_to_accept"] = (
                    metrics["avg_hours_to_accept"] / metrics["count"]
                )
                metrics["payout_per_day"] = (
                    metrics["total_payout"] / days
                )  # Average per day

        # Sort by payout per day descending (highest ROI programs first)
        return dict(
            sorted(
                roi_map.items(),
                key=lambda x: x[1]["payout_per_day"],
                reverse=True,
            )
        )

    def get_vulnerability_roi(self, days: int = 30) -> Dict[str, Dict[str, Any]]:
        """Compute ROI metrics per vulnerability type over the last N days."""
        cutoff = int(time.time()) - (days * 86400)
        recent = [h for h in self.payout_history if h["timestamp"] >= cutoff]

        roi_map = {}
        for entry in recent:
            vuln_type = entry["vulnerability_type"]
            if vuln_type not in roi_map:
                roi_map[vuln_type] = {
                    "count": 0,
                    "total_payout": 0,
                    "avg_payout": 0,
                    "avg_hours_to_accept": 0,
                    "payout_per_day": 0,
                    "programs": {},
                }
            roi_map[vuln_type]["count"] += 1
            roi_map[vuln_type]["total_payout"] += entry["payout"]
            roi_map[vuln_type]["avg_hours_to_accept"] += (
                entry["time_to_acceptance_hours"]
            )

            prog = entry["program_id"]
            if prog not in roi_map[vuln_type]["programs"]:
                roi_map[vuln_type]["programs"][prog] = {"count": 0, "total": 0}
            roi_map[vuln_type]["programs"][prog]["count"] += 1
            roi_map[vuln_type]["programs"][prog]["total"] += entry["payout"]

        # Finalize calculations
        for vuln_type, metrics in roi_map.items():
            if metrics["count"] > 0:
                metrics["avg_payout"] = metrics["total_payout"] / metrics["count"]
                metrics["avg_hours_to_accept"] = (
                    metrics["avg_hours_to_accept"] / metrics["count"]
                )
                metrics["payout_per_day"] = (
                    metrics["total_payout"] / days
                )  # Average per day

        # Sort by payout per day descending (highest ROI vulnerabilities first)
        return dict(
            sorted(
                roi_map.items(),
                key=lambda x: x[1]["payout_per_day"],
                reverse=True,
            )
        )

    def rank_programs_by_roi(self, days: int = 30) -> List[Tuple[str, float]]:
        """Return programs ranked by payout_per_day (ROI). Highest first."""
        roi = self.get_program_roi(days)
        return [(prog, metrics["payout_per_day"]) for prog, metrics in roi.items()]

    def rank_vulnerabilities_by_roi(self, days: int = 30) -> List[Tuple[str, float]]:
        """Return vulnerability types ranked by payout_per_day (ROI). Highest first."""
        roi = self.get_vulnerability_roi(days)
        return [(vuln, metrics["payout_per_day"]) for vuln, metrics in roi.items()]

    def save_roi_reports(self):
        """Save ROI reports to disk for dashboard."""
        program_roi = self.get_program_roi(30)
        vuln_roi = self.get_vulnerability_roi(30)

        with open(PROGRAM_ROI, "w") as f:
            json.dump(program_roi, f, indent=2)

        with open(VULNERABILITY_ROI, "w") as f:
            json.dump(vuln_roi, f, indent=2)

        return {"program_roi": program_roi, "vuln_roi": vuln_roi}


revenue_tracker = RevenueTracker()
