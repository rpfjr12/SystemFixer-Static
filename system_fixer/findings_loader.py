import json
import os
from module_loader import load_modules

def load_findings(path):
    # Load existing findings (JSON)
    base_findings = []
    if os.path.exists(path):
        with open(path, "r") as f:
            base_findings = json.load(f)

    # Load modules
    modules = load_modules()

    # Run each module's safe internal scan() if available
    module_findings = []
    for name, module in modules.items():
        if hasattr(module, "scan"):
            try:
                result = module.scan()
                if isinstance(result, list):
                    module_findings.extend(result)
            except Exception:
                # Fail-safe: module errors never break pipeline
                continue

    # Combine JSON findings + module findings
    return base_findings + module_findings
