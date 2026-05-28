"""Autonomous daemon with self-healing watchdog and revenue optimization."""

import os
import sys
import time
import signal
import json
import subprocess
from pathlib import Path
from typing import Optional
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
STATE_FILE = BASE_DIR / "daemon_state.json"
LOG_FILE = BASE_DIR / "logs" / "daemon.log"
LOG_FILE.parent.mkdir(exist_ok=True)

# Daemon state tracking
DEFAULT_DAEMON_STATE = {
    "pid": None,
    "started": None,
    "last_heartbeat": None,
    "uptime_seconds": 0,
    "cycles_completed": 0,
    "total_findings": 0,
    "total_queued": 0,
    "estimated_revenue": 0,
    "status": "stopped",  # stopped, running, recovering, error
    "last_error": None,
    "error_count": 0,
}


def log(message: str, level: str = "INFO"):
    """Log message to daemon log."""
    timestamp = datetime.utcnow().isoformat()
    log_entry = f"[{timestamp}] [{level}] {message}\n"
    print(log_entry.rstrip())
    with open(LOG_FILE, "a") as f:
        f.write(log_entry)


def load_daemon_state() -> dict:
    """Load daemon state from disk."""
    if STATE_FILE.exists():
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return DEFAULT_DAEMON_STATE.copy()


def save_daemon_state(state: dict):
    """Save daemon state to disk."""
    state["last_heartbeat"] = int(time.time())
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def get_daemon_pid() -> Optional[int]:
    """Get running daemon PID if it exists."""
    state = load_daemon_state()
    if state.get("status") == "running" and state.get("pid"):
        try:
            os.kill(state["pid"], 0)  # Check if process exists
            return state["pid"]
        except (OSError, ProcessLookupError):
            pass
    return None


def is_daemon_running() -> bool:
    """Check if daemon is already running."""
    return get_daemon_pid() is not None


def start_daemon(foreground: bool = False):
    """Start the autonomous daemon."""
    if is_daemon_running() and not foreground:
        log("Daemon is already running", "WARN")
        return

    state = load_daemon_state()
    state["pid"] = os.getpid()
    state["started"] = int(time.time())
    state["status"] = "running"
    state["cycles_completed"] = 0
    save_daemon_state(state)

    log(f"Daemon started (PID: {os.getpid()})", "INFO")

    # Import scheduler here to avoid circular imports
    from system_fixer.scheduler import AutonomousScheduler
    from system_fixer.report_queue import report_queue
    from system_fixer.roi_optimizer import roi_optimizer
    from system_fixer.loader import load_programs

    scheduler = AutonomousScheduler()

    def handle_shutdown(signum, frame):
        """Handle graceful shutdown."""
        log(f"Received signal {signum}, shutting down gracefully...", "INFO")
        state = load_daemon_state()
        state["status"] = "stopped"
        state["uptime_seconds"] = int(time.time()) - state["started"]
        save_daemon_state(state)
        sys.exit(0)

    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    cycle_count = 0
    consecutive_errors = 0
    max_consecutive_errors = 5

    try:
        while True:
            try:
                cycle_count += 1
                log(f"Starting scan cycle {cycle_count}...", "INFO")

                # Get programs and prioritize by ROI
                programs = load_programs()
                ranked_programs = roi_optimizer.get_recommended_scan_order(programs)

                # Run one scheduler cycle
                findings_count = scheduler.run_once()
                
                result = {
                    "total_findings": findings_count,
                }
                consecutive_errors = 0

                # Update state
                state = load_daemon_state()
                state["cycles_completed"] = cycle_count
                state["total_findings"] = result.get("total_findings", 0)
                queue_stats = report_queue.get_queue_stats()
                state["total_queued"] = queue_stats.get("total_queued", 0)

                # Get revenue projection
                revenue_est = roi_optimizer.estimate_expected_revenue(ranked_programs)
                state["estimated_revenue"] = revenue_est.get("estimated_daily_revenue", 0)

                save_daemon_state(state)

                log(
                    f"Cycle {cycle_count} complete. "
                    f"Findings: {result.get('total_findings')}, "
                    f"Queued: {state['total_queued']}, "
                    f"Est. Daily Revenue: ${state['estimated_revenue']:.2f}",
                    "INFO",
                )

            except Exception as e:
                consecutive_errors += 1
                log(f"Cycle {cycle_count} error: {str(e)}", "ERROR")

                state = load_daemon_state()
                state["last_error"] = str(e)
                state["error_count"] += 1
                state["status"] = "recovering" if consecutive_errors < max_consecutive_errors else "error"
                save_daemon_state(state)

                if consecutive_errors >= max_consecutive_errors:
                    log(
                        f"Max errors ({max_consecutive_errors}) reached, stopping daemon",
                        "ERROR",
                    )
                    break

                # Exponential backoff
                backoff = min(300, 10 * consecutive_errors)
                log(f"Backing off for {backoff} seconds...", "WARN")
                time.sleep(backoff)

            # Sleep before next cycle
            time.sleep(scheduler.config.get("interval_seconds", 300))

    except KeyboardInterrupt:
        log("Daemon interrupted by user", "INFO")
    except Exception as e:
        log(f"Fatal daemon error: {str(e)}", "FATAL")
        state = load_daemon_state()
        state["status"] = "error"
        state["last_error"] = str(e)
        save_daemon_state(state)
        raise
    finally:
        state = load_daemon_state()
        state["status"] = "stopped"
        state["uptime_seconds"] = int(time.time()) - state.get("started", int(time.time()))
        save_daemon_state(state)
        log(f"Daemon stopped. Uptime: {state['uptime_seconds']}s", "INFO")


def stop_daemon():
    """Stop the running daemon."""
    pid = get_daemon_pid()
    if not pid:
        log("Daemon is not running", "WARN")
        return False

    try:
        os.kill(pid, signal.SIGTERM)
        log(f"Sent SIGTERM to daemon (PID: {pid})", "INFO")
        return True
    except (OSError, ProcessLookupError):
        log("Could not stop daemon", "ERROR")
        return False


def get_daemon_status() -> dict:
    """Get current daemon status."""
    state = load_daemon_state()
    pid = get_daemon_pid()

    status = {
        "is_running": pid is not None,
        "pid": pid,
        "status": state.get("status"),
        "started": state.get("started"),
        "cycles_completed": state.get("cycles_completed"),
        "total_findings": state.get("total_findings"),
        "total_queued": state.get("total_queued"),
        "estimated_daily_revenue": state.get("estimated_revenue"),
        "error_count": state.get("error_count"),
        "last_error": state.get("last_error"),
    }

    if state.get("started"):
        uptime = int(time.time()) - state["started"]
        status["uptime_seconds"] = uptime
        status["uptime_readable"] = format_uptime(uptime)

    return status


def format_uptime(seconds: int) -> str:
    """Format uptime in human-readable format."""
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{int(hours)}h {int(minutes)}m {int(secs)}s"


def restart_daemon():
    """Restart the daemon."""
    log("Restarting daemon...", "INFO")
    if is_daemon_running():
        stop_daemon()
        time.sleep(2)
    start_daemon()
