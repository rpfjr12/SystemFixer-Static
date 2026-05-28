import glob
import json
import os
import signal
import time
import traceback
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from system_fixer import orchestrator
from system_fixer.event_logger import log_event
from system_fixer.safety_kernel import safety_kernel
from system_fixer.report_queue import report_queue
from system_fixer.report_filter import filter_findings

BASE_DIR = Path(__file__).resolve().parent.parent
STATE_PATH = BASE_DIR / "autonomous_state.json"
HEARTBEAT_PATH = BASE_DIR / "autonomous_heartbeat.json"

DEFAULT_SCHEDULER_CONFIG = {
    "interval_seconds": 300,
    "max_tasks_per_cycle": 5,
    "queue_backpressure_threshold": 20,
    "backoff_base_seconds": 30,
    "max_backoff_seconds": 900,
    "task_timeout_seconds": 120,
}

DEFAULT_STATE = {
    "last_run_timestamp": None,
    "last_successful_run": None,
    "last_failure_reason": None,
    "last_learning_version": None,
    "last_report_generated": None,
    "processed_files": {},
    "consecutive_failures": 0,
    "last_heartbeat": None,
    "backoff_seconds": DEFAULT_SCHEDULER_CONFIG["backoff_base_seconds"],
}


@dataclass(order=True)
class PendingTask:
    priority: float
    path: str = field(compare=False)
    mtime: float = field(compare=False)


class SchedulerState:
    def __init__(self, state_path: Path = STATE_PATH):
        self.state_path = state_path
        self.state = self._load_state()

    def _load_state(self) -> Dict:
        if not self.state_path.exists():
            return DEFAULT_STATE.copy()

        try:
            with open(self.state_path, "r") as fh:
                data = json.load(fh)
            if not isinstance(data, dict):
                raise ValueError("State data not a dict")
            return {**DEFAULT_STATE, **data}
        except Exception as exc:
            backup = self.state_path.with_name(f"{self.state_path.name}.corrupt.{int(time.time())}")
            self.state_path.rename(backup)
            log_event("state_corruption", "State file was corrupted and backed up", {"backup_path": str(backup), "error": str(exc)})
            return DEFAULT_STATE.copy()

    def save(self):
        self.state["last_heartbeat"] = datetime.now(timezone.utc).isoformat()
        with open(self.state_path, "w") as fh:
            json.dump(self.state, fh, indent=2)

    def update(self, **kwargs):
        self.state.update(kwargs)
        self.save()

    def mark_processed(self, path: str, mtime: float, report_name: Optional[str] = None):
        processed = self.state.get("processed_files", {})
        processed[path] = {"mtime": mtime, "processed_at": datetime.now(timezone.utc).isoformat()}
        self.state["processed_files"] = processed
        if report_name:
            self.state["last_report_generated"] = report_name
        self.state["last_successful_run"] = datetime.now(timezone.utc).isoformat()
        self.state["last_failure_reason"] = None
        self.state["consecutive_failures"] = 0
        self.state["backoff_seconds"] = DEFAULT_SCHEDULER_CONFIG["backoff_base_seconds"]
        self.save()

    def mark_failure(self, reason: str):
        self.state["last_failure_reason"] = reason
        self.state["consecutive_failures"] = self.state.get("consecutive_failures", 0) + 1
        backoff = self.state.get("backoff_seconds", DEFAULT_SCHEDULER_CONFIG["backoff_base_seconds"])
        self.state["backoff_seconds"] = min(backoff * 2, DEFAULT_SCHEDULER_CONFIG["max_backoff_seconds"])
        self.save()


