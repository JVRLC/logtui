import asyncio
from pathlib import Path

from textual.widgets import DataTable, Input, Label

from logtui.sources import FileSource
from logtui.tui.app import DetailScreen, ExportScreen, HelpScreen, LogTuiApp


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


async def test_level_filtering_and_shortcuts(tmp_path: Path) -> None:
    path = tmp_path / "app.log"
    path.write_text(
        '{"level":"DEBUG","message":"dbg"}\n'
        '{"level":"INFO","message":"inf"}\n'
        '{"level":"WARN","message":"wrn"}\n'
        '{"level":"ERROR","message":"err"}\n',
        encoding="utf-8",
    )
    app = LogTuiApp([FileSource(path)])
    async with app.run_test() as pilot:
        await pilot.pause(0.1)
        assert app.query_one("#logs", DataTable).row_count == 4

        # Cycle level filter with 'l'
        await pilot.press("l")
        assert app.level_filter_index == 1  # DEBUG+
        assert app.query_one("#logs", DataTable).row_count == 4

        await pilot.press("l")
        assert app.level_filter_index == 2  # INFO+
        assert app.query_one("#logs", DataTable).row_count == 3

        await pilot.press("l")
        assert app.level_filter_index == 3  # WARN+
        assert app.query_one("#logs", DataTable).row_count == 2

        await pilot.press("l")
        assert app.level_filter_index == 4  # ERROR+
        assert app.query_one("#logs", DataTable).row_count == 1

        # Direct number shortcuts
        await pilot.press("0")
        assert app.level_filter_index == 0  # ALL
        assert app.query_one("#logs", DataTable).row_count == 4

        await pilot.press("3")
        assert app.level_filter_index == 3  # WARN+
        assert app.query_one("#logs", DataTable).row_count == 2

        await pilot.press("1")
        assert app.level_filter_index == 1

        await pilot.press("2")
        assert app.level_filter_index == 2

        await pilot.press("4")
        assert app.level_filter_index == 4


async def test_source_filtering_and_click(tmp_path: Path) -> None:
    first = tmp_path / "api.log"
    second = tmp_path / "worker.log"
    first.write_text('{"level":"INFO","message":"api event"}\n', encoding="utf-8")
    second.write_text('{"level":"INFO","message":"worker event"}\n', encoding="utf-8")
    app = LogTuiApp([FileSource(first), FileSource(second)])

    async with app.run_test() as pilot:
        await pilot.pause(0.1)
        assert app.query_one("#logs", DataTable).row_count == 2

        # Cycle source with 's'
        await pilot.press("s")
        assert app.active_source_index == 0
        assert app.query_one("#logs", DataTable).row_count == 1

        await pilot.press("s")
        assert app.active_source_index == 1
        assert app.query_one("#logs", DataTable).row_count == 1

        await pilot.press("s")
        assert app.active_source_index == -1
        assert app.query_one("#logs", DataTable).row_count == 2

        # Click on source-0 label in sidebar
        source_lbl = app.query_one("#source-0", Label)
        await pilot.click(source_lbl)
        assert app.active_source_index == 0
        assert app.query_one("#logs", DataTable).row_count == 1

        # Click again to toggle back to ALL
        await pilot.click(source_lbl)
        assert app.active_source_index == -1
        assert app.query_one("#logs", DataTable).row_count == 2


async def test_follow_mode_and_navigation(tmp_path: Path) -> None:
    path = tmp_path / "app.log"
    path.write_text(
        "line 1\nline 2\nline 3\nline 4\nline 5\n",
        encoding="utf-8",
    )
    app = LogTuiApp([FileSource(path)])

    async with app.run_test() as pilot:
        await pilot.pause(0.1)
        assert app.follow is True

        # Moving cursor up should disable follow
        await pilot.press("k")
        assert app.follow is False

        # Moving down back to bottom should re-enable follow
        for _ in range(5):
            await pilot.press("j")
        assert app.follow is True

        # 'f' key toggles follow
        await pilot.press("f")
        assert app.follow is False
        await pilot.press("f")
        assert app.follow is True

        # 'g' jumps to top and disables follow
        await pilot.press("g")
        assert app.follow is False
        assert app.query_one("#logs", DataTable).cursor_row == 0

        # 'G' jumps to bottom and re-enables follow
        await pilot.press("G")
        assert app.follow is True


async def test_detail_screen_and_copy(tmp_path: Path) -> None:
    path = tmp_path / "app.log"
    path.write_text(
        '{"timestamp":"2026-10-18T18:00:00.123Z","level":"INFO",'
        '"service":"api","message":"server started","tag":"prod"}\n',
        encoding="utf-8",
    )
    app = LogTuiApp([FileSource(path)])

    async with app.run_test() as pilot:
        await pilot.pause(0.1)
        await pilot.press("enter")
        assert isinstance(app.screen, DetailScreen)

        screen = app.screen
        screen.action_copy_raw()
        await pilot.press("escape")
        assert not isinstance(app.screen, DetailScreen)


