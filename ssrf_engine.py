# ssrf_engine.py

from typing import List, Dict, Any


def scan(target: str, http_client) -> List[Dict[str, Any]]:
    """
    SSRF Probe Engine

    Strategy:
    - Identify parameters likely to fetch URLs (url, target, callback, feed, etc.).
    - Inject internal/metadata URLs:
      - http://169.254.169.254/
      - http://127.0.0.1/
      - http://localhost/
    - Detect differences in timing, status, or content that suggest server-side fetching.
    """
    findings: List[Dict[str, Any]] = []

    # TODO: integrate with your endpoint + param inventory
    url_params_endpoints: List[Dict[str, Any]] = []  # e.g. {"method": "GET", "url": "...", "params": ["url"]}

    ssrf_payloads = [
        "http://169.254.169.254/",
        "http://127.0.0.1/",
        "http://localhost/",
    ]

    for ep in url_params_endpoints:
        url = ep["url"]
        method = ep.get("method", "GET")
        params = ep.get("params", [])

        for param in params:
            for payload in ssrf_payloads:
                try:
                    # req_params = {param: payload}
                    # resp = http_client.request(method, url, params=req_params)
                    # TODO: analyze resp for signs of SSRF (errors, timeouts, internal data)
                    looks_like_ssrf = False

                    if looks_like_ssrf:
                        findings.append(
                            {
                                "type": "SSRF",
                                "severity": "CRITICAL",
                                "target": target,
                                "endpoint": url,
                                "details": f"Potential SSRF via parameter '{param}' using payload '{payload}'.",
                                "evidence": {
                                    "parameter": param,
                                    "payload": payload,
                                    # "status": resp.status_code,
                                    # "body_sample": resp.text[:300],
                                },
                            }
                        )
                except Exception:
                    continue

    return findings
