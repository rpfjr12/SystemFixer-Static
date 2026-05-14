import os
import json
from system_fixer.pipeline import run_pipeline
from system_fixer.output_writer import write_output

DASHBOARD_PATH = "dashboard/generated/dashboard.json"

def regenerate_dashboard(program, findings_path):
    """
    Rebuilds the dashboard JSON using the strict-mode pipeline.
    """
    results = run_pipeline(program, findings_path)

    dashboard = {
        "program": program,
        "total_findings": len(results),
        "findings": results
    }

    directory = os.path.dirname(DASHBOARD_PATH)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    write_output(DASHBOARD_PATH, json.dumps(dashboard, indent=4))
    return dashboard
