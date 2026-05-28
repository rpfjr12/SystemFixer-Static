import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse
import types

BASE_DIR = Path(__file__).resolve().parent.parent
PROGRAMS_PATH = BASE_DIR / "programs.json"


@dataclass(frozen=True)
class ProgramScope:
    id: str
    name: str
    platform: str
    scope: Tuple[str, ...]
    active: bool
    added: str
    notes: str


def _normalize_scope_url(raw_url: str) -> str:
    raw_url = raw_url.strip()
    if not raw_url:
        return ""
    parsed = urlparse(raw_url)
    if not parsed.scheme:
        raw_url = f"https://{raw_url}"
    return raw_url.rstrip("/")


def _normalize_path(path: str) -> str:
    path = path or "/"
    if not path.endswith("/"):
        path = path + "/"
    return path


class ScopeManager:
    def __init__(self, programs_path: Optional[str] = None):
        # Load programs into an immutable mapping to prevent runtime mutation.
        raw = self._load_programs(programs_path or PROGRAMS_PATH)
        self._programs: Dict[str, ProgramScope] = types.MappingProxyType(raw)

    def _load_programs(self, path: str) -> Dict[str, ProgramScope]:
        if not os.path.exists(path):
            return {}

        with open(path, "r") as fh:
            raw_programs = json.load(fh)

        programs = {}
        for program_data in raw_programs:
            program_id = (program_data.get("id") or program_data.get("name") or "").strip().lower()
            if not program_id:
                continue

            scope_items = tuple(_normalize_scope_url(item) for item in program_data.get("scope", []) if item)
            programs[program_id] = ProgramScope(
                id=program_id,
                name=program_data.get("name", "").strip(),
                platform=program_data.get("platform", "").strip(),
                scope=scope_items,
                active=bool(program_data.get("active", False)),
                added=program_data.get("added", ""),
                notes=program_data.get("notes", "").strip(),
            )

        return programs

    @property
    def programs(self) -> Tuple[ProgramScope, ...]:
        return tuple(self._programs.values())

    def get_program(self, program_id: str) -> Optional[ProgramScope]:
        if not program_id:
            return None
        return self._programs.get(program_id.lower())

    def is_target_in_scope(self, target: str, program_id: str) -> bool:
        program = self.get_program(program_id)
        if not program or not program.active:
            return False

        target_url = _normalize_scope_url(target)
        if not target_url:
            return False

        target_parsed = urlparse(target_url)
        for scope_url in program.scope:
            scope_parsed = urlparse(scope_url)
            if not scope_parsed.hostname or not target_parsed.hostname:
                continue
            if scope_parsed.hostname != target_parsed.hostname:
                continue
            scope_path = _normalize_path(scope_parsed.path)
            target_path = _normalize_path(target_parsed.path)
            if target_path.startswith(scope_path):
                return True

        return False


scope_manager = ScopeManager()
