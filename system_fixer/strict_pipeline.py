from system_fixer.loader import load_json
from system_fixer.strict_mode import apply_strict_mode

def run_strict_pipeline(program, findings_path):
    findings = load_json(findings_path)
    if not findings:
        return []

    return apply_strict_mode(program, findings)
