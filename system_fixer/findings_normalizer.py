def normalize_findings(findings):
    normalized = []

    for f in findings:
        n = {
            "program": f.get("program", "Unknown Program"),
            "target": f.get("target", "Unknown Target"),
            "title": f.get("title", "Untitled Finding"),
            "description": f.get("description", ""),
            "reproduction_steps": f.get("reproduction_steps", ""),
            "impact": f.get("impact", ""),
            "severity": f.get("severity", "Unrated"),
            "exploitability_score": f.get("exploitability_score", 1),
            "raw": f  # keep original for debugging
        }
        normalized.append(n)

    print(f"[findings_normalizer] Normalized {len(normalized)} findings")
    return normalized
