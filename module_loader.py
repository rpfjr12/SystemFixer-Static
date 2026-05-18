# module_loader.py
# Dynamically loads ONLY high‑value engines from /modules

import importlib
import os

HIGH_VALUE_ENGINES = {
    "idor_engine",
    "ssrf_engine",
    "auth_bypass_engine",
    "rate_limit_engine",
    "sensitive_data_engine",
    "jwt_engine"
}

def load_modules():
    modules = {}
    module_dir = "modules"

    for filename in os.listdir(module_dir):
        if filename.endswith("_engine.py"):
            name = filename[:-3]  # remove .py

            # skip low‑value engines
            if name not in HIGH_VALUE_ENGINES:
                continue

            module_path = f"{module_dir}.{name}"
            modules[name] = importlib.import_module(module_path)

    return modules
