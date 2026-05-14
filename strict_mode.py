from system_fixer.report_filter import filter_findings

def apply_strict_mode(program, findings):
    return filter_findings(findings, program)
