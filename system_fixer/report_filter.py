from system_fixer.exploitability_engine import score_exploitability
from system_fixer.intelligence_engine import intelligence_filter
from system_fixer.severity_engine import severity_value


def _normalize_dedupe_key(finding):
    return (
        finding.get("issue", "").strip().lower(),
        finding.get("target", "").strip().lower(),
        finding.get("severity", "").strip().upper(),
        finding.get("description", "").strip().lower(),
    )


def _normalize_program_key(program):
    if isinstance(program, str):
        return program.lower()
    return (program.get("id") or program.get("name") or "").lower()


def _priority_score(finding, program):
    severity_score = severity_value(finding.get("severity", "LOW"))
    exploit_score = score_exploitability(finding, _normalize_program_key(program))
    payout = float(finding.get("estimated_payout", 0) or 0)
    confidence = float(finding.get("confidence", 1.0) or 1.0)

    # Weight severity and exploitability heavily, but still promote real payouts.
    score = (severity_score * 10) + (exploit_score * 2) + min(payout / 100.0, 20)
    score *= confidence
    return score


def filter_findings(findings, program):
    dedupe_map = {}

    for finding in findings:
        if not intelligence_filter(finding, program):
            continue

        key = _normalize_dedupe_key(finding)
        score = _priority_score(finding, program)
        existing = dedupe_map.get(key)

        if existing is None or score > existing[0]:
            dedupe_map[key] = (score, finding)

    ordered = sorted(dedupe_map.values(), key=lambda item: item[0], reverse=True)
    return [item[1] for item in ordered]
