#!/usr/bin/env python3
"""
System-Fixer autonomous scanner.
Reads programs.json, scans each in-scope target, outputs findings JSON.
"""
import json
import os
import sys
import socket
import ssl
import re
import time
import datetime
from pathlib import Path
from urllib.parse import urlparse

try:
    import requests
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except ImportError:
    print("ERROR: Run `pip install -r scanner/requirements.txt` first", file=sys.stderr)
    sys.exit(1)

try:
    import dns.resolver
    HAS_DNS = True
except ImportError:
    HAS_DNS = False

ROOT = Path(__file__).parent.parent
PROGRAMS_FILE = ROOT / "programs.json"
FINDINGS_DIR = ROOT / "data" / "findings"
TODAY = datetime.date.today().isoformat()

TIMEOUT = 10
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SystemFixer/1.0; security-research)"
}


# ─── Helpers ──────────────────────────────────────────────────────────────────

def normalise_url(raw: str) -> str:
    raw = raw.strip()
    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw
    return raw.rstrip("/")


def fetch(url: str, follow_redirects: bool = True, timeout: int = TIMEOUT):
    try:
        resp = requests.get(
            url,
            headers=HEADERS,
            timeout=timeout,
            verify=False,
            allow_redirects=follow_redirects,
        )
        return resp
    except requests.exceptions.Timeout:
        return None
    except requests.exceptions.ConnectionError:
        return None
    except Exception:
        return None


def finding(title, description, severity, evidence=None, remediation=None,
            target=None, program_id=None):
    return {
        "title": title,
        "description": description,
        "severity": severity,
        "evidence": evidence or "",
        "remediation": remediation or "",
        "target": target or "",
        "program_id": program_id or "",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
    }


# ─── Individual checks ────────────────────────────────────────────────────────

def check_reachability(url, pid):
    resp = fetch(url)
    if resp is None:
        return [finding(
            "Host unreachable",
            f"Could not connect to {url}. The host may be offline or blocking scanners.",
            "high",
            evidence=f"GET {url} → no response",
            remediation="Verify the host is online and reachable.",
            target=url, program_id=pid,
        )], None
    return [], resp


def check_https_redirect(url, pid):
    findings = []
    parsed = urlparse(url)
    if parsed.scheme == "https":
        http_url = "http://" + parsed.netloc + parsed.path
        resp = fetch(http_url, follow_redirects=False)
        if resp and resp.status_code not in (301, 302, 307, 308):
            findings.append(finding(
                "HTTP not redirected to HTTPS",
                "The server accepts plain HTTP connections without redirecting to HTTPS, "
                "allowing traffic interception.",
                "medium",
                evidence=f"GET {http_url} → HTTP {resp.status_code} (no redirect)",
                remediation="Configure your web server to redirect all HTTP traffic to HTTPS.",
                target=url, program_id=pid,
            ))
    return findings


def check_security_headers(url, resp, pid):
    findings = []
    h = {k.lower(): v for k, v in resp.headers.items()}

    checks = [
        ("strict-transport-security", "Missing Strict-Transport-Security (HSTS)",
         "Without HSTS, browsers can be tricked into downgrading HTTPS connections.",
         "medium",
         'Add: Strict-Transport-Security: max-age=31536000; includeSubDomains; preload'),

        ("content-security-policy", "Missing Content-Security-Policy (CSP)",
         "No CSP means arbitrary scripts can execute, greatly increasing XSS risk.",
         "medium",
         "Define a strict Content-Security-Policy for your application."),

        ("x-content-type-options", "Missing X-Content-Type-Options",
         "Without this header, browsers may MIME-sniff responses, enabling attacks.",
         "low",
         "Add: X-Content-Type-Options: nosniff"),

        ("x-frame-options", "Missing X-Frame-Options",
         "Pages can be embedded in iframes, enabling clickjacking attacks.",
         "medium",
         "Add: X-Frame-Options: DENY (or use CSP frame-ancestors)"),

        ("referrer-policy", "Missing Referrer-Policy",
         "Full URLs including sensitive parameters may leak in Referer headers.",
         "info",
         "Add: Referrer-Policy: strict-origin-when-cross-origin"),

        ("permissions-policy", "Missing Permissions-Policy",
         "Browser features (camera, mic, geolocation) are not explicitly restricted.",
         "info",
         "Add a Permissions-Policy header restricting unused browser features."),
    ]

    for header, title, desc, sev, remediation in checks:
        if header not in h:
            findings.append(finding(
                title, desc, sev,
                evidence=f"Header '{header}' not present in response from {url}",
                remediation=remediation,
                target=url, program_id=pid,
            ))

    # Check HSTS max-age if present
    hsts = h.get("strict-transport-security", "")
    if hsts:
        m = re.search(r"max-age=(\d+)", hsts)
        if m and int(m.group(1)) < 15768000:
            findings.append(finding(
                "Weak HSTS max-age (< 6 months)",
                "HSTS max-age is set but too short to provide meaningful protection.",
                "low",
                evidence=f"Strict-Transport-Security: {hsts}",
                remediation="Set max-age to at least 31536000 (1 year).",
                target=url, program_id=pid,
            ))

    return findings


