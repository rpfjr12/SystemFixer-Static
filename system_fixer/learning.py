import os
import json
import time
from pathlib import Path
from typing import Dict, Any
from system_fixer.scope_manager import scope_manager
from system_fixer.safety_kernel import safety_kernel

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "learning_models"
MODEL_DIR.mkdir(exist_ok=True)


class LearningEngine:
    """Simple local learning engine with versioned model snapshots.

    Only learns from validated, legal outcomes with confirmed payouts.
    Models are simple JSON artifacts (no external services) and support
    versioning and rollback.
    """

    def __init__(self):
        self.current = None

    def _next_version_path(self):
        existing = sorted(MODEL_DIR.glob("model-*.json"))
        if not existing:
            return MODEL_DIR / "model-1.json"
        last = existing[-1].stem
        try:
            v = int(last.split("-",1)[1])
        except Exception:
            v = len(existing)
        return MODEL_DIR / f"model-{v+1}.json"

    def record_validation(self, finding: Dict[str, Any], program: Dict[str, Any], payout_amount: float, validator: str):
        """Record a validated outcome.

        Only record when safety kernel allows learning and target is in scope.
        """
        if not safety_kernel.is_action_allowed("learning_write"):
            raise PermissionError("Learning writes are disabled by safety policy")

        program_id = (program.get("id") or program.get("name") or "").strip().lower()
        if not scope_manager.is_target_in_scope(finding.get("target", ""), program_id):
            raise ValueError("Finding not in program scope")

        if payout_amount is None or payout_amount <= 0:
            # Do not learn from zero/negative payouts
            return False

        entry = {
            "timestamp": int(time.time()),
            "program": program_id,
            "finding": finding,
            "payout": float(payout_amount),
            "validator": validator,
        }

        path = self._next_version_path()
        model = {
            "meta": {"created": int(time.time()), "note": "auto-update"},
            "data": [entry],
        }
        with open(path, "w") as fh:
            json.dump(model, fh, indent=2)
        # update current pointer
        current = MODEL_DIR / "current.json"
        if current.exists():
            current.unlink()
        current.symlink_to(path.name)
        self.current = path
        return True

    def list_models(self):
        return sorted([p.name for p in MODEL_DIR.glob("model-*.json")])

    def rollback_to(self, version_name: str):
        target = MODEL_DIR / version_name
        if not target.exists():
            raise FileNotFoundError("Model version not found")
        # point current to target
        current = MODEL_DIR / "current.json"
        if current.exists():
            current.unlink()
        current.symlink_to(target.name)
        self.current = target
        return True


learning_engine = LearningEngine()
