"""Report queue and submission formatter for bounty platform integration."""

import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
QUEUE_DIR = BASE_DIR / "submission_queue"
QUEUE_DIR.mkdir(exist_ok=True)

SUBMISSION_LOG = QUEUE_DIR / "submissions.jsonl"
QUEUED_FINDINGS = QUEUE_DIR / "queued.json"


class ReportQueue:
    """Manages findings queued for submission to bounty platforms."""

    def __init__(self):
        self.queued = []
        self.submitted = []
        self._load_state()

    def _load_state(self):
        """Load queued findings from disk."""
        if QUEUED_FINDINGS.exists():
            with open(QUEUED_FINDINGS, "r") as f:
                data = json.load(f)
                self.queued = data.get("queued", [])

        if SUBMISSION_LOG.exists():
            with open(SUBMISSION_LOG, "r") as f:
                for line in f:
                    if line.strip():
                        self.submitted.append(json.loads(line))

    def _save_state(self):
        """Persist queue to disk."""
        with open(QUEUED_FINDINGS, "w") as f:
            json.dump({"queued": self.queued}, f, indent=2)

    def _generate_submission_id(self, program_id: str, finding_hash: str) -> str:
        """Generate unique submission ID."""
        key = f"{program_id}:{finding_hash}:{int(time.time())}"
        return hashlib.sha256(key.encode()).hexdigest()[:12]

    def enqueue_finding(
        self,
        program: Dict[str, Any],
        finding: Dict[str, Any],
        priority_score: float = 1.0,
    ):
        """Add a finding to the submission queue."""
        # Compute hash to detect duplicates
        finding_key = (
            finding.get("issue", ""),
            finding.get("target", ""),
            finding.get("severity", ""),
            finding.get("description", "")[:100],
        )
        finding_hash = hashlib.md5(
            str(finding_key).encode()
        ).hexdigest()

        # Check if already queued
        for queued in self.queued:
            if queued["finding_hash"] == finding_hash and queued["program_id"] == program.get("id"):
                return None  # Already queued

        submission_id = self._generate_submission_id(program.get("id", ""), finding_hash)

        entry = {
            "submission_id": submission_id,
            "timestamp": int(time.time()),
            "iso_date": datetime.utcnow().isoformat(),
            "program_id": program.get("id"),
            "program_name": program.get("name"),
            "platform": program.get("platform"),
            "priority_score": float(priority_score),
            "finding": finding,
            "finding_hash": finding_hash,
            "status": "queued",  # queued, submitted, accepted, paid, rejected
            "formatted_payload": None,
            "submission_timestamp": None,
        }

        self.queued.append(entry)
        self._save_state()
        return entry

    def get_next_submissions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get the top N queued findings sorted by priority."""
        queued_only = [f for f in self.queued if f["status"] == "queued"]
        sorted_findings = sorted(
            queued_only, key=lambda x: x["priority_score"], reverse=True
        )
        return sorted_findings[:limit]

    def format_for_hackerone(self, finding: Dict[str, Any], program: Dict[str, Any]) -> str:
        """Format finding as HackerOne submission."""
        issue = finding.get("issue", "N/A")
        target = finding.get("target", "N/A")
        severity = finding.get("severity", "UNKNOWN")
        description = finding.get("description", "")
        impact = finding.get("impact", "Unauthorized access or data exposure.")
        steps = finding.get("steps_to_reproduce", f"1. Request {target}\n2. Analyze response headers")
        proof = finding.get("proof_of_concept", "See step reproduction.")

        payload = f"""**Title:** {issue}

**Severity:** {severity}

**Affected URL(s):** {target}

**Vulnerability Description:**
{description}

**Steps to Reproduce:**
{steps}

**Impact:**
{impact}

**Proof of Concept:**
{proof}

---
*Submitted by autonomous vulnerability scanner - {datetime.utcnow().isoformat()}*"""

        return payload

    def format_for_bugcrowd(self, finding: Dict[str, Any], program: Dict[str, Any]) -> str:
        """Format finding as Bugcrowd submission."""
        issue = finding.get("issue", "N/A")
        target = finding.get("target", "N/A")
        severity = finding.get("severity", "UNKNOWN")
        description = finding.get("description", "")
        impact = finding.get("impact", "Unauthorized access or data exposure.")

        payload = f"""**Issue:** {issue}
**Severity:** {severity}
**Target:** {target}

**Description:**
{description}

**Impact:**
{impact}

---
*Autonomous scanner submission - {datetime.utcnow().isoformat()}*"""

        return payload

    def mark_submitted(self, submission_id: str) -> bool:
        """Mark a submission as submitted to the platform."""
        for entry in self.queued:
            if entry["submission_id"] == submission_id:
                entry["status"] = "submitted"
                entry["submission_timestamp"] = int(time.time())

                # Log to submission history
                with open(SUBMISSION_LOG, "a") as f:
                    f.write(json.dumps(entry) + "\n")

                self._save_state()
                return True
        return False

    def mark_accepted(self, submission_id: str) -> bool:
        """Mark a submission as accepted by the program."""
        for entry in self.queued:
            if entry["submission_id"] == submission_id:
                entry["status"] = "accepted"
                self._save_state()
                return True
        return False

    def mark_paid(self, submission_id: str, payout_amount: float) -> bool:
        """Mark a submission as paid."""
        for entry in self.queued:
            if entry["submission_id"] == submission_id:
                entry["status"] = "paid"
                entry["payout_amount"] = float(payout_amount)
                entry["paid_timestamp"] = int(time.time())
                self._save_state()
                return True
        return False

    def get_queue_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        statuses = {}
        total_estimated_value = 0

        for entry in self.queued:
            status = entry.get("status", "unknown")
            statuses[status] = statuses.get(status, 0) + 1
            finding = entry.get("finding", {})
            estimated_payout = float(finding.get("estimated_payout", 0) or 0)
            total_estimated_value += estimated_payout

        return {
            "total_queued": len(self.queued),
            "status_breakdown": statuses,
            "total_estimated_value": total_estimated_value,
            "queued_count": len([f for f in self.queued if f["status"] == "queued"]),
            "submitted_count": len([f for f in self.queued if f["status"] == "submitted"]),
            "accepted_count": len([f for f in self.queued if f["status"] == "accepted"]),
            "paid_count": len([f for f in self.queued if f["status"] == "paid"]),
        }

    def export_for_manual_submission(self) -> Dict[str, List[Dict[str, Any]]]:
        """Export queued findings organized by platform for manual submission."""
        by_platform = {}
        for entry in self.queued:
            if entry["status"] == "queued":
                platform = entry.get("platform", "Unknown")
                if platform not in by_platform:
                    by_platform[platform] = []
                by_platform[platform].append(entry)
        return by_platform


report_queue = ReportQueue()
