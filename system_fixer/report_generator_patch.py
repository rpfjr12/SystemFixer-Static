from system_fixer.report_generator_integration import run_report_generation

def patched_generate_reports(findings):
    """
    Compatibility wrapper for older modules that still call
    `patched_generate_reports` instead of the new integration layer.

    This ensures the system remains stable even if older components
    haven't been updated yet.
    """
    print("[report_generator_patch] Using compatibility wrapper")
    return run_report_generation(findings)
