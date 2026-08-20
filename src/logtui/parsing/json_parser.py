import json
from datetime import datetime
from typing import Any

from logtui.models import LogEntry

TIMESTAMP_KEYS = ("timestamp", "time", "@timestamp", "datetime")
LEVEL_KEYS = ("level", "severity", "loglevel", "log_level")
MESSAGE_KEYS = ("message", "msg", "event")
SERVICE_KEYS = ("service", "logger", "component")


def _take(data: dict[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in data:
            return data.pop(key)
    return None


def _timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


class JsonParser:
    def parse(self, line: str, source: str) -> LogEntry:
        decoded = json.loads(line)
        if not isinstance(decoded, dict):
            raise ValueError("JSON log entries must be objects")
        data = dict(decoded)
        timestamp_value = _take(data, TIMESTAMP_KEYS)
        level = _take(data, LEVEL_KEYS)
        service = _take(data, SERVICE_KEYS)
        message = _take(data, MESSAGE_KEYS)
        return LogEntry(
            timestamp=_timestamp(timestamp_value),
            level=str(level).upper() if level is not None else None,
            service=str(service) if service is not None else None,
            message=str(message) if message is not None else line.rstrip("\r\n"),
            source=source,
            fields=data,
            raw=line.rstrip("\r\n"),
        )
