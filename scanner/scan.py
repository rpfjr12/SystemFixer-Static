# scanner/scan.py
# High-value automated scanner for normalized targets.

"""
scanner/scan.py
Passive, safety-first scanner runner for normalized targets.

This module only performs passive checks by default and defers any risky
or active action to the `safety_kernel`. Engines are optional plugins and
must be safe and non-destructive. The scanner will not perform any
exploitation or destructive actions.
"""

import json
import os
import importlib
from datetime import datetime

try:
    import requests
except Exception:
    requests = None

from system_fixer.scope_manager import scope_manager
from system_fixer.safety_kernel import safety_kernel

OUTPUT_DIR = "data"
DEFAULT_TIMEOUT = 10


def _try_import(engine_module, fn_name):
    try:
        m = importlib.import_module(engine_module)
        return getattr(m, fn_name, None)
    except Exception:
        return None


# Optional engines: only include if present and callable
check_idor = _try_import("idor_engine", "check_idor")
check_ssrf = _try_import("ssrf_engine", "check_ssrf")
check_auth_bypass = _try_import("auth_bypass_engine", "check_auth_bypass")
check_rate_limit = _try_import("rate_limit_engine", "check_rate_limit")
check_sensitive_data = _try_import("sensitive_data_engine", "check_sensitive_data")
check_jwt = _try_import("jwt_engine", "check_jwt")


def _available_engines():
    engines = [
        check_idor,
        check_ssrf,
        check_auth_bypass,
        check_rate_limit,
        check_sensitive_data,
        check_jwt,
    ]
    return [e for e in engines if callable(e)]


def load_programs(path="programs.json"):
    if not os.path.exists(path):
        return []
    with open(path, "r") as f:
        return json.load(f)


def scan_target(url):
    """Run passive safety-first checks on a single target and return findings."""
    findings = []

    engines = _available_engines()

    # Run each engine under safety guard
    for engine in engines:
        if not safety_kernel.is_action_allowed("engine_run"):
            break
        try:
            res = engine(url)
            if not res:
                continue
            for item in res:
                if isinstance(item, dict):
                    findings.append(item)
                elif isinstance(item, (list, tuple)) and len(item) >= 2:
                    findings.append({"severity": item[0], "title": item[1], "details": {}})
        except Exception:
            # engine-specific errors should not stop scanning
            continue

    # Passive header request (safe) if allowed
    if requests and safety_kernel.is_action_allowed("passive_header_request"):
        try:
            r = requests.get(url, timeout=DEFAULT_TIMEOUT, allow_redirects=True)
            headers = r.headers or {}

            if "strict-transport-security" not in (k.lower() for k in headers):
                findings.append({"severity": "MEDIUM", "title": "Missing Strict-Transport-Security (HSTS)", "details": {}})
            if "content-security-policy" not in (k.lower() for k in headers):
                findings.append({"severity": "MEDIUM", "title": "Missing Content-Security-Policy (CSP)", "details": {}})
            if "x-frame-options" not in (k.lower() for k in headers):
                findings.append({"severity": "MEDIUM", "title": "Missing X-Frame-Options", "details": {}})
            if "server" in headers:
                findings.append({"severity": "LOW", "title": "Server version disclosure", "details": {"server": headers.get("Server")}})

            # cookies best-effort
            for c in getattr(r, "cookies", []):
                try:
                    if not getattr(c, "httponly", False):
                        findings.append({"severity": "MEDIUM", "title": "Cookie missing HttpOnly flag", "details": {"cookie": getattr(c, "name", "")}})
                except Exception:
                    continue
        except Exception:
            findings.append({"severity": "LOW", "title": "Target unreachable", "details": {}})

    return findings


def _normalize_finding_for_output(f, target, program_name, date):
    title = f.get("title") or f.get("issue") or "Unknown finding"
    severity = f.get("severity", "LOW")
    impact = f.get("impact", "")
    description = f.get("description") or title
    details = f.get("details", {})

    return {
        "issue": title,
        "severity": severity,
        "impact": impact,
        "description": description,
        "target": target,
        "program": program_name,
        "date": date,
        "details": details,
    }


def save_findings(program, findings):
    """Save findings for a program into a clean JSON file. No-op if findings empty."""
    if not findings:
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    date = datetime.utcnow().strftime("%Y-%m-%d")

    program_id = program.get("id", program.get("name", "unknown")).replace(" ", "_")
    filename = f"{program_id}-{date}.json"
    path = os.path.join(OUTPUT_DIR, filename)

    output = []
    program_name = program.get("name", "Unknown Program")
    for f in findings:
        target = f.get("target")
        if target and not scope_manager.is_target_in_scope(target, program_id):
            # Skip out-of-scope targets
            continue
        output.append(_normalize_finding_for_output(f, target, program_name, date))

    with open(path, "w") as fp:
        json.dump(output, fp, indent=2)

    print(f"[scanner] Saved: {path}")


def scan_program(program):
    targets = program.get("normalized_scope") or program.get("scope") or []
    all_findings = []

    for target in targets:
        print(f"[scanner] Scanning target: {target}")
        findings = scan_target(target)

        for f in findings:
            if not f.get("target"):
                f["target"] = target

        all_findings.extend(findings)

    return all_findings


def main():
    programs = load_programs()
    for program in programs:
        findings = scan_program(program)
        save_findings(program, findings)


if __name__ == "__main__":
    main()
