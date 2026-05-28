import glob
import json
import os
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple

from system_fixer.pipeline import run_pipeline
from system_fixer.report_generator_patch import generate_filtered_report

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROGRAMS_PATH = os.path.join(BASE_DIR, "programs.json")
DATA_DIR = os.path.join(BASE_DIR, "data")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")


def load_programs(path=PROGRAMS_PATH):
    if not os.path.exists(path):
        return []
    with open(path, "r") as fh:
        return json.load(fh)


def find_data_files(data_dir=DATA_DIR):
    return sorted(glob.glob(os.path.join(data_dir, "*.json")))


def program_id_from_filename(filename):
    return os.path.basename(filename).split("-")[0].lower()


def ensure_reports_dir(reports_dir=REPORTS_DIR):
    os.makedirs(reports_dir, exist_ok=True)
    return reports_dir


def process_data_file(data_path, programs_by_id, reports_dir=REPORTS_DIR):
    program_id = program_id_from_filename(data_path)
    program = programs_by_id.get(program_id)
    if not program or not program.get("active"):
        return False

    findings = run_pipeline(program, data_path)
    if not findings:
        return False

    report_text = generate_filtered_report(program.get("name", program_id), findings)
    if not report_text:
        return False

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
    output_name = f"{program_id}-{timestamp}.md"
    report_path = os.path.join(reports_dir, output_name)
    with open(report_path, "w") as out:
        out.write(report_text)
    return True


def orchestrate_reports(data_paths=None, data_dir=None, reports_dir=None, programs_path=None) -> Dict[str, Any]:
    """Generate reports and return findings for queuing."""
    data_dir = data_dir or DATA_DIR
    reports_dir = reports_dir or REPORTS_DIR
    programs_path = programs_path or PROGRAMS_PATH

    programs = load_programs(programs_path)
    programs_by_id = {p.get("id", "").lower(): p for p in programs if p}
    ensure_reports_dir(reports_dir)

    if data_paths is None:
        data_paths = find_data_files(data_dir)

    processed = 0
    all_findings = []
    findings_by_program = {}

    for data_path in data_paths:
        program_id = program_id_from_filename(data_path)
        program = programs_by_id.get(program_id)
        if not program or not program.get("active"):
            continue

        findings = run_pipeline(program, data_path)
        if not findings:
            continue

        # Track findings for queuing
        all_findings.extend(findings)
        if program_id not in findings_by_program:
            findings_by_program[program_id] = []
        findings_by_program[program_id].extend(findings)

        report_text = generate_filtered_report(program.get("name", program_id), findings)
        if not report_text:
            continue

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M%S")
        output_name = f"{program_id}-{timestamp}.md"
        report_path = os.path.join(reports_dir, output_name)
        with open(report_path, "w") as out:
            out.write(report_text)
        processed += 1

    return {
        "processed": processed,
        "total_findings": len(all_findings),
        "findings_by_program": findings_by_program,
        "all_findings": all_findings,
    }


def main():
        result = orchestrate_reports()
        print(f"[orchestrator] Generated {result['processed']} report(s) with {result['total_findings']} finding(s) into {REPORTS_DIR}")


if __name__ == "__main__":
    main()
