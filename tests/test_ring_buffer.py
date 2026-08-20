import pytest

from logtui.buffer import RingBuffer


def test_overflow_discards_oldest_items() -> None:
    buffer = RingBuffer[int](2)
    buffer.extend([1, 2, 3])
    assert list(buffer) == [2, 3]


def test_capacity_must_be_positive() -> None:
    with pytest.raises(ValueError):
        RingBuffer[int](0)
