def is_valid_finding(f):
    required = ["issue", "severity", "impact", "description", "target"]
    return all(k in f for k in required)
