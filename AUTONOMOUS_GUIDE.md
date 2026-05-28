# Autonomous Vulnerability Detection & Bounty Reporting System

**Turn your security research into revenue. Autonomously. Legally. Fast.**

This system automatically scans high-value bug bounty programs for vulnerabilities, prioritizes findings by payout potential, and prepares them for submission to bounty platforms. It learns from your historical payouts to optimize for maximum revenue.

---

## ⚡ Quick Start

```bash
# Setup
bash quickstart.sh

# Start autonomous daemon
python3 run_daemon.py start

# Check status
python3 run_daemon.py status

# View ROI analysis
python3 run_daemon.py roi-report

# Export findings for submission
python3 run_daemon.py export-queue
```

---

## 🎯 Core Features

### Autonomous Operation
- **Daemon Mode**: Runs continuously in background, scanning programs on ROI-optimized schedules
- **Self-Healing**: Automatic error recovery with exponential backoff and graceful degradation
- **State Persistence**: Resumes from where it left off; never re-scans unchanged targets

### Revenue Optimization
- **ROI Tracking**: Records payouts and learns which programs/vulnerabilities pay best
- **Smart Prioritization**: Allocates scan time based on historical payout performance
- **Payout Forecasting**: Estimates daily/weekly/monthly revenue from active programs

### Intelligent Filtering
- **Deduplication**: Merges duplicate findings; keeps highest-quality/highest-payout version
- **False Positive Filtering**: Machine-learning-based false positive detection
- **Scope Enforcement**: Only reports findings in authorized scope
- **Safety Gating**: Kill switches and manual approval for sensitive operations

### Findings Management
- **Submission Queue**: Batch findings ready for bounty platform submission
- **Platform Formatting**: Formats findings for HackerOne, Bugcrowd, and other platforms
- **Tracking**: Records submission status from queued → submitted → accepted → paid

---

## 📊 System Architecture

### Pipeline Flow

```
┌─────────────────┐
│  Raw Scan Data  │  (JSON findings from scanner)
│  (daily data)   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  Intelligence Filter        │  (Exploit potential, severity)
│  + Validity Check           │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Deduplication & Prioritize │  (Merge duplicates, rank by ROI)
│  (Report Filter)            │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Queue for Submission       │  (Report Queue)
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Export / Submit to Bounty  │  (Manual or API integration)
│  Platforms (H1, Bugcrowd)   │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Record Payouts             │  (Revenue Tracker)
│  (Update ROI Models)        │
└─────────────────────────────┘
```

### Key Components

| Component | Purpose | Location |
|-----------|---------|----------|
| **Scheduler** | Autonomous loop; processes data → orchestrates reports | `system_fixer/scheduler.py` |
| **Orchestrator** | Runs pipeline on data files; returns findings | `system_fixer/orchestrator.py` |
| **Report Filter** | Deduplicates & prioritizes by ROI | `system_fixer/report_filter.py` |
| **Report Queue** | Batches findings for submission | `system_fixer/report_queue.py` |
| **Revenue Tracker** | Tracks payouts; computes ROI metrics | `system_fixer/revenue_tracker.py` |
| **ROI Optimizer** | Ranks programs by historical ROI | `system_fixer/roi_optimizer.py` |
| **Daemon** | Self-healing watchdog; manages lifecycle | `system_fixer/daemon.py` |
| **Safety Kernel** | Permissions & kill switches | `system_fixer/safety_kernel.py` |
| **Scope Manager** | Ensures in-scope targets only | `system_fixer/scope_manager.py` |

---

## 🚀 Usage Guide

### 1. Configure Your Programs

Edit `programs.json` to add the bounty programs you want to scan:

```json
[
  {
    "id": "coinbase",
    "name": "Coinbase",
    "platform": "HackerOne",
    "scope": [
      "https://coinbase.com",
      "https://api.coinbase.com"
    ],
    "active": true,
    "added": "2026-05-14",
    "notes": "Elite crypto; fast triage; high payouts"
  }
]
```

**Required fields:**
- `id`: Unique identifier (lowercase)
- `name`: Display name
- `platform`: HackerOne, Bugcrowd, etc.
- `scope`: Array of authorized target URLs
- `active`: boolean
- `notes`: Optional notes (e.g., payout info)

### 2. Start the Daemon

```bash
# Start in background
python3 run_daemon.py start

# Or start in foreground for debugging
python3 run_daemon.py start --foreground
```

### 3. Monitor Daemon Status

```bash
# Show daemon status
python3 run_daemon.py status

# Output:
# ==================================================
# AUTONOMOUS DAEMON STATUS
# ==================================================
# Running:              True
# Status:               running
# PID:                  12345
# Uptime:               2h 45m 30s
# Scan Cycles:          18
# Total Findings:       456
# Queued for Submission: 89
# Est. Daily Revenue:   $245.50
# ==================================================
```

