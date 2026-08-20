from collections import deque
from collections.abc import Iterable, Iterator
from typing import TypeVar

T = TypeVar("T")


class RingBuffer[T]:
    def __init__(self, capacity: int = 10_000) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be greater than zero")
        self.capacity = capacity
        self._items: deque[T] = deque(maxlen=capacity)

    def append(self, item: T) -> None:
        self._items.append(item)

    def extend(self, items: Iterable[T]) -> None:
        self._items.extend(items)

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self) -> Iterator[T]:
        return iter(self._items)

    def __getitem__(self, index: int) -> T:
        return self._items[index]
