import json
import os
from datetime import datetime, timezone

EVENT_LOG_PATH = "system-fixer/events.log"


def _ensure_dir():
    directory = os.path.dirname(EVENT_LOG_PATH)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)


def log_event(event_type, message, metadata=None):
    _ensure_dir()
    entry = {
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "event": event_type,
        "message": message,
        "metadata": metadata or {},
    }
    with open(EVENT_LOG_PATH, "a") as fh:
        fh.write(json.dumps(entry) + "\n")
    return entry