### 4. View ROI Analysis

```bash
python3 run_daemon.py roi-report

# Shows:
# - Expected revenue (daily/weekly/monthly)
# - Top-paying programs
# - Top-paying vulnerability types
# - Recommended scan order
```

### 5. Check Submission Queue

```bash
python3 run_daemon.py queue

# Output:
# ==================================================
# SUBMISSION QUEUE STATUS
# ==================================================
# Total Queued:         89
#   Queued              34
#   Submitted           22
#   Accepted            18
#   Paid                15
# Estimated Value:      $5,420.00
# ==================================================
```

### 6. Export Findings for Manual Submission

```bash
python3 run_daemon.py export-queue -o my_findings.json

# Generates JSON organized by platform:
# {
#   "HackerOne": [
#     {
#       "submission_id": "abc123",
#       "program_name": "Coinbase",
#       "finding": {...},
#       "status": "queued"
#     }
#   ],
#   "Bugcrowd": [...]
# }
```

### 7. Record Payouts

When you receive a bounty payout, record it so the system learns and optimizes future scans:

```bash
# Interactive mode
python3 record_payout.py

# Batch import from CSV
python3 record_payout.py batch payouts.csv

# CSV format:
# program_id,vulnerability_type,payout_amount,severity,hours_to_acceptance,submission_id,notes
# coinbase,reflected_xss,150,HIGH,24,sub_abc123,"Fast triage"
# kraken,csrf,200,MEDIUM,48,sub_def456,""
```

---

## 📈 How Revenue Optimization Works

### Historical Payout Tracking

When you record payouts, the system builds a 30-day historical record:

```
revenue_data/
├── payout_history.jsonl        # All payouts (newline-delimited JSON)
├── program_roi.json             # ROI metrics by program
└── vulnerability_roi.json       # ROI metrics by vulnerability type
```

### ROI Computation

For each program and vulnerability type, the system computes:

- **Daily ROI**: Total payout ÷ 30 days = $/day
- **Average payout**: Total payout ÷ count
- **Acceptance speed**: Average hours to acceptance
- **Severity breakdown**: Which severities pay best

### Scan Scheduling

Based on ROI, the daemon adjusts scan intervals:

- **High ROI** (>$100/day): Scan every 6 hours
- **Medium ROI** ($20-100/day): Scan every 12-24 hours
- **Low ROI** (<$20/day): Scan weekly

---

## 🔒 Safety & Scope Enforcement

### Legal & Scope Protection

All scans are strictly limited to authorized scope:

- ✅ Only targets in `programs.json` scope are scanned
- ✅ Findings outside scope are filtered out
- ✅ Report format includes scope disclaimer

### Kill Switches

Emergency shutdown mechanisms:

```bash
# Environment variable (immediate)
export SYSTEM_FIXER_KILL_SWITCH=1
python3 run_daemon.py start

# Or create kill switch file
touch kill_switch.enabled
python3 run_daemon.py start
```

### Safety Policies

The `safety_kernel` enforces policies:

- `is_action_allowed("learning_write")`: Gating for payout recording
- `is_action_allowed("queue_findings")`: Gating for submission queuing
- `is_action_allowed("restart")`: Auto-recovery permission

---

## 📝 Data Formats

### Queued Finding Entry

```json
{
  "submission_id": "abc123456",
  "timestamp": 1609459200,
  "iso_date": "2026-05-28T12:00:00",
  "program_id": "coinbase",
  "program_name": "Coinbase",
  "platform": "HackerOne",
  "priority_score": 145.5,
  "finding": {
    "issue": "Reflected XSS in login form",
    "target": "https://coinbase.com/login",
    "severity": "HIGH",
    "description": "User input not properly escaped...",
    "impact": "Account takeover",
    "estimated_payout": 250,
    "confidence": 0.95
  },
  "status": "queued"
}
```

### Payout History Entry

```json
{
  "timestamp": 1609459200,
  "iso_date": "2026-05-28T12:00:00",
  "program_id": "coinbase",
  "vulnerability_type": "reflected_xss",
  "payout": 250.0,
  "severity": "HIGH",
  "time_to_acceptance_hours": 24.5,
  "submission_id": "sub_abc123"
}
```

---

## 🔧 Configuration

### Daemon Config

Edit intervals in `system_fixer/scheduler.py`:

```python
DEFAULT_SCHEDULER_CONFIG = {
    "interval_seconds": 300,           # Base scan interval
    "max_tasks_per_cycle": 5,          # Max findings per cycle
    "queue_backpressure_threshold": 20, # Max pending before backoff
    "backoff_base_seconds": 30,        # Initial error backoff
    "max_backoff_seconds": 900,        # Max error backoff
    "task_timeout_seconds": 120,       # Scan timeout
}
```

### Programs & Scope

