def filter_for_reporting(findings):
    filtered = []

    for f in findings:
        # Must have a fingerprint
        if not f.get("fingerprint"):
            continue

        # Must have a money score
        if f.get("money_score", 0) <= 0:
            continue

        # Must have intelligence metadata
        intel = f.get("intelligence", {})
        if not intel or intel.get("tag_count", 0) == 0:
            continue

        # Must have essential fields for a report
        if not f.get("title"):
            continue
        if not f.get("description"):
            continue
        if not f.get("reproduction_steps"):
            continue
        if not f.get("impact"):
            continue

        filtered.append(f)

    print(f"[report_filter] {len(filtered)} findings passed reporting requirements")
    return filtered
