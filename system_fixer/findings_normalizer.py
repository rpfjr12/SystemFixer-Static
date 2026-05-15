def normalize_finding(f):
    return {
        "issue": f.get("issue", "").strip(),
        "severity": f.get("severity", "LOW").strip(),
        "impact": f.get("impact", "").strip(),
        "description": f.get("description", "").strip(),
        "target": f.get("target", "").strip(),
        "content_type": f.get("content_type", "").strip(),
        "source": f.get("source", "module").strip()
    }
