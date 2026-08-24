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
