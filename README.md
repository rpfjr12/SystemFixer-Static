# System-Fixer

Autonomous daily vulnerability scanner for bug bounty programs.  
No servers. No build tools. Runs free on GitHub Actions.

---

## How it works

1. Edit `programs.json` to add your targets  
2. Push to GitHub — Actions runs the scanner every day at 06:00 UTC  
3. Findings are saved to `data/YYYY-MM-DD.json` and committed back  
4. `dashboard/data.js` is regenerated automatically  
5. Pull the repo and open `dashboard/index.html` locally — no server needed  

---

## Quick start

### 1. Fork this repo on GitHub  
Go to **Settings → Actions → General → Allow all actions**

### 2. Add your programs to `programs.json`

```json
[
  {
    "id": "acme",
    "name": "Acme Corp",
    "platform": "HackerOne",
    "scope": ["https://acme.com", "https://api.acme.com"],
    "active": true,
    "added": "2026-05-08",
    "notes": "Max payout $5k"
  }
]
Only scan targets you own or have written permission to test.

3. Trigger the first scan
Actions → Autonomous Daily Scan → Run workflow

4. View the dashboard
After the scan commits results, pull the repo and open dashboard/index.html in any browser.

What gets scanned
Check	Severity
Exposed .env / .git/config	Critical
Reflected CORS + credentials	Critical
Exposed database dump	Critical
Invalid / expiring SSL cert	High
Missing HSTS	Medium
Missing Content-Security-Policy	Medium
Missing X-Frame-Options	Medium
Wildcard CORS	Medium
Cookie missing HttpOnly/Secure	Medium
HTTP not redirected to HTTPS	Medium
Server version disclosure	Low
Missing X-Content-Type-Options	Low
Weak HSTS max-age	Low
Missing Referrer-Policy	Info
Subdomain discovery (DNS)	Info
Admin panels reachable	Low–Med
Spring Boot Actuator exposed	Med–High
WordPress login exposed	Medium


File structure
Code
system-fixer/
├── programs.json
├── README.md
├── .gitignore
├── scanner/
│   └── scan.py
├── scripts/
│   └── generate_data.py
├── dashboard/
│   ├── index.html
│   └── data.js
├── data/
└── .github/
    └── workflows/
        └── scan.yml
Running locally
bash
pip install -r requirements.txt
python scanner/scan.py
python scripts/generate_data.py
# Open dashboard/index.html in your browser
Legal
Only scan targets you own or have explicit written permission to test.
Unauthorized scanning may be illegal.

