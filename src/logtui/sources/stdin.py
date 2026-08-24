import asyncio
import sys
from collections.abc import AsyncIterator
from typing import TextIO


class StdinSource:
    """Read lines from standard input without blocking the TUI event loop."""

    name = "stdin"

    def __init__(self, stream: TextIO | None = None) -> None:
        self._stream = stream or sys.stdin

    async def lines(self) -> AsyncIterator[str]:
        while line := await asyncio.to_thread(self._stream.readline):
            yield line
