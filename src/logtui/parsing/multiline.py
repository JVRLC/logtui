import re

from logtui.models import LogEntry

CONTINUATION_PATTERNS = [
    re.compile(r"^\s+"),  # Starts with whitespace or tab
    re.compile(r"^Traceback \(most recent call last\):", re.IGNORECASE),
    re.compile(r"^Caused by:", re.IGNORECASE),
    re.compile(r"^\s*at\s+[\w\.\$]+\(", re.IGNORECASE),  # Java stacktrace
    re.compile(r"^(?:[\w\.]+Exception|[\w\.]+Error):", re.IGNORECASE),
    re.compile(r"^\t+"),
]


def is_continuation_line(line: str) -> bool:
    """Check if a line is a stacktrace or multi-line continuation."""
    stripped = line.rstrip("\r\n")
    if not stripped:
        return False
    return any(pattern.search(stripped) is not None for pattern in CONTINUATION_PATTERNS)


def merge_continuation(entry: LogEntry, line: str) -> None:
    """Append a continuation line to an existing log entry."""
    stripped = line.rstrip("\r\n")
    entry.message = f"{entry.message}\n{stripped}"
    if entry.raw is not None:
        entry.raw = f"{entry.raw}\n{stripped}"
    else:
        entry.raw = entry.message

    # Auto-elevate level to ERROR if a traceback or exception is detected
    if (not entry.level or entry.level.upper() in ("DEBUG", "INFO")) and (
        "traceback" in stripped.casefold() or "exception" in stripped.casefold()
    ):
        entry.level = "ERROR"
