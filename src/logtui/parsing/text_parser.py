import re
from datetime import datetime

from logtui.models import LogEntry

PYTHON_LOG = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:[,.]\d+)?)"
    r"\s+(?:-\s+)?(?P<level>DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL)"
    r"\s+(?:-\s+)?(?P<message>.*)$",
    re.IGNORECASE,
)


class TextParser:
    def parse(self, line: str, source: str) -> LogEntry:
        raw = line.rstrip("\r\n")
        match = PYTHON_LOG.match(raw)
        if not match:
            return LogEntry(message=raw, source=source, raw=raw)
        value = match.group("timestamp").replace(",", ".")
        try:
            timestamp = datetime.fromisoformat(value)
        except ValueError:
            timestamp = None
        return LogEntry(
            timestamp=timestamp,
            level=match.group("level").upper(),
            message=match.group("message"),
            source=source,
            raw=raw,
        )
