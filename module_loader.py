import importlib.util
from pathlib import Path


def load_modules(modules_dir=None):
    modules = {}

    if modules_dir is None:
        modules_dir = Path(__file__).resolve().parent / "modules"

    modules_path = Path(modules_dir)

    if not modules_path.exists() or not modules_path.is_dir():
        print(f"[module_loader] Modules directory not found: {modules_path}")
        return modules

    for file_path in modules_path.glob("*_engine.py"):
        module_name = file_path.stem

        try:
            spec = importlib.util.spec_from_file_location(
                module_name,
                str(file_path)
            )

            if spec is None or spec.loader is None:
                continue

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            modules[module_name] = module

        except Exception as e:
            print(f"[module_loader] Failed to load {module_name}: {e}")

    return modules