class AutonomousScheduler:
    def __init__(self, config: Optional[Dict] = None, data_dir: Optional[str] = None, reports_dir: Optional[str] = None, programs_path: Optional[str] = None, state_path: Optional[str] = None):
        self.config = {**DEFAULT_SCHEDULER_CONFIG, **(config or {})}
        self.data_dir = data_dir or orchestrator.DATA_DIR
        self.reports_dir = reports_dir or orchestrator.REPORTS_DIR
        self.programs_path = programs_path or orchestrator.PROGRAMS_PATH
        self.state = SchedulerState(Path(state_path) if state_path else STATE_PATH)
        self._shutdown_requested = False
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)

    def _handle_shutdown(self, signum, frame):
        self._shutdown_requested = True
        log_event("shutdown_requested", "Scheduler shutdown requested", {"signal": signum})

    def _write_heartbeat(self):
        heartbeat = {
            "heartbeat": datetime.now(timezone.utc).isoformat(),
            "last_run": self.state.state.get("last_run_timestamp"),
            "last_success": self.state.state.get("last_successful_run"),
        }
        with open(HEARTBEAT_PATH, "w") as fh:
            json.dump(heartbeat, fh)

    def is_kill_switch_active(self) -> bool:
        if os.environ.get("SYSTEM_FIXER_KILL_SWITCH", "").lower() in {"1", "true", "yes"}:
            return True
        kill_file = BASE_DIR / "kill_switch.enabled"
        return kill_file.exists()

    def _build_pending_tasks(self) -> List[PendingTask]:
        tasks: List[PendingTask] = []
        files = glob.glob(os.path.join(self.data_dir, "*.json"))
        processed = self.state.state.get("processed_files", {})

        for path in files:
            try:
                mtime = os.path.getmtime(path)
            except OSError:
                continue
            record = processed.get(path)
            if record and record.get("mtime") == mtime:
                continue
            priority = self._estimate_priority(path)
            tasks.append(PendingTask(priority=priority, path=path, mtime=mtime))

        tasks.sort(reverse=True)
        return tasks

    def _estimate_priority(self, path: str) -> float:
        try:
            with open(path, "r") as fh:
                data = json.load(fh)
            findings = data if isinstance(data, list) else []
            best_payout = 0.0
            best_severity = 0
            for finding in findings:
                payout = float(finding.get("estimated_payout", 0) or 0)
                severity = finding.get("severity", "LOW").upper()
                severity_score = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "INFO": 0}.get(severity, 0)
                best_payout = max(best_payout, payout)
                best_severity = max(best_severity, severity_score)
            return (best_severity * 10) + min(best_payout / 100.0, 20)
        except Exception:
            return 0.0

    def run_once(self) -> int:
        if self.is_kill_switch_active():
            log_event("kill_switch", "Kill switch active, scheduler will not run.", {})
            return 0

        self.state.update(last_run_timestamp=datetime.now(timezone.utc).isoformat())
        self._write_heartbeat()
        tasks = self._build_pending_tasks()

        if not tasks:
            log_event("scheduler_idle", "No pending data files to process.", {"data_dir": self.data_dir})
            return 0

        if len(tasks) > self.config["queue_backpressure_threshold"]:
            log_event("backpressure", "Pending task queue exceeded threshold.", {"pending_tasks": len(tasks)})
            tasks = tasks[: self.config["max_tasks_per_cycle"]]

        selected = tasks[: self.config["max_tasks_per_cycle"]]
        data_paths = [task.path for task in selected]
        log_event("scheduler_run", "Processing queued tasks.", {"task_count": len(data_paths)})

        try:
            result = orchestrator.orchestrate_reports(
                data_paths=data_paths,
                data_dir=self.data_dir,
                reports_dir=self.reports_dir,
                programs_path=self.programs_path,
            )
            
            processed = result.get("processed", 0)
            total_findings = result.get("total_findings", 0)
            findings_by_program = result.get("findings_by_program", {})
            
            # Queue findings for submission
            if findings_by_program and safety_kernel.is_action_allowed("queue_findings"):
                # Load programs to pair with findings
                with open(self.programs_path, "r") as f:
                    programs = json.load(f)
                programs_by_id = {p.get("id", "").lower(): p for p in programs if p}
                
                queued_count = 0
                for program_id, findings in findings_by_program.items():
                    program = programs_by_id.get(program_id)
                    if program:
                        for finding in findings:
                            # Filter with report_filter for quality control
                            filtered = filter_findings([finding], program)
                            if filtered:
                                entry = report_queue.enqueue_finding(
                                    program, filtered[0],
                                    priority_score=float(finding.get("estimated_payout", 0) or 0)
                                )
                                if entry:
                                    queued_count += 1
                
                if queued_count > 0:
                    log_event("findings_queued", f"Queued {queued_count} findings for submission", {"count": queued_count})
            
            if processed:
                self.state.update(
                    last_report_generated=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H%M%SZ'),
                    last_failure_reason=None,
                    consecutive_failures=0,
                    backoff_seconds=self.config["backoff_base_seconds"],
                )
            
            for task in selected:
                self.state.mark_processed(task.path, task.mtime)
            
            log_event("scheduler_cycle_complete", f"Cycle complete", {
                "processed_reports": processed,
                "total_findings": total_findings,
            })
            
            return total_findings
        except Exception as exc:
            reason = str(exc)
            log_event("scheduler_error", "Scheduler run failed.", {"error": reason, "traceback": traceback.format_exc()})
            self.state.mark_failure(reason)
            if not safety_kernel.is_action_allowed("restart"):
                raise
            return 0

    def run_cycle(self) -> Dict[str, int]:
        """Run one full cycle and return results as dict."""
        findings_count = self.run_once()
        return {
            "total_findings": findings_count,
            "processed": findings_count,
        }

    def run(self):
        interval = self.config["interval_seconds"]
        backoff = self.state.state.get("backoff_seconds", self.config["backoff_base_seconds"])

        while not self._shutdown_requested:
            if self.is_kill_switch_active():
                log_event("kill_switch", "Scheduler detected kill switch and is exiting.", {})
                break

            processed = self.run_once()
            self._write_heartbeat()

            if self.state.state.get("consecutive_failures", 0) > 0:
                log_event("watchdog", "Scheduler will back off due to failure.", {"backoff_seconds": backoff})
                time.sleep(backoff)
                backoff = min(backoff * 2, self.config["max_backoff_seconds"])
            else:
                time.sleep(interval)

        log_event("scheduler_exit", "Scheduler stopped cleanly.", {"shutdown_requested": self._shutdown_requested})


def main():
    scheduler = AutonomousScheduler()
    scheduler.run()


if __name__ == "__main__":
    main()
