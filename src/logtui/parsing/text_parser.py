import re
from datetime import datetime

from logtui.models import LogEntry

PYTHON_LOG = re.compile(
    r"^(?P<timestamp>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:[,.]\d+)?)"
    r"\s+(?:-\s+)?(?P<level>DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL)"
    r"\s+(?:-\s+)?(?P<message>.*)$",
    re.IGNORECASE,
)

BRACKET_LOG = re.compile(
    r"^\[?(?P<timestamp>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}"
    r"(?:[,.]\d+)?(?:Z|[+-]\d{2}:?\d{2})?)\]?"
    r"\s*(?:\[(?P<level>[A-Za-z]+)\]|"
    r"(?P<level_bare>DEBUG|INFO|WARNING|WARN|ERROR|CRITICAL|TRACE|FATAL))"
    r"\s*(?:\[(?P<service>[^\]]+)\]\s*)?(?:[-:]\s*)?(?P<message>.*)$",
    re.IGNORECASE,
)

LOGFMT_KV = re.compile(r'([a-zA-Z0-9_]+)=(?:"([^"]*)"|(\S+))')


def _parse_timestamp(value: str) -> datetime | None:
    sanitized = value.strip().replace("Z", "+00:00").replace(",", ".")
    try:
        return datetime.fromisoformat(sanitized)
    except ValueError:
        return None


class TextParser:
    def parse(self, line: str, source: str) -> LogEntry:
        raw = line.rstrip("\r\n")
        match = PYTHON_LOG.match(raw)
        if match:
            return LogEntry(
                timestamp=_parse_timestamp(match.group("timestamp")),
                level=match.group("level").upper(),
                message=match.group("message"),
                source=source,
                raw=raw,
            )

        match = BRACKET_LOG.match(raw)
        if match:
            level = match.group("level") or match.group("level_bare")
            return LogEntry(
                timestamp=_parse_timestamp(match.group("timestamp")),
                level=level.upper() if level else None,
                service=match.group("service"),
                message=match.group("message"),
                source=source,
                raw=raw,
            )

        if "level=" in raw or "msg=" in raw:
            kvs: dict[str, str] = {}
            for m in LOGFMT_KV.finditer(raw):
                k = m.group(1)
                v = m.group(2) if m.group(2) is not None else m.group(3)
                kvs[k] = v
            if ("level" in kvs or "msg" in kvs or "message" in kvs) and len(kvs) >= 2:
                ts_val = kvs.pop("time", None) or kvs.pop("timestamp", None)
                lvl_val = kvs.pop("level", None)
                msg_val = kvs.pop("msg", None) or kvs.pop("message", None) or raw
                srv_val = kvs.pop("service", None) or kvs.pop("component", None)
                return LogEntry(
                    timestamp=_parse_timestamp(ts_val) if ts_val else None,
                    level=lvl_val.upper() if lvl_val else None,
                    service=srv_val,
                    message=msg_val,
                    source=source,
                    fields=kvs,
                    raw=raw,
                )

        return LogEntry(message=raw, source=source, raw=raw)
