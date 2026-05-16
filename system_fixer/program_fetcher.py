import requests
import json

def fetch_hackerone():
    url = "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/hackerone_data.json"
    try:
        data = requests.get(url, timeout=10).json()
        return [p["url"] for p in data if "url" in p]
    except:
        return []

def fetch_bugcrowd():
    url = "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/bugcrowd_data.json"
    try:
        data = requests.get(url, timeout=10).json()
        return [p["url"] for p in data if "url" in p]
    except:
        return []

def fetch_intigriti():
    url = "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/intigriti_data.json"
    try:
        data = requests.get(url, timeout=10).json()
        return [p["url"] for p in data if "url" in p]
    except:
        return []

def fetch_yeswehack():
    url = "https://raw.githubusercontent.com/arkadiyt/bounty-targets-data/master/data/yeswehack_data.json"
    try:
        data = requests.get(url, timeout=10).json()
        return [p["url"] for p in data if "url" in p]
    except:
        return []

def fetch_all_programs():
    programs = set()

    programs.update(fetch_hackerone())
    programs.update(fetch_bugcrowd())
    programs.update(fetch_intigriti())
    programs.update(fetch_yeswehack())

    return sorted(list(programs))

def write_programs_json(path="programs.json"):
    programs = fetch_all_programs()
    with open(path, "w") as f:
        json.dump({"programs": programs}, f, indent=2)
