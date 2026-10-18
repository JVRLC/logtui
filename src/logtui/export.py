import csv
import io
import json
from collections.abc import Iterable
from pathlib import Path
from typing import TextIO

from logtui.models import LogEntry


def export_logs(
    entries: Iterable[LogEntry],
    target: Path | str | TextIO,
    format_type: str = "jsonl",
) -> int:
    """Export log entries to JSONL, JSON, or CSV.

    Returns the count of exported entries.
    """
    entries_list = list(entries)
    fmt = format_type.lower().strip().lstrip(".")

    if isinstance(target, (str, Path)):
        path = Path(target)
        # Infer format from extension if not explicitly specified
        if not format_type or format_type == "auto":
            ext = path.suffix.lower().lstrip(".")
            if ext in ("jsonl", "ndjson"):
                fmt = "jsonl"
            elif ext == "json":
                fmt = "json"
            elif ext == "csv":
                fmt = "csv"
            else:
                fmt = "jsonl"

        with path.open("w", encoding="utf-8") as stream:
            return _write_to_stream(entries_list, stream, fmt)

    return _write_to_stream(entries_list, target, fmt)


def _write_to_stream(entries: list[LogEntry], stream: TextIO, fmt: str) -> int:
    if fmt == "json":
        data = [entry.model_dump(mode="json") for entry in entries]
        json.dump(data, stream, indent=2, default=str)
        stream.write("\n")
        return len(entries)

    if fmt == "csv":
        writer = csv.writer(stream)
        writer.writerow(["id", "timestamp", "level", "service", "source", "message", "fields"])
        for entry in entries:
            ts = entry.timestamp.isoformat() if entry.timestamp else ""
            fields_str = json.dumps(entry.fields, default=str) if entry.fields else ""
            writer.writerow(
                [
                    entry.id if entry.id is not None else "",
                    ts,
                    entry.level or "",
                    entry.service or "",
                    entry.source or "",
                    entry.message,
                    fields_str,
                ]
            )
        return len(entries)

    # Default: jsonl
    for entry in entries:
        stream.write(json.dumps(entry.model_dump(mode="json"), default=str) + "\n")
    return len(entries)


def export_to_string(entries: Iterable[LogEntry], format_type: str = "jsonl") -> str:
    """Export log entries to a string in the specified format."""
    buffer = io.StringIO()
    export_logs(entries, buffer, format_type)
    return buffer.getvalue()
