import asyncio
import os
from collections.abc import AsyncIterator
from contextlib import suppress
from pathlib import Path
from typing import TextIO


class FileSource:
    """Read a file from the beginning, then follow appended lines."""

    def __init__(self, path: Path, poll_interval: float = 0.1) -> None:
        self.path = path
        self.name = str(path)
        self.poll_interval = poll_interval

    async def lines(self) -> AsyncIterator[str]:
        stream = self._open()
        try:
            while True:
                line = stream.readline()
                if line:
                    yield line
                    continue
                await asyncio.sleep(self.poll_interval)
                try:
                    path_stat = self.path.stat()
                    if self._was_replaced(stream, path_stat.st_ino):
                        stream.close()
                        stream = self._open()
                    elif path_stat.st_size < stream.tell():
                        stream.seek(0)
                except FileNotFoundError:
                    pass
        finally:
            stream.close()

    def _open(self) -> TextIO:
        return self.path.open(encoding="utf-8", errors="replace")

    @staticmethod
    def _was_replaced(stream: TextIO, path_inode: int) -> bool:
        with suppress(OSError):
            return os.fstat(stream.fileno()).st_ino != path_inode
        return False
