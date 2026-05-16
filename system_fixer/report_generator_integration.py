from system_fixer.report_filter import filter_for_reporting
from system_fixer.report_generator import generate_reports

def run_report_generation(findings):
    print("[report_generator_integration] Starting report generation pipeline...")

    # Filter findings to only those eligible for reporting
    filtered = filter_for_reporting(findings)
    print(f"[report_generator_integration] {len(filtered)} findings eligible for reporting")

    # Generate payout-ready Markdown reports
    generate_reports(filtered)

    print("[report_generator_integration] Report generation complete")
    return filtered