def check_information_disclosure(url, resp, pid):
    findings = []
    h = {k.lower(): v for k, v in resp.headers.items()}

    if "server" in h and h["server"].lower() not in ("", "-", "server"):
        findings.append(finding(
            "Server version disclosure",
            f"The Server header reveals software/version info, helping attackers target CVEs.",
            "low",
            evidence=f"Server: {h['server']}",
            remediation="Remove or genericise the Server header in your web server config.",
            target=url, program_id=pid,
        ))

    if "x-powered-by" in h:
        findings.append(finding(
            "Technology disclosure via X-Powered-By",
            "X-Powered-By reveals backend stack information to attackers.",
            "low",
            evidence=f"X-Powered-By: {h['x-powered-by']}",
            remediation="Disable the X-Powered-By header.",
            target=url, program_id=pid,
        ))

    if "x-aspnet-version" in h or "x-aspnetmvc-version" in h:
        val = h.get("x-aspnet-version") or h.get("x-aspnetmvc-version")
        findings.append(finding(
            "ASP.NET version disclosure",
            "ASP.NET version headers reveal precise stack versions to attackers.",
            "low",
            evidence=f"ASP.NET version header: {val}",
            remediation="Disable version disclosure in Web.config.",
            target=url, program_id=pid,
        ))

    return findings


def check_cors(url, resp, pid):
    findings = []
    h = {k.lower(): v for k, v in resp.headers.items()}
    acao = h.get("access-control-allow-origin", "")

    if acao == "*":
        findings.append(finding(
            "Wildcard CORS policy",
            "Access-Control-Allow-Origin: * allows any website to read responses, "
            "which may expose sensitive data if credentials are involved.",
            "medium",
            evidence=f"Access-Control-Allow-Origin: *",
            remediation="Restrict CORS to specific trusted origins.",
            target=url, program_id=pid,
        ))

    # Test reflective CORS
    try:
        evil = "https://evil.attacker.com"
        r2 = requests.get(url, headers={**HEADERS, "Origin": evil},
                          timeout=TIMEOUT, verify=False)
        acao2 = r2.headers.get("Access-Control-Allow-Origin", "")
        acac = r2.headers.get("Access-Control-Allow-Credentials", "")
        if acao2 == evil and acac.lower() == "true":
            findings.append(finding(
                "Reflected CORS with credentials",
                "The server reflects the Origin header and allows credentials, "
                "enabling cross-origin reads of authenticated responses.",
                "critical",
                evidence=f"Origin: {evil} → ACAO: {acao2}, ACAC: {acac}",
                remediation="Validate Origin against a strict allowlist. Never combine "
                            "wildcard/reflected origin with Allow-Credentials: true.",
                target=url, program_id=pid,
            ))
    except Exception:
        pass

    return findings


