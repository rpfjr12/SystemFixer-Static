def enrich_findings(findings):
    enriched = []

    for f in findings:
        desc = f.get("description", "").lower()
        title = f.get("title", "").lower()

        # Basic intelligence tags
        tags = []

        # Common high‑value vulnerability classes
        if "injection" in desc or "injection" in title:
            tags.append("injection")
        if "xss" in desc or "cross-site scripting" in desc:
            tags.append("xss")
        if "csrf" in desc:
            tags.append("csrf")
        if "authentication" in desc or "auth bypass" in desc:
            tags.append("auth_bypass")
        if "rce" in desc or "remote code execution" in desc:
            tags.append("rce")
        if "sqli" in desc or "sql injection" in desc:
            tags.append("sqli")
        if "exposed" in desc or "leak" in desc:
            tags.append("data_exposure")

        # Add intelligence metadata
        f["intelligence"] = {
            "tags": tags,
            "tag_count": len(tags),
            "is_high_value": len(tags) > 0
        }

        enriched.append(f)

    print(f"[intelligence_enricher] Added intelligence metadata to {len(enriched)} findings")
    return enriched
