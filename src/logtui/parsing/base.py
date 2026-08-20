from typing import Protocol

from logtui.models import LogEntry


class LogParser(Protocol):
    def parse(self, line: str, source: str) -> LogEntry: ...
