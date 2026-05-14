# sensitive_data_engine.py

from typing import List, Dict, Any
import re


EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
API_KEY_RE = re.compile(r"(?:api_key|apikey|x-api-key)['\"]?\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}")
TOKEN_RE = re.compile(r"(?:token|access_token|auth_token)['\"]?\s*[:=]\s*['\"][A-Za-z0-9_\-]{16,}")


def scan(target: str, http_client) -> List[Dict[str, Any]]:
    """
    Sensitive Data Classifier

    Strategy:
    - Inspect responses for:
      - emails
      - API keys
      - access tokens
      - secrets in JSON or text
    - Flag endpoints leaking sensitive data.
    """
    findings: List[Dict[str, Any]] = []

    # TODO: integrate with your response capture (e.g. replay or logging)
    sampled_responses: List[Dict[str, Any]] = []  # {"url": "...", "status": 200, "body": "..."}

    for item in sampled_responses:
        url = item["url"]
        body = item.get("body", "") or ""

        emails = EMAIL_RE.findall(body)
        api_keys = API_KEY_RE.findall(body)
        tokens = TOKEN_RE.findall(body)

        if emails or api_keys or tokens:
            findings.append(
                {
                    "type": "SENSITIVE_DATA_EXPOSURE",
                    "severity": "HIGH",
                    "target": target,
                    "endpoint": url,
                    "details": "Potential sensitive data exposure detected in response body.",
                    "evidence": {
                        "emails_sample": emails[:5],
                        "api_keys_sample": api_keys[:3],
                        "tokens_sample": tokens[:3],
                    },
                }
            )

    return findings