Edit `programs.json` to:
- Add/remove programs
- Update scope URLs
- Enable/disable with `"active": true/false`
- Add notes about payout ranges

---

## 📊 Monitoring & Logs

### Daemon Logs

```
logs/
└── daemon.log          # Daemon lifecycle events
```

### Event Logs

```
system-fixer/
└── events.log          # Detailed event stream (JSONL)
```

### Viewing Logs

```bash
# Watch daemon log in real-time
tail -f logs/daemon.log

# Watch event stream
tail -f system-fixer/events.log | jq .  # Pretty JSON

# Filter specific events
grep "findings_queued" system-fixer/events.log
```

---

## 🎮 Commands Reference

| Command | Purpose | Example |
|---------|---------|---------|
| `start` | Start daemon | `python3 run_daemon.py start` |
| `start --foreground` | Debug mode | `python3 run_daemon.py start --foreground` |
| `stop` | Stop daemon | `python3 run_daemon.py stop` |
| `restart` | Restart daemon | `python3 run_daemon.py restart` |
| `status` | Show daemon status | `python3 run_daemon.py status` |
| `queue` | Show submission queue | `python3 run_daemon.py queue` |
| `roi-report` | Revenue analysis | `python3 run_daemon.py roi-report` |
| `export-queue` | Export findings | `python3 run_daemon.py export-queue` |

---

## 🚨 Troubleshooting

### Daemon won't start

```bash
# Check logs
tail logs/daemon.log

# Start in foreground for immediate errors
python3 run_daemon.py start --foreground

# Check if already running
python3 run_daemon.py status
```

### No findings being queued

```bash
# Check if targets are in scope
cat programs.json | jq .[].scope

# Check pipeline
python3 scanner/scan.py

# Verify report generation
python3 -m system_fixer.orchestrator
```

### Revenue optimizer not working

```bash
# Check if payouts are recorded
ls -la revenue_data/payout_history.jsonl

# View ROI reports
cat revenue_data/program_roi.json | jq .
```

---

## 📄 Legal Notice

**IMPORTANT:** This system is designed for authorized security research only.

- ✅ Only scan targets you own or have explicit written permission to test
- ✅ Follow each program's rules and scope limits
- ✅ Report findings responsibly through official channels
- ✅ Respect responsible disclosure timelines
- ✅ Never exploit vulnerabilities for profit outside bounty programs

Unauthorized security testing is illegal and unethical. Always ensure you have proper authorization before scanning.

---

## 🔄 How the Autonomous Loop Works

1. **Daemon starts** → Loads configuration and historical ROI data
2. **Each cycle** (default 5 minutes):
   - Rank programs by recent ROI
   - Check for new/updated scan data
   - Run pipeline on high-priority programs
   - Filter findings (quality, scope, deduplication)
   - **Queue valid findings** for submission
   - Update event log
3. **On error** → Exponential backoff (30s → 900s max)
4. **You record payouts** → System learns; adjusts future priorities
5. **Loop continues** → Continuously improves ROI

---

## 📦 What's Included

```
SystemFixer-Static/
├── run_daemon.py              # Main entry point
├── record_payout.py           # Payout recording utility
├── quickstart.sh              # Setup script
├── programs.json              # Your bounty programs
├── scanner/                   # Raw vulnerability scanning
├── system_fixer/
│   ├── scheduler.py           # Autonomous loop
│   ├── orchestrator.py        # Pipeline orchestration
│   ├── report_queue.py        # Submission queuing
│   ├── revenue_tracker.py     # ROI tracking
│   ├── roi_optimizer.py       # Smart prioritization
│   ├── daemon.py              # Self-healing watchdog
│   ├── safety_kernel.py       # Permissions & killswitches
│   ├── scope_manager.py       # Scope enforcement
│   └── ...other modules...
├── data/                      # Raw scan data (by program/date)
├── reports/                   # Generated markdown reports
├── revenue_data/              # ROI metrics & payout history
├── submission_queue/          # Queued findings & submissions log
├── logs/                       # Daemon logs
└── tests/                     # Unit tests
```

---

## 🚀 Next Steps

1. **Run quickstart**: `bash quickstart.sh`
2. **Configure programs**: Edit `programs.json` with your targets
3. **Start daemon**: `python3 run_daemon.py start`
4. **Check status**: `python3 run_daemon.py status`
5. **Monitor ROI**: `python3 run_daemon.py roi-report`
6. **Record payouts**: `python3 record_payout.py`
7. **Export & submit**: `python3 run_daemon.py export-queue`

---

## 📞 Support

For issues or questions:
1. Check logs: `tail -f logs/daemon.log`
2. View events: `tail -f system-fixer/events.log`
3. Test manually: `python3 run_daemon.py start --foreground`
4. Run tests: `python3 -m unittest discover -s tests`

---

**Happy hunting! 🎯🚀💰**
