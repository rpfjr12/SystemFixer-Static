import json
import os

def load_all_findings():
    all_data = []
    for file in os.listdir("data"):
        if file.endswith(".json"):
            with open(os.path.join("data", file)) as f:
                all_data.extend(json.load(f))
    return all_data

def write_dashboard_js(findings):
    with open("dashboard/data.js", "w") as f:
        f.write("window.FINDINGS = ")
        json.dump(findings, f, indent=2)

def main():
    findings = load_all_findings()
    write_dashboard_js(findings)

if __name__ == "__main__":
    main()