async def test_source_error_state(tmp_path: Path) -> None:
    path = tmp_path / "app.log"
    path.write_text("initial\n", encoding="utf-8")
    app = LogTuiApp([FileSource(path)])

    async with app.run_test() as pilot:
        await pilot.pause(0.1)
        app._source_errors[str(path)] = "Permission denied"
        app._refresh_chrome()
        assert "SOURCE ERROR" in str(app.query_one("#stream-state", Label).render())


async def test_export_screen_and_action(tmp_path: Path) -> None:
    path = tmp_path / "app.log"
    path.write_text('{"level":"INFO","message":"ready"}\n', encoding="utf-8")
    app = LogTuiApp([FileSource(path)])

    async with app.run_test() as pilot:
        await pilot.pause(0.1)
        await pilot.press("e")
        assert isinstance(app.screen, ExportScreen)

        export_target = tmp_path / "out.jsonl"
        screen = app.screen
        screen.query_one("#export-input", Input).value = str(export_target)
        await pilot.press("enter")
        assert not isinstance(app.screen, ExportScreen)
        assert export_target.is_file()
        assert "ready" in export_target.read_text(encoding="utf-8")


async def test_multiline_aggregation_in_app(tmp_path: Path) -> None:
    path = tmp_path / "app.log"
    path.write_text(
        "2026-10-18 12:00:00 - ERROR - Exception occurred\n"
        "Traceback (most recent call last):\n"
        "  File 'app.py', line 10, in foo\n"
        "ZeroDivisionError: division by zero\n",
        encoding="utf-8",
    )
    app = LogTuiApp([FileSource(path)])

    async with app.run_test() as pilot:
        await pilot.pause(0.1)
        # Should be aggregated into 1 entry instead of 4 entries
        assert len(app.entries) == 1
        assert "ZeroDivisionError" in app.entries[0].message
        assert app.entries[0].level == "ERROR"


async def test_streaming_while_modal_open(tmp_path: Path) -> None:
    path = tmp_path / "app.log"
    path.write_text('{"level":"INFO","message":"first"}\n', encoding="utf-8")
    app = LogTuiApp([FileSource(path)])

    async with app.run_test() as pilot:
        await pilot.pause(0.1)

        # 1. Open HelpScreen and stream lines
        await pilot.press("question_mark")
        assert isinstance(app.screen, HelpScreen)
        with path.open("a", encoding="utf-8") as f:
            f.write('{"level":"ERROR","message":"second"}\n')
            f.flush()
        await pilot.pause(0.15)
        await pilot.press("escape")
        assert not isinstance(app.screen, HelpScreen)

        # 2. Open DetailScreen and stream lines
        await pilot.press("enter")
        assert isinstance(app.screen, DetailScreen)
        with path.open("a", encoding="utf-8") as f:
            f.write('{"level":"WARN","message":"third"}\n')
            f.flush()
        await pilot.pause(0.15)
        await pilot.press("escape")
        assert not isinstance(app.screen, DetailScreen)

        # Ensure main table updated without crashing
        table = app._query_main("#logs", DataTable)
        assert table.row_count >= 3


async def test_navigation_and_level_shortcuts(tmp_path: Path) -> None:
    path = tmp_path / "app.log"
    path.write_text(
        '{"level":"DEBUG","message":"d"}\n'
        '{"level":"INFO","message":"i"}\n'
        '{"level":"WARN","message":"w"}\n'
        '{"level":"ERROR","message":"e"}\n',
        encoding="utf-8",
    )
    app = LogTuiApp([FileSource(path)])

    async with app.run_test() as pilot:
        await pilot.pause(0.1)
        # Test navigation keys
        await pilot.press("g")
        assert not app.follow
        await pilot.press("G")
        assert app.follow
        await pilot.press("k")
        assert not app.follow
        await pilot.press("j")
        assert app.follow
        await pilot.press("f")
        assert not app.follow
        await pilot.press("f")
        assert app.follow

        # Test level number shortcuts 0..4
        await pilot.press("0")
        assert app.level_filter_index == 0
        await pilot.press("1")
        assert app.level_filter_index == 1
        await pilot.press("2")
        assert app.level_filter_index == 2
        await pilot.press("3")
        assert app.level_filter_index == 3
        await pilot.press("4")
        assert app.level_filter_index == 4
        await pilot.press("0")
        assert app.level_filter_index == 0
