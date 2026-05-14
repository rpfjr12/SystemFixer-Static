# idor_engine.py

from typing import List, Dict, Any


def scan(target: str, http_client) -> List[Dict[str, Any]]:
    """
    IDOR Pattern Detector

    Strategy (automatable):
    - Crawl/receive a list of endpoints with IDs in path/query.
    - For each endpoint, try nearby IDs (id-1, id+1, random).
    - Compare responses: status, length, key fields.
    - If different objects are accessible with same auth, flag as potential IDOR.
    """
    findings: List[Dict[str, Any]] = []

    # TODO: integrate with your endpoint inventory
    id_endpoints: List[Dict[str, Any]] = []  # e.g. [{"method": "GET", "url": ".../users/123"}]

    for ep in id_endpoints:
        original_url = ep["url"]
        method = ep.get("method", "GET")

        # TODO: extract numeric/UUID IDs from URL/query
        # TODO: generate candidate IDs (id-1, id+1, random)
        candidate_urls: List[str] = []

        # TODO: send baseline request
        # base_resp = http_client.request(method, original_url)

        for cand_url in candidate_urls:
            try:
                # cand_resp = http_client.request(method, cand_url)
                # TODO: compare base_resp vs cand_resp (status, length, key fields)
                # if looks like different user/object data with same auth:
                looks_like_idor = False

                if looks_like_idor:
                    findings.append(
                        {
                            "type": "IDOR",
                            "severity": "HIGH",
                            "target": target,
                            "endpoint": cand_url,
                            "details": "Potential IDOR: changing ID returns different object with same authorization.",
                            "evidence": {
                                # "base_status": base_resp.status_code,
                                # "cand_status": cand_resp.status_code,
                                # "base_len": len(base_resp.text),
                                # "cand_len": len(cand_resp.text),
                            },
                        }
                    )
            except Exception:
                continue

    return findings
