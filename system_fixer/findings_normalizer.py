def normalize_finding(f):
    issue = f.get("issue") or f.get("title") or ""
    return {
        "issue": issue.strip(),
        "severity": (f.get("severity") or "LOW").strip(),
        "impact": (f.get("impact") or "").strip(),
        "description": (f.get("description") or "").strip(),
        "target": (f.get("target") or "").strip(),
        "content_type": (f.get("content_type") or "").strip()
    }
