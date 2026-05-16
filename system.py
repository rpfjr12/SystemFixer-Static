import json
import subprocess
import os
from datetime import datetime

# === PATHS ===
PROGRAMS_FILE = "programs.json"
SCANNER_SCRIPT = "scanner/scan.py"
REPORT_GENERATOR = "report_generator.py"
DASHBOARD_REGEN = "dashboard/regenerator.py"
DATA_DIR = "data"
REPORTS_DIR = "reports"

def load_programs():
    with open(PROGRAMS_FILE, "r") as f:
        return json.load(f)

def run_scanner():
    print("[1] Running scanner...")
    subprocess.run(["python3", SCANNER_SCRIPT], check=True)

def run_analysis_pipeline():
    print("[2] Running analysis pipeline...")
    subprocess.run(["python3", "-m", "system_fixer.pipeline"], check=True)

def generate_reports():
    print("[3] Generating Markdown reports...")
    subprocess.run(["python3", REPORT_GENERATOR], check=True)

def update_dashboard():
    print("[4] Updating dashboard...")
    subprocess.run(["python3", DASHBOARD_REGEN], check=True)

def commit_results():
    print("[5] Committing results to GitHub...")
    subprocess.run(["git", "add", "."], check=True)
    subprocess.run(["git", "commit", "-m", f"Automated scan results {datetime.now()}"], check=False)
    subprocess.run(["git", "push"], check=False)

def main():
    print("=== Autonomous Bug Bounty System ===")

    programs = load_programs()
    print(f"Loaded {len(programs)} programs.")

    run_scanner()
    run_analysis_pipeline()
    generate_reports()
    update_dashboard()
    commit_results()

    print("=== System run complete ===")

if __name__ == "__main__":
    main()
