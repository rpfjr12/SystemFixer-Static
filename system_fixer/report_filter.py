from system_fixer.intelligence_engine import intelligence_filter

def filter_findings(findings, program):
    filtered = []
    for f in findings:
        if intelligence_filter(f, program):
            filtered.append(f)
    return filtered
