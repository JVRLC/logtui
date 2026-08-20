from collections.abc import AsyncIterator
from typing import Protocol


class LogSource(Protocol):
    name: str

    def lines(self) -> AsyncIterator[str]: ...
