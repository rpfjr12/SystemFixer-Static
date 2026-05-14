from system_fixer.findings_loader import load_findings
from system_fixer.findings_normalizer import normalize_finding
from system_fixer.validation import is_valid_finding
from system_fixer.strict_mode import apply_strict_mode

def run_pipeline(program, findings_path):
    raw = load_findings(findings_path)
    if not raw:
        return []

    normalized = [normalize_finding(f) for f in raw if is_valid_finding(f)]
    return apply_strict_mode(program, normalized)
