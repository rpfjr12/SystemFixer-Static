import datetime

TEMPLATE_PATH = "system-fixer/templates/submission_template.md"

def load_template():
    with open(TEMPLATE_PATH, "r") as f:
        return f.read()

def format_submission(program, finding):
    template = load_template()

    return template.format(
        program=program,
        title=finding.get("title", "Untitled Finding"),
        severity=finding.get("severity", "LOW"),
        score=finding.get("score", 0),
        impact=finding.get("impact", "No impact provided"),
        description=finding.get("description", "No description provided"),
        steps=finding.get("steps", "No steps provided"),
        timestamp=datetime.datetime.utcnow().isoformat() + "Z"
    )
