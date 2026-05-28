import os
import json

BASE_DIR = os.path.dirname(__file__)
RULES_PATH = os.path.join(BASE_DIR, "program_rules.json")

def load_program_rules():
    if not os.path.exists(RULES_PATH):
        return {}
    with open(RULES_PATH, "r") as f:
        return json.load(f)

def is_false_positive(finding, program):
    """
    Returns True if the finding should be rejected as a false positive.
    """

    issue = finding.get("issue", "").lower()
    target = finding.get("target", "").lower()
    content_type = finding.get("content_type", "").lower()
    description = finding.get("description", "").lower()

    # -------------------------
    # 1. API endpoints cannot be clickjacked or framed
    # -------------------------
    if "/api" in target or "api." in target:
        if "clickjack" in issue or "frame" in issue:
            return True

    # -------------------------
    # 2. JSON endpoints cannot have UI-based vulnerabilities
    # -------------------------
    if "json" in content_type:
        ui_keywords = ["clickjack", "frame", "csp", "xss"]
        if any(k in issue for k in ui_keywords):
            return True

    # -------------------------
    # 3. Redirect-protected endpoints
    # -------------------------
    if "redirects to login" in description:
        return True
    if "requires authentication" in description and "public" not in description:
        if "open redirect" in issue:
            return True

    # -------------------------
    # 4. Missing header noise
    # -------------------------
    header_noise = [
        "missing x-frame-options",
        "missing content-security-policy",
        "missing strict-transport-security",
        "missing x-content-type-options",
        "missing referrer-policy"
    ]
    if any(h in issue for h in header_noise):
        rules = load_program_rules()
        program_key = program.lower()
        allow_header = rules.get(program_key, {}).get("allow_header_issues", False)
        if not allow_header:
            return True

    # -------------------------
    # 5. Program-specific API filtering
    # -------------------------
    rules = load_program_rules()
    program_key = program.lower() if isinstance(program, str) else (program.get("id") or program.get("name") or "").lower()
    allow_api_findings = rules.get(program_key, {}).get("allow_api_findings", False)
    if not allow_api_findings and ("/api" in target or "api." in target):
        api_noise = ["clickjack", "frame", "csp", "xss", "csrf", "open redirect"]
        if any(k in issue for k in api_noise):
            return True

    # -------------------------
    # 6. Program-specific disallowed issue types
    # -------------------------
    if program_key in rules:
        allowed = rules[program_key].get("allowed_issue_types", [])
        if allowed and not any(a in issue for a in allowed):
            return True

    return False
