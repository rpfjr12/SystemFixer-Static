from system_fixer.submission_exporter import export_submissions
from system_fixer.submission_formatter import format_submission

def generate_submission_preview(finding):
    """
    Returns a formatted submission preview (string),
    without writing anything to disk.
    """
    return format_submission(finding)

def export_all_submissions(findings):
    """
    Formats and exports all findings into Markdown files.
    Returns the number of exported submissions.
    """
    print("[submission_manager] Exporting submissions...")
    count = export_submissions(findings)
    print(f"[submission_manager] Export complete: {count} files written")
    return count

def run_submission_pipeline(findings):
    """
    Full submission pipeline:
    - preview first finding
    - export all findings
    - return summary
    """
    print("[submission_manager] Running submission pipeline...")

    preview = None
    if findings:
        preview = generate_submission_preview(findings[0])
        print("[submission_manager] Preview generated for first finding")

    exported = export_all_submissions(findings)

    print("[submission_manager] Submission pipeline complete")

    return {
        "preview": preview,
        "exported_count": exported
    }
