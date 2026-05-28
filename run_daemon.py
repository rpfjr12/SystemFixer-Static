#!/usr/bin/env python3
"""Main entry point for autonomous vulnerability detection and reporting daemon."""

import sys
import argparse
from pathlib import Path

# Add parent dir to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from system_fixer.daemon import (
    start_daemon,
    stop_daemon,
    get_daemon_status,
    restart_daemon,
    log,
)
from system_fixer.report_queue import report_queue
from system_fixer.revenue_tracker import revenue_tracker
from system_fixer.roi_optimizer import roi_optimizer
from system_fixer.loader import load_programs
import json


def cmd_start(args):
    """Start the autonomous daemon."""
    log("Starting autonomous vulnerability scanner daemon...", "INFO")
    start_daemon(foreground=args.foreground)


def cmd_stop(args):
    """Stop the running daemon."""
    if stop_daemon():
        log("Daemon stopped", "INFO")
    else:
        log("Failed to stop daemon", "ERROR")


def cmd_status(args):
    """Show daemon status."""
    status = get_daemon_status()
    print("\n" + "=" * 60)
    print("AUTONOMOUS DAEMON STATUS")
    print("=" * 60)
    print(f"Running:              {status['is_running']}")
    print(f"Status:               {status['status']}")
    if status['pid']:
        print(f"PID:                  {status['pid']}")
    if status.get('started'):
        print(f"Uptime:               {status.get('uptime_readable', 'N/A')}")
    print(f"Scan Cycles:          {status['cycles_completed']}")
    print(f"Total Findings:       {status['total_findings']}")
    print(f"Queued for Submission: {status['total_queued']}")
    print(f"Est. Daily Revenue:   ${status['estimated_daily_revenue']:.2f}")
    if status['error_count'] > 0:
        print(f"Errors:               {status['error_count']}")
        print(f"Last Error:           {status['last_error']}")
    print("=" * 60 + "\n")


def cmd_restart(args):
    """Restart the daemon."""
    log("Restarting daemon...", "INFO")
    restart_daemon()
    status = get_daemon_status()
    print(f"Daemon restarted. PID: {status['pid']}")


def cmd_queue_status(args):
    """Show submission queue status."""
    stats = report_queue.get_queue_stats()
    print("\n" + "=" * 60)
    print("SUBMISSION QUEUE STATUS")
    print("=" * 60)
    print(f"Total Queued:         {stats['total_queued']}")
    for status, count in stats['status_breakdown'].items():
        print(f"  {status.capitalize():20} {count}")
    print(f"Estimated Value:      ${stats['total_estimated_value']:.2f}")
    print("=" * 60 + "\n")


def cmd_roi_report(args):
    """Show ROI analysis and opportunities."""
    opportunities = roi_optimizer.get_top_opportunity_areas()
    programs = load_programs()
    estimates = roi_optimizer.estimate_expected_revenue(programs)

    print("\n" + "=" * 60)
    print("REVENUE OPPORTUNITY ANALYSIS")
    print("=" * 60)

    print("\nEXPECTED REVENUE (if scanning all active programs):")
    print(f"  Daily:    ${estimates['estimated_daily_revenue']:.2f}")
    print(f"  Weekly:   ${estimates['estimated_weekly_revenue']:.2f}")
    print(f"  Monthly:  ${estimates['estimated_monthly_revenue']:.2f}")

    print("\nTOP REVENUE PROGRAMS (30-day history):")
    for prog in opportunities['top_revenue_programs']:
        print(f"  {prog['program']:20} Daily: ${prog['daily_roi']:8.2f}  "
              f"Avg: ${prog['avg_payout']:7.2f}  Count: {prog['count']}")

    print("\nTOP VULNERABILITY TYPES (30-day history):")
    for vuln in opportunities['top_vulnerability_types']:
        print(f"  {vuln['vulnerability']:30} Daily: ${vuln['daily_roi']:8.2f}  "
              f"Avg: ${vuln['avg_payout']:7.2f}  Count: {vuln['count']}")

    print("\nRECOMMENDED SCAN ORDER (by ROI):")
    ranked = roi_optimizer.get_recommended_scan_order(programs)
    for i, prog in enumerate(ranked[:10], 1):
        interval = prog.get('recommended_scan_interval_hours', 'N/A')
        roi = prog.get('estimated_daily_roi', 0)
        print(f"  {i:2}. {prog['name']:25} Daily ROI: ${roi:8.2f}  "
              f"Scan every {interval}h")

    print("=" * 60 + "\n")


def cmd_export_queue(args):
    """Export queued findings for manual submission."""
    by_platform = report_queue.export_for_manual_submission()
    
    output_file = args.output or Path("queued_findings_export.json")
    
    with open(output_file, "w") as f:
        json.dump(by_platform, f, indent=2)
    
    total = sum(len(findings) for findings in by_platform.values())
    print(f"Exported {total} queued findings to {output_file}")
    
    for platform, findings in by_platform.items():
        print(f"  {platform}: {len(findings)} findings")


def main():
    parser = argparse.ArgumentParser(
        description="Autonomous vulnerability scanner and bounty platform integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s start              # Start the daemon in background
  %(prog)s start --foreground # Start in foreground for debugging
  %(prog)s status             # Show daemon and queue status
  %(prog)s roi-report         # Show revenue opportunities
  %(prog)s export-queue       # Export findings for manual submission
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Start command
    start_parser = subparsers.add_parser("start", help="Start autonomous daemon")
    start_parser.add_argument(
        "--foreground",
        action="store_true",
        help="Run in foreground (for debugging)",
    )
    start_parser.set_defaults(func=cmd_start)

    # Stop command
    stop_parser = subparsers.add_parser("stop", help="Stop the running daemon")
    stop_parser.set_defaults(func=cmd_stop)

    # Status command
    status_parser = subparsers.add_parser("status", help="Show daemon status")
    status_parser.set_defaults(func=cmd_status)

    # Restart command
    restart_parser = subparsers.add_parser("restart", help="Restart the daemon")
    restart_parser.set_defaults(func=cmd_restart)

    # Queue status command
    queue_parser = subparsers.add_parser("queue", help="Show submission queue status")
    queue_parser.set_defaults(func=cmd_queue_status)

    # ROI report command
    roi_parser = subparsers.add_parser("roi-report", help="Show ROI analysis and opportunities")
    roi_parser.set_defaults(func=cmd_roi_report)

    # Export queue command
    export_parser = subparsers.add_parser("export-queue", help="Export queued findings")
    export_parser.add_argument(
        "-o", "--output",
        help="Output file (default: queued_findings_export.json)",
    )
    export_parser.set_defaults(func=cmd_export_queue)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        args.func(args)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
