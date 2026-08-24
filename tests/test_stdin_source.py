import io

from logtui.sources import StdinSource


async def test_reads_stdin_until_eof() -> None:
    source = StdinSource(io.StringIO("first\nsecond\n"))

    assert [line async for line in source.lines()] == ["first\n", "second\n"]
