import json
import os
from system_fixer.severity_engine import meets_severity_threshold
from system_fixer.exploitability_engine import score_exploitability
from system_fixer.false_positive_engine import is_false_positive
from system_fixer.scope_manager import scope_manager

BASE_DIR = os.path.dirname(__file__)
RULES_PATH = os.path.join(BASE_DIR, "program_rules.json")

def load_program_rules():
    if not os.path.exists(RULES_PATH):
        return {}
    with open(RULES_PATH, "r") as f:
        return json.load(f)

def is_allowed_issue_type(issue, program):
    rules = load_program_rules()
    program_key = program.lower()
    issue = issue.lower()

    # If there are no program-specific rules, allow issue types by default.
    # Previously this returned False which caused all findings to be rejected
    # when `program_rules.json` was missing or did not include the program.
    if program_key not in rules:
        return True

    allowed = rules[program_key].get("allowed_issue_types", [])
    return any(a in issue for a in allowed)

def intelligence_filter(finding, program):
    issue = finding.get("issue", "").lower()
    severity = finding.get("severity", "LOW")
    program_key = program.lower() if isinstance(program, str) else (program.get("id") or program.get("name") or "").lower()

    rules = load_program_rules().get(program_key, {})
    min_conf = float(rules.get("min_confidence", 0.6))
    min_payout = float(rules.get("min_payout", 0.0))

    # 0. Scope enforcement: reject findings outside declared program scope.
    if not scope_manager.is_target_in_scope(finding.get("target", ""), program_key):
        return False

    # 1. Confidence threshold to reduce noise
    confidence = float(finding.get("confidence", 1.0))
    if confidence < min_conf:
        return False

    # 2. Severity threshold
    if not meets_severity_threshold(program_key, severity):
        return False

    # 3. False positive detection
    if is_false_positive(finding, program_key):
        return False

    # 4. Allowed issue types
    if not is_allowed_issue_type(issue, program_key):
        return False

    # 5. Exploitability score and optional payout estimate filtering
    score = score_exploitability(finding, program_key)
    if score < 4:
        return False

    estimated_payout = float(finding.get("estimated_payout", 0.0))
    if estimated_payout and estimated_payout < min_payout:
        return False

    return True
