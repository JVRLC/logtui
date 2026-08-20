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
