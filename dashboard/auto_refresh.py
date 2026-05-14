import time
import threading
from dashboard.regenerator import regenerate_dashboard

class DashboardAutoRefresher:
    """
    Automatically regenerates the dashboard at a fixed interval.
    """

    def __init__(self, program, findings_path, interval_seconds=60):
        self.program = program
        self.findings_path = findings_path
        self.interval = interval_seconds
        self._running = False
        self._thread = None

    def _loop(self):
        while self._running:
            regenerate_dashboard(self.program, self.findings_path)
            time.sleep(self.interval)

    def start(self):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
