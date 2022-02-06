from collections import namedtuple
from time import time
from typing import Optional

LogEntry = namedtuple("LogEntry", ["time", "value", "unit"])

class Logger:
    def __init__(self, output: Optional[str] = None):
        self.loop = None
        self.queue = None

        if not output:
            output = f"{time}-dmm-log.csv"
    
    def start(self):
        def _logger():
            self.running = True

            self.running = False
        pass

    def stop(self):
        pass

    def log(self, entry: LogEntry):
        pass

    def running(self) -> bool:
        pass
