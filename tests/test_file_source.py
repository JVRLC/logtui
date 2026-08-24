import asyncio
from pathlib import Path

from logtui.sources import FileSource


async def test_reads_existing_content_and_follows_append(tmp_path: Path) -> None:
    path = tmp_path / "app.log"
    path.write_text("first\n", encoding="utf-8")
    lines = FileSource(path, poll_interval=0.01).lines()
    assert await anext(lines) == "first\n"
    with path.open("a", encoding="utf-8") as stream:
        stream.write("second\n")
    assert await asyncio.wait_for(anext(lines), timeout=0.2) == "second\n"
    await lines.aclose()


async def test_follows_replaced_file(tmp_path: Path) -> None:
    path = tmp_path / "app.log"
    path.write_text("before\n", encoding="utf-8")
    lines = FileSource(path, poll_interval=0.01).lines()
    assert await anext(lines) == "before\n"

    replacement = tmp_path / "replacement.log"
    replacement.write_text("after\n", encoding="utf-8")
    replacement.replace(path)

    assert await asyncio.wait_for(anext(lines), timeout=0.2) == "after\n"
    await lines.aclose()


async def test_reads_from_start_after_truncation(tmp_path: Path) -> None:
    path = tmp_path / "app.log"
    path.write_text("a much longer first line\n", encoding="utf-8")
    lines = FileSource(path, poll_interval=0.01).lines()
    assert await anext(lines) == "a much longer first line\n"

    path.write_text("new\n", encoding="utf-8")

    assert await asyncio.wait_for(anext(lines), timeout=0.2) == "new\n"
    await lines.aclose()
