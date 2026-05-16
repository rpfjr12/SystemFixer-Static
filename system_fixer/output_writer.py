import json
import os

OUTPUT_DIR = "output"
JSON_OUTPUT = "final_findings.json"

def write_output(findings):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    json_path = os.path.join(OUTPUT_DIR, JSON_OUTPUT)

    try:
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(findings, f, indent=4)
        print(f"[output_writer] Wrote {len(findings)} findings to {json_path}")
    except Exception as e:
        print(f"[output_writer] Error writing JSON output: {e}")

    return json_path

