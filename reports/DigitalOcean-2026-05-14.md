# DigitalOcean – Automated Findings

**Date:** 2026-05-14
**Total findings:** 1

## Summary by severity
- **MEDIUM:** 1

## Findings

### 1. Missing Strict-Transport-Security (HSTS) (MEDIUM)

- **Target:** `https://api.digitalocean.com`
- **Program:** DigitalOcean
- **Date detected:** 2026-05-12

**Description:**
- Automated detection of: **Missing Strict-Transport-Security (HSTS)**.

**Potential impact (generic):**
- Without HSTS, users may be exposed to downgrade or MITM attacks if they ever hit HTTP.

**Suggested remediation (generic):**
- Add a Strict-Transport-Security header with an appropriate max-age and includeSubDomains.

---
