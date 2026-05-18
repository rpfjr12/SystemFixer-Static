import requests
import json

SOURCES = {
    "hackerone": "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/hackerone_data.json",
    "bugcrowd": "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/bugcrowd_data.json",
    "intigriti": "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/intigriti_data.json",
    "yeswehack": "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/yeswehack_data.json"
}

def fetch_source(url):
    try:
        data = requests.get(url, timeout=10).json()
        return [p["url"] for p in data if "url" in p]
    except:
        return []

def fetch_all_programs():
    programs = set()
    for name, url in SOURCES.items():
        programs.update(fetch_source(url))
    return sorted(list(programs))

def write_programs_json(path="programs.json"):
    programs = fetch_all_programs()
    with open(path, "w") as f:
        json.dump({"programs": programs}, f, indent=2)
