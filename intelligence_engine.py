import json
import os
from system_fixer.severity_engine import meets_severity_threshold
from system_fixer.exploitability_engine import score_exploitability
from system_fixer.false_positive_engine import is_false_positive

RULES_PATH = "system-fixer/program_rules.json"

def load_program_rules():
    if not os.path.exists(RULES_PATH):
        return {}
    with open(RULES_PATH, "r") as f:
        return json.load(f)

def is_allowed_issue_type(issue, program):
    rules = load_program_rules()
    program_key = program.lower()
    issue = issue.lower()

    if program_key not in rules:
        return False

    allowed = rules[program_key].get("allowed_issue_types", [])
    return any(a in issue for a in allowed)

def intelligence_filter(finding, program):
    issue = finding.get("issue", "").lower()
    severity = finding.get("severity", "LOW")
    program_key = program.lower()

    # 1. Severity threshold
    if not meets_severity_threshold(program_key, severity):
        return False

    # 2. False positive detection
    if is_false_positive(finding, program_key):
        return False

    # 3. Allowed issue types
    if not is_allowed_issue_type(issue, program_key):
        return False

    # 4. Exploitability score
    score = score_exploitability(finding, program_key)
    if score < 4:
        return False

    return True
