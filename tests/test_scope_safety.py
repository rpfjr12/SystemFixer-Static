import os
import unittest
from system_fixer.scope_manager import scope_manager
from system_fixer.safety_kernel import safety_kernel
from system_fixer.intelligence_engine import intelligence_filter


class ScopeSafetyTests(unittest.TestCase):
    def test_scope_manager_allows_in_scope_target(self):
        self.assertTrue(scope_manager.is_target_in_scope("https://coinbase.com/login", "coinbase"))
        self.assertTrue(scope_manager.is_target_in_scope("https://api.coinbase.com/v2/users", "coinbase"))

    def test_scope_manager_blocks_out_of_scope_target(self):
        self.assertFalse(scope_manager.is_target_in_scope("https://example.com", "coinbase"))
        self.assertFalse(scope_manager.is_target_in_scope("https://api.unknown.com", "coinbase"))

    def test_safety_kernel_default_policy(self):
        self.assertTrue(safety_kernel.is_action_allowed("scope_check"))
        self.assertTrue(safety_kernel.is_action_allowed("passive_header_request"))
        self.assertFalse(safety_kernel.is_action_allowed("active_http_request"))
        self.assertFalse(safety_kernel.is_action_allowed("exploit_action"))

    def test_intelligence_filter_rejects_out_of_scope_finding(self):
        finding = {
            "issue": "XSS vulnerability",
            "severity": "HIGH",
            "target": "https://example.com",
            "description": "Stored XSS in comment field",
            "impact": "data exposure"
        }
        self.assertFalse(intelligence_filter(finding, "coinbase"))

    def test_intelligence_filter_accepts_valid_in_scope_finding(self):
        finding = {
            "issue": "xss",
            "severity": "HIGH",
            "target": "https://coinbase.com",
            "description": "Reflected XSS in login page",
            "impact": "sensitive data exposure"
        }
        self.assertTrue(intelligence_filter(finding, "coinbase"))


if __name__ == "__main__":
    unittest.main()
