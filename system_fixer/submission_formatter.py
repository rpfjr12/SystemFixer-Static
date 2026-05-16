def format_submission(finding):
    """
    Produces a clean, platform-ready submission text block
    for HackerOne, Bugcrowd, Intigriti, etc.
    """

    title = finding.get("title", "Untitled Finding")
    target = finding.get("target", "Unknown Target")
    severity = finding.get("severity", "UNRATED")
    impact = finding.get("impact", "")
    repro = finding.get("reproduction_steps", "")
    description = finding.get("description", "")
    tags = finding.get("intelligence", {}).get("tags", [])
    money_score = finding.get("money_score", 0)

    submission = f"""
# {title}

**Target:** {target}  
**Severity:** {severity}  
**Money Score:** {money_score}  
**Tags:** {", ".join(tags) if tags else "None"}

---

## Summary
{description}

---

## Impact
{impact}

---

## Steps to Reproduce
{repro}

---

## Additional Notes
- Automatically enriched by internal analysis engine
- Intelligence tags applied: {", ".join(tags) if tags else "None"}
- Money score used for prioritization: {money_score}
"""

    return submission.strip()
