import json
import os
import tempfile
import unittest
from pathlib import Path

from system_fixer.scheduler import AutonomousScheduler


class SchedulerTests(unittest.TestCase):
    def make_programs(self, path):
        programs = [
            {
                "id": "coinbase",
                "name": "Coinbase",
                "platform": "HackerOne",
                "scope": ["https://coinbase.com"],
                "active": True,
                "added": "2026-05-14",
                "notes": "Test program",
            }
        ]
        with open(path, "w") as fh:
            json.dump(programs, fh)

    def make_data_file(self, path, issue, payout=100, severity="HIGH"):
        finding = [
            {
                "issue": issue,
                "severity": severity,
                "target": "https://coinbase.com",
                "description": "Test",
                "impact": "sensitive data exposure",
                "estimated_payout": payout,
                "confidence": 0.9,
            }
        ]
        with open(path, "w") as fh:
            json.dump(finding, fh)

    def test_scheduler_processes_pending_tasks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = os.path.join(temp_dir, "data")
            reports_dir = os.path.join(temp_dir, "reports")
            os.makedirs(data_dir)
            os.makedirs(reports_dir)
            programs_path = os.path.join(temp_dir, "programs.json")
            state_path = os.path.join(temp_dir, "autonomous_state.json")
            self.make_programs(programs_path)
            self.make_data_file(os.path.join(data_dir, "coinbase-2026-05-28.json"), "XSS in login", payout=500)

            scheduler = AutonomousScheduler(
                config={"interval_seconds": 1, "max_tasks_per_cycle": 1, "queue_backpressure_threshold": 10},
                data_dir=data_dir,
                reports_dir=reports_dir,
                programs_path=programs_path,
                state_path=state_path,
            )

            processed = scheduler.run_once()
            self.assertEqual(processed, 1)
            self.assertTrue(any(fname.endswith(".md") for fname in os.listdir(reports_dir)))
            with open(state_path, "r") as fh:
                state = json.load(fh)
            self.assertIn(os.path.join(data_dir, "coinbase-2026-05-28.json"), state["processed_files"])

    def test_scheduler_backpressure_and_queue_limit(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            data_dir = os.path.join(temp_dir, "data")
            reports_dir = os.path.join(temp_dir, "reports")
            os.makedirs(data_dir)
            os.makedirs(reports_dir)
            programs_path = os.path.join(temp_dir, "programs.json")
            state_path = os.path.join(temp_dir, "autonomous_state.json")
            self.make_programs(programs_path)
            self.make_data_file(os.path.join(data_dir, "coinbase-1.json"), "XSS", payout=1000)
            self.make_data_file(os.path.join(data_dir, "coinbase-2.json"), "Open redirect", payout=2000)
            self.make_data_file(os.path.join(data_dir, "coinbase-3.json"), "HSTS missing", payout=10, severity="MEDIUM")

            scheduler = AutonomousScheduler(
                config={"interval_seconds": 1, "max_tasks_per_cycle": 1, "queue_backpressure_threshold": 2},
                data_dir=data_dir,
                reports_dir=reports_dir,
                programs_path=programs_path,
                state_path=state_path,
            )

            processed = scheduler.run_once()
            self.assertEqual(processed, 1)
            self.assertEqual(len(os.listdir(reports_dir)), 1)
            with open(state_path, "r") as fh:
                state = json.load(fh)
            self.assertEqual(len(state["processed_files"]), 1)


if __name__ == "__main__":
    unittest.main()
