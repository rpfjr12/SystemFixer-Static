# eligibility_engine.py
# Decides if a program should be scanned based on rules, scope, and automation permissions.

def automation_allowed(rules):
    text = rules.lower()
    forbidden = [
        "no automated testing",
        "automation prohibited",
        "automated scanning not allowed",
        "automated tools are forbidden",
        "no scanners",
        "no fuzzing",
        "no brute force"
    ]
    return not any(x in text for x in forbidden)

def methods_allowed(rules, required_methods):
    text = rules.lower()
    for method in required_methods:
        if f"no {method}" in text or f"{method} not allowed" in text:
            return False
    return True

def scope_valid(scope):
    if not scope:
        return False
    cleaned = [s for s in scope if "*" not in s and "out of scope" not in s.lower()]
    return len(cleaned) > 0

def payout_potential(program):
    reward = program.get("max_reward", 0)
    return reward >= 500  # adjust threshold if needed

def eligible(program):
    rules = program.get("rules", "")
    scope = program.get("scope", [])

    if not automation_allowed(rules):
        return False

    required_methods = [
        "ssrf",
        "idor",
        "rate limit",
        "auth bypass",
        "jwt",
        "sensitive data"
    ]

    if not methods_allowed(rules, required_methods):
        return False

    if not scope_valid(scope):
        return False

    if not payout_potential(program):
        return False

    return True
