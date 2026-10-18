import json
from datetime import datetime
from pathlib import Path

from logtui.export import export_logs, export_to_string
from logtui.models import LogEntry


def test_export_to_jsonl(tmp_path: Path) -> None:
    dest = tmp_path / "out.jsonl"
    entries = [
        LogEntry(
            id=1,
            timestamp=datetime(2026, 10, 18, 12, 0, 0),
            level="INFO",
            service="api",
            message="ready",
            source="api.log",
            fields={"port": 8080},
        ),
        LogEntry(id=2, level="ERROR", message="fail", source="api.log"),
    ]

    count = export_logs(entries, dest)
    assert count == 2
    assert dest.is_file()

    lines = dest.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    obj = json.loads(lines[0])
    assert obj["level"] == "INFO"
    assert obj["fields"]["port"] == 8080


def test_export_to_json(tmp_path: Path) -> None:
    dest = tmp_path / "out.json"
    entries = [LogEntry(id=1, level="INFO", message="msg", source="src")]

    count = export_logs(entries, dest, format_type="json")
    assert count == 1

    content = json.loads(dest.read_text(encoding="utf-8"))
    assert isinstance(content, list)
    assert content[0]["level"] == "INFO"


def test_export_to_csv(tmp_path: Path) -> None:
    dest = tmp_path / "out.csv"
    entries = [
        LogEntry(
            id=1,
            timestamp=datetime(2026, 10, 18, 12, 0, 0),
            level="WARN",
            service="worker",
            message="slow",
            source="w.log",
            fields={"latency": 120},
        )
    ]

    count = export_logs(entries, dest, format_type="csv")
    assert count == 1

    content = dest.read_text(encoding="utf-8")
    assert "WARN" in content
    assert "worker" in content
    assert "slow" in content


def test_export_to_string() -> None:
    entries = [LogEntry(message="hello", source="src")]
    res = export_to_string(entries, "jsonl")
    assert '"message": "hello"' in res


def test_export_auto_detection(tmp_path: Path) -> None:
    entries = [LogEntry(id=1, message="hello", source="src")]
    p_json = tmp_path / "auto.json"
    p_csv = tmp_path / "auto.csv"
    p_ndjson = tmp_path / "auto.ndjson"

    export_logs(entries, p_json, "auto")
    export_logs(entries, p_csv, "auto")
    export_logs(entries, p_ndjson, "auto")

    assert p_json.read_text(encoding="utf-8").startswith("[")
    assert "message" in p_csv.read_text(encoding="utf-8")
    assert p_ndjson.read_text(encoding="utf-8").startswith("{")
