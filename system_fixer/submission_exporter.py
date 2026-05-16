import os
from system_fixer.submission_formatter import format_submission

OUTPUT_DIR = "submissions"

def export_submissions(findings):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    exported = 0

    for f in findings:
        title = f.get("title", "untitled").replace(" ", "_").replace("/", "_")
        program = f.get("program", "unknown_program").replace(" ", "_")
        filename = f"{program}__{title}.md".lower()

        path = os.path.join(OUTPUT_DIR, filename)
        content = format_submission(f)

        try:
            with open(path, "w", encoding="utf-8") as file:
                file.write(content)
            exported += 1
        except Exception as e:
            print(f"[submission_exporter] Error writing {filename}: {e}")

    print(f"[submission_exporter] Exported {exported} submissions to {OUTPUT_DIR}")
    return exported