def check_cookies(url, resp, pid):
    findings = []
    raw_cookies = resp.headers.get("Set-Cookie", "")
    if not raw_cookies:
        return findings

    cookies_raw = resp.raw.headers.getlist("Set-Cookie") if hasattr(resp.raw.headers, "getlist") else [raw_cookies]

    for cookie in cookies_raw:
        lower = cookie.lower()
        name = cookie.split("=")[0].strip()

        if "httponly" not in lower:
            findings.append(finding(
                "Cookie missing HttpOnly flag",
                f"Cookie '{name}' is accessible via JavaScript, enabling theft via XSS.",
                "medium",
                evidence=f"Set-Cookie: {cookie[:200]}",
                remediation="Add the HttpOnly attribute to all session/auth cookies.",
                target=url, program_id=pid,
            ))

        if "secure" not in lower:
            findings.append(finding(
                "Cookie missing Secure flag",
                f"Cookie '{name}' can be transmitted over HTTP, risking interception.",
                "medium",
                evidence=f"Set-Cookie: {cookie[:200]}",
                remediation="Add the Secure attribute to all cookies.",
                target=url, program_id=pid,
            ))

        if "samesite" not in lower:
            findings.append(finding(
                "Cookie missing SameSite attribute",
                f"Cookie '{name}' has no SameSite attribute, increasing CSRF risk.",
                "low",
                evidence=f"Set-Cookie: {cookie[:200]}",
                remediation="Add SameSite=Strict or SameSite=Lax to session cookies.",
                target=url, program_id=pid,
            ))

    return findings


def check_sensitive_paths(url, pid):
    findings = []
    paths = [
        ("/.env",              "critical", "Exposed .env file",
         "Environment file may contain secrets, API keys, and database credentials."),
        ("/.git/config",       "critical", "Exposed Git config",
         "Git config may reveal repo URLs and internal infrastructure."),
        ("/.git/HEAD",         "critical", "Exposed Git repository",
         "The .git directory is publicly accessible, enabling full source code extraction."),
        ("/phpinfo.php",       "high",    "PHP info page exposed",
         "phpinfo() reveals PHP version, configuration, and server paths."),
        ("/wp-login.php",      "medium",  "WordPress login detected",
         "WordPress admin login is publicly accessible and may be brute-forceable."),
        ("/wp-json/wp/v2/users","medium", "WordPress user enumeration",
         "WordPress REST API exposes usernames, aiding credential attacks."),
        ("/admin",             "low",     "Admin panel accessible",
         "An admin interface is publicly reachable."),
        ("/administrator",     "low",     "Admin panel (Joomla-style)",
         "An admin interface is publicly reachable."),
        ("/server-status",     "medium",  "Apache server-status exposed",
         "Exposes active requests, worker state, and internal IPs."),
        ("/actuator",          "medium",  "Spring Boot Actuator exposed",
         "Actuator endpoints may expose heap dumps, env vars, and internal config."),
        ("/actuator/env",      "high",    "Spring Actuator /env exposed",
         "Exposes all environment variables including secrets."),
        ("/actuator/health",   "low",     "Spring Actuator health exposed",
         "Health endpoint is publicly accessible."),
        ("/.DS_Store",         "low",     "macOS .DS_Store file exposed",
         "May reveal directory structure and file names."),
        ("/backup.zip",        "high",    "Backup archive exposed",
         "A backup archive is publicly downloadable."),
        ("/backup.sql",        "critical","Database dump exposed",
         "A SQL dump may contain all application data."),
        ("/robots.txt",        "info",    "robots.txt present",
         "robots.txt may reveal hidden paths and admin areas."),
        ("/.well-known/security.txt", "info", "security.txt present",
         "The site has a security.txt file — good practice."),
    ]

    for path, sev, title, desc in paths:
        resp = fetch(url + path, follow_redirects=False)
        if resp is None:
            continue
        if resp.status_code == 200:
            # For info-level, don't flag security.txt as a problem
            if path == "/.well-known/security.txt":
                continue
            findings.append(finding(
                title, desc, sev,
                evidence=f"GET {url + path} → HTTP {resp.status_code} "
                         f"({len(resp.content)} bytes)",
                remediation=f"Restrict or remove access to {path} via your server config.",
                target=url, program_id=pid,
            ))
        time.sleep(0.3)

    return findings


def check_ssl(url, pid):
    findings = []
    parsed = urlparse(url)
    if parsed.scheme != "https":
        return findings
    host = parsed.hostname
    port = parsed.port or 443

    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=TIMEOUT) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                not_after = ssl.cert_time_to_seconds(cert.get("notAfter", ""))
                days_left = (not_after - time.time()) / 86400
                if days_left < 30:
                    findings.append(finding(
                        f"SSL certificate expiring in {int(days_left)} days",
                        "The TLS certificate is about to expire. Browsers will show "
                        "security warnings once it does.",
                        "high" if days_left < 14 else "medium",
                        evidence=f"Certificate for {host} expires in {int(days_left)} days",
                        remediation="Renew the TLS certificate immediately.",
                        target=url, program_id=pid,
                    ))
    except ssl.SSLCertVerificationError as e:
        findings.append(finding(
            "Invalid SSL certificate",
            "The TLS certificate is invalid (expired, self-signed, or wrong hostname).",
            "high",
            evidence=str(e),
            remediation="Install a valid TLS certificate from a trusted CA.",
            target=url, program_id=pid,
        ))
    except Exception:
        pass

    return findings


