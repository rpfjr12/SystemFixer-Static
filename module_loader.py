# module_loader.py
import importlib
import os

def load_modules():
    modules = {}
    module_dir = "modules"

    for filename in os.listdir(module_dir):
        if filename.endswith("_engine.py"):
            name = filename[:-3]
            module_path = f"{module_dir}.{name}"
            modules[name] = importlib.import_module(module_path)

    return modules
