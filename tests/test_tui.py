import asyncio
from pathlib import Path

from textual.widgets import DataTable, Input, Label

from logtui.sources import FileSource
from logtui.tui.app import DetailScreen, HelpScreen, LogTuiApp


async def test_live_table_pause_help_and_details(tmp_path: Path) -> None:
    path = tmp_path / "app.log"
    path.write_text(
        '{"level":"ERROR","service":"api","message":"Database timeout","request_id":"abc123"}\n',
        encoding="utf-8",
    )
    app = LogTuiApp([FileSource(path)], buffer_size=20)

    async with app.run_test() as pilot:
        await pilot.pause(0.1)
        assert app.query_one("#logs", DataTable).row_count == 1
        assert "1 event" in str(app.query_one("#stream-count", Label).render())

        await pilot.press("space")
        assert app.paused
        with path.open("a", encoding="utf-8") as stream:
            stream.write("another event\n")
        await asyncio.sleep(0.05)
        assert app.query_one("#logs", DataTable).row_count == 1

        await pilot.press("space")
        assert not app.paused
        assert app.query_one("#logs", DataTable).row_count == 2
        assert app._pending_count == 0

        app.action_help()
        await pilot.pause()
        assert isinstance(app.screen, HelpScreen)
        await pilot.press("escape")

        app.action_details()
        await pilot.pause()
        assert isinstance(app.screen, DetailScreen)


async def test_table_remains_visible_in_a_short_terminal(tmp_path: Path) -> None:
    path = tmp_path / "short.log"
    path.write_text('{"level":"INFO","message":"visible"}\n', encoding="utf-8")
    app = LogTuiApp([FileSource(path)])

    async with app.run_test(size=(100, 12)) as pilot:
        await pilot.pause(0.1)
        table = app.query_one("#logs", DataTable)
        assert table.row_count == 1
        assert table.size.height >= 3


async def test_pause_keeps_only_ring_buffer_capacity(tmp_path: Path) -> None:
    path = tmp_path / "busy.log"
    path.write_text("first\n", encoding="utf-8")
    app = LogTuiApp([FileSource(path)], buffer_size=2)

    async with app.run_test() as pilot:
        await pilot.pause(0.1)
        await pilot.press("space")
        with path.open("a", encoding="utf-8") as stream:
            stream.write("second\nthird\nfourth\n")
        await pilot.pause(0.1)

        assert len(app.entries) == 2
        assert app._pending_count == 3
        await pilot.press("space")
        assert app.query_one("#logs", DataTable).row_count == 2


async def test_search_filters_all_structured_log_values(tmp_path: Path) -> None:
    path = tmp_path / "search.log"
    path.write_text(
        '{"level":"INFO","message":"ready","request_id":"abc123"}\n'
        '{"level":"ERROR","message":"database timeout"}\n',
        encoding="utf-8",
    )
    app = LogTuiApp([FileSource(path)])

    async with app.run_test() as pilot:
        await pilot.pause(0.1)
        await pilot.press("/")
        assert app.query_one("#search-input", Input).has_class("visible")
        await pilot.press("a", "b", "c", "1", "2", "3", "enter")

        assert app.search_query == "abc123"
        assert app.query_one("#logs", DataTable).row_count == 1
        await pilot.press("escape")
        assert app.search_query == ""
        assert app.query_one("#logs", DataTable).row_count == 2


def test_duplicate_basenames_use_full_source_names(tmp_path: Path) -> None:
    first = tmp_path / "api" / "app.log"
    second = tmp_path / "worker" / "app.log"
    first.parent.mkdir()
    second.parent.mkdir()
    first.touch()
    second.touch()
    app = LogTuiApp([FileSource(first), FileSource(second)])

    assert app._display_name(str(first)) == str(first)
    assert app._display_name(str(second)) == str(second)
