import json
import os

RULES_PATH = "system-fixer/program_rules.json"

def load_program_rules():
    """
    Load program-specific rules from JSON.
    If the file does not exist, return an empty ruleset.
    """
    if not os.path.exists(RULES_PATH):
        return {}

    with open(RULES_PATH, "r") as f:
        return json.load(f)


def severity_value(sev):
    """
    Convert severity labels to numeric values for comparison.
    """
    sev = sev.upper()
    mapping = {
        "CRITICAL": 4,
        "HIGH": 3,
        "MEDIUM": 2,
        "LOW": 1,
        "INFO": 0
    }
    return mapping.get(sev, 0)


def meets_severity_threshold(program, severity):
    """
    Check if a finding meets the minimum severity required by the program.
    Default strict mode: MEDIUM+
    """
    rules = load_program_rules()
    program_key = program.lower()

    if program_key not in rules:
        return severity_value(severity) >= severity_value("MEDIUM")

    min_required = rules[program_key].get("min_severity", "MEDIUM")
    return severity_value(severity) >= severity_value(min_required)


def is_allowed_issue_type(program, issue_type):
    """
    Check if a finding's issue type is allowed for the program.
    If no rules exist, allow all issue types.
    """
    rules = load_program_rules()
    program_key = program.lower()

    if program_key not in rules:
        return True

    allowed = rules[program_key].get("allowed_issue_types", [])
    if not allowed:
        return True

    return issue_type.lower() in [a.lower() for a in allowed]


def apply_program_rules(program, findings):
    """
    Apply all program-specific rules to a list of findings.
    Filters out findings that do not meet severity or issue-type requirements.
    """
    filtered = []

    for f in findings:
        sev = f.get("severity", "LOW")
        issue_type = f.get("type", "unknown")

        if not meets_severity_threshold(program, sev):
            continue

        if not is_allowed_issue_type(program, issue_type):
            continue

        filtered.append(f)

    return filtered
