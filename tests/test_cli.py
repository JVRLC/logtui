from pathlib import Path

import pytest
from typer.testing import CliRunner

from logtui.cli import app
from logtui.sources import FileSource, StdinSource
from logtui.tui import LogTuiApp

runner = CliRunner()


def test_rejects_missing_file() -> None:
    result = runner.invoke(app, ["missing.log"])

    assert result.exit_code == 2
    assert "file not found" in result.output


def test_rejects_duplicate_stdin() -> None:
    result = runner.invoke(app, ["-", "-"])

    assert result.exit_code == 2
    assert "stdin may only be specified once" in result.output


def test_builds_file_and_stdin_sources(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "app.log"
    path.write_text("ready\n", encoding="utf-8")
    launched: list[LogTuiApp] = []
    monkeypatch.setattr(LogTuiApp, "run", lambda instance: launched.append(instance))

    result = runner.invoke(app, [str(path), "-", "--buffer-size", "42"])

    assert result.exit_code == 0
    assert len(launched) == 1
    assert launched[0].entries.capacity == 42
    assert isinstance(launched[0].sources[0], FileSource)
    assert isinstance(launched[0].sources[1], StdinSource)


def test_headless_jsonl_output(tmp_path: Path) -> None:
    path = tmp_path / "app.log"
    path.write_text('{"level":"INFO","message":"ready"}\n', encoding="utf-8")

    result = runner.invoke(app, [str(path), "--jsonl"])
    assert result.exit_code == 0
    assert '"level":"INFO"' in result.output
    assert '"message":"ready"' in result.output


def test_headless_plaintext_output(tmp_path: Path) -> None:
    path = tmp_path / "app.log"
    path.write_text('{"level":"INFO","message":"ready"}\n', encoding="utf-8")

    result = runner.invoke(app, [str(path), "--headless", "--query", "ready"])
    assert result.exit_code == 0
    assert "ready" in result.output
    assert "INFO" in result.output


def test_cli_initial_level(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "app.log"
    path.write_text("ready\n", encoding="utf-8")
    launched: list[LogTuiApp] = []
    monkeypatch.setattr(LogTuiApp, "run", lambda instance: launched.append(instance))

    result = runner.invoke(app, [str(path), "--level", "WARN"])
    assert result.exit_code == 0
    assert len(launched) == 1
    assert launched[0].level_filter_index == 3  # WARN+


def test_headless_export_to_file(tmp_path: Path) -> None:
    path = tmp_path / "app.log"
    out = tmp_path / "filtered.jsonl"
    path.write_text(
        '{"level":"INFO","message":"hello"}\n{"level":"ERROR","message":"critical failure"}\n',
        encoding="utf-8",
    )

    result = runner.invoke(app, [str(path), "--level", "ERROR", "--export", str(out)])
    assert result.exit_code == 0
    assert out.is_file()
    content = out.read_text(encoding="utf-8")
    assert "critical failure" in content
    assert "hello" not in content


def test_cli_docker_source(monkeypatch: pytest.MonkeyPatch) -> None:
    launched: list[LogTuiApp] = []
    monkeypatch.setattr(LogTuiApp, "run", lambda instance: launched.append(instance))

    result = runner.invoke(app, ["docker:my-api"])
    assert result.exit_code == 0
    assert len(launched) == 1
    assert launched[0].sources[0].name == "docker:my-api"


def test_cli_wait_for_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    path = tmp_path / "future.log"
    launched: list[LogTuiApp] = []
    monkeypatch.setattr(LogTuiApp, "run", lambda instance: launched.append(instance))

    result = runner.invoke(app, [str(path), "--wait"])
    assert result.exit_code == 0
    assert len(launched) == 1
    file_source = launched[0].sources[0]
    assert isinstance(file_source, FileSource)
    assert file_source.wait_for_creation is True
