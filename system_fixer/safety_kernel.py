import json
import os
from dataclasses import dataclass, field
from pathlib import Path
import types

BASE_DIR = Path(__file__).resolve().parent.parent
APPROVALS_PATH = BASE_DIR / "safety_approvals.json"
KILL_SWITCH_PATH = BASE_DIR / "kill_switch.enabled"

# Make default actions immutable to prevent runtime tampering
_DEFAULT_ACTIONS = {
    "scope_check": True,
    "passive_header_request": True,
    "active_http_request": False,
    "exploit_action": False,
    "restart": True,
}
DEFAULT_ACTIONS = types.MappingProxyType(_DEFAULT_ACTIONS)


def _load_manual_approvals() -> frozenset:
    approvals = os.environ.get("SYSTEM_FIXER_MANUAL_APPROVALS", "")
    if approvals:
        return frozenset([item.strip().lower() for item in approvals.split(",") if item.strip()])

    if APPROVALS_PATH.exists():
        try:
            with open(APPROVALS_PATH, "r") as fh:
                data = json.load(fh)
            approvals = data.get("approved_actions", [])
            return frozenset([str(item).strip().lower() for item in approvals if str(item).strip()])
        except Exception:
            return frozenset()

    return frozenset()


@dataclass(frozen=True)
class SafetyKernel:
    manual_approvals: frozenset = field(default_factory=_load_manual_approvals)

    def is_action_allowed(self, action: str) -> bool:
        if not action:
            return False
        action_key = action.lower()
        if action_key in self.manual_approvals:
            return True
        return bool(DEFAULT_ACTIONS.get(action_key, False))

    def require_manual_approval(self, action: str) -> bool:
        return not self.is_action_allowed(action)

    def is_kill_switch_active(self) -> bool:
        if os.environ.get("SYSTEM_FIXER_KILL_SWITCH", "").lower() in {"1", "true", "yes"}:
            return True
        return bool(KILL_SWITCH_PATH.exists())


safety_kernel = SafetyKernel()
