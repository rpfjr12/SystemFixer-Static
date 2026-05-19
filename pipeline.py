import json
import os
from datetime import datetime

from module_loader import load_modules


OUTPUT_DIR = "output"
REPORTS_DIR = os.path.join(OUTPUT_DIR, "reports")
SUMMARY_FILE = os.path.join(OUTPUT_DIR, "pipeline_summary.json")


def run_pipeline():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(REPORTS_DIR, exist_ok=True)

    print("[pipeline] Loading engine modules...")
    modules = load_modules()

    findings = []

    for module_name, module in modules.items():
        scan_func = getattr(module, "scan", None)

        if not callable(scan_func):
            print(f"[pipeline] Skipping {module_name}: missing scan()")
            continue

        try:
            print(f"[pipeline] Running {module_name}...")
            results = scan_func()

            if results is None:
                results = []

            if isinstance(results, dict):
                results = [results]

            if not isinstance(results, list):
                print(f"[pipeline] Invalid result type from {module_name}")
                continue

            findings.extend(results)

        except Exception as e:
            print(f"[pipeline] Error in {module_name}: {e}")

    findings_file = os.path.join(REPORTS_DIR, "findings.json")

    with open(findings_file, "w", encoding="utf-8") as f:
        json.dump(findings, f, indent=2)

    summary = {
        "timestamp": datetime.utcnow().isoformat(),
        "modules_loaded": list(modules.keys()),
        "total_modules": len(modules),
        "total_findings": len(findings),
        "output_file": findings_file
    }

    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    if os.path.exists(findings_file) and os.path.exists(SUMMARY_FILE):
        print("[pipeline] Pipeline completed successfully.")
        print(f"[pipeline] Findings saved to: {findings_file}")
        print(f"[pipeline] Summary saved to: {SUMMARY_FILE}")


if __name__ == "__main__":
    run_pipeline()
