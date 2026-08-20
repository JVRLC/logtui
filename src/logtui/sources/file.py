import asyncio
from collections.abc import AsyncIterator
from pathlib import Path


class FileSource:
    """Read a file from the beginning, then follow appended lines."""

    def __init__(self, path: Path, poll_interval: float = 0.1) -> None:
        self.path = path
        self.name = path.name
        self.poll_interval = poll_interval

    async def lines(self) -> AsyncIterator[str]:
        with self.path.open(encoding="utf-8", errors="replace") as stream:
            while True:
                line = stream.readline()
                if line:
                    yield line
                    continue
                await asyncio.sleep(self.poll_interval)
                try:
                    if self.path.stat().st_size < stream.tell():
                        stream.seek(0)
                except FileNotFoundError:
                    pass
