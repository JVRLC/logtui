from logtui.models import LogEntry
from logtui.parsing.multiline import is_continuation_line, merge_continuation


def test_is_continuation_line() -> None:
    assert is_continuation_line("  File 'app.py', line 42")
    assert is_continuation_line("\tat com.example.MyService.run(MyService.java:10)")
    assert is_continuation_line("Traceback (most recent call last):")
    assert is_continuation_line("Caused by: java.io.IOException")
    assert is_continuation_line("ValueError: invalid input")

    assert not is_continuation_line("2026-10-18 12:00:00 - INFO - Starting service")
    assert not is_continuation_line('{"level":"INFO","message":"hello"}')
    assert not is_continuation_line("")


def test_merge_continuation() -> None:
    entry = LogEntry(level="INFO", message="Exception caught", source="api.log")
    merge_continuation(entry, "Traceback (most recent call last):")
    merge_continuation(entry, "  File 'app.py', line 10, in run")
    merge_continuation(entry, "ZeroDivisionError: division by zero")

    assert "ZeroDivisionError" in entry.message
    assert entry.level == "ERROR"
    assert entry.raw is not None and "Traceback" in entry.raw
