"""Utility script to record payouts and update learning models from bounty platform submissions."""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add parent dir to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from system_fixer.revenue_tracker import revenue_tracker
from system_fixer.learning_engine import learning_engine
from system_fixer.report_queue import report_queue


def record_submission_payout(
    program_id: str,
    vulnerability_type: str,
    payout_amount: float,
    severity: str,
    time_to_acceptance_hours: float,
    submission_id: Optional[str] = None,
    notes: str = "",
):
    """Record a confirmed payout from a bounty platform submission."""
    
    # Record in revenue tracker
    entry = revenue_tracker.record_payout(
        program_id=program_id,
        vulnerability_type=vulnerability_type,
        payout_amount=payout_amount,
        severity=severity,
        time_to_acceptance_hours=time_to_acceptance_hours,
        submission_id=submission_id,
    )
    
    # Update submission status in queue if matching submission_id
    if submission_id:
        report_queue.mark_paid(submission_id, payout_amount)
    
    print(f"✓ Recorded payout: ${payout_amount} for {program_id}/{vulnerability_type}")
    print(f"  Severity: {severity}, Hours to acceptance: {time_to_acceptance_hours}")
    
    if notes:
        print(f"  Notes: {notes}")
    
    # Save updated ROI reports
    revenue_tracker.save_roi_reports()
    print("✓ ROI reports updated")
    
    return entry


def batch_import_payouts(csv_file: str):
    """Import payouts from a CSV file.
    
    CSV format:
    program_id,vulnerability_type,payout_amount,severity,hours_to_acceptance,submission_id,notes
    coinbase,reflected_xss,150,HIGH,24,sub_abc123,"Fast triage"
    """
    
    import csv
    
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            try:
                record_submission_payout(
                    program_id=row['program_id'],
                    vulnerability_type=row['vulnerability_type'],
                    payout_amount=float(row['payout_amount']),
                    severity=row['severity'],
                    time_to_acceptance_hours=float(row['hours_to_acceptance']),
                    submission_id=row.get('submission_id'),
                    notes=row.get('notes', ''),
                )
                count += 1
            except Exception as e:
                print(f"✗ Error importing row {count + 1}: {e}")
    
    print(f"\n✓ Imported {count} payouts")


def interactive_payout_recording():
    """Interactive CLI for recording payouts one at a time."""
    
    print("\n" + "=" * 60)
    print("PAYOUT RECORDING UTILITY")
    print("=" * 60)
    
    programs = [
        "coinbase", "kraken", "binance", "stripe", "paypal",
        "cloudflare", "digitalocean", "gitlab", "dropbox", "hackerone"
    ]
    
    print("\nAvailable programs:")
    for i, prog in enumerate(programs, 1):
        print(f"  {i}. {prog}")
    
    while True:
        program_idx = input("\nSelect program (number or name, or 'quit'): ").strip().lower()
        
        if program_idx == 'quit':
            break
        
        # Try to parse as number or name
        try:
            if program_idx.isdigit():
                program_id = programs[int(program_idx) - 1]
            else:
                if program_idx in programs:
                    program_id = program_idx
                else:
                    print("Invalid program")
                    continue
        except (IndexError, ValueError):
            print("Invalid selection")
            continue
        
        # Get vulnerability type
        vuln_type = input("Vulnerability type (e.g., 'reflected_xss', 'csrf'): ").strip().lower().replace(" ", "_")
        if not vuln_type:
            print("Vulnerability type required")
            continue
        
        # Get payout amount
        try:
            payout = float(input("Payout amount ($): ").strip())
        except ValueError:
            print("Invalid amount")
            continue
        
        # Get severity
        severity = input("Severity (CRITICAL/HIGH/MEDIUM/LOW): ").strip().upper()
        if severity not in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            severity = "HIGH"
        
        # Get time to acceptance
        try:
            hours = float(input("Hours to acceptance: ").strip())
        except ValueError:
            hours = 24
        
        # Optional fields
        submission_id = input("Submission ID (optional): ").strip() or None
        notes = input("Notes (optional): ").strip() or None
        
        # Record it
        record_submission_payout(
            program_id=program_id,
            vulnerability_type=vuln_type,
            payout_amount=payout,
            severity=severity,
            time_to_acceptance_hours=hours,
            submission_id=submission_id,
            notes=notes,
        )
        
        print(f"\n✓ Payout recorded. Estimated daily ROI from {program_id}: "
              f"${revenue_tracker.rank_programs_by_roi(30)[0][1]:.2f}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "batch" and len(sys.argv) > 2:
            batch_import_payouts(sys.argv[2])
        else:
            print(f"Usage: {sys.argv[0]} [batch <csv_file>]")
            print("\nIf no arguments provided, launches interactive mode")
            interactive_payout_recording()
    else:
        interactive_payout_recording()
