# rate_limit_engine.py

from typing import List, Dict, Any
import time


def scan(target: str, http_client) -> List[Dict[str, Any]]:
    """
    Rate-Limit Tester

    Strategy:
    - Identify endpoints that should be rate-limited (login, OTP, password reset, etc.).
    - Send bursts of requests with same payload.
    - Detect absence of:
      - 429 responses
      - lockouts
      - captchas
    """
    findings: List[Dict[str, Any]] = []

    # TODO: integrate with your endpoint classification
    sensitive_endpoints: List[Dict[str, Any]] = []  # e.g. {"method": "POST", "url": ".../login", "body": {...}}

    burst_size = 20
    delay_between = 0.05  # seconds

    for ep in sensitive_endpoints:
        url = ep["url"]
        method = ep.get("method", "POST")
        body = ep.get("body", {})

        statuses = []

        for _ in range(burst_size):
            try:
                # resp = http_client.request(method, url, json=body)
                # statuses.append(resp.status_code)
                time.sleep(delay_between)
            except Exception:
                continue

        # TODO: real logic using statuses
        # Example: if no 429 and all 200/400, might be missing rate limiting
        looks_unlimited = False

        if looks_unlimited:
            findings.append(
                {
                    "type": "RATE_LIMIT_BYPASS",
                    "severity": "HIGH",
                    "target": target,
                    "endpoint": url,
                    "details": "Potential missing or weak rate limiting on sensitive endpoint.",
                    "evidence": {
                        "burst_size": burst_size,
                        "statuses": statuses,
                    },
                }
            )

    return findings
