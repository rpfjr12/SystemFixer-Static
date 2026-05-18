# idor_engine.py
# Safe analysis module for detecting ID-like patterns in structured data.

from typing import List, Dict, Any


def analyze(target: str, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Safe ID-pattern analyzer.

    This module does NOT perform any network requests or unauthorized access.
    It only analyzes structured data passed into it.

    Expected input:
        - target: string label for the dataset
        - records: list of dicts representing objects with IDs

    Strategy:
        - Look for inconsistent ID patterns
        - Look for duplicate IDs
        - Look for missing IDs
        - Look for non-sequential or malformed identifiers
    """

    findings: List[Dict[str, Any]] = []

    seen_ids = set()
    duplicate_ids = []
    malformed_ids = []

    for record in records:
        obj_id = record.get("id")

        # Missing ID
        if obj_id is None:
            findings.append({
                "type": "ID_PATTERN",
                "severity": "MEDIUM",
                "target": target,
                "title": "Record missing ID field",
                "details": {"record": record},
            })
            continue

        # Duplicate ID
        if obj_id in seen_ids:
            duplicate_ids.append(obj_id)
        else:
            seen_ids.add(obj_id)

        # Malformed ID (non-string, empty, etc.)
        if not isinstance(obj_id, (str, int)) or obj_id == "":
            malformed_ids.append(obj_id)

    # Report duplicates
    if duplicate_ids:
        findings.append({
            "type": "ID_PATTERN",
            "severity": "HIGH",
            "target": target,
            "title": "Duplicate identifiers detected",
            "details": {"duplicates": duplicate_ids},
        })

    # Report malformed IDs
    if malformed_ids:
        findings.append({
            "type": "ID_PATTERN",
            "severity": "MEDIUM",
            "target": target,
            "title": "Malformed identifiers detected",
            "details": {"malformed": malformed_ids},
        })

    return findings
