import asyncio
from pathlib import Path

from textual.widgets import DataTable, Label

from logtui.tui.app import DetailScreen, HelpScreen, LogTuiApp


async def test_live_table_pause_help_and_details(tmp_path: Path) -> None:
    path = tmp_path / "app.log"
    path.write_text(
        '{"level":"ERROR","service":"api","message":"Database timeout","request_id":"abc123"}\n',
        encoding="utf-8",
    )
    app = LogTuiApp([path], buffer_size=20)

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
    app = LogTuiApp([path])

    async with app.run_test(size=(100, 12)) as pilot:
        await pilot.pause(0.1)
        table = app.query_one("#logs", DataTable)
        assert table.row_count == 1
        assert table.size.height >= 3
