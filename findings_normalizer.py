# findings_normalizer.py
# Scope engine: cleans, normalizes, and validates program scope.

import re
from urllib.parse import urlparse

def normalize_domain(domain):
    """Normalize domains by stripping protocols, ports, paths, and wildcards."""
    if not domain:
        return None

    domain = domain.strip().lower()

    # Remove protocol
    if domain.startswith("http://") or domain.startswith("https://"):
        domain = urlparse(domain).netloc

    # Remove paths
    domain = domain.split("/")[0]

    # Remove ports
    domain = domain.split(":")[0]

    # Remove wildcards
    domain = domain.replace("*.", "")

    # Basic sanity check
    if "." not in domain:
        return None

    return domain


def extract_domains(scope_list):
    """Extract valid domains from raw scope entries."""
    clean = []

    for entry in scope_list:
        if not entry:
            continue

        entry = entry.strip()

        # Skip out-of-scope markers
        if "out of scope" in entry.lower():
            continue

        # Extract domain-like patterns
        match = re.findall(r"[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", entry)
        if not match:
            continue

        for m in match:
            norm = normalize_domain(m)
            if norm:
                clean.append(norm)

    return list(sorted(set(clean)))


def remove_bad_targets(domains):
    """Remove domains that are obviously invalid or dangerous."""
    bad = [
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        "example.com",
        "test.com",
        "invalid",
    ]

    return [d for d in domains if d not in bad]


def normalize_scope(scope):
    """Full scope normalization pipeline."""
    if not scope:
        return []

    domains = extract_domains(scope)
    domains = remove_bad_targets(domains)

    return domains


def normalize_program(program):
    """Attach normalized scope to a program dict."""
    raw_scope = program.get("scope", [])
    program["normalized_scope"] = normalize_scope(raw_scope)
    return program
