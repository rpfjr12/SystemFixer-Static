# pipeline.py
# Full autonomous pipeline: fetch → normalize → evaluate → scan → filter → report

from program_fetcher import fetch_all_programs
from eligibility_engine import eligible
from findings_normalizer import normalize_program
from money_filter import filter_money_findings
from report_generator import generate_report

def scan_program(program):
    """
    Placeholder for your actual scanning logic.
    This function should return a list of findings.
    """
    # TODO: integrate your scanner here
    return []

def run_pipeline():
    print("[pipeline] Fetching programs...")
    programs = fetch_all_programs()

    print(f"[pipeline] {len(programs)} programs fetched.")
    print("[pipeline] Normalizing scope...")

    normalized = [normalize_program(p) for p in programs]

    print("[pipeline] Evaluating eligibility...")
    eligible_programs = [p for p in normalized if eligible(p)]

    print(f"[pipeline] {len(eligible_programs)} programs eligible for scanning.")

    for program in eligible_programs:
        name = program.get("name", "Unknown Program")
        print(f"\n[pipeline] Scanning: {name}")

        findings = scan_program(program)

        if not findings:
            print(f"[pipeline] No findings for {name}.")
            continue

        print(f"[pipeline] {len(findings)} findings detected. Applying money filter...")

        money_findings = filter_money_findings(findings)

        if not money_findings:
            print(f"[pipeline] No payout-worthy findings for {name}.")
            continue

        print(f"[pipeline] {len(money_findings)} payout-worthy findings. Generating report...")

        generate_report(program, money_findings)

    print("\n[pipeline] Completed.")
