import asyncio
import json
from pathlib import Path
from typing import Any

from rich.syntax import Syntax
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import DataTable, Footer, Header, Label, Static

from logtui.buffer import RingBuffer
from logtui.models import LogEntry
from logtui.parsing import AutoDetectParser
from logtui.sources import FileSource


class DetailScreen(ModalScreen[None]):
    BINDINGS = [Binding("escape", "dismiss", "Back"), Binding("q", "dismiss", "Back")]
    CSS = """
    DetailScreen { align: center middle; }
    #detail { width: 80%; height: 80%; padding: 1 2; border: round $accent; overflow: auto; }
    """

    def __init__(self, entry: LogEntry) -> None:
        super().__init__()
        self.entry = entry

    def compose(self) -> ComposeResult:
        payload = self.entry.model_dump(mode="json", exclude_none=True)
        yield Static(Syntax(json.dumps(payload, indent=2), "json"), id="detail")

    async def action_dismiss(self, result: None = None) -> None:
        self.dismiss(result)


class LogTuiApp(App[None]):
    TITLE = "LogTUI"
    SUB_TITLE = "Exploring live logs"
    CSS = """
    #layout { height: 1fr; }
    #status { height: 1; padding: 0 1; background: $panel; }
    DataTable { height: 1fr; }
    """
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("space", "toggle_pause", "Pause/resume"),
        Binding("enter", "details", "Details"),
    ]

    def __init__(self, paths: list[Path], buffer_size: int = 10_000) -> None:
        super().__init__()
        self.paths = paths
        self.entries: RingBuffer[LogEntry] = RingBuffer(buffer_size)
        self.parser = AutoDetectParser()
        self.paused = False
        self._pending: list[LogEntry] = []
        self._next_id = 0
        self._tasks: list[asyncio.Task[Any]] = []

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(id="layout"):
            yield DataTable(cursor_type="row", zebra_stripes=True, id="logs")
            yield Label("LIVE", id="status")
        yield Footer()

    async def on_mount(self) -> None:
        table = self.query_one("#logs", DataTable)
        table.add_columns("Time", "Level", "Service", "Source", "Message")
        for path in self.paths:
            self._tasks.append(asyncio.create_task(self._consume(FileSource(path))))

    async def _consume(self, source: FileSource) -> None:
        async for line in source.lines():
            entry = self.parser.parse(line, source.name)
            entry.id = self._next_id
            self._next_id += 1
            self.entries.append(entry)
            if self.paused:
                self._pending.append(entry)
            else:
                self._add_row(entry)

    def _add_row(self, entry: LogEntry) -> None:
        table = self.query_one("#logs", DataTable)
        timestamp = entry.timestamp.strftime("%H:%M:%S") if entry.timestamp else ""
        table.add_row(
            timestamp,
            entry.level or "",
            entry.service or "",
            entry.source,
            entry.message,
            key=str(entry.id),
        )
        overflow = table.row_count - self.entries.capacity
        if overflow > 0:
            for key in list(table.rows)[:overflow]:
                table.remove_row(key)
        if table.row_count:
            table.move_cursor(row=table.row_count - 1)

    def action_toggle_pause(self) -> None:
        self.paused = not self.paused
        status = self.query_one("#status", Label)
        if self.paused:
            status.update(f"PAUSED · {len(self._pending)} pending")
            return
        for entry in self._pending:
            self._add_row(entry)
        self._pending.clear()
        status.update("LIVE")

    def action_details(self) -> None:
        table = self.query_one("#logs", DataTable)
        if table.cursor_row < 0 or table.row_count == 0:
            return
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        entry_id = int(str(row_key.value))
        entry = next((item for item in self.entries if item.id == entry_id), None)
        if entry is not None:
            self.push_screen(DetailScreen(entry))

    def on_data_table_row_selected(self, _: DataTable.RowSelected) -> None:
        self.action_details()

    async def on_unmount(self) -> None:
        for task in self._tasks:
            task.cancel()
