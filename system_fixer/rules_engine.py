import json
import os

RULES_FILE = "system_fixer/program_rules.json"

def load_rules():
    if not os.path.exists(RULES_FILE):
        print(f"[rules_engine] No rules file found at {RULES_FILE}, using empty ruleset")
        return {}

    try:
        with open(RULES_FILE, "r", encoding="utf-8") as f:
            rules = json.load(f)
            print(f"[rules_engine] Loaded rules for {len(rules)} programs")
            return rules
    except Exception as e:
        print(f"[rules_engine] Error loading rules: {e}")
        return {}

def apply_program_rules(finding, rules):
    program = finding.get("program", "")
    if program not in rules:
        return finding  # no rules for this program

    program_rules = rules[program]

    # Apply exclusions
    excluded_tags = program_rules.get("exclude_tags", [])
    intel = finding.get("intelligence", {})
    tags = intel.get("tags", [])

    if any(tag in excluded_tags for tag in tags):
        finding["excluded_by_rules"] = True
        return finding

    # Apply severity boosts
    severity_boosts = program_rules.get("severity_boosts", {})
    sev = finding.get("severity", "")

    if sev in severity_boosts:
        finding["severity"] = severity_boosts[sev]

    # Apply money score boosts
    money_boost = program_rules.get("money_boost", 0)
    finding["money_score"] = finding.get("money_score", 0) + money_boost

    return finding

def apply_rules_to_all(findings):
    rules = load_rules()
    updated = []

    for f in findings:
        updated.append(apply_program_rules(f, rules))

    print(f"[rules_engine] Applied rules to {len(updated)} findings")
    return updated
