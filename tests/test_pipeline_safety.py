import os
import json
import tempfile
import unittest
from pathlib import Path

from system_fixer.learning import learning_engine
from system_fixer.report_filter import filter_findings
from system_fixer.safety_kernel import safety_kernel
from system_fixer.scope_manager import scope_manager


class PipelineSafetyTests(unittest.TestCase):
    def test_scope_manager_is_immutable(self):
        with self.assertRaises(TypeError):
            scope_manager._programs["new_program"] = None

    def test_safety_kernel_manual_approval(self):
        original_env = os.environ.get("SYSTEM_FIXER_MANUAL_APPROVALS")
        os.environ["SYSTEM_FIXER_MANUAL_APPROVALS"] = "active_http_request"
        try:
            # Reload a new SafetyKernel instance by importing module fresh
            from importlib import reload
            import system_fixer.safety_kernel as safety_mod
            safety_mod.safety_kernel = safety_mod.SafetyKernel()
            self.assertTrue(safety_mod.safety_kernel.is_action_allowed("active_http_request"))
        finally:
            if original_env is None:
                os.environ.pop("SYSTEM_FIXER_MANUAL_APPROVALS", None)
            else:
                os.environ["SYSTEM_FIXER_MANUAL_APPROVALS"] = original_env

    def test_filter_findings_dedupes_same_issue_target(self):
        program = "coinbase"
        findings = [
            {
                "issue": "XSS in login form",
                "severity": "HIGH",
                "target": "https://coinbase.com/login",
                "description": "Stored XSS",
                "impact": "sensitive data exposure",
                "estimated_payout": 1200,
                "confidence": 0.95,
            },
            {
                "issue": "XSS in login form",
                "severity": "HIGH",
                "target": "https://coinbase.com/login",
                "description": "Stored XSS",
                "impact": "sensitive data exposure",
                "estimated_payout": 500,
                "confidence": 0.50,
            },
        ]

        filtered = filter_findings(findings, program)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["estimated_payout"], 1200)

    def test_filter_findings_sorts_by_priority(self):
        program = "coinbase"
        findings = [
            {
                "issue": "Open redirect",
                "severity": "HIGH",
                "target": "https://coinbase.com/redirect",
                "description": "Open redirect on return_url",
                "impact": "sensitive data exposure",
                "estimated_payout": 900,
                "confidence": 0.9,
            },
            {
                "issue": "Missing HSTS",
                "severity": "MEDIUM",
                "target": "https://coinbase.com",
                "description": "Missing Strict-Transport-Security",
                "impact": "security header missing",
                "estimated_payout": 50,
                "confidence": 0.8,
            },
        ]

        filtered = filter_findings(findings, program)
        self.assertGreaterEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["issue"].lower(), "open redirect")

    def test_learning_engine_records_and_rolls_back(self):
        original_env = os.environ.get("SYSTEM_FIXER_MANUAL_APPROVALS")
        os.environ["SYSTEM_FIXER_MANUAL_APPROVALS"] = "learning_write"
        with tempfile.TemporaryDirectory() as temp_dir:
            base = Path(temp_dir)
            model_dir = base / "learning_models"
            model_dir.mkdir()
            import importlib
            import system_fixer.learning as learning_mod
            import system_fixer.safety_kernel as safety_mod
            safety_mod = importlib.reload(safety_mod)
            learning_mod.safety_kernel = safety_mod.safety_kernel
            original_model_dir = learning_mod.MODEL_DIR
            learning_mod.MODEL_DIR = model_dir
            try:
                engine = learning_mod.LearningEngine()
                program = {"id": "coinbase", "name": "Coinbase"}
                finding = {
                    "issue": "Open redirect",
                    "severity": "HIGH",
                    "target": "https://coinbase.com/redirect",
                }
                result = engine.record_validation(finding, program, payout_amount=1500, validator="test")
                self.assertTrue(result)
                models = engine.list_models()
                self.assertIn("model-1.json", models)
                engine.rollback_to("model-1.json")
                self.assertTrue((model_dir / "current.json").exists())
            finally:
                learning_mod.MODEL_DIR = original_model_dir
                if original_env is None:
                    os.environ.pop("SYSTEM_FIXER_MANUAL_APPROVALS", None)
                else:
                    os.environ["SYSTEM_FIXER_MANUAL_APPROVALS"] = original_env

    def test_orchestrator_runs_with_no_data(self):
        import importlib
        import system_fixer.orchestrator as orchestrator

        with tempfile.TemporaryDirectory() as temp_dir:
            original_data = orchestrator.DATA_DIR
            original_reports = orchestrator.REPORTS_DIR
            original_programs = orchestrator.PROGRAMS_PATH
            orchestrator.DATA_DIR = temp_dir
            orchestrator.REPORTS_DIR = os.path.join(temp_dir, "reports")
            orchestrator.PROGRAMS_PATH = os.path.join(temp_dir, "programs.json")

            with open(orchestrator.PROGRAMS_PATH, "w") as fh:
                json.dump([], fh)

            processed = orchestrator.orchestrate_reports()
            self.assertEqual(processed.get("processed"), 0)

            orchestrator.DATA_DIR = original_data
            orchestrator.REPORTS_DIR = original_reports
            orchestrator.PROGRAMS_PATH = original_programs


if __name__ == "__main__":
    unittest.main()
