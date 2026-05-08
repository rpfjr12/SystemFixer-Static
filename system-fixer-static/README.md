# System-Fixer

Autonomous vulnerability scanner for bug bounty programs. Zero cost. No servers. Runs entirely on GitHub Actions.

## How it works

1. You add programs to `programs.json`
2. GitHub Actions runs `scanner/scan.py` every day at 06:00 UTC
3. Findings are saved to `data/findings/YYYY-MM-DD.json`
4. `dashboard/data.js` is regenerated and committed back
5. Open `dashboard/index.html` locally — no hosting needed

## Quick Start

### 1. Fork this repo on GitHub

Fork → Settings → Actions → Allow all actions

### 2. Add your programs

Edit `programs.json`:

```json
[
  {
    "id": "acme-1",
    "name": "Acme Corp",
    "platform": "HackerOne",
    "scope": [
      "https://acme.com",
      "https://api.acme.com"
    ],
    "active": true,
    "added": "2026-05-08",
    "notes": "Main app + API, max $10k"
  }
]
```

Only scan targets you own or have **written permission** to test.

### 3. Trigger the first scan

Go to **Actions → Autonomous Daily Scan → Run workflow**

The scanner will:
- Check all in-scope URLs for security issues
- Save findings to `data/findings/`
- Regenerate `dashboard/data.js`
- Commit everything back to the repo

### 4. Open the dashboard

Pull the latest changes, then open `dashboard/index.html` in any browser. No server required.

## What gets scanned

| Check | Severity |
|---|---|
| Exposed `.env` / `.git/config` | Critical |
| Reflected CORS with credentials | Critical |
| Database dump exposed | Critical |
| SSL certificate issues | High |
| Missing HSTS header | Medium |
| Missing Content-Security-Policy | Medium |
| Missing X-Frame-Options | Medium |
| Wildcard CORS policy | Medium |
| Cookie missing HttpOnly/Secure/SameSite | Medium |
| Server / technology version disclosure | Low |
| Missing X-Content-Type-Options | Low |
| Weak HSTS max-age | Low |
| Missing Referrer-Policy | Info |
| Missing Permissions-Policy | Info |
| Subdomain discovery | Info |
| HTTP not redirected to HTTPS | Medium |
| Admin panels exposed | Low–Medium |
| Spring Boot Actuator exposed | Medium–High |
| WordPress login / user enumeration | Medium |

## Dashboard features

- **Overview** — live stat cards, 30-day findings timeline chart, severity pie chart, per-program summary
- **Findings** — searchable/filterable table with expandable rows (description, evidence, remediation)
- **Programs** — add/manage programs; local additions saved in browser storage
- **Export CSV** — download all findings as a CSV file
- **Works offline** — `chart.min.js` is bundled; no internet needed after first download

## Manually adding programs in the dashboard

Use the **Programs** page to add programs via the UI. These are saved in your browser's local storage and show up in the dashboard immediately. To include them in automated scans, copy the entry into `programs.json` in your repo.

## Vulnerability submission

Submission is intentional. The scanner intentionally stops at detection — it does **not** auto-submit findings. Review each finding in the dashboard, verify it manually, then submit through the platform.

## File structure

```
system-fixer/
├── .github/
│   └── workflows/
│       └── scan.yml          ← Runs daily, commits results
├── scanner/
│   ├── scan.py               ← Main scanner (Python)
│   └── requirements.txt
├── scripts/
│   └── generate_data.py      ← Builds dashboard/data.js from findings
├── dashboard/
│   ├── index.html            ← Offline dashboard (open locally)
│   ├── chart.min.js          ← Bundled Chart.js (no CDN needed)
│   └── data.js               ← Auto-generated: all findings data
├── data/
│   └── findings/
│       └── YYYY-MM-DD.json   ← Daily scan output
└── programs.json             ← Your target programs
```

## Running locally

```bash
pip install -r scanner/requirements.txt
python scanner/scan.py
python scripts/generate_data.py
# Then open dashboard/index.html
```

## Legal notice

Only scan targets you own or have explicit written permission to test. Unauthorised scanning may be illegal in your jurisdiction. This tool is provided for legitimate security research only.
