def filter_false_positives(findings):
    filtered = []

    for f in findings:
        title = f.get("title", "").lower()
        desc = f.get("description", "").lower()

        # Basic noise filters — these are ALWAYS junk
        if "test" in title and "example" in desc:
            continue
        if "dummy" in title or "placeholder" in title:
            continue
        if "no vulnerability" in desc:
            continue
        if "scanner error" in desc:
            continue

        # Skip findings missing essential fields
        if not f.get("target"):
            continue
        if not f.get("title"):
            continue

        filtered.append(f)

    print(f"[false_positive_filter] Removed {len(findings) - len(filtered)} false positives")
    return filtered
