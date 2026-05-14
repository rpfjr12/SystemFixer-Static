# jwt_engine.py

from typing import List, Dict, Any
import base64
import json


def _decode_jwt_header(token: str) -> Dict[str, Any]:
    try:
        header_b64 = token.split(".")[0]
        padded = header_b64 + "=" * (-len(header_b64) % 4)
        data = base64.urlsafe_b64decode(padded.encode("utf-8"))
        return json.loads(data.decode("utf-8"))
    except Exception:
        return {}


def scan(target: str, http_client) -> List[Dict[str, Any]]:
    """
    JWT Signature Validator (static checks)

    Strategy:
    - Extract JWTs from responses (Authorization headers, cookies, JSON fields).
    - Decode header, check:
      - alg: none
      - weak algorithms (HS256 where RS256 expected, etc.)
    - (Optional) Try signing with common weak secrets (if configured).
    """
    findings: List[Dict[str, Any]] = []

    # TODO: integrate with your token discovery (responses, config, etc.)
    discovered_tokens: List[str] = []

    for token in discovered_tokens:
        header = _decode_jwt_header(token)
        alg = header.get("alg")

        if not alg:
            continue

        if alg.lower() == "none":
            findings.append(
                {
                    "type": "JWT_INSECURE_ALG_NONE",
                    "severity": "HIGH",
                    "target": target,
                    "endpoint": "N/A",
                    "details": "JWT uses 'alg':'none', which is insecure and often exploitable.",
                    "evidence": {"header": header},
                }
            )

        # TODO: add more rules for weak algorithms / key confusion
        # Example: HS256 where RS256 expected, etc.

    return findings
