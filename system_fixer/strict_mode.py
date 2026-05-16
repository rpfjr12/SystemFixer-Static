def enforce_strict_mode(findings):
    strict = []

    for f in findings:
        # Must have essential fields
        if not f.get("program"):
            continue
        if not f.get("target"):
            continue
        if not f.get("title"):
            continue
        if not f.get("description"):
            continue
        if not f.get("reproduction_steps"):
            continue
        if not f.get("impact"):
            continue

        # Must have severity assigned
        if f.get("severity") in [None, "", "UNRATED"]:
            continue

        # Must have intelligence metadata
        intel = f.get("intelligence", {})
        if not intel or intel.get("tag_count", 0) == 0:
            continue

        # Must have a money score
        if f.get("money_score", 0) <= 0:
            continue

        # Must not be excluded by rules
        if f.get("excluded_by_rules"):
            continue

        strict.append(f)

    print(f"[strict_mode] {len(strict)} findings passed strict mode")
    return strict
