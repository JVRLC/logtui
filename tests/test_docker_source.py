import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from logtui.sources.docker import DockerSource


async def test_docker_source_missing_binary(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("shutil.which", lambda _: None)
    source = DockerSource("my-container")

    with pytest.raises(RuntimeError, match="docker binary not found"):
        async for _ in source.lines():
            pass


def test_docker_source_name() -> None:
    source = DockerSource("web-api")
    assert source.name == "docker:web-api"
    assert source.container == "web-api"


async def test_docker_source_streams_lines(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("shutil.which", lambda _: "/usr/local/bin/docker")

    mock_stdout = MagicMock()
    # simulate 2 lines then EOF
    mock_stdout.readline = AsyncMock(side_effect=[b"line 1\n", b"line 2\n", b""])

    mock_process = MagicMock()
    mock_process.stdout = mock_stdout
    mock_process.returncode = None
    mock_process.terminate = MagicMock()
    mock_process.wait = AsyncMock()

    monkeypatch.setattr(asyncio, "create_subprocess_exec", AsyncMock(return_value=mock_process))

    source = DockerSource("test-app")
    collected = [line async for line in source.lines()]

    assert collected == ["line 1\n", "line 2\n"]
    mock_process.terminate.assert_called_once()
