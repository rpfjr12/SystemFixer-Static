import os
import datetime

LOG_PATH = "system-fixer/system.log"

def log(message):
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{timestamp}] {message}\n"

    directory = os.path.dirname(LOG_PATH)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    with open(LOG_PATH, "a") as f:
        f.write(line)