def check_subdomains(base_url, pid):
    """Simple common-subdomain check via DNS."""
    findings = []
    if not HAS_DNS:
        return findings

    parsed = urlparse(base_url)
    host = parsed.hostname
    # Only check apex domains (not already a subdomain)
    parts = host.split(".")
    if len(parts) > 2:
        return findings

    common = ["www", "api", "dev", "staging", "test", "admin", "mail",
              "vpn", "remote", "beta", "old", "portal", "app", "static",
              "assets", "cdn", "docs", "support", "status", "login"]

    resolver = dns.resolver.Resolver()
    resolver.timeout = 3
    resolver.lifetime = 3

    for sub in common:
        fqdn = f"{sub}.{host}"
        try:
            answers = resolver.resolve(fqdn, "A")
            if answers:
                findings.append(finding(
                    f"Subdomain discovered: {fqdn}",
                    f"The subdomain {fqdn} resolves to an IP. It may be in scope and should be assessed.",
                    "info",
                    evidence=f"{fqdn} → {answers[0].address}",
                    remediation="Ensure this subdomain is in scope and assess it separately.",
                    target=base_url, program_id=pid,
                ))
        except Exception:
            pass

    return findings


# ─── Per-target scan ──────────────────────────────────────────────────────────

def scan_target(raw_url: str, program_id: str) -> list:
    url = normalise_url(raw_url)
    print(f"  → scanning {url}")
    all_findings = []

    reach_findings, resp = check_reachability(url, program_id)
    all_findings.extend(reach_findings)
    if resp is None:
        return all_findings

    all_findings.extend(check_https_redirect(url, program_id))
    all_findings.extend(check_security_headers(url, resp, program_id))
    all_findings.extend(check_information_disclosure(url, resp, program_id))
    all_findings.extend(check_cors(url, resp, program_id))
    all_findings.extend(check_cookies(url, resp, program_id))
    all_findings.extend(check_ssl(url, program_id))
    all_findings.extend(check_sensitive_paths(url, program_id))
    all_findings.extend(check_subdomains(url, program_id))

    return all_findings


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    FINDINGS_DIR.mkdir(parents=True, exist_ok=True)

    if not PROGRAMS_FILE.exists():
        print(f"ERROR: {PROGRAMS_FILE} not found", file=sys.stderr)
        sys.exit(1)

    programs = json.loads(PROGRAMS_FILE.read_text())
    active = [p for p in programs if p.get("active", True)]
    print(f"System-Fixer: scanning {len(active)} active program(s) — {TODAY}")

    all_findings = []
    summary = []

    for prog in active:
        pid = prog["id"]
        name = prog["name"]
        scope = prog.get("scope", [])
        print(f"\n[{name}] — {len(scope)} target(s)")

        prog_findings = []
        for target in scope:
            f = scan_target(target, pid)
            prog_findings.extend(f)
            print(f"     {len(f)} finding(s)")

        all_findings.extend(prog_findings)
        summary.append({
            "program_id": pid,
            "program_name": name,
            "targets_scanned": len(scope),
            "findings_count": len(prog_findings),
        })

    output = {
        "date": TODAY,
        "scan_started": datetime.datetime.utcnow().isoformat() + "Z",
        "programs_scanned": len(active),
        "total_findings": len(all_findings),
        "summary": summary,
        "findings": all_findings,
    }

    out_file = FINDINGS_DIR / f"{TODAY}.json"
    out_file.write_text(json.dumps(output, indent=2))
    print(f"\n✓ {len(all_findings)} total finding(s) saved to {out_file}")

    # Print severity breakdown
    from collections import Counter
    sevs = Counter(f["severity"] for f in all_findings)
    for sev in ["critical", "high", "medium", "low", "info"]:
        if sevs[sev]:
            print(f"  {sev.upper()}: {sevs[sev]}")


if __name__ == "__main__":
    main()
