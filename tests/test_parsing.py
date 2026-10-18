from datetime import UTC, datetime

from logtui.parsing import AutoDetectParser


def test_parses_json_and_preserves_dynamic_fields() -> None:
    entry = AutoDetectParser().parse(
        '{"timestamp":"2026-08-20T14:31:05Z","level":"error",'
        '"service":"api","message":"Database timeout","request_id":"abc123"}',
        "app.log",
    )
    assert entry.timestamp == datetime(2026, 8, 20, 14, 31, 5, tzinfo=UTC)
    assert entry.level == "ERROR"
    assert entry.service == "api"
    assert entry.message == "Database timeout"
    assert entry.fields == {"request_id": "abc123"}


def test_invalid_json_falls_back_to_plain_text() -> None:
    entry = AutoDetectParser().parse("{not json}\n", "app.log")
    assert entry.message == "{not json}"
    assert entry.raw == "{not json}"


def test_parses_standard_python_log() -> None:
    entry = AutoDetectParser().parse(
        "2026-08-20 14:31:05,123 - ERROR - Database timeout", "app.log"
    )
    assert entry.level == "ERROR"
    assert entry.message == "Database timeout"
    assert entry.timestamp == datetime(2026, 8, 20, 14, 31, 5, 123000)


def test_parses_bracketed_log() -> None:
    entry = AutoDetectParser().parse(
        "[2026-08-20 14:31:05] [WARN] [worker] High memory usage", "worker.log"
    )
    assert entry.level == "WARN"
    assert entry.service == "worker"
    assert entry.message == "High memory usage"
    assert entry.timestamp == datetime(2026, 8, 20, 14, 31, 5)


def test_parses_logfmt() -> None:
    entry = AutoDetectParser().parse(
        'time="2026-08-20T14:31:05Z" level=info msg="Server started" component=web port=8080',
        "app.log",
    )
    assert entry.level == "INFO"
    assert entry.service == "web"
    assert entry.message == "Server started"
    assert entry.fields == {"port": "8080"}
    assert entry.timestamp == datetime(2026, 8, 20, 14, 31, 5, tzinfo=UTC)
